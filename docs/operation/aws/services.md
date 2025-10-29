# 推奨AWSサービス

本プロジェクトのアーキテクチャ（FastAPI、WebSocket、PostgreSQL、DynamoDB、Redis、ベクトル検索）と相性の良いAWSサービスを紹介します。

## データベース関連

### Amazon RDS for PostgreSQL

- **用途**: 会話履歴の保存・pgvector拡張によるベクトル検索
- **選定理由**
  - PostgreSQL互換で既存コードとの統合が容易
  - pgvector拡張が利用可能
  - マネージドサービスによる運用負荷の削減
  - 自動バックアップ・リカバリ機能
  - マルチAZ配置による高可用性
- **現在の構成**: DockerのPostgreSQL
- **移行メリット**: 運用の自動化、スケーラビリティ向上

### Amazon DynamoDB

- **用途**: ユーザーセッション管理、設定データ保存
- **選定理由**
  - 既にLocalStackでエミュレーション済み
  - スキーマレスで柔軟なデータ構造
  - 自動スケーリング
  - TTL機能によるセッション自動削除
- **現在の構成**: LocalStackでエミュレーション
- **移行メリット**: 本番環境との統合、高いパフォーマンス

### Amazon ElastiCache for Redis

- **用途**: キャッシュ、セッション管理、レート制限
- **選定理由**
  - 既にLocalStackでエミュレーション済み
  - インメモリキャッシュによる高速アクセス
  - 自動フェイルオーバー機能
  - クラスタリングによるスケールアウト
- **現在の構成**: LocalStackでエミュレーション
- **移行メリット**: 高可用性、管理コスト削減

## AI・機械学習関連

### Amazon Bedrock

- **用途**: AIモデル連携（Google AI Studioの代替・補完）
- **選定理由**
  - 複数のAIモデル（Claude、Llama2等）に統一インターフェースでアクセス
  - ベクトルデータベース（Amazon Bedrock Knowledge Bases）との統合
  - RAG（Retrieval-Augmented Generation）の実装が容易
  - サーバーレス運用でスケーリング対応
- **現在の構成**: Google AI Studio API
- **移行メリット**: マルチプロバイダー対応、コスト最適化

### Amazon OpenSearch Serverless

- **用途**: ベクトル検索、セマンティック検索
- **選定理由**
  - ネイティブベクトル検索機能（k-NN）
  - サーバーレスで運用負荷ゼロ
  - pgvectorからの移行も検討可能
  - 全文検索とベクトル検索のハイブリッド検索
- **現在の構成**: PostgreSQL + pgvector
- **移行メリット**: 検索パフォーマンス向上、スケーラビリティ

## コンピューティング・ホスティング

### Amazon ECS (Fargate)

- **用途**: FastAPIバックエンドのコンテナ実行
- **選定理由**
  - Docker Compose環境からの移行が容易
  - サーバーレス運用（Fargate）でインフラ管理不要
  - 自動スケーリング対応
  - 既存Dockerfileの再利用可能
- **現在の構成**: Docker Compose
- **移行メリット**: スケーラビリティ、可用性向上

### AWS App Runner

- **用途**: 軽量なAPIサービスのホスティング
- **選定理由**
  - よりシンプルなデプロイプロセス
  - 自動スケーリングとヘルスチェック
  - GitHub連携による自動デプロイ
  - ECSよりシンプルな運用

### AWS Lambda

- **用途**: 非同期処理、バッチ処理、Webhook受信
- **選定理由**
  - イベント駆動型の軽量処理に最適
  - サーバーレスでコスト効率が高い
  - FastAPIエンドポイントの一部をLambda関数として実装可能

## ネットワーク・通信

### Amazon API Gateway

- **用途**: REST API管理、WebSocket API管理
- **選定理由**
  - WebSocket API対応によりリアルタイム通信をサポート
  - 認証・認可の一元管理
  - レート制限、リクエストバリデーション
  - CloudWatch連携による監視
