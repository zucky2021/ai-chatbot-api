"""セッションエンティティ"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class SessionStatus(str, Enum):
    """セッションステータス"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"


@dataclass
class Session:
    """
    ユーザーセッションエンティティ

    チャットセッションを管理するドメインエンティティ
    """

    session_id: str
    user_id: str
    status: SessionStatus
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: int | None = None

    def __post_init__(self):
        """エンティティ作成後の初期化"""
        if not self.session_id:
            raise ValueError("session_idは必須です")
        if not self.user_id:
            raise ValueError("user_idは必須です")
        if self.status not in SessionStatus:
            raise ValueError(f"無効なstatus: {self.status}")

    def activate(self) -> None:
        """セッションをアクティブにする"""
        self.status = SessionStatus.ACTIVE
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """セッションを非アクティブにする"""
        self.status = SessionStatus.INACTIVE
        self.updated_at = datetime.now()

    def end(self) -> None:
        """セッションを終了する"""
        self.status = SessionStatus.ENDED
        self.updated_at = datetime.now()

    def is_active(self) -> bool:
        """セッションがアクティブかどうか"""
        return self.status == SessionStatus.ACTIVE

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """メタデータを更新"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
