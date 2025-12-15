"""
リクエストIDミドルウェア

各リクエストに一意のIDを付与し、ログとレスポンスヘッダーに含める
"""

from collections.abc import Awaitable, Callable
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog


class RequestIDMiddleware(BaseHTTPMiddleware):
    """リクエストIDを付与するミドルウェア"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        リクエストにIDを付与し、レスポンスヘッダーとログコンテキストに追加

        Args:
            request: リクエストオブジェクト
            call_next: 次のミドルウェアまたはエンドポイント

        Returns:
            レスポンスオブジェクト
        """
        # リクエストIDを生成（クライアントから送信された場合はそれを使用）
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # structlogのコンテキストにリクエストIDを追加
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # リクエストの状態にリクエストIDを保存（エンドポイントから参照可能）
        request.state.request_id = request_id

        # 次の処理を実行
        response = await call_next(request)

        # レスポンスヘッダーにリクエストIDを追加
        response.headers["X-Request-ID"] = request_id

        return response
