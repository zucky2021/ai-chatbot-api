# LocalStack

- AWSサービスのローカルエミュレーション環境
- [公式サイト](https://docs.localstack.cloud/)

## 現在エミュレートしているサービス

- **DynamoDB**: ユーザーセッション管理
- **ElastiCache (Redis)**: キャッシュ、セッション管理

## 推奨：追加エミュレートすべきサービス

開発効率とコスト削減の観点から、以下のサービスを追加でエミュレートすることを推奨します。

### 高優先度

#### Amazon S3

- **用途**: ファイル保存、ログファイルのエクスポート、バックアップ、フロントエンド配信のテスト
- **理由**
  - 開発時にS3の挙動を確認できる
  - S3へのアップロード機能のテストが可能
  - CloudWatch LogsのS3エクスポート機能のテスト
  - フロントエンドのS3+CloudFront構成の事前検証
- **実装**: `SERVICES=dynamodb,elasticache,s3` に追加
- **初期化**: バケット作成スクリプトを `init-localstack.sh` に追加

#### AWS Secrets Manager

- **用途**: シークレット管理の開発・テスト
- **理由**
  - 本番環境と同じ方法でシークレットを管理できる
  - コード変更なしで本番環境に移行可能
  - 環境変数ファイル（.env）からの移行がスムーズ
- **実装**: `SERVICES=dynamodb,elasticache,s3,secretsmanager` に追加
- **初期化**: APIキー等のシークレット作成スクリプトを追加

### 中優先度

#### Amazon SNS (Simple Notification Service)

- **用途**: 通知機能の開発・テスト（将来拡張時）
- **理由**
  - エラーハンドリング時の通知機能のテスト
  - CloudWatchアラームの通知先として使用
  - 将来のpush通知機能の準備
- **実装**: `SERVICES=...,sns` に追加

#### Amazon SES (Simple Email Service)

- **用途**: メール送信機能の開発・テスト（将来拡張時）
- **理由**
  - ユーザー認証時のメール送信テスト
  - 通知メール機能の開発
  - 本番環境と同じAPIを使用できる
- **実装**: `SERVICES=...,ses` に追加

#### Amazon SQS (Simple Queue Service)

- **用途**: 非同期処理の開発・テスト
- **理由**
  - 非同期タスクキューイングのテスト
  - バックグラウンド処理の実装検証
  - メッセージ配信の検証
- **実装**: `SERVICES=...,sqs` に追加

#### DynamoDB

ユーザーセッション、設定の保存に使用

```bash
# DynamoDBテーブル一覧
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

### 低優先度（将来拡張時）

#### AWS Lambda

- **用途**: サーバーレス関数の開発・テスト
- **注意**: LocalStack Pro版が必要な場合がある
- **理由**
  - 非同期処理の実装
  - イベント駆動処理のテスト

#### Amazon API Gateway

- **用途**: API Gatewayの設定テスト
- **注意**: LocalStack Pro版が必要な場合がある
- **理由**
  - 本番環境のAPI Gateway設定の事前検証
  - WebSocket設定のテスト

## 実装例

### compose.yml の更新例

```yaml
localstack:
  environment:
    - SERVICES=dynamodb,elasticache,s3,secretsmanager,ssm,sns,ses,sqs
```

### init-localstack.sh の追加例

```bash
# S3バケットの作成
awslocal s3 mb s3://chatbot-files --region us-east-1
awslocal s3 mb s3://chatbot-logs --region us-east-1
awslocal s3 mb s3://chatbot-frontend --region us-east-1

# Secrets Manager にシークレットを作成
awslocal secretsmanager create-secret \
    --name chatbot/google-ai-api-key \
    --secret-string "${GOOGLE_AI_API_KEY:-dummy-key}" \
    --region us-east-1

# SSM Parameter Store にパラメータを作成
awslocal ssm put-parameter \
    --name /chatbot/database/url \
    --value "${DATABASE_URL}" \
    --type String \
    --region us-east-1
```

## 本番環境への移行

LocalStackでエミュレートしたサービスは、本番環境でも同じAPIを使用しているため、エンドポイントURLを変更するだけで移行できます。

```python
# 開発環境（LocalStack）
AWS_ENDPOINT_URL=http://localstack:4566

# 本番環境（AWS）
# AWS_ENDPOINT_URL を削除または未設定（デフォルトでAWSエンドポイントを使用）
```

## 参考リンク

- [LocalStack 公式ドキュメント](https://docs.localstack.cloud/)
- [LocalStack サポートサービス一覧](https://docs.localstack.cloud/user-guide/aws/feature-coverage/)
