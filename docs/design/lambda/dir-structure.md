# Lambda関数のディレクトリ構造

## 概要

- Lambda関数のディレクトリ構造を設計

## ディレクトリ構造

```sh
ai-chatbot-api/
├── backend/
├── frontend/
└── lambda/
│   ├── archive_conversation/
│   │   ├── src/
│   │   │   └── handler.py # Lambdaハンドラー（エントリーポイント）
│   │   └── project.toml # 依存関係管理
│   │
│   └── shared/ # Lambda関数間で共有するコード
│       ├── __init__.py
│       ├── database.py # データベース接続（Lambda用）
│       ├── config.py # 設定管理（Lambda用）
│       └── logging.py # ロギング設定（Lambda用）
└── ...
```
