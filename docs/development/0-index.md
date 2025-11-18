# 開発ドキュメント

## 目次

1. [セットアップ](./setup.md)
2. [開発ツール](./tools/0-index.md)
3. [パッケージ](./packages/0-index.md)
4. [ブランチ戦略](./branch.md)
5. [コーディング規約](./coding-rules/0-index.md)
6. [CI](./ci/0-index.md)
7. [WebSocketチャット機能](./websocket.md)
8. [AIサービス比較](./ai-services-comparison.md.md)

## 🛠️ ローカル開発

### Backend

#### uvを使用（推奨 - 高速）

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

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## 📚 使用方法

### WebSocketチャット機能

詳細な使用方法については、[WebSocketチャット機能](./websocket.md)を参照してください。

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

### ElastiCache (Redis via LocalStack)

キャッシングに使用（ElastiCache を LocalStack でエミュレート）

```bash
# Redis接続（LocalStack経由）
docker compose exec localstack redis-cli -h localhost

# または直接接続
redis-cli -h localhost -p 6379

# データ確認
KEYS *

# ElastiCache クラスター確認
aws --endpoint-url=http://localhost:4566 elasticache describe-cache-clusters
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
  - '8001:8000' # 例: 8000を8001に変更
```
