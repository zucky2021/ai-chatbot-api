"""サービスインターフェース"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.domain.value_objects.message import Message


class IAIService(ABC):
    """AIサービスインターフェース"""

    @abstractmethod
    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        pass

    @abstractmethod
    async def generate_stream(
        self, message: Message, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """AIレスポンスをストリームで生成"""
        pass


class ICacheService(ABC):
    """キャッシュサービスインターフェース"""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """キャッシュから値を取得"""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """キャッシュに値を設定"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """キャッシュから値を削除"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """キャッシュキーの存在確認"""
        pass
