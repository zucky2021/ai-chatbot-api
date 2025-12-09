#!/bin/bash

# CDK削除スクリプト

set -e

# 環境名を引数またはデフォルトで設定
ENVIRONMENT=${1:-dev}

echo "🗑️  AI Chatbot Lambda CDK Destroy (Environment: $ENVIRONMENT)"

# 仮想環境の確認
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  仮想環境が有効化されていません。uvを使用して環境をアクティベートしてください。"
    echo "   cd lambda && source .venv/bin/activate"
    echo "   または"
    echo "   cd lambda && uv sync --all-extras"
    exit 1
fi

# AWS認証確認
echo "🔐 AWS認証確認中..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS認証に失敗しました。"
    echo "   aws configure を実行して認証情報を設定してください。"
    exit 1
fi

# AWS認証情報を取得
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

echo "📍 削除対象: Account=$CDK_DEFAULT_ACCOUNT, Region=$CDK_DEFAULT_REGION"

# CDKディレクトリに移動（スクリプトはlambda/直下で実行される想定）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 削除対象のスタックを確認
echo "📋 削除対象のスタックを確認中..."
cdk list

# 警告メッセージ
echo ""
echo "⚠️  警告: この操作は以下のリソースを削除します:"
echo "   - Lambda関数（archive-conversation, cleanup-sessions, generate-stats）"
echo "   - EventBridgeルール"
echo "   - IAMロールとポリシー"
echo "   - CloudWatch Logsグループ"
echo ""
echo "⚠️  この操作は取り消せません。"
echo ""

# 確認プロンプト（安全のため）
read -p "本当に削除しますか？ (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "削除をキャンセルしました。"
    exit 0
fi

# 削除実行
echo "🗑️  スタックを削除します..."
cdk destroy --all

echo "✅ 削除が完了しました！"

