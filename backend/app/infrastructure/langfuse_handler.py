"""LangFuseコールバックハンドラーの設定"""

from langfuse.langchain import CallbackHandler

from app.infrastructure.config import settings
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


def create_langfuse_handler() -> CallbackHandler | None:
    """LangFuseコールバックハンドラーを作成

    Returns:
        LangFuseが有効な場合: CallbackHandlerインスタンス
        LangFuseが無効な場合: None
    """
    if not settings.LANGFUSE_ENABLED:
        logger.debug("langfuse_disabled", message="LangFuse is disabled")
        return None

    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        logger.warning(
            "langfuse_keys_missing",
            message="LangFuse is enabled but API keys are not set",
        )
        return None

    try:
        handler = CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
        logger.info(
            "langfuse_handler_created",
            host=settings.LANGFUSE_HOST,
        )
        return handler
    except Exception as e:
        logger.error(
            "langfuse_handler_creation_error",
            error=str(e),
            exc_info=True,
        )
        return None
