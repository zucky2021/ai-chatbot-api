# WebSocketチャット機能

このドキュメントでは、実装されたWebSocketチャット機能の使用方法を説明します。

## 📚 目次

1. [概要](#概要)
2. [接続方法](#接続方法)
3. [メッセージ形式](#メッセージ形式)
4. [レスポンス形式](#レスポンス形式)
5. [使用例](#使用例)
6. [フロントエンド実装](#フロントエンド実装)
7. [エラーハンドリング](#エラーハンドリング)
8. [ベストプラクティス](#ベストプラクティス)
9. [トラブルシューティング](#トラブルシューティング)

---

## 概要

WebSocketチャット機能により、リアルタイムでAIチャットボットと対話できます。

**主な特徴：**

- ストリーミングレスポンスでAI回答をリアルタイムに受信
- ChatGPTのような自然な会話体験
- セッション管理との統合
- エラーハンドリングと接続管理

---

## 接続方法

### エンドポイント

```sh
ws://localhost:8000/api/chat/ws?session_id={session_id}&user_id={user_id}
```

### パラメータ

- **session_id** (必須): セッションID（事前に作成が必要）
- **user_id** (オプション): ユーザーID（デフォルト: `default_user`）

### 例

```javascript
const sessionId = 'sess_123456'
const userId = 'user_789'
const ws = new WebSocket(
  `ws://localhost:8000/api/chat/ws?session_id=${sessionId}&user_id=${userId}`
)
```

---

## メッセージ形式

### メッセージ送信

クライアントからサーバーへのメッセージ形式：

```json
{
  "type": "message",
  "message": "こんにちは",
  "metadata": {
    "language": "ja"
  }
}
```

**フィールド：**

- `type` (必須): メッセージタイプ（`"message"` または `"ping"`）
- `message` (必須): メッセージ内容（1-10000文字）
- `metadata` (オプション): メタデータ（任意のJSONオブジェクト）

### ハートビート（接続維持）

```json
{
  "type": "ping"
}
```

サーバーは `{"type": "pong"}` を返します。

---

## レスポンス形式

サーバーからクライアントへのメッセージ形式：

### 1. 接続確立 (`connected`)

```json
{
  "type": "connected",
  "session_id": "sess_123456",
  "message": "WebSocket接続が確立されました"
}
```

### 2. 処理開始 (`processing`)

```json
{
  "type": "processing",
  "message": "AIが回答を生成中です..."
}
```

### 3. ストリーミングチャンク (`chunk`)

```json
{
  "type": "chunk",
  "content": "こんにちは"
}
```

**注意**: このメッセージは複数回送信されます（AIが回答を生成するたびに）。

### 4. ストリーミング完了 (`done`)

```json
{
  "type": "done",
  "message": "回答の生成が完了しました"
}
```

### 5. 会話保存完了 (`saved`)

```json
{
  "type": "saved",
  "conversation_id": 123,
  "message": "会話が保存されました"
}
```

### 6. エラー (`error`)

```json
{
  "type": "error",
  "message": "エラーメッセージ"
}
```

---

## 使用例

### JavaScript (ブラウザ)

```javascript
// セッションを作成（REST API）
const sessionResponse = await fetch('http://localhost:8000/api/chat/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ metadata: { language: 'ja' } }),
})
const session = await sessionResponse.json()
const sessionId = session.session_id

// WebSocket接続
const ws = new WebSocket(`ws://localhost:8000/api/chat/ws?session_id=${sessionId}`)

// 接続確立
ws.onopen = () => {
  console.log('WebSocket接続が確立されました')
}

// メッセージ受信
let currentResponse = ''
ws.onmessage = event => {
  const data = JSON.parse(event.data)

  switch (data.type) {
    case 'connected':
      console.log('接続確立:', data.message)
      break

    case 'processing':
      console.log('処理開始:', data.message)
      currentResponse = '' // 新しい回答を開始
      break

    case 'chunk':
      currentResponse += data.content
      // UIに表示（リアルタイム更新）
      document.getElementById('response').textContent = currentResponse
      break

    case 'done':
      console.log('完了:', data.message)
      break

    case 'saved':
      console.log('保存完了:', data.conversation_id)
      break

    case 'error':
      console.error('エラー:', data.message)
      break
  }
}

// エラーハンドリング
ws.onerror = error => {
  console.error('WebSocketエラー:', error)
}

ws.onclose = () => {
  console.log('WebSocket接続が切断されました')
}

// メッセージ送信
function sendMessage(message) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: 'message',
        message: message,
        metadata: { language: 'ja' },
      })
    )
  }
}

// 使用例
sendMessage('こんにちは')
```

### Python (クライアント)

```python
import asyncio
import json
import websockets

async def chat_with_websocket():
    # セッションを作成（REST API）
    import requests
    session_response = requests.post(
        'http://localhost:8000/api/chat/sessions',
        json={'metadata': {'language': 'ja'}}
    )
    session_id = session_response.json()['session_id']

    # WebSocket接続
    uri = f"ws://localhost:8000/api/chat/ws?session_id={session_id}"

    async with websockets.connect(uri) as websocket:
        # 接続確立を待つ
        connected = await websocket.recv()
        print(f"接続確立: {connected}")

        # メッセージ送信
        message = {
            "type": "message",
            "message": "こんにちは",
            "metadata": {"language": "ja"}
        }
        await websocket.send(json.dumps(message))

        # レスポンスを受信
        current_response = ""
        while True:
            response = await websocket.recv()
            data = json.loads(response)

            if data["type"] == "chunk":
                current_response += data["content"]
                print(data["content"], end="", flush=True)
            elif data["type"] == "done":
                print(f"\n完了: {data['message']}")
                break
            elif data["type"] == "error":
                print(f"\nエラー: {data['message']}")
                break

# 実行
asyncio.run(chat_with_websocket())
```

### cURL (テスト用)

```bash
# WebSocketはcURLで直接テストできないため、
# websocatなどのツールを使用

# websocatのインストール（macOS）
brew install websocat

# 接続とメッセージ送信
echo '{"type":"message","message":"こんにちは"}' | \
  websocat ws://localhost:8000/api/chat/ws?session_id=sess_123
```

---

## フロントエンド実装

このプロジェクトには、Reactを使用したフロントエンド実装が含まれています。

### 実装内容

#### 1. `useWebSocket` フック

WebSocket接続を管理するカスタムフックです。

**主な機能：**

- WebSocket接続の確立・切断
- ストリーミングレスポンスの受信
- 自動再接続
- ハートビート（接続維持）
- エラーハンドリング

**ファイル:** `frontend/src/hooks/useWebSocket.ts`

**使用例：**

```typescript
const { isConnected, error, sendMessage, messages } = useWebSocket({
  sessionId: 'sess_123456',
  userId: 'user_789',
  autoReconnect: true,
  reconnectInterval: 3000, // 3秒後に再接続
  onError: err => {
    console.error('WebSocketエラー:', err)
  },
})
```

#### 2. `ChatInterface` コンポーネント

チャットUIを提供するコンポーネントです。

**主な機能：**

- メッセージの送信・表示
- リアルタイムでAI回答を表示
- 接続状態の表示
- エラーメッセージの表示

**ファイル:** `frontend/src/components/ChatInterface.tsx`

#### 3. `App` コンポーネント

アプリケーションのエントリーポイントです。

**主な機能：**

- セッションの自動作成
- エラーハンドリング
- ChatInterfaceの表示

**ファイル:** `frontend/src/App.tsx`

### コンポーネント構成

```sh
frontend/src/
├── App.tsx                    # メインコンポーネント
├── App.css                    # アプリケーションスタイル
├── hooks/
│   └── useWebSocket.ts        # WebSocketフック
└── components/
    ├── ChatInterface.tsx       # チャットUI
    └── ChatInterface.css      # チャットスタイル
```

### セットアップ手順

#### 1. 環境変数の設定

```bash
cd frontend

# .envファイルを作成
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
```

#### 2. 依存関係のインストール

```bash
cd frontend
pnpm install
```

#### 3. 開発サーバーの起動

```bash
pnpm dev
```

#### 4. ブラウザでアクセス

```txt
http://localhost:5173
```

### 動作確認

#### 1. バックエンドの起動

```bash
# バックエンドを起動
cd backend
uv run uvicorn app.main:app --reload
```

#### 2. フロントエンドの起動

```bash
# フロントエンドを起動
cd frontend
pnpm dev
```

#### 3. ブラウザで確認

1. ブラウザで `http://localhost:5173` にアクセス
2. セッションが自動作成される
3. WebSocket接続が確立される（接続状態が「● 接続中」になる）
4. メッセージを入力して送信
5. AI回答がリアルタイムで表示される

### フロントエンド固有の機能

#### 自動再接続

接続が切断された場合、自動的に再接続を試みます。

```typescript
const { isConnected, error } = useWebSocket({
  autoReconnect: true,
  reconnectInterval: 3000, // 3秒後に再接続
})
```

#### ハートビート

30秒ごとに`ping`メッセージを送信して接続を維持します。

#### Frontend エラーハンドリング

エラーが発生した場合、ユーザーに分かりやすいメッセージを表示します。

```typescript
const { error } = useWebSocket({
  onError: err => {
    console.error('WebSocketエラー:', err)
    alert(`エラーが発生しました: ${err.message}`)
  },
})
```

---

## エラーハンドリング

### セッションが見つからない場合

```json
{
  "type": "error",
  "message": "セッションが見つかりません: sess_123"
}
```

接続は自動的に切断されます（ステータスコード: 1008）。

### セッションがアクティブでない場合

```json
{
  "type": "error",
  "message": "セッションがアクティブではありません: sess_123"
}
```

接続は自動的に切断されます（ステータスコード: 1008）。

### メッセージが空の場合

```json
{
  "type": "error",
  "message": "メッセージが空です"
}
```

接続は維持されます。

### メッセージが長すぎる場合

```json
{
  "type": "error",
  "message": "メッセージが長すぎます（最大10000文字）"
}
```

接続は維持されます。

### AI生成エラーの場合

```json
{
  "type": "error",
  "message": "メッセージ処理中にエラーが発生しました: ..."
}
```

接続は維持されます。

---

## ベストプラクティス

### 1. 接続管理

- 接続が確立されたら `connected` メッセージを待つ
- 定期的に `ping` を送信して接続を維持
- エラー発生時は適切に再接続

### 2. UI更新

- `chunk` メッセージを受信するたびにUIを更新
- `done` メッセージで完了を表示
- エラーメッセージを適切に表示

### 3. セッション管理

- 事前にセッションを作成（REST API）
- セッションIDを適切に管理
- セッションが無効になった場合は再接続

### 4. エラーハンドリング

- すべてのエラーメッセージを処理
- 接続切断時の再試行ロジックを実装
- ユーザーに分かりやすいエラーメッセージを表示

---

## トラブルシューティング

### 接続できない

1. セッションが存在するか確認
2. セッションがアクティブか確認
3. サーバーが起動しているか確認
4. ポートが正しいか確認（デフォルト: 8000）

**フロントエンドの場合：**

1. バックエンドが起動しているか確認
2. 環境変数`VITE_API_URL`が正しいか確認
3. ブラウザのコンソールでエラーを確認

### メッセージが送信されない

1. WebSocket接続が確立されているか確認
2. メッセージ形式が正しいか確認
3. サーバーログを確認

**フロントエンドの場合：**

1. WebSocket接続が確立されているか確認（接続状態を確認）
2. ブラウザのコンソールでエラーを確認
3. ネットワークタブでWebSocket接続を確認

### ストリーミングが動作しない

1. AIサービス（Google AI）の設定を確認
2. ネットワーク接続を確認
3. サーバーログを確認

---

## 参考資料

- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [WebSocket API (MDN)](https://developer.mozilla.org/ja/docs/Web/API/WebSocket)
- [websocat](https://github.com/vi/websocat)
