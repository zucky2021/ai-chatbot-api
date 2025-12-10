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
│   ├── generate_stats/
│   │   └── lambda_function.py
│   └── shared/ # Lambda関数間で共有するコード（オプション）
│       ├── __init__.py
│       ├── config.py # 設定管理（Lambda用）
│       └── logging.py # ロギング設定（Lambda用）
├── infra/
│   └── lambda_stack.py # CDKスタック定義
├── tests/
├── app.py # CDKアプリのエントリーポイント
├── cdk.json # CDK設定ファイル
├── pyproject.toml # 依存関係管理（Lambda関数 + CDK）
└── uv.lock # 依存関係ロックファイル
```

## 構造の説明

### functions/

- 各Lambda関数を格納するディレクトリ
- 各関数は独立したディレクトリに配置され、`lambda_function.py`をエントリーポイントとして使用します。
- **依存関係管理**: `lambda/pyproject.toml`で統一管理
  - Lambda関数の実行時依存関係（`boto3`, `psycopg2-binary`, `asyncpg`など）は`dependencies`に定義
  - CDK依存関係（`aws-cdk-lib`など）は`[project.optional-dependencies]`の`infra`グループに定義
  - `PythonFunction`は`dependencies`のみを使用するため、CDK依存関係はLambdaパッケージに含まれない

### infra/

- CDKスタック定義を格納するディレクトリ
- Lambda関数のデプロイ設定、EventBridgeルール、IAMロールなどを定義

### shared/（オプション）

- Lambda関数間で共有するコードを格納するディレクトリ
- 設定管理、ロギング、データベース接続などの共通機能を提供
- **配置場所**: `lambda/shared/` または `lambda/functions/shared/`
  - `PythonFunction`の`entry="."`により、`lambda/`ルート配下のコードが自動的にパッケージングされる
  - `lambda/shared/`に配置する場合: 各Lambda関数からは`from shared import ...`でインポート可能
  - `lambda/functions/shared/`に配置する場合: 各Lambda関数からは`from functions.shared import ...`でインポート可能
  - 複数のLambda関数（`archive_conversation/`, `cleanup_sessions/`, `generate_stats/`）が`shared`を共有するため、どちらでも使用可能
