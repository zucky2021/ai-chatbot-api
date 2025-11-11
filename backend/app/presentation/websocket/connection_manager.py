"""WebSocket接続管理クラス"""

import asyncio
import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket接続管理クラス"""

    def __init__(self):
        # セッションIDごとの接続を管理
        self._active_connections: dict[str, set[WebSocket]] = {}
        # 接続のロック（並行処理対策）
        self._locks: dict[str, asyncio.Lock] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """
        WebSocket接続を確立

        Args:
            websocket: WebSocket接続
            session_id: セッションID
        """
        await websocket.accept()

        # セッションIDごとのロックを取得
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()

        async with self._locks[session_id]:
            if session_id not in self._active_connections:
                self._active_connections[session_id] = set()
            self._active_connections[session_id].add(websocket)

        logger.info(
            f"WebSocket接続確立: session_id={session_id}, "
            f"接続数={len(self._active_connections[session_id])}"
        )

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """
        WebSocket接続を切断

        Args:
            websocket: WebSocket接続
            session_id: セッションID
        """
        if session_id in self._active_connections:
            self._active_connections[session_id].discard(websocket)

            # 接続がなくなったらセッションを削除
            if not self._active_connections[session_id]:
                del self._active_connections[session_id]
                if session_id in self._locks:
                    del self._locks[session_id]

        logger.info(f"WebSocket接続切断: session_id={session_id}")

    async def send_personal_message(
        self, message: dict, websocket: WebSocket
    ) -> None:
        """
        特定のWebSocket接続にメッセージを送信

        Args:
            message: 送信するメッセージ（辞書形式）
            websocket: 送信先のWebSocket接続

        Raises:
            RuntimeError: 送信に失敗した場合
        """
        try:
            # 接続が閉じられているかチェック
            if websocket.client_state.name != "CONNECTED":
                logger.debug("WebSocket接続が既に閉じられています")
                return
            await websocket.send_json(message)
        except WebSocketDisconnect:
            # WebSocket接続が切断された場合は無視
            logger.debug(
                "WebSocket接続が切断されたため、メッセージ送信をスキップ"
            )
            return
        except Exception as e:
            # その他の接続関連エラーも無視
            error_type = type(e).__name__
            if (
                "disconnect" in error_type.lower()
                or "disconnected" in error_type.lower()
                or "close" in str(e).lower()
            ):
                logger.debug(
                    f"WebSocket接続が閉じられているため、メッセージ送信をスキップ: {error_type}"
                )
                return
            logger.error(f"メッセージ送信エラー: {str(e)}")
            raise RuntimeError(f"メッセージ送信に失敗しました: {str(e)}")

    async def send_to_session(self, message: dict, session_id: str) -> None:
        """
        セッション内の全接続にメッセージを送信

        Args:
            message: 送信するメッセージ（辞書形式）
            session_id: セッションID

        Raises:
            RuntimeError: 予期しないエラーが発生した場合（通常は発生しない）
        """
        if session_id not in self._active_connections:
            logger.debug(
                f"セッション {session_id} にアクティブな接続がありません"
            )
            return

        connections = self._active_connections[session_id]
        if not connections:
            return

        # 切断された接続を削除するためのセット
        disconnected = set()

        # 接続のコピーを作成（イテレーション中に変更される可能性があるため）
        for websocket in list(connections):
            try:
                # 接続状態を事前チェック
                if websocket.client_state.name != "CONNECTED":
                    logger.debug(
                        f"WebSocket接続が既に閉じられています: session_id={session_id}"
                    )
                    disconnected.add(websocket)
                    continue

                await websocket.send_json(message)
            except WebSocketDisconnect:
                # WebSocket接続が切断された場合は無視
                logger.debug(
                    f"WebSocket接続が切断されました: session_id={session_id}"
                )
                disconnected.add(websocket)
            except Exception as e:
                # その他の接続関連エラーも無視
                error_type = type(e).__name__
                if (
                    "disconnect" in error_type.lower()
                    or "disconnected" in error_type.lower()
                    or "close" in str(e).lower()
                ):
                    logger.debug(
                        f"WebSocket接続が閉じられています: session_id={session_id}, "
                        f"error_type={error_type}"
                    )
                    disconnected.add(websocket)
                else:
                    # 予期しないエラーは警告として記録
                    logger.warning(
                        f"セッション {session_id} へのメッセージ送信エラー: {str(e)}"
                    )
                    disconnected.add(websocket)

        # 切断された接続を削除（ロックを使用して並行処理を安全に）
        if disconnected:
            if session_id in self._locks:
                async with self._locks[session_id]:
                    for websocket in disconnected:
                        self.disconnect(websocket, session_id)
            else:
                # ロックが存在しない場合（通常は発生しない）
                for websocket in disconnected:
                    self.disconnect(websocket, session_id)

    def get_connection_count(self, session_id: str) -> int:
        """
        セッションの接続数を取得

        Args:
            session_id: セッションID

        Returns:
            接続数
        """
        return len(self._active_connections.get(session_id, set()))

    def get_total_connections(self) -> int:
        """
        全セッションの合計接続数を取得

        Returns:
            合計接続数
        """
        return sum(
            len(connections)
            for connections in self._active_connections.values()
        )


# グローバルな接続マネージャーインスタンス
connection_manager = ConnectionManager()
