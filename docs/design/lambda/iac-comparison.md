# Lambda開発におけるIaCツールの比較

## 概要

Lambda関数の開発・デプロイに使用するInfrastructure as Code（IaC）ツールの比較

## Point(結論)

### 本プロジェクトでの推奨アプローチ

- **CDK + SAM（ローカルテスト）の併用パターンを推奨**

#### 推奨構成

- **インフラ定義・デプロイ**: **AWS CDK (Python)**
  - 型安全性とIDE補完のメリット
  - 既存プロジェクト（Python）との統一
  - 複数のLambda関数や他のAWSリソースを統合管理

- **ローカル開発・テスト**: **AWS SAM**
  - `sam local invoke`でローカル実行・デバッグが容易
  - CDKで生成したテンプレートをSAMで実行可能
  - 開発効率を向上

#### ワークフロー

```bash
# 1. CDKでテンプレートを生成
cdk synth

# 2. SAMでローカルテスト（開発時）
sam local invoke ArchiveConversationFunction \
  --template cdk.out/LambdaStack.template.json

# 3. CDKでデプロイ（本番環境）
cdk deploy
```

#### メリット

- ✅ **CDKの型安全性**: Pythonの型ヒントでIDE補完が効く
- ✅ **SAMのローカル開発**: `sam local`で簡単にローカルテスト
- ✅ **統合管理**: CDKでインフラ全体を一元管理
- ✅ **開発効率**: ローカル開発と本番デプロイの両方に最適なツールを使用

## Reason(CDK vs Terraform vs SAM)

### AWS CDK (Cloud Development Kit)

- **推奨度: ⭐⭐⭐⭐⭐（AWS専用プロジェクトの場合）**

#### CDKの特徴

- **言語**: TypeScript、Python、Java、C#、Go
- **AWSネイティブ**: AWS専用に最適化
- **高レベル抽象化**: リソースを簡単に定義可能
- **再利用可能なコンポーネント**: Constructライブラリが豊富

#### CDKのメリット

- ✅ **Pythonで記述可能**（既存プロジェクトと統一）
- ✅ **型安全性**: IDEの補完が効く
- ✅ **AWS公式サポート**: 最新機能への対応が早い
- ✅ **テストが容易**: ユニットテストが書きやすい
- ✅ **ドキュメントが充実**: AWS公式ドキュメント

#### CDKのデメリット

- ❌ **AWS専用**: マルチクラウドには不向き
- ❌ **学習曲線**: 初期学習コストがある

#### 使用例（Python）

```python
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
)
from constructs import Construct

class BatchProcessingStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda関数
        archive_function = lambda_.Function(
            self, "ArchiveConversationFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("lambda/archive_conversation"),
            timeout=Duration.minutes(5),
        )

        # EventBridgeルール（毎日深夜2時実行）
        rule = events.Rule(
            self, "ArchiveConversationRule",
            schedule=events.Schedule.cron(hour=2, minute=0),
        )
        rule.add_target(targets.LambdaFunction(archive_function))
```

---

### Terraform

- **推奨度: ⭐⭐⭐（マルチクラウド対応が必要な場合）**

#### 特徴

- **言語**: HCL（HashiCorp Configuration Language）
- **マルチクラウド**: AWS、Azure、GCPなどに対応
- **状態管理**: Terraform Stateでリソース状態を管理
- **プロバイダー**: 豊富なプロバイダーライブラリ

#### Terraformのメリット

- ✅ **マルチクラウド対応**: 複数のクラウドプロバイダーに対応
- ✅ **宣言的**: 望ましい状態を記述するだけ
- ✅ **コミュニティ**: 大規模なコミュニティとモジュール
- ✅ **企業採用**: 多くの企業で採用実績あり

#### Terraformのデメリット

- ❌ **HCL言語**: 新しい言語を学習する必要がある
- ❌ **型安全性**: CDKほど型安全ではない
- ❌ **AWS専用プロジェクトでは過剰**: マルチクラウド不要ならCDKの方が簡単

#### 使用例（HCL）

```hcl
resource "aws_lambda_function" "archive_conversation" {
  filename         = "archive_conversation.zip"
  function_name    = "archive-conversation"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.12"
  timeout         = 300
}

resource "aws_cloudwatch_event_rule" "archive_schedule" {
  name                = "archive-conversation-schedule"
  description         = "Archive old conversations daily"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "archive_target" {
  rule      = aws_cloudwatch_event_rule.archive_schedule.name
  target_id = "ArchiveConversationTarget"
  arn       = aws_lambda_function.archive_conversation.arn
}
```

---

### AWS SAM (Serverless Application Model)

- **推奨度: ⭐⭐⭐⭐（Lambda開発に特化した場合）**

#### SAMの特徴

- **言語**: YAML/JSON
- **Lambda特化**: サーバーレスアプリケーションに最適化
- **ローカルテスト**: `sam local`でローカル実行可能
- **CloudFormationベース**: CloudFormationの拡張

#### SAMのメリット

- ✅ **Lambda開発に最適**: サーバーレスアプリケーションに特化
- ✅ **ローカル開発**: `sam local`でローカル実行・デバッグが容易
- ✅ **シンプル**: YAMLで記述するため学習コストが低い
- ✅ **統合ツール**: SAM CLIでビルド・デプロイが簡単

#### SAMのデメリット

- ❌ **Lambda特化**: 他のリソース（ECS等）には不向き
- ❌ **YAML**: 複雑なロジックには向かない

#### 使用例（YAML）

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ArchiveConversationFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: archive-conversation
      Runtime: python3.12
      Handler: handler.lambda_handler
      CodeUri: lambda/archive_conversation/
      Timeout: 300
      Events:
        ScheduleRule:
          Type: Schedule
          Properties:
            Schedule: cron(0 2 * * ? *)
```

## 参考リンク

- [AWS CDK ドキュメント](https://docs.aws.amazon.com/cdk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS SAM ドキュメント](https://docs.aws.amazon.com/serverless-application-model/)
