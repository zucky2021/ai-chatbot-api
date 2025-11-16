"""チャットユースケース"""

from datetime import datetime

from app.domain.entities.conversation import Conversation
from app.domain.entities.session import Session
from app.domain.repositories import IConversationRepository, ISessionRepository
from app.domain.services import IAIService, ICacheService
from app.domain.value_objects.message import Message


class SendMessageUseCase:
    """メッセージ送信ユースケース"""

    def __init__(
        self,
        conversation_repository: IConversationRepository,
        session_repository: ISessionRepository,
        ai_service: IAIService,
        cache_service: ICacheService,
    ):
        self._conversation_repo = conversation_repository
        self._session_repo = session_repository
        self._ai_service = ai_service
        self._cache_service = cache_service

    async def execute(
        self,
        user_id: str,
        session_id: str,
        message_content: str,
        metadata: dict | None = None,
    ) -> Conversation:
        """
        メッセージを送信し、AIレスポンスを取得

        Args:
            user_id: ユーザーID
            session_id: セッションID
            message_content: メッセージ内容
            metadata: メタデータ

        Returns:
            作成されたConversationエンティティ

        Raises:
            ValueError: 無効なパラメータの場合
            RuntimeError: セッションが見つからない場合
        """
        # セッションの存在確認
        session = await self._session_repo.get_by_id(session_id)
        if not session:
            raise RuntimeError(f"セッションが見つかりません: {session_id}")

        if not session.is_active():
            raise RuntimeError(
                f"セッションがアクティブではありません: {session_id}"
            )

        # キャッシュから会話履歴を取得（コンテキスト用）
        cache_key = f"conversation:{session_id}"
        context = await self._cache_service.get(cache_key) or ""

        # メッセージ値オブジェクトを作成
        message = Message(
            content=message_content,
            timestamp=datetime.now(),
            sender=user_id,
            metadata=metadata,
        )

        # AIレスポンスを生成
        ai_response = await self._ai_service.generate_response(
            message, context
        )

        # Conversationエンティティを作成
        conversation = Conversation(
            id=None,
            user_id=user_id,
            session_id=session_id,
            message=message.content,
            response=ai_response,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=None,
        )

        # 会話を保存
        saved_conversation = await self._conversation_repo.create(conversation)

        # キャッシュに会話履歴を更新
        updated_context = (
            f"{context}\nUser: {message.content}\nAI: {ai_response}"
        )
        await self._cache_service.set(
            cache_key,
            updated_context[-5000:],  # 最新5000文字のみ保持
            ttl=3600,
        )

        return saved_conversation


class CreateSessionUseCase:
    """セッション作成ユースケース"""

    def __init__(self, session_repository: ISessionRepository):
        self._session_repo = session_repository

    async def execute(
        self, user_id: str, session_id: str, metadata: dict | None = None
    ) -> Session:
        """
        新しいセッションを作成

        Args:
            user_id: ユーザーID
            session_id: セッションID
            metadata: メタデータ

        Returns:
            作成されたSessionエンティティ

        Raises:
            ValueError: 無効なパラメータの場合
        """
        from app.domain.entities.session import SessionStatus

        session = Session(
            session_id=session_id,
            user_id=user_id,
            status=SessionStatus.ACTIVE,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=None,
            expires_at=None,
        )

        return await self._session_repo.create(session)


class GetConversationHistoryUseCase:
    """会話履歴取得ユースケース"""

    def __init__(self, conversation_repository: IConversationRepository):
        self._conversation_repo = conversation_repository

    async def execute(self, session_id: str) -> list[Conversation]:
        """
        セッションIDで会話履歴を取得

        Args:
            session_id: セッションID

        Returns:
            会話履歴のリスト
        """
        return await self._conversation_repo.get_by_session_id(session_id)
