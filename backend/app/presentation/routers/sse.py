"""
SSE（Server-Sent Events）エンドポイント
Apidogでのテスト用シンプル実装
"""

import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()


async def event_generator() -> AsyncGenerator[str, None]:
    """
    SSEイベントを生成するジェネレーター
    5回のイベントを1秒間隔で送信
    """
    for i in range(1, 6):
        # SSEフォーマット: "data: メッセージ\n\n"
        yield f"data: Message {i}: Hello from SSE!\n\n"
        await asyncio.sleep(1)

    # 完了イベント
    yield "data: [DONE]\n\n"


@router.get("/stream")
async def sse_stream() -> StreamingResponse:
    """
    シンプルなSSEストリーミングエンドポイント
    1秒間隔で5つのメッセージを送信し、最後に[DONE]を送信
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginxのバッファリング無効化
        },
    )


async def countdown_generator(count: int) -> AsyncGenerator[str, None]:
    """
    カウントダウンイベントを生成するジェネレーター
    """
    for i in range(count, 0, -1):
        yield f"event: countdown\ndata: {i}\n\n"
        await asyncio.sleep(1)

    yield "event: complete\ndata: Countdown finished!\n\n"


@router.get("/countdown/{count}")
async def sse_countdown(count: int = 10) -> StreamingResponse:
    """
    カウントダウンSSEエンドポイント
    指定した数からカウントダウン（デフォルト: 10）
    """
    # 最大60秒に制限
    count = min(count, 60)

    return StreamingResponse(
        countdown_generator(count),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
