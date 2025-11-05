"""チャットAPIルーター"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.chat import (
    ConversationHistoryResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.infrastructure.database import get_db
from app.presentation.controllers.chat_controller import ChatController

router = APIRouter()


@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, db: AsyncSession = Depends(get_db)):
    """
    メッセージを送信してAIレスポンスを取得

    - **message**: メッセージ内容（1-10000文字）
    - **session_id**: セッションID
    - **metadata**: メタデータ（オプション）
    """
    return await ChatController.send_message(request, db=db)


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    新しいチャットセッションを作成

    - **session_id**: セッションID（省略時は自動生成）
    - **metadata**: メタデータ（オプション）
    """
    return await ChatController.create_session(request)


@router.get(
    "/sessions/{session_id}/history", response_model=ConversationHistoryResponse
)
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    セッションの会話履歴を取得

    - **session_id**: セッションID
    """
    return await ChatController.get_history(session_id, db=db)
