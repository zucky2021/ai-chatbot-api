"""ヘルスチェックAPIルーター"""

from fastapi import APIRouter

from app.infrastructure.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def health_check():
    """ヘルスチェックエンドポイント"""
    logger.debug("health_check")
    return {"status": "healthy", "service": "AI Chatbot API"}


@router.get("/ready")
async def readiness_check():
    """レディネスチェック（本番環境での確認用）"""
    logger.debug("readiness_check")
    return {"status": "ready"}
