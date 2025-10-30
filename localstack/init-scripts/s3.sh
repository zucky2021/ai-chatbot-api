#!/bin/sh

set -e

echo "================================================"
echo "Initializing LocalStack S3..."
echo "================================================"

BUCKET_NAME="ai-chatbot-assets"

echo "Creating bucket: $BUCKET_NAME"
awslocal s3 mb s3://$BUCKET_NAME

echo "Listing buckets:"
awslocal s3 ls

echo "Copying initial data to bucket..."
awslocal s3 cp --recursive /init-data/s3/$BUCKET_NAME/ s3://$BUCKET_NAME/

echo "Listing bucket contents:"
awslocal s3 ls --recursive s3://$BUCKET_NAME

echo "================================================"
echo "LocalStack S3 initialization completed!"
echo "================================================"
