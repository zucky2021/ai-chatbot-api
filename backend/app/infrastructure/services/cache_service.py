"""Redisキャッシュサービス実装"""

import redis.asyncio as redis

from app.domain.services import ICacheService
from app.infrastructure.config import settings
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


class RedisCacheService(ICacheService):
    """Redisキャッシュサービス実装"""

    def __init__(self):
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Redisクライアントを取得"""
        if self._redis is None:
            self._redis = await redis.from_url(
                settings.REDIS_URL, decode_responses=True, encoding="utf-8"
            )
        return self._redis

    async def get(self, key: str) -> str | None:
        """キャッシュから値を取得"""
        try:
            client = await self._get_redis()
            value = await client.get(key)
            return value
        except Exception as e:
            # キャッシュエラーはログに記録するが、例外は発生させない
            logger.error(
                "cache_get_error", key=key, error=str(e), exc_info=True
            )
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """キャッシュに値を設定"""
        try:
            client = await self._get_redis()
            await client.setex(key, ttl, value)
        except Exception as e:
            # キャッシュエラーはログに記録するが、例外は発生させない
            logger.error(
                "cache_set_error",
                key=key,
                ttl=ttl,
                error=str(e),
                exc_info=True,
            )

    async def delete(self, key: str) -> None:
        """キャッシュから値を削除"""
        try:
            client = await self._get_redis()
            await client.delete(key)
        except Exception as e:
            logger.error(
                "cache_delete_error", key=key, error=str(e), exc_info=True
            )

    async def exists(self, key: str) -> bool:
        """キャッシュキーの存在確認"""
        try:
            client = await self._get_redis()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(
                "cache_exists_error", key=key, error=str(e), exc_info=True
            )
            return False

    async def close(self) -> None:
        """Redisクライアントをクローズ"""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
