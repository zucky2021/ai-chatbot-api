"""MCPサーバー定義

FastMCPを使用してAIアシスタント（Claude Desktop、VS Code等）向けの
ツールを提供するサーバーです。

提供する機能:
- 会話履歴の検索・取得
- AIチャット機能の呼び出し
- セッション情報の取得
"""

from datetime import datetime
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from app.infrastructure.logging import get_logger

logger = get_logger(__name__)

# MCPサーバーの初期化
mcp = FastMCP(
    name="AI Chatbot MCP Server",
    instructions="""
    このMCPサーバーはAIチャットボットの機能を提供します。

    利用可能なツール:
    - search_conversations: 会話履歴をキーワードで検索
    - get_session_history: 特定セッションの会話履歴を取得
    - get_session_info: セッション情報を取得
    - chat: AIとチャット（新しいメッセージを送信）
    - list_sessions: ユーザーのセッション一覧を取得
    """,
)


# ============================================================
# レスポンスモデル
# ============================================================


class ConversationResult(BaseModel):
    """会話検索結果"""

    id: int
    session_id: str
    user_id: str
    message: str
    response: str | None
    created_at: str | None


class SessionInfo(BaseModel):
    """セッション情報"""

    session_id: str
    user_id: str
    status: str
    created_at: str | None
    metadata: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    """チャットレスポンス"""

    session_id: str
    message: str
    response: str


# ============================================================
# 会話履歴ツール
# ============================================================


