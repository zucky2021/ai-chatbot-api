# Backend (Python/FastAPI) コーディング規約

## 基本

- こちらのサイトの記載内容に従っていること
  - [PEP 8 -- Style Guide for Python Code](https://pep8.org/)
  - [FastAPI Best Practices](https://fastapi.tiangolo.com/ja/tutorial/)

## ディレクトリ構造

```sh
backend/app/
├── __init__.py
├── main.py           # アプリケーションエントリーポイント
├── config.py         # 設定管理
├── database.py       # データベース接続
├── models/           # データモデル
│   ├── __init__.py
│   ├── postgres.py   # PostgreSQLモデル（SQLAlchemy）
│   └── dynamodb.py   # DynamoDBモデル（Pydantic）
└── routers/          # APIエンドポイント
    ├── __init__.py
    ├── chat.py       # チャット関連
    └── health.py     # ヘルスチェック
```

## 命名規則

### 変数・関数名

- **スネークケース**を使用: `snake_case`
- 関数名は動詞で始める: `get_user`, `create_session`, `update_conversation`
- ブール値は `is_`, `has_`, `should_` などで始める: `is_active`, `has_permission`

```python
# Good
def get_user_by_id(user_id: str) -> User:
    pass

is_active: bool = True
has_permission: bool = False

# Bad
def GetUserById(userId: str):  # キャメルケース（Pythonには不適切）
    pass
```

#### クラス名

- **パスカルケース**を使用: `PascalCase`
- 名詞で始める: `UserSession`, `ConnectionManager`

```python
# Good
class ConnectionManager:
    pass

class UserSession(BaseModel):
    pass

# Bad
class connection_manager:  # スネークケース（クラスには不適切）
    pass
```

#### 定数

- **全大文字**、**スネークケース**を使用: `UPPER_SNAKE_CASE`

```python
# Good
API_VERSION = "1.0.0"
MAX_CONNECTIONS = 100

# Bad
api_version = "1.0.0"  # 定数に見えない
```

## 型ヒント

- **型アノテーションは必須**（PEP 484準拠）
- 複雑な型は `typing` モジュールを活用
- 戻り値の型も明示: `def func() -> ReturnType:`

```python
# Good
from typing import List, Optional, Dict, Any
from datetime import datetime

def create_session(
    user_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> UserSession:
    """セッションを作成する"""
    pass

# Bad
def create_session(user_id, metadata=None):  # 型が不明確
    pass
```

## 関数・メソッド

#### 単一責任の原則

1つの関数は1つのことだけを行う

```python
# Good
def calculate_total(items: List[Item]) -> float:
    return sum(item.price for item in items)

def format_currency(amount: float) -> str:
    return f"${amount:.2f}"

# Bad
def calculate_and_format(items: List[Item]) -> str:
    total = sum(item.price for item in items)  # 計算と整形が混在
    return f"${total:.2f}"
```

#### 関数の長さ

- 1つの関数は**50行以下**を目安とする
- 長くなる場合は、論理的な単位に分割

#### Docstring

- **docstring**で関数の目的、引数、戻り値を説明
- **Google形式**または**NumPy形式**を使用

```python
def create_user_session(
    user_id: str,
    session_metadata: Optional[Dict[str, Any]] = None
) -> UserSession:
    """
    ユーザーセッションを作成する
    
    Args:
        user_id: ユーザーID
        session_metadata: セッションのメタデータ（オプション）
    
    Returns:
        作成されたUserSessionオブジェクト
    
    Raises:
        ValueError: user_idが無効な場合
    
    Example:
        >>> session = create_user_session("user_123", {"language": "ja"})
    """
    pass
```

#### ルーター

- ルーターは機能ごとに分離: `routers/chat.py`, `routers/health.py`
- プレフィックスは設定ファイルで統一管理

```python
# Good
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続エンドポイント"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# main.py
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
```

#### 依存性注入

- `Depends()`を使用して依存性を注入
- 共通の処理は依存性として切り出す

```python
# Good
from fastapi import Depends

def get_current_user() -> str:
    """現在のユーザーを取得"""
    return "user_123"  # 実際は認証ロジックから取得

@router.get("/me")
async def get_profile(current_user: str = Depends(get_current_user)):
    return {"user_id": current_user}

# Bad
@router.get("/me")
async def get_profile():
    user = "user_123"  # ロジックがハードコーディング
    return {"user_id": user}
```

#### Pydanticモデル

- リクエスト/レスポンスはPydanticモデルで定義
- バリデーション、シリアライゼーションを活用

```python
# Good
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    """チャットメッセージモデル"""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "こんにちは",
                "session_id": "sess_123",
                "timestamp": "2024-01-01T00:00:00"
            }
        }

@router.post("/send")
async def send_message(message: ChatMessage):
    return {"status": "sent", "message": message.dict()}
```

### エラーハンドリング

#### 例外処理

- 具体的な例外型をキャッチ
- 適切なログを記録
- ユーザーに分かりやすいエラーメッセージを返す

```python
# Good
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

async def create_session(user_id: str) -> UserSession:
    try:
        session = await db.create_session(user_id)
        return session
    except ValueError as e:
        logger.error(f"Invalid user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_id: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating session for {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Bad
async def create_session(user_id: str) -> UserSession:
    try:
        return await db.create_session(user_id)
    except:  # すべての例外をキャッチ
        return None  # エラーを隠蔽
```

### データベースアクセス

#### PostgreSQL (SQLAlchemy)

- セッション管理は依存性注入で行う
- トランザクションは明示的に管理

```python
# Good
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db() -> Session:
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

#### DynamoDB

- リソースは再利用する
- 適切なリトライロジックを実装

```python
# Good
import boto3
from botocore.config import Config

def get_dynamodb_resource():
    """DynamoDBリソースを取得（シングルトン）"""
    if not hasattr(get_dynamodb_resource, '_resource'):
        config = Config(retries={'max_attempts': 5})
        get_dynamodb_resource._resource = boto3.resource(
            'dynamodb',
            endpoint_url=settings.DYNAMODB_ENDPOINT,
            config=config
        )
    return get_dynamodb_resource._resource
```

### テスト

#### テストファイル構造

- テストファイルは `tests/` ディレクトリに配置
- テストクラス名は `Test*` で始める

```python
# tests/test_chat.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_websocket_connection():
    """WebSocket接続が正常に行われることを確認"""
    with client.websocket_connect("/api/chat/ws") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "Echo: Hello"

def test_send_message_invalid():
    """無効なメッセージが拒否されることを確認"""
    response = client.post(
        "/api/chat/send",
        json={"message": ""}  # 空文字列（無効）
    )
    assert response.status_code == 400
```

### ログ

```python
# Good
import logging

logger = logging.getLogger(__name__)

async def process_message(message: str):
    logger.info(f"Processing message: {message[:50]}...")
    try:
        result = await ai_client.generate(message)
        logger.debug(f"AI response generated: {len(result)} chars")
        return result
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}", exc_info=True)
        raise
```

### リファクタリング

- コードスメルを避ける: 長すぎる関数、重複コード、循環参照など
- 定期的にコードレビューを行い、改善点を洗い出す

### ツール・フォーマッター

- **black**: コードフォーマッター
- **flake8**: リンター
- **mypy**: 型チェッカー

```bash
# フォーマット
black backend/

# チェック
flake8 backend/
mypy backend/
```
