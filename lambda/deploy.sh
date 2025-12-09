#!/bin/bash

# CDKデプロイスクリプト

set -e

# 環境名を引数またはデフォルトで設定
ENVIRONMENT=${1:-dev}

echo "🚀 AI Chatbot Lambda CDK Deploy (Environment: $ENVIRONMENT)"

echo "🔍 仮想環境の確認中..."
echo "   $VIRTUAL_ENV"
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  仮想環境が有効化されていません。uvを使用して環境をアクティベートしてください。"
    echo "   cd lambda && source .venv/bin/activate"
    echo "   または"
    echo "   cd lambda && uv sync --all-extras"
    exit 1
fi

echo "🔐 AWS認証確認中..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS認証に失敗しました。"
    echo "   aws configure を実行して認証情報を設定してください。"
    exit 1
fi

echo "🔐 AWS認証情報を取得中..."
CALLER_IDENTITY=$(aws sts get-caller-identity)
if command -v jq &> /dev/null; then
    ACCOUNT_ID=$(echo "$CALLER_IDENTITY" | jq -r '.Account')
    USER_ARN=$(echo "$CALLER_IDENTITY" | jq -r '.Arn')
else
    # jqがない場合は、awsコマンドで直接取得
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
fi

echo "🔑 AWS認証情報:"
echo "   Account: $ACCOUNT_ID"
echo "   User: $USER_ARN"

# 環境変数を設定
export ENVIRONMENT=$ENVIRONMENT
export CDK_DEFAULT_ACCOUNT=$ACCOUNT_ID
export CDK_DEFAULT_REGION="ap-northeast-1"

echo "📍 デプロイ先: Account=$CDK_DEFAULT_ACCOUNT, Region=$CDK_DEFAULT_REGION"

# CDKディレクトリに移動（スクリプトはlambda/直下で実行される想定）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 初回デプロイ時のみブートストラップを確認
# CDKのbootstrapを実行すると、CloudFormationに「CDKToolkit」という名前のスタックが作成される
# このスタックには、CDKがアーティファクト（Lambda関数のコードなど）を保存するための
# S3バケットやその他の必要なリソースが含まれている
# したがって、CDKToolkitスタックの存在を確認することで、bootstrapが実行済みかどうかを判断できる
echo "🔍 CDKブートストラップ確認中..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region "$CDK_DEFAULT_REGION" >/dev/null 2>&1; then
    echo "⚠️  CDKブートストラップが必要です。実行します..."
    cdk bootstrap
else
    echo "✅ CDKブートストラップ済み"
fi

echo "🏗️  CDK Synthesize実行(CloudFormationテンプレートの生成)中..."
cdk synth

echo "📊 デプロイ内容の差分確認中..."
cdk diff || true  # 差分がない場合もエラーにしない

echo "🚀 デプロイを開始します..."
cdk deploy --all

echo "✅ デプロイが完了しました！"

