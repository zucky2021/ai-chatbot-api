"""Lambda関数とEventBridgeルールを定義するCDKスタック"""

from aws_cdk import (
    Duration,
    Stack,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class LambdaStack(Stack):
    """バッチ処理用Lambda関数とEventBridgeルールを定義するスタック"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 環境変数の定義（パラメータ化する場合は後で変更）
        # 本番環境では Secrets Manager や Systems Manager Parameter Store から取得
        # 注意: AWS_REGION は Lambda ランタイムによって自動設定されるため、手動で設定しない
        common_env = {
            "LOG_LEVEL": "INFO",
        }

        # 1. 古い会話データのアーカイブLambda関数
        # PythonFunction を使用すると、uv.lock を自動検出してビルドしてくれる
        archive_function = PythonFunction(
            self,
            "ArchiveConversationFunction",
            function_name="archive-conversation",
            entry=".",  # lambda/ ルートを指定（pyproject.toml と uv.lock がある場所）
            index="functions/archive_conversation/lambda_function.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            timeout=Duration.minutes(10),  # 大量データ処理のため10分
            memory_size=512,
            environment={
                **common_env,
                # 本番環境では環境変数やSecrets Managerから取得
                "DATABASE_URL": "postgresql://...",  # TODO: パラメータ化
                "S3_ARCHIVE_BUCKET": "ai-chatbot-archive",  # TODO: パラメータ化
            },
        )

        # S3への書き込み権限を付与
        archive_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                ],
                resources=["arn:aws:s3:::ai-chatbot-archive/*"],  # TODO: パラメータ化
            )
        )

        # EventBridgeルール（毎日深夜2時実行）
        archive_rule = events.Rule(
            self,
            "ArchiveConversationRule",
            rule_name="archive-conversation-schedule",
            description="Archive old conversations daily",
            schedule=events.Schedule.cron(
                minute="0",
                hour="2",
                day="*",
                month="*",
                year="*",
            ),
        )
        archive_rule.add_target(targets.LambdaFunction(archive_function))

        # 2. 期限切れセッションの自動削除Lambda関数
        cleanup_function = PythonFunction(
            self,
            "CleanupSessionsFunction",
            function_name="cleanup-sessions",
            entry=".",  # lambda/ ルートを指定（pyproject.toml と uv.lock がある場所）
            index="functions/cleanup_sessions/lambda_function.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            timeout=Duration.minutes(5),
            memory_size=256,
            environment={
                **common_env,
                "DYNAMODB_SESSION_TABLE": "sessions",  # TODO: パラメータ化
            },
        )

        # DynamoDBへの読み書き権限を付与
        cleanup_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:Scan",
                    "dynamodb:Query",
                    "dynamodb:DeleteItem",
                ],
                resources=["arn:aws:dynamodb:*:*:table/sessions"],  # TODO: パラメータ化
            )
        )

        # EventBridgeルール（毎日深夜3時実行）
        cleanup_rule = events.Rule(
            self,
            "CleanupSessionsRule",
            rule_name="cleanup-sessions-schedule",
            description="Cleanup expired sessions daily",
            schedule=events.Schedule.cron(
                minute="0",
                hour="3",
                day="*",
                month="*",
                year="*",
            ),
        )
        cleanup_rule.add_target(targets.LambdaFunction(cleanup_function))

        # 3. 統計データの集計・レポート生成Lambda関数
        stats_function = PythonFunction(
            self,
            "GenerateStatsFunction",
            function_name="generate-stats",
            entry=".",  # lambda/ ルートを指定（pyproject.toml と uv.lock がある場所）
            index="functions/generate_stats/lambda_function.py",
            handler="lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            timeout=Duration.minutes(5),
            memory_size=256,
            environment={
                **common_env,
                "DATABASE_URL": "postgresql://...",  # TODO: パラメータ化
                "S3_REPORTS_BUCKET": "ai-chatbot-reports",  # TODO: パラメータ化
            },
        )

        # S3への書き込み権限を付与
        stats_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                ],
                resources=["arn:aws:s3:::ai-chatbot-reports/*"],  # TODO: パラメータ化
            )
        )

        # EventBridgeルール（毎日深夜4時実行）
        stats_rule = events.Rule(
            self,
            "GenerateStatsRule",
            rule_name="generate-stats-schedule",
            description="Generate daily statistics report",
            schedule=events.Schedule.cron(
                minute="0",
                hour="4",
                day="*",
                month="*",
                year="*",
            ),
        )
        stats_rule.add_target(targets.LambdaFunction(stats_function))
