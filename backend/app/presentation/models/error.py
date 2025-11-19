"""
エラーレスポンスモデル

統一されたエラーレスポンス形式を提供
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """エラーコードの定義"""

    # バリデーションエラー
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # リソースが見つからない
    NOT_FOUND = "NOT_FOUND"

    # セッション関連エラー
    INVALID_SESSION = "INVALID_SESSION"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # AI サービスのエラー
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    AI_RESPONSE_TIMEOUT = "AI_RESPONSE_TIMEOUT"

    # データベースエラー
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"

    # Redis エラー
    CACHE_ERROR = "CACHE_ERROR"

    # 認証・認可エラー
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # その他の内部エラー
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """エラー詳細"""

    code: ErrorCode = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    details: dict[str, Any] | None = Field(
        None, description="エラーの詳細情報（任意）"
    )
    request_id: str | None = Field(None, description="リクエストID")


class ErrorResponse(BaseModel):
    """統一されたエラーレスポンス"""

    error: ErrorDetail = Field(..., description="エラー情報")


# エラーコードとHTTPステータスコードのマッピング
ERROR_CODE_TO_HTTP_STATUS = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INVALID_SESSION: 400,
    ErrorCode.SESSION_EXPIRED: 401,
    ErrorCode.AI_SERVICE_ERROR: 500,
    ErrorCode.AI_RESPONSE_TIMEOUT: 504,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.DATABASE_CONNECTION_ERROR: 503,
    ErrorCode.CACHE_ERROR: 500,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.INTERNAL_ERROR: 500,
}
