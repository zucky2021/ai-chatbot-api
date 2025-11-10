"""Google AI Studioサービス実装"""

from collections.abc import AsyncGenerator
import logging

import google.generativeai as genai

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)


class GoogleAIService(IAIService):
    """Google AI Studioサービス実装"""

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        # モデル名は設定から取得（デフォルト: gemini-flash-latest）
        model_name = settings.GOOGLE_AI_MODEL
        logger.info(f"Google AIモデルを初期化: {model_name}")

        # 利用可能なモデルを確認（INFOレベルで出力して確認しやすくする）
        try:
            all_models = list(genai.list_models())
            # generateContentをサポートするモデルのみをフィルタリング
            supported_models = [
                m.name
                for m in all_models
                if "generateContent" in m.supported_generation_methods
            ]
            logger.info(
                f"利用可能なモデル（generateContent対応）: {supported_models}"
            )
            model_names = [m.name for m in all_models]
            if model_name not in model_names:
                logger.warning(
                    f"指定されたモデル '{model_name}' が利用可能なモデルリストにありません。"
                    f"利用可能なモデル: {supported_models}"
                )
        except Exception as e:
            logger.warning(f"利用可能なモデルの取得に失敗: {str(e)}")

        self._model = genai.GenerativeModel(model_name)

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
            error_msg = str(e)
            # モデルが見つからない場合の詳細なエラーメッセージ
            if "404" in error_msg and "model" in error_msg.lower():
                try:
                    available_models = [m.name for m in genai.list_models()]
                    logger.error(
                        f"モデル '{settings.GOOGLE_AI_MODEL}' が見つかりません。"
                        f"利用可能なモデル: {available_models}"
                    )
                except Exception:
                    pass
            raise RuntimeError(f"AIストリーム生成エラー: {error_msg}")

    def _build_prompt(self, message: Message, context: str = "") -> str:
        """プロンプトを構築"""
        if context:
            return f"{context}\n\nUser: {message.content}\nAI:"
        return f"User: {message.content}\nAI:"
