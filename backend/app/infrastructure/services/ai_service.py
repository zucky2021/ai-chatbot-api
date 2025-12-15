"""Google AI Studioサービス実装（LangChain使用）"""

from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings
from app.infrastructure.logging import get_logger
from app.infrastructure.services.chunk_utils import normalize_chunk_content

logger = get_logger(__name__)


class GoogleAIService(IAIService):
    """Google AI Studioサービス実装（LangChain使用）"""

    def __init__(self) -> None:
        # モデル名は設定から取得（デフォルト: gemini-flash-latest）
        model_name = settings.GOOGLE_AI_MODEL
        logger.info("google_ai_model_initializing", model_name=model_name)

        # ChatGoogleGenerativeAIを初期化
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_AI_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True,
        )

        logger.info("google_ai_service_initialized", model_name=model_name)

    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        try:
            prompt = self._build_prompt(message, context)
            messages = [HumanMessage(content=prompt)]
            response = await self._llm.ainvoke(messages)
            content = response.content
            if isinstance(content, str):
                return content
            return str(content)
        except Exception as e:
            raise RuntimeError(f"AIレスポンス生成エラー: {str(e)}")

    async def generate_stream(
        self, message: Message, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """AIレスポンスをストリームで生成"""
        try:
            prompt = self._build_prompt(message, context)
            messages = [HumanMessage(content=prompt)]

            async for chunk in self._llm.astream(messages):
                if chunk.content:
                    content = normalize_chunk_content(chunk.content)

                    # 空のコンテンツはスキップ
                    if not content:
                        continue

                    yield content
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "ai_stream_generation_error",
                error=error_msg,
                message_sender=message.sender,
                exc_info=True,
            )
            raise RuntimeError(f"AIストリーム生成エラー: {error_msg}")

    def _build_prompt(self, message: Message, context: str = "") -> str:
        """プロンプトを構築"""
        if context:
            return f"{context}\n\nUser: {message.content}\nAI:"
        return f"User: {message.content}\nAI:"