- **現在の構成**: FastAPI直接公開
- **移行メリット**: API管理機能の強化、セキュリティ向上

### AWS CloudFront

- **用途**: フロントエンド（React）のCDN配信、APIのキャッシング、DDoS保護
- **選定理由**
  - グローバルエッジロケーションによる低遅延配信
  - 静的コンテンツ（JS、CSS、画像）の高速配信
  - 動的コンテンツのキャッシング機能
  - DDoS保護（AWS Shield Standard統合）
  - SSL/TLS証明書の自動管理（ACM統合）
  - S3とのシームレスな統合
  - カスタムエラーページ、アクセスログ取得
- **本プロジェクトでの活用例**
  - Reactアプリケーションのグローバル配信
  - APIレスポンスのキャッシング（認証が必要なもの以外）
  - WebSocket接続のルーティング最適化
- **現在の構成**: 未実装
- **導入メリット**: ユーザー体験の向上、グローバルスケール対応、セキュリティ強化

## 認証・セキュリティ

### Amazon Cognito

- **用途**: ユーザー認証・認可
- **選定理由**
  - ユーザープールによる認証管理
  - OAuth2、OpenID Connect対応
  - マルチファクター認証（MFA）
  - ソーシャルログイン（Google、GitHub等）の統合
- **現在の構成**: 未実装
- **導入メリット**: セキュアな認証機能の実装

### AWS Secrets Manager

- **用途**: APIキー、データベース認証情報の安全な管理
- **選定理由**
  - シークレットの自動ローテーション
  - IAMによるアクセス制御
  - CloudWatch連携による監査ログ
- **現在の構成**: 環境変数ファイル（.env）
- **移行メリット**: セキュリティ強化、コンプライアンス対応

### AWS Systems Manager Parameter Store

- **用途**: 設定値の管理（Secrets Managerより低コスト）
- **選定理由**
  - シンプルな設定値管理
  - 階層構造による整理
  - 暗号化パラメータ対応
  - コスト効率（Secrets Managerより安価）

## 監視・ログ

### Amazon CloudWatch

- **用途**: ログ収集、メトリクス監視、アラート、ダッシュボード
- **選定理由**
  - AWSサービスの標準監視ツールで統合監視が可能
  - CloudWatch Logsによるログ集約と検索機能
  - カスタムメトリクスの作成と可視化
  - アラーム通知（SNS、Email連携）
  - CloudWatch Insightsによるログ分析
  - ダッシュボードによるリアルタイム監視
  - コスト効率的なログ保存（S3への自動エクスポート）
- **本プロジェクトでの活用例**
  - FastAPIアプリケーションのアクセスログ監視
  - WebSocket接続数のモニタリング
  - API応答時間、エラー率の追跡
  - RDS、ElastiCacheのパフォーマンス監視
  - カスタムビジネスメトリクス（会話数、ユーザー数など）
- **現在の構成**: 未実装
- **導入メリット**: 運用監視の自動化、問題の早期発見、システム健全性の可視化

### AWS X-Ray

- **用途**: 分散トレーシング、パフォーマンス分析
- **選定理由**
  - マイクロサービス間のトレーシング
  - レイテンシー分析
  - ボトルネックの特定
  - FastAPIと相性が良い

## ストレージ

### Amazon S3

- **用途**: ファイル保存、ログファイル保管、バックアップ、静的ウェブサイトホスティング
- **選定理由**
  - オブジェクトストレージとして柔軟でスケーラブル
  - ライフサイクルポリシーによる自動アーカイブ・削除
  - バージョニング機能によるデータ保護
  - 静的ウェブサイトホスティング（フロントエンド配信）
  - CloudFrontとの統合による高速配信
  - Intelligent-Tieringによる自動コスト最適化
  - コスト効率が高く、大容量データ保存に適している
