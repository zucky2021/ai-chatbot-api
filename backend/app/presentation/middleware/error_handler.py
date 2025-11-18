"""
グローバル例外ハンドラー

統一されたエラーレスポンスと構造化ログを提供
"""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog

from app.presentation.models.error import (
    ERROR_CODE_TO_HTTP_STATUS,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
)

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """アプリケーション例外の基底クラス"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def app_exception_handler(
    request: Request, exc: AppError
) -> JSONResponse:
    """
    アプリケーション例外のハンドラー

    Args:
        request: リクエストオブジェクト
        exc: アプリケーション例外

    Returns:
        統一されたエラーレスポンス
    """
    request_id = getattr(request.state, "request_id", None)

    # ログ出力
    logger.error(
        "application_error",
        error_code=exc.error_code.value,
        message=exc.message,
        details=exc.details,
        exc_info=True,
    )

    error_detail = ErrorDetail(
        code=exc.error_code,
        message=exc.message,
        details=exc.details if exc.details else None,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=ERROR_CODE_TO_HTTP_STATUS.get(exc.error_code, 500),
        content=ErrorResponse(error=error_detail).model_dump(),
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    HTTPException のハンドラー

    Args:
        request: リクエストオブジェクト
        exc: HTTP例外

    Returns:
        統一されたエラーレスポンス
    """
    request_id = getattr(request.state, "request_id", None)

    # エラーコードを決定
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        error_code = ErrorCode.NOT_FOUND
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        error_code = ErrorCode.UNAUTHORIZED
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        error_code = ErrorCode.FORBIDDEN
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        error_code = ErrorCode.VALIDATION_ERROR
    else:
        error_code = ErrorCode.INTERNAL_ERROR

    # ログ出力
    logger.warning(
        "http_error",
        status_code=exc.status_code,
        error_code=error_code.value,
        message=str(exc.detail),
    )

    error_detail = ErrorDetail(
        code=error_code,
        message=str(exc.detail),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error_detail).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """
    バリデーションエラーのハンドラー

    Args:
        request: リクエストオブジェクト
        exc: バリデーション例外

    Returns:
        統一されたエラーレスポンス
    """
    request_id = getattr(request.state, "request_id", None)

    # エラー詳細を整形
    errors = []
    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
    else:
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

    # ログ出力
    logger.warning(
        "validation_error",
        error_code=ErrorCode.VALIDATION_ERROR.value,
        errors=errors,
    )

    error_detail = ErrorDetail(
        code=ErrorCode.VALIDATION_ERROR,
        message="入力値の検証に失敗しました",
        details={"errors": errors},
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(error=error_detail).model_dump(),
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    その他の例外のハンドラー

    Args:
        request: リクエストオブジェクト
        exc: 例外

    Returns:
        統一されたエラーレスポンス
    """
    request_id = getattr(request.state, "request_id", None)

    # ログ出力（スタックトレース付き）
    logger.error(
        "unhandled_error",
        error_code=ErrorCode.INTERNAL_ERROR.value,
        error_type=type(exc).__name__,
        message=str(exc),
        exc_info=True,
    )

    error_detail = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR,
        message="予期しないエラーが発生しました",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error=error_detail).model_dump(),
    )
