"""PostgreSQL会話リポジトリ実装"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import IConversationRepository
from app.domain.entities.conversation import Conversation
from app.models.postgres import Conversation as ConversationModel


class PostgresConversationRepository(IConversationRepository):
    """PostgreSQL会話リポジトリ実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, conversation: Conversation) -> Conversation:
        """会話を作成"""
        db_conversation = ConversationModel(
            user_id=conversation.user_id,
            session_id=conversation.session_id,
            message=conversation.message,
            response=conversation.response,
            metadata_json=conversation.metadata,
        )
        self._session.add(db_conversation)
        await self._session.commit()
        await self._session.refresh(db_conversation)

        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            session_id=db_conversation.session_id,
            message=db_conversation.message,
            response=db_conversation.response,
            metadata=db_conversation.metadata_json,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
        )

    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        """IDで会話を取得"""
        result = await self._session.execute(
            select(ConversationModel).where(
                ConversationModel.id == conversation_id
            )
        )
        db_conversation = result.scalar_one_or_none()

        if not db_conversation:
            return None

        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            session_id=db_conversation.session_id,
            message=db_conversation.message,
            response=db_conversation.response,
            metadata=db_conversation.metadata_json,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
        )

    async def get_by_session_id(self, session_id: str) -> list[Conversation]:
        """セッションIDで会話を取得"""
        result = await self._session.execute(
            select(ConversationModel)
            .where(ConversationModel.session_id == session_id)
            .order_by(ConversationModel.created_at)
        )
        db_conversations = result.scalars().all()

        return [
            Conversation(
                id=conv.id,
                user_id=conv.user_id,
                session_id=conv.session_id,
                message=conv.message,
                response=conv.response,
                metadata=conv.metadata_json,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
            for conv in db_conversations
        ]

    async def update(self, conversation: Conversation) -> Conversation:
        """会話を更新"""
        result = await self._session.execute(
            select(ConversationModel).where(
                ConversationModel.id == conversation.id
            )
        )
        db_conversation = result.scalar_one_or_none()

        if not db_conversation:
            raise ValueError(f"会話が見つかりません: {conversation.id}")

        db_conversation.message = conversation.message
        db_conversation.response = conversation.response
        db_conversation.metadata_json = conversation.metadata
        db_conversation.updated_at = conversation.updated_at

        await self._session.commit()
        await self._session.refresh(db_conversation)

        return Conversation(
            id=db_conversation.id,
            user_id=db_conversation.user_id,
            session_id=db_conversation.session_id,
            message=db_conversation.message,
            response=db_conversation.response,
            metadata=db_conversation.metadata_json,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
        )

    async def delete(self, conversation_id: int) -> None:
        """会話を削除"""
        result = await self._session.execute(
            select(ConversationModel).where(
                ConversationModel.id == conversation_id
            )
        )
        db_conversation = result.scalar_one_or_none()

        if db_conversation:
            await self._session.delete(db_conversation)
            await self._session.commit()
