# LangChain / LangGraph 動作確認ガイド

## 概要

このドキュメントでは、実装したLangChain/LangGraphサービスの動作確認方法を説明します。

## 前提条件

1. 依存関係がインストールされていること

   ```bash
   cd backend
   uv sync
   ```

2. 環境変数が設定されていること
   - `.env`ファイルに`GOOGLE_AI_API_KEY`が設定されている必要があります

## 動作確認方法

### 1. 単体テストスクリプトの実行

最も簡単な確認方法です。

```bash
cd backend
uv run python test_langchain_service.py
```

このスクリプトは以下のテストを実行します:

- **テスト1**: 基本的なレスポンス生成
- **テスト2**: 会話履歴を含むコンテキストでの応答
- **テスト3**: ストリーミング応答
- **テスト4**: 会話履歴の構築

### 2. 依存性注入を変更してAPIで確認

#### ステップ1: `dependencies.py`を変更

```python
# backend/app/infrastructure/dependencies.py

from app.infrastructure.services.langchain_ai_service import LangChainAIService

def get_ai_service() -> IAIService:
    """AIサービスを取得"""
    return LangChainAIService()  # GoogleAIService() から変更
```

#### ステップ2: アプリケーションを起動

```bash
cd backend
uv run uvicorn app.main:app --reload
```

#### ステップ3: APIエンドポイントで確認

**セッション作成:**

```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "metadata": {}
  }'
```

**メッセージ送信:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "message": "こんにちは、元気ですか？",
    "metadata": {}
  }'
```

**会話履歴を含むメッセージ送信:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "message": "私の名前を覚えていますか？",
    "metadata": {}
  }'
```

### 3. WebSocket経由での確認

#### ステップ1: WebSocketクライアントを使用

ブラウザの開発者ツールのコンソールで実行:

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/chat?session_id=test_session_123&user_id=test_user'
)

ws.onopen = () => {
  console.log('接続成功')
  ws.send(
    JSON.stringify({
      type: 'message',
      content: 'こんにちは、元気ですか？',
    })
  )
}

ws.onmessage = event => {
  const data = JSON.parse(event.data)
  console.log('受信:', data)
}

ws.onerror = error => {
  console.error('エラー:', error)
}
```

#### ステップ2: フロントエンドアプリケーションを使用

```bash
cd frontend
pnpm dev
```

ブラウザで `http://localhost:5173` を開き、チャットインターフェースでメッセージを送信して確認します。

### 4. Pythonインタラクティブシェルでの確認

```bash
cd backend
uv run python
```

```python
import asyncio
from datetime import datetime
from app.domain.value_objects.message import Message
from app.infrastructure.services.langchain_ai_service import LangChainAIService

async def test():
    service = LangChainAIService()
    message = Message(
        content="こんにちは",
        timestamp=datetime.now(),
        sender="test_user"
    )
    response = await service.generate_response(message, context="")
    print(response)

asyncio.run(test())
```

## 確認すべきポイント

### 基本的な動作

- [ ] サービスが正常に初期化される
- [ ] 基本的なメッセージに対してレスポンスが返る
- [ ] エラーハンドリングが正しく動作する

### 会話履歴の管理

- [ ] 空のコンテキストで動作する
- [ ] 会話履歴を含むコンテキストで動作する
- [ ] 会話履歴が正しく解析される
- [ ] 新しい会話が履歴に追加される

### ストリーミング

- [ ] ストリーミング応答が正常に動作する
- [ ] チャンクが順番に受信される
- [ ] 完全なレスポンスが生成される

### プロンプトテンプレート

- [ ] システムプロンプトが適用される
- [ ] 会話履歴がプロンプトに含まれる
- [ ] ユーザー入力が正しく処理される

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'langchain'`

依存関係がインストールされていません。

```bash
cd backend
uv sync
```

### エラー: `RuntimeError: AIレスポンス生成エラー`

Google AI APIキーが設定されていないか、無効です。

`.env`ファイルを確認してください:

```bash
GOOGLE_AI_API_KEY=your_api_key_here
```

### エラー: `ImportError: cannot import name 'ConversationBufferMemory'`

LangChain 1.0では`ConversationBufferMemory`が削除されています。
`ChatMessageHistory`を使用するように実装を確認してください。

### ストリーミングが動作しない

- チェーンの`astream`メソッドが正しく実装されているか確認
- レスポンスオブジェクトの`content`属性が存在するか確認

## 次のステップ

動作確認が完了したら:

1. **LangGraphの確認**: `LangGraphAIService`の動作確認
2. **統合テスト**: 実際のアプリケーションでの動作確認
3. **パフォーマンステスト**: レスポンス時間の測定
4. **エラーハンドリング**: エラーケースの確認

## 参考

- [LangChain公式ドキュメント](https://python.langchain.com/)
- [LangGraph公式ドキュメント](https://langchain-ai.github.io/langgraph/)
- [プロジェクトのLangChain実装ガイド](./langchain.md)
