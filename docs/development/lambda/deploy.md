# Lambda デプロイ手順（AWS環境）

## 概要

CDKを使用してLambda関数をAWS環境にデプロイし、動作確認する手順を説明します。

## 前提条件

### 1. AWSアカウントの準備

- AWSアカウントを持っていること
- 適切なIAM権限を持っていること

### 2. 必要なツールのインストール

以下のツールがインストールされていることを確認してください：

```bash
# バージョン確認
python3 --version  # 3.12以上
uv --version
aws --version
cdk --version
```

詳細は [setup.md](./setup.md) を参照してください。

## デプロイ前の準備

### 1. AWS認証情報の設定

AWS CLIを使用して認証情報を設定します：

```bash
aws configure
```

以下の情報を入力します：

- **AWS Access Key ID**: IAMユーザーのアクセスキーID
- **AWS Secret Access Key**: IAMユーザーのシークレットアクセスキー
- **Default region name**: `ap-northeast-1`（東京リージョン）
- **Default output format**: `json`

> **注意**: 本番環境では、IAMユーザーに最小限の権限を付与してください。

### 2. 必要なIAM権限

CDKデプロイに必要な主な権限：

- `cloudformation:*` - CloudFormationスタックの作成・更新
- `s3:*` - アーティファクトの保存（bootstrap用）
- `iam:*` - IAMロール・ポリシーの作成
- `lambda:*` - Lambda関数の作成・更新
- `events:*` - EventBridgeルールの作成
- `logs:*` - CloudWatch Logsの作成

### 3. 依存関係のインストール

```bash
cd lambda
uv sync --all-extras
```

### 4. 環境変数の設定（本番環境用）

`lambda/infra/lambda_stack.py` の環境変数を本番環境の値に更新します：

```python
# 例: Secrets Managerから取得する場合
common_env = {
    "LOG_LEVEL": "INFO",
    "DATABASE_URL": "postgresql://...",  # 本番環境のDB URL
    "S3_ARCHIVE_BUCKET": "ai-chatbot-archive-prod",
    "S3_REPORTS_BUCKET": "ai-chatbot-reports-prod",
    "DYNAMODB_SESSION_TABLE": "sessions-prod",
}
```

> **推奨**: 本番環境では、環境変数ではなく **AWS Secrets Manager** や **Systems Manager Parameter Store** を使用してください。

### 5. CDKブートストラップ（初回のみ）

初回デプロイ時のみ、CDKブートストラップを実行します：

```bash
cd lambda

# ブートストラップ実行
cdk bootstrap
```

> **重要**:
>
> - `cdk bootstrap`は、CDKがアーティファクト（Lambda関数のコードなど）を保存するためのS3バケットとCloudFormationスタックを作成します
> - リージョンごとに1回だけ実行すればOKです
> - 既にブートストラップ済みの場合はスキップできます
> - **デプロイスクリプト（`deploy.sh`）を使用する場合、ブートストラップは自動的に確認・実行されます**

#### CDKブートストラップの確認方法

`cdk bootstrap`を実行すると、CloudFormationに**`CDKToolkit`**という名前のスタックが作成されます。このスタックには以下のリソースが含まれています：

- **S3バケット**: CDKがアーティファクト（Lambda関数のコードなど）を保存するためのバケット
- **IAMロール**: CDKがリソースをデプロイするために必要な権限

したがって、`CDKToolkit`スタックの存在を確認することで、bootstrapが実行済みかどうかを判断できます：

```bash
# CDKToolkitスタックの存在確認
aws cloudformation describe-stacks --stack-name CDKToolkit --region ap-northeast-1
```

デプロイスクリプト（`deploy.sh`）では、この方法で自動的にbootstrapの実行状況を確認しています。

## デプロイ手順

### デプロイスクリプトを使用

デプロイスクリプトを使用すると、認証確認、ブートストラップ確認、環境変数設定などが自動化されます。

```bash
cd lambda

# 仮想環境をアクティベート（まだの場合）
source .venv/bin/activate

# デプロイスクリプトを実行
./deploy.sh
```

スクリプトは以下の処理を自動実行します：

1. 仮想環境の確認
2. AWS認証情報の確認
3. CDKブートストラップの確認（未実行の場合は自動実行）
4. CloudFormationテンプレートの生成確認（`cdk synth`）
5. デプロイ内容の差分確認（`cdk diff`）
6. デプロイ実行（`cdk deploy`）

