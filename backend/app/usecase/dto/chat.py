"""チャット関連のDTO"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SendMessageRequest(BaseModel):
    """メッセージ送信リクエストDTO"""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="メッセージ内容"
    )
    session_id: str = Field(..., description="セッションID")
    metadata: dict[str, Any] | None = Field(None, description="メタデータ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "こんにちは",
                "session_id": "sess_123456",
                "metadata": {"language": "ja"},
            }
        }
    )


class SendMessageResponse(BaseModel):
    """メッセージ送信レスポンスDTO"""

    conversation_id: int | None
    message: str
    response: str
    session_id: str
    created_at: datetime | None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": 1,
                "message": "こんにちは",
                "response": "こんにちは！何かお手伝いできることはありますか？",
                "session_id": "sess_123456",
                "created_at": "2024-01-01T00:00:00",
            }
        }
    )


class CreateSessionRequest(BaseModel):
    """セッション作成リクエストDTO"""

    session_id: str | None = Field(
        None, description="セッションID（省略時は自動生成）"
    )
    metadata: dict[str, Any] | None = Field(None, description="メタデータ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "sess_123456",
                "metadata": {"language": "ja"},
            }
        }
    )


class CreateSessionResponse(BaseModel):
    """セッション作成レスポンスDTO"""

    session_id: str
    status: str
    created_at: datetime | None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "sess_123456",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
            },
        }
    )


class ConversationItem(BaseModel):
    """会話履歴DTO"""

    id: int | None
    user_id: str
    session_id: str
    message: str
    response: str | None
    metadata: dict[str, Any] | None
    created_at: str | None
    updated_at: str | None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "message": "こんにちは",
                "response": "こんにちは！",
                "created_at": "2024-01-01T00:00:00",
            }
        }
    )


class ConversationHistoryResponse(BaseModel):
    """会話履歴レスポンスDTO"""

    conversations: list[ConversationItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversations": [
                    {
                        "id": 1,
                        "message": "こんにちは",
                        "response": "こんにちは！",
                        "created_at": "2024-01-01T00:00:00",
                    }
                ]
            }
        }
    )
