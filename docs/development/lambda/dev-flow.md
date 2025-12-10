# 開発フロー

## 概要

- Lambda関数の開発フローを記述
- 本プロジェクトでは **CDK + SAM（ローカルテスト）** の併用パターンを採用

## CDK + SAM 開発フロー（推奨）

ここでは、**CDK でインフラ定義・デプロイを行い、SAM でローカルテストをする**  
「CDK + SAM」方針の具体的な手順

### 実際の流れ（CDKを使う場合）

CDK を使った開発の全体フローは以下の通りです：

1. **`cdk init`** → CDKプロジェクトを作成（インフラ定義のコードを書く準備）
2. **CDKコードを書く**（`lambda_stack.py` など）
3. **`cdk synth`** → CloudFormationテンプレートを生成
4. **`sam local invoke`** → 生成したテンプレートでローカルテスト（この時点でLambda関数のコードがビルドされる）
5. **`cdk deploy`** → 本番環境にデプロイ

以下、各ステップの詳細を説明します。

### 1. CDKプロジェクトの初期化

```bash
# Lambda関数のディレクトリに移動
cd lambda

# CDKプロジェクト用のディレクトリを作成
mkdir -p cdk
cd cdk

# CDKプロジェクトを初期化（Python）
cdk init app --language python

# CDK用の依存関係をインストール
uv sync
```

> **重要**: LambdaプロジェクトとCDKプロジェクトの関連
>
> - **Lambdaプロジェクト**（`lambda/functions/`）:
>   - Lambda関数の実装コード（`archive_conversation/`, `cleanup_sessions/`, `generate_stats/`）
>   - 共有コード（`functions/shared/`、オプション）
>   - **役割**: 実際に実行されるLambda関数のコード
> - **CDKプロジェクト**（`lambda/` ルート）:
>   - インフラ定義コード（`infra/lambda_stack.py`, `app.py` など）
>   - **役割**: Lambda関数をAWSにデプロイするための定義（EventBridgeルール、IAMロールなど）
> - **関係性**:
>   - CDKプロジェクトは、Lambdaプロジェクトのコードを参照してデプロイ定義を作成します
>   - CDK で定義した内容が `cdk synth` で CloudFormation テンプレートとして生成され、それが SAM のローカルテストで使われます

### 2. CDKスタックの実装

`lambda/cdk/lambda_stack.py` に、バッチ系 Lambda と EventBridge ルールを定義します。

設計サンプルは `docs/design/lambda/iac-comparison.md` を参照してください。

### 3. CDKアプリのエントリーポイント

`lambda/cdk/app.py` を作成し、`LambdaStack` を組み立てます。

### 4. CDK設定（`pyproject.toml`, `cdk.json`）

- `lambda/cdk/pyproject.toml` に `aws-cdk-lib`, `constructs` などを定義（`cdk init` で自動生成される）
- `lambda/cdk/cdk.json` に `app` コマンドや `watch` 設定、`context`（CDK の推奨フラグ）を記述（`cdk init` で自動生成される）

### 5. CDKでテンプレート生成 & 差分確認

```bash
cd lambda/cdk

# CloudFormation テンプレートを生成（ローカル）
cdk synth

# 現在のスタックとの差分を確認（デプロイ前）
cdk diff
```

### 6. CDK + SAM でローカル実行（ステップ4）

```bash
cd lambda/cdk

# 1. CDKでテンプレートを生成（ステップ3と同じ）
cdk synth

# 2. 生成されたテンプレートをSAMでローカル実行
# テンプレートは cdk.out/ ディレクトリに生成される
# この時点でLambda関数のコードがビルドされる
sam local invoke ArchiveConversationFunction \
  --template cdk.out/LambdaStack.template.json \
  --event ../events/test-event.json
```

> **注意**:
>
> - `events/test-event.json` は `lambda/events/` ディレクトリに配置する想定です。
> - まだ存在しない場合は、テスト用のイベントファイルを作成してください。
> - `sam local invoke` を実行すると、Lambda関数のコードが自動的にビルドされます（`sam build` を事前に実行する必要はありません）。

### 7. ホットリロード開発（任意）

```bash
# ファイル変更を自動検知して再デプロイ（開発環境のみ）
cdk watch
```

### 8. デプロイ（CDK）（ステップ5）

```bash
cd lambda

# 初回デプロイ時のみブートストラップが必要（AWS環境への初回デプロイ時のみ）
# ローカル開発（cdk synth, sam local invoke）では不要
cdk bootstrap

# スタックをデプロイ
cdk deploy

# 特定のスタックのみデプロイ
cdk deploy LambdaStack
```

> **注意**:
>
> - `cdk deploy` を実行すると、Lambda関数のコードが自動的にビルド・パッケージ化されてデプロイされます。
> - **`cdk bootstrap`は初回デプロイ時のみ必要**です。ローカル開発（`cdk synth`、`sam local invoke`）では不要です。
> - `cdk bootstrap`は、CDKがアーティファクト（Lambda関数のコードなど）を保存するためのS3バケットとCloudFormationスタックを作成します。
>   **詳細**: AWS環境へのデプロイ手順は [deploy.md](./deploy.md) を参照してください。

---

## 設定・環境変数

### 共通で使用する主な環境変数

- `DATABASE_URL`: PostgreSQL 接続 URL
- `S3_ARCHIVE_BUCKET`: アーカイブ用 S3 バケット名
- `S3_REPORTS_BUCKET`: レポート用 S3 バケット名
- `DYNAMODB_SESSION_TABLE`: DynamoDB セッションテーブル名
- `AWS_ENDPOINT_URL`: LocalStack 用（開発環境のみ）
- `AWS_REGION`: AWS リージョン
- `LOG_LEVEL`: ログレベル（`INFO`, `DEBUG` など）

---

### スケジュール変更（EventBridge）

CDK を使用する場合、`lambda/cdk/lambda_stack.py` 内の `Schedule` 定義を変更することで、実行タイミングを調整できます。

```python
# CDKでの例
rule = events.Rule(
    self, "ArchiveConversationRule",
    schedule=events.Schedule.cron(hour=2, minute=0),  # 毎日深夜2時（UTC）
)
```

SAM テンプレート（`lambda/template.yaml`）を使用する場合：

```yaml
Schedule: cron(0 2 * * ? *) # 毎日深夜2時（UTC）
```

cron 式の形式は `cron(分 時 日 月 曜日 年)` です。

---

## 参考

- [Lambda - Design](/docs/design/lambda/0-index.md)
