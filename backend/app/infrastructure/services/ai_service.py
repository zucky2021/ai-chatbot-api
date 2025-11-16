"""Google AI Studioサービス実装（LangChain使用）"""

from collections.abc import AsyncGenerator
import logging

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)


class GoogleAIService(IAIService):
    """Google AI Studioサービス実装（LangChain使用）"""

    def __init__(self):
        # モデル名は設定から取得（デフォルト: gemini-flash-latest）
        model_name = settings.GOOGLE_AI_MODEL
        logger.info(f"Google AIモデルを初期化: {model_name}")

        # ChatGoogleGenerativeAIを初期化
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_AI_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True,
        )

        logger.info("Google AIサービスが初期化されました（LangChain使用）")

    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        try:
            prompt = self._build_prompt(message, context)
            messages = [HumanMessage(content=prompt)]
            response = await self._llm.ainvoke(messages)
            return response.content
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
                    yield chunk.content
        except Exception as e:
            error_msg = str(e)
            logger.error(f"AIストリーム生成エラー: {error_msg}")
            raise RuntimeError(f"AIストリーム生成エラー: {error_msg}")

    def _build_prompt(self, message: Message, context: str = "") -> str:
        """プロンプトを構築"""
        if context:
            return f"{context}\n\nUser: {message.content}\nAI:"
        return f"User: {message.content}\nAI:"
