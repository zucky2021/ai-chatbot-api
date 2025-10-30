#!/bin/sh
set -e

echo "================================================"
echo "Initializing LocalStack DynamoDB..."
echo "================================================"

REGION="ap-northeast-1"

echo "Checking if table already exists..."
if awslocal dynamodb describe-table --table-name chatbot-sessions --region "$REGION" >/dev/null 2>&1; then
  echo "Table already exists: chatbot-sessions"
else
  echo "Creating table: chatbot-sessions"
  awslocal dynamodb create-table \
    --table-name chatbot-sessions \
    --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region "$REGION"
fi

echo "================================================"
echo "LocalStack DynamoDB initialization completed!"
echo "================================================"
