"""Google AI Studioサービス実装"""

from collections.abc import AsyncGenerator

import google.generativeai as genai

from app.application.interfaces.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings


class GoogleAIService(IAIService):
    """Google AI Studioサービス実装"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self._model = genai.GenerativeModel("gemini-pro")

    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        try:
            prompt = self._build_prompt(message, context)
            response = await self._model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"AIレスポンス生成エラー: {str(e)}")

    async def generate_stream(
        self, message: Message, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """AIレスポンスをストリームで生成"""
        try:
            prompt = self._build_prompt(message, context)
            response = await self._model.generate_content_async(
                prompt, stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise RuntimeError(f"AIストリーム生成エラー: {str(e)}")

    def _build_prompt(self, message: Message, context: str = "") -> str:
        """プロンプトを構築"""
        if context:
            return f"{context}\n\nUser: {message.content}\nAI:"
        return f"User: {message.content}\nAI:"
