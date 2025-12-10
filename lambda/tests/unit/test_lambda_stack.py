"""LambdaStackのユニットテスト"""

import aws_cdk as cdk
import aws_cdk.assertions as assertions
from infra.lambda_stack import LambdaStack


def test_lambda_functions_created():
    """Lambda関数が正しく作成されることを確認"""
    app = cdk.App()
    stack = LambdaStack(app, "LambdaStack")
    template = assertions.Template.from_stack(stack)

    # 3つのLambda関数が作成されることを確認
    template.resource_count_is("AWS::Lambda::Function", 3)

    # archive-conversation関数の存在確認
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "FunctionName": "archive-conversation",
            "Runtime": "python3.12",
            "Timeout": 600,  # 10分 = 600秒
            "MemorySize": 512,
        },
    )

    # cleanup-sessions関数の存在確認
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "FunctionName": "cleanup-sessions",
            "Runtime": "python3.12",
            "Timeout": 300,  # 5分 = 300秒
            "MemorySize": 256,
        },
    )

    # generate-stats関数の存在確認
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "FunctionName": "generate-stats",
            "Runtime": "python3.12",
            "Timeout": 300,  # 5分 = 300秒
            "MemorySize": 256,
        },
    )


def test_eventbridge_rules_created():
    """EventBridgeルールが正しく作成されることを確認"""
    app = cdk.App()
    stack = LambdaStack(app, "LambdaStack")
    template = assertions.Template.from_stack(stack)

    # 3つのEventBridgeルールが作成されることを確認
    template.resource_count_is("AWS::Events::Rule", 3)

    # archive-conversation-scheduleルールの存在確認
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "Name": "archive-conversation-schedule",
            "Description": "Archive old conversations daily",
        },
    )

    # cleanup-sessions-scheduleルールの存在確認
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "Name": "cleanup-sessions-schedule",
            "Description": "Cleanup expired sessions daily",
        },
    )

    # generate-stats-scheduleルールの存在確認
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "Name": "generate-stats-schedule",
            "Description": "Generate daily statistics report",
        },
    )


def test_lambda_iam_roles_created():
    """Lambda関数用のIAMロールが正しく作成されることを確認"""
    app = cdk.App()
    stack = LambdaStack(app, "LambdaStack")
    template = assertions.Template.from_stack(stack)

    # 3つのIAMロールが作成されることを確認（各Lambda関数に1つずつ）
    template.resource_count_is("AWS::IAM::Role", 3)
