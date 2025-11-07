"""リポジトリインターフェース"""

from app.domain.repositories.repositories import (
    IConversationRepository,
    ISessionRepository,
)

__all__ = ["IConversationRepository", "ISessionRepository"]
