"""WebSocketチャットハンドラー"""

import asyncio
from datetime import datetime
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.message import Message
from app.infrastructure.dependencies import (
    get_ai_service,
    get_cache_service,
    get_conversation_repository,
    get_session_repository,
)
from app.infrastructure.logging import get_logger
from app.presentation.websocket.connection_manager import connection_manager

# ロガーの設定
logger = get_logger(__name__)


async def handle_websocket_chat(
    websocket: WebSocket,
    session_id: str,
    user_id: str = "default_user",  # TODO: 認証機能実装後に置き換え
    db: AsyncSession | None = None,
) -> None:
    """
    WebSocketチャットハンドラー

    Args:
        websocket: WebSocket接続
        session_id: セッションID
        user_id: ユーザーID（現在はデフォルト）
        db: データベースセッション

    Raises:
        WebSocketDisconnect: 接続が切断された場合
    """
    # 接続を確立（FastAPI公式ドキュメントに従って、accept()を最初に呼び出す）
    await connection_manager.connect(websocket, session_id)

    try:
        # セッションの存在確認（リトライ付き）
        logger.info(
            "websocket_session_validation_started", session_id=session_id
        )
        session_repo = get_session_repository()
        session = None
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            session = await session_repo.get_by_id(session_id)
            if session:
                logger.info(
                    "websocket_session_found",
                    session_id=session_id,
                    status=session.status.value,
                )
                break
            if attempt < max_retries - 1:
                logger.warning(
                    "websocket_session_not_found_retrying",
                    session_id=session_id,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )
                await asyncio.sleep(retry_delay)

        if not session:
            logger.error(
                "websocket_session_not_found",
                session_id=session_id,
                message="全試行失敗",
            )
            try:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"セッションが見つかりません: {session_id}",
                    },
                    websocket,
                )
            except Exception:
                pass  # 接続が既に閉じられている場合は無視
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            except Exception:
                pass  # 既に閉じられている場合は無視
            return

        if not session.is_active():
            try:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"セッションがアクティブではありません: {session_id}",
                    },
                    websocket,
                )
            except Exception:
                pass  # 接続が既に閉じられている場合は無視
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            except Exception:
                pass  # 既に閉じられている場合は無視
            return

        # 依存性を注入
        logger.debug("websocket_dependencies_injected", session_id=session_id)
        conversation_repo = await get_conversation_repository(db)
        ai_service = get_ai_service()
        cache_service = get_cache_service()

        # 接続成功を通知
        await connection_manager.send_personal_message(
            {
                "type": "connected",
                "session_id": session_id,
                "message": "WebSocket接続が確立されました",
            },
            websocket,
        )
        logger.info("websocket_connection_notified", session_id=session_id)

        # メインループ（FastAPI公式ドキュメントに従って、try-except WebSocketDisconnectで囲む）
        logger.info("websocket_message_loop_started", session_id=session_id)
        try:
            while True:
                # クライアントからのメッセージを受信
                data = await websocket.receive_json()

                # メッセージタイプに応じて処理
                message_type = data.get("type", "message")

                if message_type == "message":
                    await _handle_message(
                        websocket=websocket,
                        data=data,
                        session_id=session_id,
                        user_id=user_id,
                        conversation_repo=conversation_repo,
                        session_repo=session_repo,
                        ai_service=ai_service,
                        cache_service=cache_service,
                    )
                elif message_type == "ping":
                    # ハートビート（接続維持）
                    await connection_manager.send_personal_message(
                        {"type": "pong"}, websocket
                    )
                else:
                    await connection_manager.send_personal_message(
                        {
                            "type": "error",
                            "message": f"不明なメッセージタイプ: {message_type}",
                        },
                        websocket,
                    )
        except WebSocketDisconnect:
            # クライアントが接続を切断した場合（正常な切断）
            logger.info(
                "websocket_disconnected",
                session_id=session_id,
                user_id=user_id,
                message="正常な切断",
            )
        except json.JSONDecodeError as e:
            logger.warning("websocket_invalid_json", error=str(e))
            try:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "無効なJSON形式です。正しい形式でメッセージを送信してください。",
                        "error_code": "INVALID_JSON",
                    },
                    websocket,
                )
            except Exception:
                pass  # 接続が閉じられている場合は無視
        except Exception as e:
            logger.error(
                "websocket_message_processing_error",
                session_id=session_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            try:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "メッセージ処理中にエラーが発生しました。しばらくしてから再試行してください。",
                        "error_code": "PROCESSING_ERROR",
                    },
                    websocket,
                )
            except Exception:
                pass  # 接続が閉じられている場合は無視

    except WebSocketDisconnect:
        # クライアントが接続を切断した場合（正常な切断）
        logger.info(
            "websocket_disconnected",
            session_id=session_id,
            user_id=user_id,
            message="正常な切断",
        )
    except Exception as e:
        logger.error(
            "websocket_handler_error",
            session_id=session_id,
            user_id=user_id,
            error=str(e),
            exc_info=True,
        )
    finally:
        # 接続を切断
        connection_manager.disconnect(websocket, session_id)
        logger.debug(
            "websocket_connection_cleanup",
            session_id=session_id,
            remaining_connections=connection_manager.get_connection_count(
                session_id
            ),
        )


