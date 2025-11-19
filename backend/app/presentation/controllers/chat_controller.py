"""チャットコントローラー"""

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.dependencies import (
    get_ai_service,
    get_cache_service,
    get_conversation_repository,
    get_session_repository,
)
from app.infrastructure.logging import get_logger
from app.presentation.middleware.error_handler import AppError
from app.presentation.models.error import ErrorCode
from app.usecase.dto.chat import (
    ConversationHistoryResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.usecase.use_cases.chat import (
    CreateSessionUseCase,
    GetConversationHistoryUseCase,
    SendMessageUseCase,
)

logger = get_logger(__name__)


class ChatController:
    """チャットコントローラー"""

    @staticmethod
    async def send_message(
        request: SendMessageRequest,
        user_id: str = "default_user",  # TODO: 認証機能実装後に置き換え
        db: AsyncSession = Depends(get_db),
    ) -> SendMessageResponse:
        """
        メッセージを送信

        Args:
            request: メッセージ送信リクエスト
            user_id: ユーザーID（現在はデフォルト）
            db: データベースセッション

        Returns:
            メッセージ送信レスポンス
        """
        logger.info(
            "send_message_started",
            user_id=user_id,
            session_id=request.session_id,
            message_length=len(request.message),
        )

        try:
            # 依存性を注入
            conversation_repo = await get_conversation_repository(db)
            session_repo = get_session_repository()
            ai_service = get_ai_service()
            cache_service = get_cache_service()

            # ユースケースを実行
            use_case = SendMessageUseCase(
                conversation_repository=conversation_repo,
                session_repository=session_repo,
                ai_service=ai_service,
                cache_service=cache_service,
            )

            conversation = await use_case.execute(
                user_id=user_id,
                session_id=request.session_id,
                message_content=request.message,
                metadata=request.metadata,
            )

            logger.info(
                "send_message_completed",
                user_id=user_id,
                session_id=request.session_id,
                conversation_id=conversation.id,
            )

            return SendMessageResponse(
                conversation_id=conversation.id,
                message=conversation.message,
                response=conversation.response or "",
                session_id=conversation.session_id,
                created_at=conversation.created_at or conversation.updated_at,
            )
        except ValueError as e:
            logger.warning(
                "send_message_validation_error",
                user_id=user_id,
                session_id=request.session_id,
                error=str(e),
            )
            raise AppError(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=str(e),
                details={"user_id": user_id, "session_id": request.session_id},
            )
        except RuntimeError as e:
            logger.warning(
                "send_message_not_found",
                user_id=user_id,
                session_id=request.session_id,
                error=str(e),
            )
            raise AppError(
                error_code=ErrorCode.INVALID_SESSION,
                message=str(e),
                details={"user_id": user_id, "session_id": request.session_id},
            )
        except Exception as e:
            logger.error(
                "send_message_error",
                user_id=user_id,
                session_id=request.session_id,
                error=str(e),
                exc_info=True,
            )
            raise AppError(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="メッセージの送信に失敗しました",
                details={"user_id": user_id, "session_id": request.session_id},
            )

    @staticmethod
    async def create_session(
        request: CreateSessionRequest,
        user_id: str = "default_user",  # TODO: 認証機能実装後に置き換え
    ) -> CreateSessionResponse:
        """
        セッションを作成

        Args:
            request: セッション作成リクエスト
            user_id: ユーザーID（現在はデフォルト）

        Returns:
            セッション作成レスポンス
        """
        logger.info("create_session_started", user_id=user_id)

        try:
            session_repo = get_session_repository()
            use_case = CreateSessionUseCase(session_repository=session_repo)

            # セッションIDが指定されていない場合は自動生成
            session_id = request.session_id or f"sess_{uuid.uuid4().hex[:12]}"

            session = await use_case.execute(
                user_id=user_id,
                session_id=session_id,
                metadata=request.metadata,
            )

            logger.info(
                "create_session_completed",
                user_id=user_id,
                session_id=session.session_id,
            )

            return CreateSessionResponse(
                session_id=session.session_id,
                status=session.status.value,
                created_at=session.created_at or session.updated_at,
            )
        except ValueError as e:
            logger.warning(
                "create_session_validation_error",
                user_id=user_id,
                error=str(e),
            )
            raise AppError(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=str(e),
                details={"user_id": user_id},
            )
        except Exception as e:
            logger.error(
                "create_session_error",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise AppError(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="セッションの作成に失敗しました",
                details={"user_id": user_id},
            )

    @staticmethod
    async def get_history(
        session_id: str,
        user_id: str = "default_user",  # TODO: 認証機能実装後に置き換え
        db: AsyncSession = Depends(get_db),
    ) -> ConversationHistoryResponse:
        """
        会話履歴を取得

        Args:
            session_id: セッションID
            user_id: ユーザーID（現在はデフォルト）
            db: データベースセッション

        Returns:
            会話履歴レスポンス
        """
        logger.info(
            "get_history_started", user_id=user_id, session_id=session_id
        )

        try:
            conversation_repo = await get_conversation_repository(db)
            use_case = GetConversationHistoryUseCase(
                conversation_repository=conversation_repo
            )

            conversations = await use_case.execute(session_id=session_id)

            logger.info(
                "get_history_completed",
                user_id=user_id,
                session_id=session_id,
                count=len(conversations),
            )

            return ConversationHistoryResponse(
                conversations=[
                    {
                        "id": conv.id,
                        "user_id": conv.user_id,
                        "session_id": conv.session_id,
                        "message": conv.message,
                        "response": conv.response,
                        "metadata": conv.metadata,
                        "created_at": conv.created_at.isoformat()
                        if conv.created_at
                        else None,
                        "updated_at": conv.updated_at.isoformat()
                        if conv.updated_at
                        else None,
                    }
                    for conv in conversations
                ]
            )
        except Exception as e:
            logger.error(
                "get_history_error",
                user_id=user_id,
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            raise AppError(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="会話履歴の取得に失敗しました",
                details={"user_id": user_id, "session_id": session_id},
            )
