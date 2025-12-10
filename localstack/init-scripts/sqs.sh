#!/bin/sh
set -e

echo "================================================"
echo "Initializing LocalStack SQS..."
echo "================================================"

echo "Creating queue: fastapi-to-lambda-queue"
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name fastapi-to-lambda-queue || true

echo "Listing queues:"
aws --endpoint-url=http://localhost:4566 sqs list-queues


echo "================================================"
echo "LocalStack SQS initialization completed!"
echo "================================================"
