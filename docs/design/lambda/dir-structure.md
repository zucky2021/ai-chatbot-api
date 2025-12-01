# Lambda関数のディレクトリ構造

## 概要

- Lambda関数のディレクトリ構造を設計
- 参考: lambda-monorepo構造に準拠

## ディレクトリ構造

```sh
lambda/
├── functions/
│   ├── archive_conversation/
│   │   └── lambda_function.py # Lambdaハンドラー（エントリーポイント）
│   ├── cleanup_sessions/
│   │   └── lambda_function.py
│   └── generate_stats/
│       └── lambda_function.py
├── infra/
│   └── lambda_stack.py # CDKスタック定義
├── shared/ # Lambda関数間で共有するコード
│   ├── __init__.py
│   ├── config.py # 設定管理（Lambda用）
│   └── logging.py # ロギング設定（Lambda用）
├── tests/
├── app.py # CDKアプリのエントリーポイント
├── cdk.json # CDK設定ファイル
├── pyproject.toml # 依存関係管理（uv使用）
└── uv.lock # 依存関係ロックファイル
```

## 構造の説明

### functions/

- 各Lambda関数を格納するディレクトリ
- 各関数は独立したディレクトリに配置され、`lambda_function.py`をエントリーポイントとして使用します。

### infra/

- CDKスタック定義を格納するディレクトリ
- Lambda関数のデプロイ設定、EventBridgeルール、IAMロールなどを定義

### shared/

- Lambda関数間で共有するコードを格納するディレクトリ
- 設定管理、ロギング、データベース接続などの共通機能を提供
- **配置場所**: `lambda/shared/`（ルート直下）
  - `PythonFunction`の`entry="."`で`lambda/`ルートを指定しているため、`lambda/shared/`は自動的にパッケージングされる
  - 複数のLambda関数（`functions/archive_conversation/`, `functions/cleanup_sessions/`, `functions/generate_stats/`）が`shared`を共有するため、ルートレベルに配置するのが適切
  - `functions/`配下に配置すると、`functions/`内の関数からしかアクセスできないため不適切