@mcp.tool
async def search_conversations(
    query: str = Field(description="検索キーワード"),
    user_id: str | None = Field(
        default=None, description="ユーザーIDでフィルタ"
    ),
    session_id: str | None = Field(
        default=None, description="セッションIDでフィルタ"
    ),
    limit: int = Field(
        default=10, description="取得する最大件数", ge=1, le=100
    ),
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """
    会話履歴をキーワードで検索します。

    PostgreSQLに保存された会話履歴から、メッセージまたはレスポンスに
    指定したキーワードを含む会話を検索します。
    """
    from sqlalchemy import or_, select

    from app.infrastructure.database import async_session
    from app.models.postgres import Conversation

    if ctx:
        await ctx.info(f"会話履歴を検索中: query='{query}', limit={limit}")

    results: list[dict[str, Any]] = []

    try:
        async with async_session() as session:
            stmt = select(Conversation)

            # キーワード検索
            if query:
                stmt = stmt.where(
                    or_(
                        Conversation.message.ilike(f"%{query}%"),
                        Conversation.response.ilike(f"%{query}%"),
                    )
                )

            # フィルタ
            if user_id:
                stmt = stmt.where(Conversation.user_id == user_id)
            if session_id:
                stmt = stmt.where(Conversation.session_id == session_id)

            # ソートと制限
            stmt = stmt.order_by(Conversation.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            conversations = result.scalars().all()

            for conv in conversations:
                results.append(
                    {
                        "id": conv.id,
                        "session_id": conv.session_id,
                        "user_id": conv.user_id,
                        "message": conv.message,
                        "response": conv.response,
                        "created_at": conv.created_at.isoformat()
                        if conv.created_at
                        else None,
                    }
                )

        if ctx:
            await ctx.info(f"検索完了: {len(results)}件の結果")

        logger.info(
            "mcp_search_conversations",
            query=query,
            results_count=len(results),
        )

    except Exception as e:
        logger.error(
            "mcp_search_conversations_error", error=str(e), exc_info=True
        )
        if ctx:
            await ctx.error(f"検索エラー: {str(e)}")
        raise

    return results


@mcp.tool
async def get_session_history(
    session_id: str = Field(description="セッションID"),
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """
    特定セッションの会話履歴を取得します。

    指定されたセッションIDに紐づくすべての会話を時系列順で取得します。
    """
    from sqlalchemy import select

    from app.infrastructure.database import async_session
    from app.models.postgres import Conversation

    if ctx:
        await ctx.info(f"セッション履歴を取得中: session_id='{session_id}'")

    results: list[dict[str, Any]] = []

    try:
        async with async_session() as session:
            stmt = (
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(Conversation.created_at.asc())
            )

            result = await session.execute(stmt)
            conversations = result.scalars().all()

            for conv in conversations:
                results.append(
                    {
                        "id": conv.id,
                        "message": conv.message,
                        "response": conv.response,
                        "created_at": conv.created_at.isoformat()
                        if conv.created_at
                        else None,
                    }
                )

        if ctx:
            await ctx.info(f"取得完了: {len(results)}件の会話")

        logger.info(
            "mcp_get_session_history",
            session_id=session_id,
            count=len(results),
        )

    except Exception as e:
        logger.error(
            "mcp_get_session_history_error", error=str(e), exc_info=True
        )
        if ctx:
            await ctx.error(f"取得エラー: {str(e)}")
        raise

    return results


# ============================================================
# セッション管理ツール
# ============================================================


@mcp.tool
async def get_session_info(
    session_id: str = Field(description="セッションID"),
    ctx: Context | None = None,
) -> dict[str, Any] | None:
    """
    セッション情報を取得します。

    DynamoDBからセッションの詳細情報（ステータス、作成日時、メタデータ等）を取得します。
    """
    from app.infrastructure.dependencies import get_session_repository

    if ctx:
        await ctx.info(f"セッション情報を取得中: session_id='{session_id}'")

    try:
        repo = get_session_repository()
        session = await repo.get_by_id(session_id)

        if session is None:
            if ctx:
                await ctx.warning(f"セッションが見つかりません: {session_id}")
            return None

        result = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "status": session.status.value,
            "created_at": session.created_at.isoformat()
            if session.created_at
            else None,
            "updated_at": session.updated_at.isoformat()
            if session.updated_at
            else None,
            "metadata": session.metadata,
        }

        if ctx:
            await ctx.info(
                f"セッション情報取得完了: status={session.status.value}"
            )

        logger.info("mcp_get_session_info", session_id=session_id)

        return result

    except Exception as e:
        logger.error("mcp_get_session_info_error", error=str(e), exc_info=True)
        if ctx:
            await ctx.error(f"取得エラー: {str(e)}")
        raise


@mcp.tool
async def list_sessions(
    user_id: str = Field(description="ユーザーID"),
    ctx: Context | None = None,
) -> list[dict[str, Any]]:
    """
    ユーザーのセッション一覧を取得します。

    指定されたユーザーIDに紐づくすべてのセッションを取得します。
    """
    from app.infrastructure.dependencies import get_session_repository

    if ctx:
        await ctx.info(f"セッション一覧を取得中: user_id='{user_id}'")

    try:
        repo = get_session_repository()
        sessions = await repo.get_by_user_id(user_id)

        results = [
            {
                "session_id": s.session_id,
                "user_id": s.user_id,
                "status": s.status.value,
                "created_at": s.created_at.isoformat()
                if s.created_at
                else None,
            }
            for s in sessions
        ]

        if ctx:
            await ctx.info(f"セッション一覧取得完了: {len(results)}件")

        logger.info(
            "mcp_list_sessions",
            user_id=user_id,
            count=len(results),
        )

        return results

    except Exception as e:
        logger.error("mcp_list_sessions_error", error=str(e), exc_info=True)
        if ctx:
            await ctx.error(f"取得エラー: {str(e)}")
        raise


# ============================================================
# AIチャットツール
# ============================================================


@mcp.tool
async def chat(
    message: str = Field(description="送信するメッセージ"),
    session_id: str | None = Field(
        default=None,
        description="セッションID（省略時は新規セッション）",
    ),
    user_id: str = Field(
        default="mcp-user",
        description="ユーザーID",
    ),
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    AIとチャットします。

    メッセージを送信し、AIからのレスポンスを取得します。
    会話履歴はPostgreSQLに保存されます。
    """
    import uuid

    from app.domain.entities.conversation import Conversation
    from app.domain.value_objects.message import Message
    from app.infrastructure.dependencies import (
        get_ai_service,
        get_conversation_repository,
    )

    # セッションIDの生成または使用
    actual_session_id = session_id or f"mcp-{uuid.uuid4().hex[:8]}"

    if ctx:
        await ctx.info(
            f"チャット開始: session_id='{actual_session_id}', message='{message[:50]}...'"
        )

    try:
        # AIサービスでレスポンスを生成
        ai_service = get_ai_service()
        msg = Message(
            content=message,
            sender=user_id,
            timestamp=datetime.now(),
            metadata={"session_id": actual_session_id},
        )

        # コンテキスト取得（既存セッションの場合）
        context = ""
        if session_id:
            repo = await get_conversation_repository()
            conversations = await repo.get_by_session_id(session_id)
            context_parts = []
            for conv in conversations[-5:]:  # 直近5件
                context_parts.append(f"User: {conv.message}")
                if conv.response:
                    context_parts.append(f"AI: {conv.response}")
            context = "\n".join(context_parts)

        # AIレスポンス生成
        response = await ai_service.generate_response(msg, context)

        # 会話履歴を保存
        repo = await get_conversation_repository()
        conversation = Conversation(
            user_id=user_id,
            session_id=actual_session_id,
            message=message,
            response=response,
            metadata={"source": "mcp"},
            created_at=datetime.now(),
        )
        await repo.create(conversation)

        result = {
            "session_id": actual_session_id,
            "message": message,
            "response": response,
        }

        if ctx:
            await ctx.info(f"チャット完了: response_length={len(response)}")

        logger.info(
            "mcp_chat",
            session_id=actual_session_id,
            message_length=len(message),
            response_length=len(response),
        )

        return result

    except Exception as e:
        logger.error("mcp_chat_error", error=str(e), exc_info=True)
        if ctx:
            await ctx.error(f"チャットエラー: {str(e)}")
        raise


# ============================================================
# リソース定義
# ============================================================


@mcp.resource("chatbot://stats")
async def get_stats() -> str:
    """チャットボットの統計情報を取得"""
    from sqlalchemy import func, select

    from app.infrastructure.database import async_session
    from app.models.postgres import Conversation

    try:
        async with async_session() as session:
            # 会話数をカウント
            result = await session.execute(select(func.count(Conversation.id)))
            total_conversations = result.scalar() or 0

            # ユニークセッション数をカウント
            result = await session.execute(
                select(func.count(func.distinct(Conversation.session_id)))
            )
            total_sessions = result.scalar() or 0

            # ユニークユーザー数をカウント
            result = await session.execute(
                select(func.count(func.distinct(Conversation.user_id)))
            )
            total_users = result.scalar() or 0

        return f"""# チャットボット統計情報

- 総会話数: {total_conversations}
- 総セッション数: {total_sessions}
- 総ユーザー数: {total_users}
- 最終更新: {datetime.now().isoformat()}
"""

    except Exception as e:
        logger.error("mcp_get_stats_error", error=str(e), exc_info=True)
        return f"統計情報の取得に失敗しました: {str(e)}"


# ============================================================
# プロンプトテンプレート
# ============================================================


@mcp.prompt
def analyze_conversation_prompt(session_id: str) -> str:
    """会話履歴を分析するためのプロンプトテンプレート"""
    return f"""
以下のセッションID: {session_id} の会話履歴を分析してください。

分析のポイント:
1. ユーザーの主な質問や関心事
2. 会話の流れとトピックの変遷
3. AIの回答の質と適切さ
4. 改善が必要な点

まず `get_session_history` ツールを使用して会話履歴を取得し、
上記の観点から分析結果をまとめてください。
"""


@mcp.prompt
def search_and_summarize_prompt(query: str) -> str:
    """会話履歴を検索して要約するためのプロンプトテンプレート"""
    return f"""
キーワード「{query}」に関連する会話を検索し、要約してください。

手順:
1. `search_conversations` ツールを使用して関連する会話を検索
2. 検索結果から主要なトピックと内容を抽出
3. 見つかった情報を要約して報告

検索結果が多い場合は、最も関連性の高いものに焦点を当ててください。
"""
