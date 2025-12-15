"""
LangChainのログをstructlogに統合

LangChainの内部ログを構造化ログに統合する設定
"""

import logging

import structlog


class StructlogHandler(logging.Handler):
    """標準loggingをstructlogに転送するハンドラー"""

    def __init__(self) -> None:
        super().__init__()
        self.logger = structlog.get_logger("langchain")

    def emit(self, record: logging.LogRecord) -> None:
        """
        ログレコードをstructlogに転送

        Args:
            record: ログレコード
        """
        # ログレベルに応じて適切なメソッドを呼び出す
        log_method = getattr(
            self.logger, record.levelname.lower(), self.logger.info
        )

        # 追加のコンテキスト情報を抽出
        extra = {
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 例外情報がある場合は追加
        if record.exc_info:
            extra["exc_info"] = record.exc_info

        # structlogに転送
        log_method(
            record.getMessage(),
            **extra,
        )


def configure_langchain_logging() -> None:
    """
    LangChainのログをstructlogに統合する

    LangChainが使用する標準loggingをstructlogに転送する設定を行う
    """
    # LangChain関連のロガーを取得
    langchain_loggers = [
        "langchain",
        "langchain_core",
        "langchain_community",
        "langchain_google_genai",
        "langgraph",
    ]

    # 各ロガーにstructlogハンドラーを設定
    for logger_name in langchain_loggers:
        logger = logging.getLogger(logger_name)
        # 既存のハンドラーをクリア
        logger.handlers.clear()
        # structlogハンドラーを追加
        logger.addHandler(StructlogHandler())
        # ログレベルを設定
        logger.setLevel(logging.INFO)
        # 親ロガーへの伝播を無効化（重複を防ぐ）
        logger.propagate = False
