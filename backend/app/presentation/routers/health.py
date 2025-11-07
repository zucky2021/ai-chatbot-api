"""ヘルスチェックAPIルーター"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "AI Chatbot API"}


@router.get("/ready")
async def readiness_check():
    """レディネスチェック（本番環境での確認用）"""
    return {"status": "ready"}
