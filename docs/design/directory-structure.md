# ディレクトリ構造

## File tree

```sh
ai-chatbot-api/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPIアプリケーション
│   │   ├── config.py         # 設定管理
│   │   ├── database.py       # DB接続管理
│   │   ├── models/           # データモデル
│   │   │   ├── postgres.py   # PostgreSQLモデル
│   │   │   └── dynamodb.py   # DynamoDBモデル
│   │   └── routers/          # APIルーター
│   │       ├── chat.py       # チャットAPI
│   │       └── health.py     # ヘルスチェック
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # メインコンポーネント
│   │   └── main.tsx          # エントリーポイント
│   ├── Dockerfile
│   └── package.json
├── compose.yml               # Docker Compose設定
└── README.md
```
