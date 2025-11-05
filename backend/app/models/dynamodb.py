from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """セッションステータス"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"


class UserSession(BaseModel):
    """DynamoDB用 ユーザーセッション"""
    session_id: str
    user_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[int] = None  # TTL用のUnix timestamp
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123456",
                "user_id": "user_789",
                "status": "active",
                "metadata": {"language": "ja"},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class UserPreferences(BaseModel):
    """ユーザー設定"""
    user_id: str
    language: str = "ja"
    theme: str = "light"
    model_preference: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_789",
                "language": "ja",
                "theme": "light",
                "model_preference": "gemini-pro"
            }
        }


class VectorEmbedding(BaseModel):
    """ベクトル埋め込みデータ"""
    id: str
    text: str
    embedding: list[float]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "emb_123",
                "text": "こんにちは",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"conversation_id": "conv_456"}
            }
        }




