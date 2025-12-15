"""
構造化ログの設定

Amazon Athenaでの検索に対応したJSON形式のログを出力
"""

from collections.abc import MutableMapping
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def mask_sensitive_fields(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    機密情報をマスキングする

    Args:
        logger: ロガーインスタンス
        method_name: メソッド名
        event_dict: イベント辞書

    Returns:
        マスキング済みのイベント辞書
    """
    sensitive_keys = {
        "GOOGLE_AI_API_KEY",
        "google_ai_api_key",
        "api_key",
        "password",
        "secret",
        "token",
        "AWS_SECRET_ACCESS_KEY",
        "aws_secret_access_key",
    }

    def mask_dict(d: MutableMapping[str, Any]) -> dict[str, Any]:
        """辞書内の機密情報をマスキング"""
        masked: dict[str, Any] = {}
        for key, value in d.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked[key] = mask_dict(value)
            elif isinstance(value, list):
                masked[key] = [
                    mask_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked[key] = value
        return masked

    return mask_dict(event_dict)


def add_app_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    アプリケーションコンテキストを追加

    Args:
        logger: ロガーインスタンス
        method_name: メソッド名
        event_dict: イベント辞書

    Returns:
        コンテキスト追加済みのイベント辞書
    """
    event_dict["application"] = "ai-chatbot-api"
    event_dict["environment"] = "production"  # 環境変数から取得することも可能
    return event_dict


def configure_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """
    構造化ログの設定

    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        json_logs: JSON形式で出力するか（本番環境ではTrue）
    """
    # 共通のプロセッサ
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
        mask_sensitive_fields,
    ]

    if json_logs:
        # 本番環境: JSON形式
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # 開発環境: 読みやすい形式
        processors = shared_processors + [
            structlog.processors.ExceptionRenderer(),
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # structlogの設定
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 標準ログの設定
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # uvicornのログレベルも設定
    logging.getLogger("uvicorn").setLevel(getattr(logging, log_level.upper()))
    logging.getLogger("uvicorn.access").setLevel(
        getattr(logging, log_level.upper())
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    構造化ロガーを取得

    Args:
        name: ロガー名（通常は __name__）

    Returns:
        構造化ロガー
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
