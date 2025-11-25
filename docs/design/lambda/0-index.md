# Lambda関数設計ドキュメント

## 概要

Lambda関数の設計、実装、デプロイに関するドキュメントです。

## ドキュメント一覧

- [IaCツールの比較](./iac-comparison.md) - CDK、Terraform、SAMの比較
- [ディレクトリ構造](./lambda-directory-structure.md) - Lambda関数のディレクトリ構造
- [ディレクトリ配置](./directory-placement.md) - モジュラモノリス観点での配置推奨
- [CDK移行ガイド](./lambda-cdk-migration.md) - SAMからCDKへの移行方法

## 推奨事項

### ディレクトリ配置

**推奨: プロジェクトルートの `lambda/`（モジュラモノリスに適している）**

```
ai-chatbot-api/
├── backend/          # モジュール1: FastAPIアプリケーション
├── frontend/         # モジュール2: Reactアプリケーション
└── lambda/           # モジュール3: Lambda関数（独立したモジュール）
```

詳細は [ディレクトリ配置](./directory-placement.md) を参照してください。

### IaCツール

- **学習段階**: SAM（シンプルで学習しやすい）
- **本格運用**: CDK（型安全性と統合管理のメリット）

詳細は [IaCツールの比較](./iac-comparison.md) を参照してください。
