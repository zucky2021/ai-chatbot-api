import asyncio
from collections.abc import AsyncGenerator

import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.infrastructure.config import settings
from app.models.postgres import Base

# PostgreSQL (非同期)
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 接続の有効性をチェック
    pool_recycle=3600,  # 接続を1時間ごとに再利用
)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# PostgreSQL (同期) - 必要に応じて
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine
)

# Redis
redis_client = redis.from_url(
    settings.REDIS_URL, decode_responses=True, encoding="utf-8"
)


async def init_db():
    """データベース初期化（リトライ付き）"""
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"⚠️ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                print(f"   Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(
                    f"❌ Database initialization failed after {max_retries} attempts: {e}"
                )
                raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション取得"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis():
    """Redisクライアント取得"""
    return redis_client
