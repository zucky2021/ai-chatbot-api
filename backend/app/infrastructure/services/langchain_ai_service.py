"""LangChain AIサービス実装"""

from collections.abc import AsyncGenerator
from typing import Any, cast

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings
from app.infrastructure.langfuse_handler import create_langfuse_handler
from app.infrastructure.logging import get_logger
from app.infrastructure.services.chunk_utils import normalize_chunk_content

logger = get_logger(__name__)


class LangChainAIService(IAIService):
    """LangChainを使用したAIサービス実装"""

    def __init__(self) -> None:
        """LangChain AIサービスを初期化"""
        model_name = settings.GOOGLE_AI_MODEL
        logger.info("langchain_ai_model_initializing", model_name=model_name)

        # ChatGoogleGenerativeAIを初期化
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_AI_API_KEY,
            temperature=settings.LANGCHAIN_TEMPERATURE,
            convert_system_message_to_human=True,
        )

        # プロンプトテンプレートを作成
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", settings.LANGCHAIN_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        # メモリタイプの設定
        self._memory_type = settings.LANGCHAIN_MEMORY_TYPE
        self._max_tokens = settings.LANGCHAIN_MAX_TOKENS

        # LangFuseコールバックハンドラーを初期化
        self._langfuse_handler = create_langfuse_handler()

        logger.info(
            "langchain_ai_service_initialized",
            model_name=model_name,
            memory_type=self._memory_type,
            max_tokens=self._max_tokens,
            langfuse_enabled=settings.LANGFUSE_ENABLED,
        )

    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        try:
            # コンテキストから会話履歴を構築
            history = self._build_history_from_context(context)

            # プロンプトテンプレートを使用してチェーンを作成
            chain = self._prompt | self._llm

            # メッセージ履歴を取得
            messages = history.messages if hasattr(history, "messages") else []

            # LangFuseコールバックを設定
            config: dict[str, Any] = {}
            if self._langfuse_handler:
                config["callbacks"] = [self._langfuse_handler]

            # チェーンを実行
            runnable_config: RunnableConfig = cast(RunnableConfig, config)
            response = await chain.ainvoke(
                {"input": message.content, "history": messages},
                config=runnable_config,
            )

            # メモリに会話を保存
            history.add_user_message(message.content)
            response_content = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
            # response.contentがリストの場合は文字列に変換
            if isinstance(response_content, list):
                response_content = "".join(
                    str(item) if not isinstance(item, str) else item
                    for item in response_content
                )
            history.add_ai_message(str(response_content))

            return str(response_content)
        except Exception as e:
            logger.error(
                "langchain_ai_response_generation_error",
                error=str(e),
                message_sender=message.sender,
                exc_info=True,
            )
            raise RuntimeError(f"AIレスポンス生成エラー: {str(e)}")

    async def generate_stream(
        self, message: Message, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """AIレスポンスをストリームで生成"""
        try:
            # コンテキストから会話履歴を構築
            history = self._build_history_from_context(context)

            # プロンプトテンプレートを使用してチェーンを作成
            chain = self._prompt | self._llm

            # メッセージ履歴を取得
            messages = history.messages if hasattr(history, "messages") else []

            # LangFuseコールバックを設定
            config: dict[str, Any] = {}
            if self._langfuse_handler:
                config["callbacks"] = [self._langfuse_handler]

            # ストリーミングでレスポンスを取得
            full_response = ""
            runnable_config: RunnableConfig = cast(RunnableConfig, config)
            async for chunk in chain.astream(
                {"input": message.content, "history": messages},
                config=runnable_config,
            ):
                if hasattr(chunk, "content") and chunk.content:
                    content = normalize_chunk_content(chunk.content)

                    # 空のコンテンツはスキップ
                    if not content:
                        continue

                    full_response += content
                    yield content

            # メモリに会話を保存
            if full_response:
                history.add_user_message(message.content)
                history.add_ai_message(full_response)
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "langchain_ai_stream_generation_error",
                error=error_msg,
                message_sender=message.sender,
                exc_info=True,
            )
            raise RuntimeError(f"AIストリーム生成エラー: {error_msg}")

    def _build_history_from_context(
        self, context: str
    ) -> BaseChatMessageHistory:
        """
        コンテキスト文字列から会話履歴を構築してメッセージ履歴を作成

        Args:
            context: 会話履歴を含むコンテキスト文字列
                "User: ...\nAI: ...\nUser: ...\nAI: ..." の形式

        Returns:
            コンテキストから解析された会話履歴を含むメッセージ履歴。
            contextが空の場合は空の履歴を返す。
            history.messagesでメッセージリストにアクセス可能。
        """
        # ChatMessageHistoryを作成
        history = ChatMessageHistory()

        if not context:
            return history

        # コンテキストを解析して会話履歴を構築
        # 形式: "User: ...\nAI: ...\nUser: ...\nAI: ..."
        lines = context.strip().split("\n")
        current_user_message = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("User:"):
                # 前のユーザーメッセージがあれば保存
                if current_user_message:
                    history.add_user_message(current_user_message)
                current_user_message = line.replace("User:", "").strip()
            elif line.startswith("AI:"):
                ai_message = line.replace("AI:", "").strip()
                if current_user_message:
                    history.add_user_message(current_user_message)
                    history.add_ai_message(ai_message)
                    current_user_message = None
                else:
                    # ユーザーメッセージがない場合はAIメッセージのみ追加
                    history.add_ai_message(ai_message)

        # 最後のユーザーメッセージがあれば保存
        if current_user_message:
            history.add_user_message(current_user_message)

        return history