async def _handle_message(
    websocket: WebSocket,
    data: dict[str, Any],
    session_id: str,
    user_id: str,
    conversation_repo: Any,
    session_repo: Any,
    ai_service: Any,
    cache_service: Any,
) -> None:
    """
    メッセージを処理してストリーミングレスポンスを送信

    Args:
        websocket: WebSocket接続
        data: 受信したデータ
        session_id: セッションID
        user_id: ユーザーID
        conversation_repo: 会話リポジトリ
        session_repo: セッションリポジトリ
        ai_service: AIサービス
        cache_service: キャッシュサービス
    """
    message_content = data.get("message", "").strip()
    metadata = data.get("metadata")

    # メッセージのバリデーション
    if not message_content:
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "message": "メッセージが空です",
            },
            websocket,
        )
        return

    if len(message_content) > 10000:
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "message": "メッセージが長すぎます（最大10000文字）",
            },
            websocket,
        )
        return

    try:
        # 処理開始を通知
        await connection_manager.send_personal_message(
            {
                "type": "processing",
                "message": "AIが回答を生成中です...",
            },
            websocket,
        )

        # キャッシュから会話履歴を取得（コンテキスト用）
        cache_key = f"conversation:{session_id}"
        context = await cache_service.get(cache_key) or ""

        # メッセージ値オブジェクトを作成
        message = Message(
            content=message_content,
            timestamp=datetime.now(),
            sender=user_id,
            metadata=metadata,
        )

        # ストリーミングでAIレスポンスを生成
        full_response = ""
        async for chunk in ai_service.generate_stream(message, context):
            if chunk:
                full_response += chunk
                await connection_manager.send_personal_message(
                    {"type": "chunk", "content": chunk}, websocket
                )

        # ストリーミング完了を通知
        await connection_manager.send_personal_message(
            {
                "type": "done",
                "message": "回答の生成が完了しました",
            },
            websocket,
        )

        # 会話を保存
        from app.domain.entities.conversation import Conversation

        conversation = Conversation(
            id=None,
            user_id=user_id,
            session_id=session_id,
            message=message.content,
            response=full_response,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=None,
        )

        saved_conversation = await conversation_repo.create(conversation)

        # キャッシュに会話履歴を更新
        updated_context = (
            f"{context}\nUser: {message.content}\nAI: {full_response}"
        )
        await cache_service.set(
            cache_key,
            updated_context[-5000:],  # 最新5000文字のみ保持
            ttl=3600,
        )

        # 保存完了を通知
        await connection_manager.send_personal_message(
            {
                "type": "saved",
                "conversation_id": saved_conversation.id,
                "message": "会話が保存されました",
            },
            websocket,
        )

    except Exception as e:
        error_message = str(e)

        # モデル名関連のエラーの場合は、より分かりやすいメッセージを返す
        if "404" in error_message and "model" in error_message.lower():
            user_friendly_message = "AIモデルの設定に問題があります。管理者にお問い合わせください。"
        elif "API" in error_message or "api_key" in error_message.lower():
            user_friendly_message = "AIサービスの認証に問題があります。管理者にお問い合わせください。"
        else:
            user_friendly_message = "メッセージ処理中にエラーが発生しました。しばらくしてから再試行してください。"

        logger.error(
            "websocket_message_error",
            session_id=session_id,
            user_id=user_id,
            message_length=len(message_content),
            error=error_message,
            exc_info=True,
        )
        await connection_manager.send_personal_message(
            {
                "type": "error",
                "message": user_friendly_message,
                "error_code": "MESSAGE_PROCESSING_ERROR",
            },
            websocket,
        )
