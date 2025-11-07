from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.domain.entities.session import SessionStatus


class UserSession(BaseModel):
    """DynamoDB用 ユーザーセッション"""

    session_id: str
    user_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    metadata: dict[str, Any] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: int | None = None  # TTL用のUnix timestamp

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123456",
                "user_id": "user_789",
                "status": "active",
                "metadata": {"language": "ja"},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


class UserPreferences(BaseModel):
    """ユーザー設定"""

    user_id: str
    language: str = "ja"
    theme: str = "light"
    model_preference: str | None = None
    updated_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_789",
                "language": "ja",
                "theme": "light",
                "model_preference": "gemini-pro",
            }
        }


class VectorEmbedding(BaseModel):
    """ベクトル埋め込みデータ"""

    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "emb_123",
                "text": "こんにちは",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"conversation_id": "conv_456"},
            }
        }
