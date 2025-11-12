"""LangChain AIサービス実装"""

from collections.abc import AsyncGenerator
import logging

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)


class LangChainAIService(IAIService):
    """LangChainを使用したAIサービス実装"""

    def __init__(self):
        """LangChain AIサービスを初期化"""
        model_name = settings.GOOGLE_AI_MODEL
        logger.info(f"LangChain AIモデルを初期化: {model_name}")

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

        logger.info(
            f"LangChain AIサービスが初期化されました (メモリタイプ: {self._memory_type})"
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

            # チェーンを実行
            response = await chain.ainvoke(
                {"input": message.content, "history": messages}
            )

            # メモリに会話を保存
            history.add_user_message(message.content)
            if hasattr(response, "content"):
                history.add_ai_message(response.content)
            else:
                history.add_ai_message(str(response))

            return (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
        except Exception as e:
            logger.error(f"LangChain AIレスポンス生成エラー: {str(e)}")
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

            # ストリーミングでレスポンスを取得
            full_response = ""
            async for chunk in chain.astream(
                {"input": message.content, "history": messages}
            ):
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    full_response += content
                    yield content

            # メモリに会話を保存
            if full_response:
                history.add_user_message(message.content)
                history.add_ai_message(full_response)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LangChain AIストリーム生成エラー: {error_msg}")
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
