"""チャットAPIルーター"""

from fastapi import APIRouter, Depends, Query, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.chat import (
    ConversationHistoryResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.infrastructure.database import AsyncSessionLocal, get_db
from app.presentation.controllers.chat_controller import ChatController
from app.presentation.websocket.chat_handler import handle_websocket_chat

router = APIRouter()


@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
):
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
    "/sessions/{session_id}/history",
    response_model=ConversationHistoryResponse,
)
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    セッションの会話履歴を取得

    - **session_id**: セッションID
    """
    return await ChatController.get_history(session_id, db=db)


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str = Query(..., description="セッションID"),
    user_id: str = Query(
        default="default_user", description="ユーザーID（現在はデフォルト）"
    ),
):
    """
    WebSocketチャットエンドポイント

    リアルタイムでAIチャットボットと対話できます。
    ストリーミングレスポンスでAI回答をリアルタイムに受信できます。

    **接続方法:**
    ```
    ws://localhost:8000/api/chat/ws?session_id=sess_123&user_id=user_456
    ```

    **メッセージ形式:**
    ```json
    {
        "type": "message",
        "message": "こんにちは",
        "metadata": {}
    }
    ```

    **レスポンス形式:**
    - `connected`: 接続確立
    - `processing`: 処理開始
    - `chunk`: ストリーミングチャンク
    - `done`: ストリーミング完了
    - `saved`: 会話保存完了
    - `error`: エラー発生

    **例:**
    ```json
    {"type": "chunk", "content": "こんにちは"}
    {"type": "chunk", "content": "！"}
    {"type": "done", "message": "回答の生成が完了しました"}
    ```
    """
    # WebSocketではDependsが使えないため、データベースセッションを直接作成
    # WebSocket接続が維持されている間はセッションを保持する必要がある
    async with AsyncSessionLocal() as db:
        try:
            await handle_websocket_chat(
                websocket=websocket,
                session_id=session_id,
                user_id=user_id,
                db=db,
            )
        except Exception:
            # エラーが発生した場合はロールバック
            await db.rollback()
            raise
        finally:
            # 接続が終了したときにセッションを閉じる（async withで自動的に閉じられる）
            pass
