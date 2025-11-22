# Makeコマンド

## 概要

- プロジェクトルートに[Makefile](/Makefile)を管理

## よく使うコマンド

```bash
make help
```

```sh
# 依存関係のインストール（開発用）
make install-dev

# セキュリティ脆弱性のスキャン
make audit-desc

# コードのリントとフォーマット
make lint
make format

# 型チェック
make type-check

# テスト実行
make test

# 開発サーバー起動
make dev-backend    # バックエンドのみ
make dev-frontend   # フロントエンドのみ
make dev            # Docker Composeで全サービス起動
```
