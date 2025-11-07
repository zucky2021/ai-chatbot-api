"""メッセージ値オブジェクト"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Message:
    """
    メッセージ値オブジェクト

    不変オブジェクトとしてメッセージを表現
    """

    content: str
    timestamp: datetime
    sender: str
    metadata: dict | None = None

    def __post_init__(self):
        """値オブジェクトの検証"""
        if not self.content or not self.content.strip():
            raise ValueError("メッセージ内容は空にできません")
        if not self.sender:
            raise ValueError("送信者は必須です")
        if len(self.content) > 10000:
            raise ValueError("メッセージは10000文字以下である必要があります")

    @property
    def length(self) -> int:
        """メッセージの長さ"""
        return len(self.content)

    def truncate(self, max_length: int = 1000) -> "Message":
        """メッセージを切り詰める"""
        if max_length <= 0:
            raise ValueError("max_lengthは正の整数である必要があります")
        if len(self.content) <= max_length:
            return self
        return Message(
            content=self.content[:max_length] + "...",
            timestamp=self.timestamp,
            sender=self.sender,
            metadata=self.metadata,
        )