- **本プロジェクトでの活用例**
  - Reactアプリケーションのビルド成果物の配信
  - CloudWatch Logsのエクスポート先
  - 会話データのバックアップ・アーカイブ
  - アップロードファイルの保存（将来拡張時）
- **現在の構成**: 未実装
- **導入メリット**: コスト効率的なストレージ、CDNとの統合による高速配信

## インフラ管理

### AWS CloudFormation

- **用途**: インフラストラクチャのコード化（Infrastructure as Code）
- **選定理由**
  - インフラのバージョン管理と再現性の確保
  - テンプレートベースで複数環境（dev/staging/prod）を管理
  - スタックによる依存関係管理
  - 変更セットによる影響確認
  - ロールバック機能による安全な更新
  - 他のIaCツール（Terraform、CDK）との比較でAWSネイティブな統合
- **本プロジェクトでの活用例**
  - ECS Fargate、RDS、ElastiCache等の一括構築
  - VPC、セキュリティグループの定義
  - IAMロール・ポリシーの管理
  - 環境ごとのパラメータファイルによる設定管理
  - CodePipelineとの統合によるインフラ更新の自動化
- **現在の構成**: 未実装（手動構築）
- **導入メリット**: インフラの再現性、変更履歴の追跡、チーム間の一貫性確保

## データ分析・ETL

### AWS Glue

- **用途**: ETL処理、データカタログ、データ準備
- **選定理由**
  - サーバーレスなETL処理でスケーラブル
  - Sparkベースのデータ処理
  - データカタログによるメタデータ管理
  - S3、RDS、DynamoDB等の多様なデータソースに対応
  - Python、ScalaでのETLジョブ作成
  - スケジュール実行（EventBridge統合）
- **本プロジェクトでの活用例**
  - 会話履歴データ（PostgreSQL）のS3へのエクスポート
  - CloudWatch LogsのETL処理
  - ユーザー行動分析用のデータ準備
  - 会話データの前処理（ベクトル化、テキストクリーニング等）
  - データウェアハウス（Redshift等）へのデータ取り込み
- **現在の構成**: 未実装
- **導入メリット**: 大規模データ処理の自動化、データ分析基盤の構築

### Amazon Athena

- **用途**: S3上のデータに対するSQLクエリ実行
- **選定理由**
  - サーバーレスでインフラ管理不要
  - S3上のJSON、CSV、Parquet等を直接クエリ可能
  - Glue Data Catalogとの統合
  - 標準SQLでクエリ可能
  - ペイパーユースモデル（クエリ実行量のみ課金）
  - CloudWatch Logsとの統合によるログ分析
- **本プロジェクトでの活用例**
  - CloudWatch Logsのエクスポートデータ（S3）の分析
  - 会話履歴のバックアップデータ（S3）の分析
  - ユーザー行動ログの分析クエリ
  - エラーログの検索・分析
  - ビジネスインテリジェンス（BI）レポートの生成
- **現在の構成**: 未実装
- **導入メリット**: データ分析の簡素化、コスト効率的な分析基盤、BIツールとの連携

## CI/CD

### AWS CodePipeline

- **用途**: 継続的インテグレーション・デプロイ（CI/CDパイプライン）
- **選定理由**
  - GitHub、CodeCommit、S3等との統合
  - ビルド・テスト・デプロイの自動化
  - ECS/Fargateへの自動デプロイ対応
  - マルチ環境対応（dev、staging、production）
  - 承認ゲートによるデプロイ制御
  - パイプラインの可視化とロールバック機能
- **本プロジェクトでの活用例**
  - GitHubへのプッシュ時の自動ビルド・テスト
  - ECS Fargateへの自動デプロイ
  - フロントエンドのS3への自動デプロイ
  - CloudFormationによるインフラ更新の自動化
- **代替案**: GitHub Actions（AWSデプロイアクション利用）
- **現在の構成**: 未実装
- **導入メリット**: デプロイプロセスの自動化、一貫性の確保、デプロイ時間の短縮

