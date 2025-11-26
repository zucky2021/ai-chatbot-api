# 技術スタック

## 概要

- 使用している技術のまとめ

## 一覧

### AWS CDK

**概要**:

- AWS が提供する Infrastructure as Code フレームワーク
- Python/TypeScript などのプログラミング言語でCloudFormationテンプレートを生成してインフラをコードとして管理可能

**選定理由**:

- 既存バックエンドが Python のため、**同じ言語で IaC を書ける**
- 型ヒント・IDE 補完により、宣言的 YAML よりも安全・読みやすい
- Lambda だけでなく、将来的な ECS / RDS / VPC なども **一括で管理可能**
- CloudFormation ベースのため、AWS ネイティブな統合がしやすい

**参考**:

- [AWS CDK ドキュメント](https://docs.aws.amazon.com/cdk/)
- [CDK Python リファレンス](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [CDK ローカル開発](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)

### AWS Serverless Application Model(SAM)

**概要**:

- Lambdaなどのサーバーレスアプリケーションを簡潔なYAMLのテンプレートで定義し、ローカル実行・デプロイをサポートするフレームワーク

**役割（本プロジェクトでの位置づけ）**:

- **ローカルテスト専用ツール**として利用
  - CDK で生成した CloudFormation テンプレートを `sam local invoke` で実行
  - Lambda 関数の挙動をローカル環境（Docker）で確認
- 必要に応じて、単体の PoC や簡易構成のときにテンプレート直書きで使うことも可能

**CDK との関係**:

- 本番・検証環境へのデプロイ: **CDK が担当**
- ローカル実行・デバッグ: **SAM が担当**
- 2 つを組み合わせた「CDK + SAM」構成を採用している

## 参考リンク

- [SAM CLI と CDK の統合](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-cdk-using.html)
