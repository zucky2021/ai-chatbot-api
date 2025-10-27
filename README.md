# AI Chatbot API

FastAPI、WebSocket、PostgreSQL、DynamoDB（LocalStack）、Redis、ベクトル検索を使用したAI Chatbotアプリケーション。

## 🎯 学習目的

- FastAPIの習得
- AIモデル連携（Google AI Studio）
- WebSocketによるリアルタイム通信
- データベース統合（PostgreSQL、DynamoDB）
- Redisキャッシング
- ベクトル検索

## 🏗️ アーキテクチャ

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│  Frontend   │◄────►│   Backend   │◄────►│  PostgreSQL  │
│  (Vite)     │ WebSocket│ (FastAPI) │   SQL   │  (会話履歴)  │
└─────────────┘      └─────────────┘      └──────────────┘
                              │
                              ├────► Redis (キャッシング)
                              │
                              ├────► LocalStack (DynamoDB)
                              │
                              └────► Google AI Studio
```

## 📋 必要要件

- Docker & Docker Compose
- Node.js & pnpm（ローカル開発時）
- Python 3.11+（ローカル開発時）

## 🚀 セットアップ

### 1. 環境変数の設定

```bash
# Google AI APIキーを取得
# https://aistudio.google.com/apikey

# 環境変数を設定
cp backend/.env.example backend/.env

# .envを編集してGOOGLE_AI_API_KEYを設定
nano backend/.env
```

### 2. Docker Composeで起動

```bash
# LocalStackの初期化スクリプトに実行権限を付与
chmod +x init-localstack.sh

# 全サービスを起動
docker compose up -d

# ログを確認
docker compose logs -f
```

### 3. サービスへのアクセス

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **LocalStack**: http://localhost:4566

## 🛠️ ローカル開発

### Backend

#### Option 1: uvを使用（推奨 - 高速）

```bash
# uvをインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
uv venv
source .venv/bin/activate  # macOS/Linux
# または Windows: .venv\Scripts\activate

uv pip install -r requirements.txt

# アプリケーションを起動
uvicorn app.main:app --reload
```

#### Option 2: pipを使用（従来の方法）

```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または Windows: venv\Scripts\activate

pip install -r requirements.txt

# アプリケーションを起動
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## 📚 使用方法

### WebSocket接続例

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

ws.onopen = () => {
  console.log('Connected');
  ws.send('Hello, AI!');
};

ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
```

## 🗄️ データベース

### PostgreSQL

会話履歴の保存に使用

```bash
# データベース接続
docker compose exec postgres psql -U chatbot -d chatbot_db

# テーブル確認
\dt
```

### DynamoDB (LocalStack)

ユーザーセッション、設定の保存に使用

```bash
# DynamoDBテーブル一覧
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

### Redis

キャッシングに使用

```bash
# Redis接続
docker compose exec redis redis-cli

# データ確認
KEYS *
```

## 🧪 テスト

```bash
# Backendテスト
cd backend
pytest

# フロントエンドテスト
cd frontend
pnpm test
```

## 📝 TODO

- [ ] Google AI Studio APIとの連携実装
- [ ] ベクトル検索機能の実装
- [ ] 会話履歴の保存機能
- [ ] DynamoDBでのユーザーセッション管理
- [ ] Redisキャッシング実装
- [ ] 認証・認可機能
- [ ] フロントエンドUI実装

## 🔧 トラブルシューティング

### LocalStackが起動しない

```bash
# ログを確認
docker compose logs localstack

# 再起動
docker compose restart localstack
```

### ポート競合

`compose.yml`のポート番号を変更してください。

```yaml
ports:
  - "8001:8000"  # 例: 8000を8001に変更
```

## 📄 ライセンス

MIT

