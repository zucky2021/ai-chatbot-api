#!/usr/bin/env python3
"""CDKアプリのエントリーポイント"""

import os

import aws_cdk as cdk
from infra.lambda_stack import LambdaStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-northeast-1"),
)

LambdaStack(
    app,
    "LambdaStack",
    env=env,
)

app.synth()
