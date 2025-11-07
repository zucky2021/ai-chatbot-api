"""リポジトリインターフェース"""

from abc import ABC, abstractmethod

from app.domain.entities.conversation import Conversation
from app.domain.entities.session import Session


class IConversationRepository(ABC):
    """会話リポジトリインターフェース"""

    @abstractmethod
    async def create(self, conversation: Conversation) -> Conversation:
        """会話を作成"""
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        """IDで会話を取得"""
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> list[Conversation]:
        """セッションIDで会話を取得"""
        pass

    @abstractmethod
    async def update(self, conversation: Conversation) -> Conversation:
        """会話を更新"""
        pass

    @abstractmethod
    async def delete(self, conversation_id: int) -> None:
        """会話を削除"""
        pass


class ISessionRepository(ABC):
    """セッションリポジトリインターフェース"""

    @abstractmethod
    async def create(self, session: Session) -> Session:
        """セッションを作成"""
        pass

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Session | None:
        """IDでセッションを取得"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[Session]:
        """ユーザーIDでセッションを取得"""
        pass

    @abstractmethod
    async def update(self, session: Session) -> Session:
        """セッションを更新"""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """セッションを削除"""
        pass

