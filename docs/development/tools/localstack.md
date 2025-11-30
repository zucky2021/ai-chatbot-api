# LocalStack

- AWSサービスのローカルエミュレーション環境
- [公式サイト](https://docs.localstack.cloud/)

## 導入済みサービス

### Amazon S3 (Simple Storage Service)

**用途**:

- ファイル保存、ログファイルのエクスポート、バックアップ、フロントエンド配信のテスト

**選定理由**:

- 開発時にS3の挙動を確認できる
- S3へのアップロード機能のテストが可能
- CloudWatch LogsのS3エクスポート機能のテスト
- フロントエンドのS3+CloudFront構成の事前検証

**[初期スクリプト](/localstack/init-scripts/s3.sh)**

### DynamoDB

**用途**:

- ユーザーセッション情報の保存
- セッションメタデータ（例: 有効期限、ステータス）の管理
- 将来的なユーザー設定やフラグ管理（feature flag 等）のストア候補

**選定理由**:

- セッション情報はスキーマが変わりやすく、**スキーマレスな DynamoDB と相性が良い**
- 高速なキーアクセス（`session_id` 単位）に最適
- TTL 機能で「期限切れセッションの自動削除」が実現しやすい
- 本番では AWS マネージドな DynamoDB を使い、ローカルでは LocalStack でほぼ同じ API 体験を得られる

**[初期スクリプト](/localstack/init-scripts/dynamodb.sh)**

**動作確認コマンド例**:

```sh
# DynamoDBテーブル一覧
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

### Amazon SQS (Simple Queue Service)

**用途**: 非同期処理の開発・テスト

**理由**:

- 非同期タスクキューイングのテスト
- バックグラウンド処理の実装検証
- メッセージ配信の検証
- 一時的にリクエストが集中してもメッセージをため込んでくれる
- 疎結合になりAPIはメッセージをキューに投げるだけで完結
- キュー自体はフルマネージドでスケーラブルなので、インフラ側の調整がシンプル

**[初期スクリプト](/localstack/init-scripts/sqs.sh)**

**動作確認コマンド例**:

```sh
aws --endpoint-url=http://localhost:4566 sqs list-queues
```

## 導入予定サービス

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

### 低優先度（将来拡張時）

#### AWS Lambda

- **用途**: サーバーレス関数の開発・テスト
- **注意**: LocalStack Pro版が必要な場合がある
- **理由**
  - 非同期処理の実装
  - イベント駆動処理のテスト
