"""会話エンティティ"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Conversation:
    """
    会話エンティティ
    
    ドメイン層のエンティティで、ビジネスロジックの基本単位
    """
    id: Optional[int]
    user_id: str
    session_id: str
    message: str
    response: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    def __post_init__(self):
        """エンティティ作成後の初期化"""
        if not self.user_id:
            raise ValueError("user_idは必須です")
        if not self.session_id:
            raise ValueError("session_idは必須です")
        if not self.message:
            raise ValueError("messageは必須です")
    
    def is_completed(self) -> bool:
        """会話が完了しているか（レスポンスがあるか）"""
        return self.response is not None
    
    def update_response(self, response: str) -> None:
        """レスポンスを更新"""
        if not response:
            raise ValueError("responseは空にできません")
        self.response = response
        self.updated_at = datetime.now()

