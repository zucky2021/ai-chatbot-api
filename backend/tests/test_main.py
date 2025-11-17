"""メインアプリケーションのシンプルなユニットテスト"""

import pytest

from app.main import root
from app.presentation.routers.health import health_check, readiness_check


@pytest.mark.asyncio
async def test_root_endpoint():
    """ルートエンドポイントのテスト"""
    result = await root()
    assert "message" in result
    assert "version" in result
    assert "docs" in result
    assert result["message"] == "AI Chatbot API"


@pytest.mark.asyncio
async def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    result = await health_check()
    assert result["status"] == "healthy"
    assert result["service"] == "AI Chatbot API"


@pytest.mark.asyncio
async def test_readiness_check():
    """レディネスチェックエンドポイントのテスト"""
    result = await readiness_check()
    assert result["status"] == "ready"