### デプロイの確認

#### AWSコンソールでの確認

1. **Lambda関数の確認**
   - AWSコンソール → Lambda → 関数
   - 以下の関数が作成されていることを確認：
     - `archive-conversation`
     - `cleanup-sessions`
     - `generate-stats`

2. **EventBridgeルールの確認**
   - AWSコンソール → EventBridge → ルール
   - 以下のルールが作成されていることを確認：
     - `archive-conversation-schedule`
     - `cleanup-sessions-schedule`
     - `generate-stats-schedule`

3. **IAMロールの確認**
   - AWSコンソール → IAM → ロール
   - Lambda関数用のロールが作成されていることを確認

#### コマンドラインでの確認

```bash
# Lambda関数の一覧確認
aws lambda list-functions --query 'Functions[?contains(FunctionName, `archive`) || contains(FunctionName, `cleanup`) || contains(FunctionName, `generate`)].FunctionName' --output table

# EventBridgeルールの確認
aws events list-rules --query 'Rules[?contains(Name, `archive`) || contains(Name, `cleanup`) || contains(Name, `generate`)].Name' --output table
```

## 動作確認

### 1. 手動実行による確認

#### 1.1. Lambda関数の手動実行

```bash
# archive-conversation関数を手動実行
aws lambda invoke \
  --function-name archive-conversation \
  --payload '{}' \
  response.json

# レスポンスを確認
cat response.json
```

#### 1.2. ログの確認

```bash
# CloudWatch Logsを確認
aws logs tail /aws/lambda/archive-conversation --follow
```

### 2. EventBridgeスケジュールの確認

EventBridgeルールが正しく設定されているか確認：

```bash
# ルールの詳細確認
aws events describe-rule --name archive-conversation-schedule
```

### 3. エラーの確認

エラーが発生した場合：

1. **CloudWatch Logs** でエラーログを確認
2. **Lambda関数の設定** で環境変数やタイムアウト設定を確認
3. **IAMロール** で必要な権限が付与されているか確認

## トラブルシューティング

### エラー: `cdk bootstrap` が失敗する

**原因**: IAM権限が不足している可能性があります。

**対処**:

- IAMユーザーに `s3:*` と `cloudformation:*` の権限を付与
- または、管理者権限を持つIAMユーザーで実行

### エラー: Lambda関数のデプロイが失敗する

**原因**:

- 依存関係のビルドエラー
- 環境変数の設定ミス
- IAMロールの権限不足

**対処**:

1. `cdk synth` でエラーを確認
2. Lambda関数のログを確認
3. IAMロールのポリシーを確認

### エラー: EventBridgeルールが実行されない

**原因**:

- cron式の設定ミス
- Lambda関数への権限不足

**対処**:

1. EventBridgeルールの設定を確認
2. Lambda関数の実行ログを確認
3. IAMロールの権限を確認

### エラー: デプロイスクリプトで `jq: command not found`

**原因**: `jq`コマンドがインストールされていない。

**対処**:

- macOS: `brew install jq`
- Linux: `sudo apt-get install jq` または `sudo yum install jq`
- または、スクリプトは`jq`がなくても動作します（`aws`コマンドで直接取得）

### エラー: `aws sts get-caller-identity` が失敗する

**原因**: AWS認証情報が設定されていない、または期限切れ。

**対処**:

1. `aws configure` を実行して認証情報を設定
2. 認証情報が期限切れの場合は、再設定

## スタックの削除

### 削除スクリプトを使用

削除スクリプトを使用すると、認証確認、削除対象の確認、安全な削除が自動化されます。

```bash
cd lambda

# 仮想環境をアクティベート（まだの場合）
source .venv/bin/activate

# 削除スクリプトを実行
./destroy.sh
```

スクリプトは以下の処理を自動実行します：

1. 仮想環境の確認
2. AWS認証情報の確認
3. 削除対象のスタック一覧を表示（`cdk list`）
4. 削除対象リソースの警告表示
5. 確認プロンプト（`yes`と入力する必要があります）
6. 削除実行（`cdk destroy`）

> **重要**: 削除操作は取り消せません。実行前に削除対象を確認してください。
