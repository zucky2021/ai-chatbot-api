"""MCP (Model Context Protocol) サーバー

FastMCPを使用してAIアシスタント向けのツールを提供します。
- 会話履歴の検索・取得
- AIチャット機能の呼び出し
- セッション管理
"""

from app.mcp.server import mcp

__all__ = ["mcp"]
