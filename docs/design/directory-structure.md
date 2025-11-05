# ディレクトリ構造

## File tree

```sh
ai-chatbot-api/
├── backend/
│   ├── app/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # メインコンポーネント
│   │   └── main.tsx          # エントリーポイント
│   ├── Dockerfile
│   └── package.json
├── compose.yml               # Docker Compose設定
└── README.md
```

### Backend

```sh
backend/app/
├── domain/                    # Domain Layer（最内側）
│   ├── entities/              # エンティティ
│   │   ├── conversation.py   # 会話エンティティ
│   │   └── session.py        # セッションエンティティ
│   └── value_objects/        # 値オブジェクト
│       └── message.py        # メッセージ値オブジェクト
│
├── application/               # Application Layer
│   ├── interfaces/           # インターフェース
│   │   ├── repositories.py   # リポジトリインターフェース
│   │   └── services.py       # サービスインターフェース
│   ├── use_cases/            # ユースケース
│   │   └── chat.py           # チャットユースケース
│   └── dto/                  # データ転送オブジェクト
│       └── chat.py           # チャットDTO
│
├── infrastructure/            # Infrastructure Layer
│   ├── config.py             # 設定管理
│   ├── repositories/         # リポジトリ実装
│   │   ├── postgres_repository.py    # PostgreSQL実装
│   │   └── dynamodb_repository.py    # DynamoDB実装
│   ├── services/             # 外部サービス実装
│   │   ├── ai_service.py     # Google AI実装
│   │   └── cache_service.py  # Redis実装
│   └── dependencies.py       # 依存性注入
│
└── presentation/              # Presentation Layer（最外側）
    ├── controllers/          # コントローラー
    │   └── chat_controller.py
    └── routers/               # APIルーター
        ├── chat.py           # チャットAPI
        └── health.py         # ヘルスチェックAPI
```
