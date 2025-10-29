# 🚀 セットアップ

## 1. 環境変数の設定

```sh
# Google AI APIキーを取得
# https://aistudio.google.com/apikey

# 環境変数を設定
cp backend/.env.example backend/.env

# .envを編集してGOOGLE_AI_API_KEYを設定
nano backend/.env
```

## 2. Docker Composeで起動

```sh
# LocalStackの初期化スクリプトに実行権限を付与
chmod +x init-localstack.sh

# 全サービスを起動
docker compose up -d

# ログを確認
docker compose logs -f
```

## 3. サービスへのアクセス

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **PostgreSQL**: `localhost:5432`
- **ElastiCache (Redis)**: `localhost:6379`
- **LocalStack**: `http://localhost:4566`
