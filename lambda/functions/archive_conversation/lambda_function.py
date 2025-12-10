"""古い会話データをアーカイブするLambda関数"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambdaハンドラー関数
    
    Args:
        event: EventBridgeから渡されるイベント
        context: Lambdaコンテキスト
    
    Returns:
        dict: 処理結果
    """
    logger.info("Archive conversation function started")
    logger.info(f"Event: {json.dumps(event)}")
    
    # TODO: 実装
    # 1. データベースから古い会話データを取得
    # 2. S3にアーカイブ
    # 3. データベースから削除
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Archive conversation completed",
        }),
    }