### AWS CodeBuild

- **用途**: ビルドプロセスの実行
- **選定理由**
  - Dockerイメージのビルド
  - テスト実行環境の提供
  - マルチ環境対応（Python、Node.js）
  - CodePipelineとの統合
  - ビルドキャッシュによる高速化
  - カスタムビルド環境の定義
- **現在の構成**: 未実装
- **導入メリット**: ビルド環境の標準化、再現性の確保

## 推奨構成パターン

### パターン1: サーバーレス重視

```text
Infrastructure: CloudFormation
Frontend: S3 + CloudFront
API: API Gateway (WebSocket) + Lambda
Database: RDS PostgreSQL + DynamoDB + ElastiCache
AI: Amazon Bedrock
Monitoring: CloudWatch
CI/CD: CodePipeline + CodeBuild
```

### パターン2: コンテナベース（既存構成に近い）

```text
Infrastructure: CloudFormation
Frontend: S3 + CloudFront
API: ECS Fargate (FastAPI)
Database: RDS PostgreSQL + DynamoDB + ElastiCache
AI: Google AI Studio / Amazon Bedrock
Monitoring: CloudWatch
CI/CD: CodePipeline + CodeBuild
```

### パターン3: ハイブリッド

```text
Infrastructure: CloudFormation
Frontend: S3 + CloudFront
API: ECS Fargate (FastAPI) + API Gateway
Database: RDS PostgreSQL + DynamoDB + ElastiCache
Search: OpenSearch Serverless (ベクトル検索)
AI: Amazon Bedrock
Monitoring: CloudWatch + X-Ray
CI/CD: CodePipeline + CodeBuild
```

### パターン4: データ分析統合

```text
Infrastructure: CloudFormation
Frontend: S3 + CloudFront
API: ECS Fargate (FastAPI)
Database: RDS PostgreSQL + DynamoDB + ElastiCache
Data Lake: S3
ETL: AWS Glue
Analytics: Amazon Athena
Monitoring: CloudWatch
CI/CD: CodePipeline + CodeBuild
```

## 段階的な移行戦略

### Phase 1: 基礎インフラ

1. S3（ログ、バックアップ、フロントエンド配信）
2. Secrets Manager（認証情報管理）
3. CloudWatch（監視）
4. CloudFormation（インフラのコード化）

### Phase 2: データベース

1. ElastiCache for Redis（キャッシュ）
2. DynamoDB（セッション管理）
3. RDS PostgreSQL（会話履歴、ベクトル検索）

### Phase 3: アプリケーション

1. ECS Fargate（FastAPIコンテナ）
2. S3 + CloudFront（フロントエンド）
3. API Gateway（API管理、WebSocket）

### Phase 4: 高度な機能

1. Amazon Bedrock（AIモデル）
2. OpenSearch Serverless（高度なベクトル検索）
3. Cognito（認証）

### Phase 5: データ分析・活用

1. AWS Glue（データETL、データカタログ）
2. Amazon Athena（ログ・データ分析）
3. データレイク（S3）の構築

## コスト最適化のポイント

1. **RDS**: リザーブドインスタンスで最大72%削減
2. **ElastiCache**: リザーブドノードで最大55%削減
3. **Lambda**: リクエスト量に応じた従量課金で無駄なコストなし
4. **S3**: Intelligent-Tieringで自動的に最適なストレージクラスに移動、ライフサイクルポリシーでアーカイブ
5. **ECS Fargate**: 使用したリソースのみ課金
6. **Athena**: クエリ実行量のみ課金で、分析の必要時にのみコスト発生
7. **Glue**: ジョブ実行時間に応じた従量課金

## 参考リンク

- [AWS公式ドキュメント](https://docs.aws.amazon.com/ja_jp/)
- [AWS Architecture Center](https://aws.amazon.com/jp/architecture/)
- [AWS Well-Architected Framework](https://aws.amazon.com/jp/architecture/well-architected/)
