"""依存性注入の設定"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import IConversationRepository, ISessionRepository
from app.domain.services import IAIService, ICacheService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.dynamodb_repository import (
    DynamoDBSessionRepository,
)
from app.infrastructure.repositories.postgres_repository import (
    PostgresConversationRepository,
)
from app.infrastructure.services.cache_service import RedisCacheService
from app.infrastructure.services.langgraph_ai_service import (
    LangGraphAIService,
)


async def get_conversation_repository(
    db: AsyncSession | None = None,
) -> IConversationRepository:
    """会話リポジトリを取得"""
    if db is None:
        async for session in get_db():
            db = session
            break

    return PostgresConversationRepository(db)


def get_session_repository() -> ISessionRepository:
    """セッションリポジトリを取得"""
    return DynamoDBSessionRepository()


def get_ai_service() -> IAIService:
    """AIサービスを取得"""
    return LangGraphAIService()


def get_cache_service() -> ICacheService:
    """キャッシュサービスを取得"""
    return RedisCacheService()
