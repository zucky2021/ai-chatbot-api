"""LangGraph AIサービス実装"""

from collections.abc import AsyncGenerator
from typing import Annotated, Any, Literal, TypedDict, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings
from app.infrastructure.langfuse_handler import create_langfuse_handler
from app.infrastructure.logging import get_logger
from app.infrastructure.services.chunk_utils import normalize_chunk_content

logger = get_logger(__name__)


class GraphState(TypedDict):
    """グラフのステート定義"""

    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    context: str
    metadata: dict
    next_action: Literal["normal", "rag", "tool", "end"] | None


class LangGraphAIService(IAIService):
    """LangGraphを使用したAIサービス実装"""

    def __init__(self) -> None:
        """LangGraph AIサービスを初期化"""
        model_name = settings.GOOGLE_AI_MODEL
        logger.info("langgraph_ai_model_initializing", model_name=model_name)

        # ChatGoogleGenerativeAIを初期化
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_AI_API_KEY,
            temperature=settings.LANGCHAIN_TEMPERATURE,
            convert_system_message_to_human=True,
        )

        # プロンプトテンプレートを作成
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", settings.LANGCHAIN_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # グラフを構築
        self._graph = self._build_graph()

        # LangFuseコールバックハンドラーを初期化
        self._langfuse_handler = create_langfuse_handler()

        logger.info(
            "langgraph_ai_service_initialized",
            model_name=model_name,
            langfuse_enabled=settings.LANGFUSE_ENABLED,
        )

    def _build_graph(self) -> CompiledStateGraph:  # noqa
        """グラフを構築"""
        graph = StateGraph(GraphState)

        # ノードを追加
        graph.add_node("input_node", self._input_node)
        graph.add_node("intent_classifier", self._intent_classifier)
        graph.add_node("normal_chat", self._normal_chat)
        graph.add_node("rag_chat", self._rag_chat)  # 将来の実装用
        graph.add_node("tool_execution", self._tool_execution)  # 将来の実装用
        graph.add_node("output_node", self._output_node)

        # エッジを追加
        graph.set_entry_point("input_node")
        graph.add_edge("input_node", "intent_classifier")
        graph.add_conditional_edges(
            "intent_classifier",
            self._route_after_intent,
            {
                "normal": "normal_chat",
                "rag": "rag_chat",
                "tool": "tool_execution",
            },
        )
        graph.add_edge("normal_chat", "output_node")
        graph.add_edge("rag_chat", "output_node")
        graph.add_edge("tool_execution", "output_node")
        graph.add_edge("output_node", END)

        return graph.compile()

    async def _input_node(self, state: GraphState) -> GraphState:
        """入力ノード: ユーザーメッセージの受信と前処理"""
        logger.debug("input_node", session_id=state["session_id"])
        return state

    async def _intent_classifier(self, state: GraphState) -> GraphState:
        """意図判定ノード: ユーザーの意図を判定"""
        messages = state["messages"]
        if not messages:
            state["next_action"] = "normal"
            return state

        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            raw_content = last_message.content
            content = str(raw_content).lower() if not isinstance(raw_content, str) else raw_content.lower()

            # 簡単な意図判定（将来はより高度な判定を実装）
            # TODO: nodeを分ける,システムプロンプトで分岐する
            if any(
                keyword in content
                for keyword in ["検索", "調べて", "情報", "データ"]
            ):
                state["next_action"] = "rag"
            elif any(
                keyword in content for keyword in ["計算", "実行", "ツール"]
            ):
                state["next_action"] = "tool"
            else:
                state["next_action"] = "normal"
        else:
            state["next_action"] = "normal"

        logger.debug("intent_classification", next_action=state["next_action"])
        return state

    def _route_after_intent(self, state: GraphState) -> str:
        """意図判定後のルーティング"""
        next_action = state.get("next_action")
        return next_action if next_action is not None else "normal"

    async def _normal_chat(self, state: GraphState) -> GraphState:
        """通常会話ノード: 標準的な会話処理"""
        try:
            # プロンプトテンプレートを使用してチェーンを作成
            chain = self._prompt | self._llm

            # チェーンを実行
            response = await chain.ainvoke({"messages": state["messages"]})

            # レスポンスをメッセージに追加
            if hasattr(response, "content"):
                state["messages"].append(AIMessage(content=response.content))
            else:
                state["messages"].append(AIMessage(content=str(response)))

            logger.debug("通常会話ノード: レスポンス生成完了")
        except Exception as e:
            logger.error("normal_chat_node_error", error=str(e), exc_info=True)
            state["messages"].append(
                AIMessage(content=f"エラーが発生しました: {str(e)}")
            )

        return state

    async def _rag_chat(self, state: GraphState) -> GraphState:
        """RAGノード: ベクトル検索を使用した情報検索（将来の実装）"""
        # 現在は通常会話と同じ処理
        logger.info("rag_node_placeholder", message="将来の実装予定")
        return await self._normal_chat(state)

    async def _tool_execution(self, state: GraphState) -> GraphState:
        """ツール実行ノード: 外部ツールの実行（将来の実装）"""
        # 現在は通常会話と同じ処理
        logger.info("tool_node_placeholder", message="将来の実装予定")
        return await self._normal_chat(state)

    async def _output_node(self, state: GraphState) -> GraphState:
        """出力ノード: レスポンスの最終処理"""
        logger.debug("output_node_completed")
        return state

    async def _stream_with_formatted_messages(
        self, formatted_messages: Any, config: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        共通のストリーミング処理

        Args:
            formatted_messages: フォーマット済みメッセージ（ChatPromptValueまたはlist[BaseMessage]）
            config: LangChain設定（コールバック等を含む）

        Yields:
            str: ストリーミングチャンクのコンテンツ
        """
        chunk_count = 0
        runnable_config: RunnableConfig = cast(RunnableConfig, config)
        async for chunk in self._llm.astream(
            formatted_messages, config=runnable_config
        ):
            if hasattr(chunk, "content") and chunk.content:
                chunk_count += 1
                content = normalize_chunk_content(chunk.content)

                # 空のコンテンツはスキップ
                if not content:
                    continue

                logger.debug(
                    "langgraph_chunk_yielding",
                    chunk_length=len(content),
                )
                yield content

        logger.info("langgraph_streaming_completed", chunk_count=chunk_count)

    async def generate_response(
        self, message: Message, context: str = ""
    ) -> str:
        """AIレスポンスを生成"""
        try:
            # ステートを初期化
            state: GraphState = {
                "messages": [],
                "session_id": message.metadata.get("session_id", "")
                if message.metadata
                else "",
                "user_id": message.sender,
                "context": context,
                "metadata": message.metadata or {},
                "next_action": None,
            }

            # コンテキストから会話履歴を構築
            if context:
                self._build_messages_from_context(state, context)

            # ユーザーメッセージを追加
            state["messages"].append(HumanMessage(content=message.content))

            # LangFuseコールバックを設定
            config: dict[str, Any] = {}
            if self._langfuse_handler:
                config["callbacks"] = [self._langfuse_handler]

            # グラフを実行
            runnable_config: RunnableConfig = cast(RunnableConfig, config)
            result = await self._graph.ainvoke(state, config=runnable_config)

            # 最後のAIメッセージを取得
            ai_messages = [
                msg for msg in result["messages"] if isinstance(msg, AIMessage)
            ]
            if ai_messages:
                content = ai_messages[-1].content
                if isinstance(content, str):
                    return content
                return str(content)

            return "レスポンスを生成できませんでした。"
        except Exception as e:
            logger.error(
                "langgraph_ai_response_generation_error",
                error=str(e),
                exc_info=True,
            )
            raise RuntimeError(f"AIレスポンス生成エラー: {str(e)}")

    async def generate_stream(
        self, message: Message, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """AIレスポンスをストリームで生成"""
        try:
            # ステートを初期化
            state: GraphState = {
                "messages": [],
                "session_id": message.metadata.get("session_id", "")
                if message.metadata
                else "",
                "user_id": message.sender,
                "context": context,
                "metadata": message.metadata or {},
                "next_action": None,
            }

            # コンテキストから会話履歴を構築
            if context:
                self._build_messages_from_context(state, context)

            # ユーザーメッセージを追加
            state["messages"].append(HumanMessage(content=message.content))

            # LangFuseコールバックを設定
            config = {}
            if self._langfuse_handler:
                config["callbacks"] = [self._langfuse_handler]

            # 意図を判定（通常の会話フローを決定）
            await self._intent_classifier(state)
            next_action = state.get("next_action", "normal")

            logger.debug(
                "langgraph_streaming_started",
                next_action=next_action,
                message_length=len(message.content),
                messages_count=len(state["messages"]),
            )

            # プロンプトテンプレートを使用してメッセージを構築
            formatted_messages = await self._prompt.ainvoke(
                {"messages": state["messages"]}
            )

            # 通常の会話の場合は、直接LLMをストリーミング実行
            if next_action == "normal":
                # 共通のストリーミング処理を使用
                async for content in self._stream_with_formatted_messages(
                    formatted_messages, config
                ):
                    yield content
            else:
                # RAGやツール実行の場合は、グラフをストリーミング実行
                # ただし、現在は実装されていないため、通常の会話と同じ処理
                # 将来的にRAG/ツール実装時は、ここで専用のストリーミング処理を実装
                logger.debug(
                    "langgraph_streaming_using_fallback",
                    action=next_action,
                )
                async for content in self._stream_with_formatted_messages(
                    formatted_messages, config
                ):
                    yield content
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "langgraph_ai_stream_generation_error",
                error=error_msg,
                exc_info=True,
            )
            raise RuntimeError(f"AIストリーム生成エラー: {error_msg}")

    def _build_messages_from_context(
        self, state: GraphState, context: str
    ) -> None:
        """
        コンテキスト文字列から会話履歴を構築してメッセージに追加

        Args:
            state: グラフのステート
            context: 会話履歴を含むコンテキスト文字列
        """
        if not context:
            return

        # コンテキストを解析して会話履歴を構築
        # 形式: "User: ...\nAI: ...\nUser: ...\nAI: ..."
        lines = context.strip().split("\n")
        current_user_message = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("User:"):
                # 前のユーザーメッセージがあれば保存
                if current_user_message:
                    state["messages"].append(
                        HumanMessage(content=current_user_message)
                    )
                current_user_message = line.replace("User:", "").strip()
            elif line.startswith("AI:"):
                ai_message = line.replace("AI:", "").strip()
                if current_user_message:
                    state["messages"].append(
                        HumanMessage(content=current_user_message)
                    )
                    state["messages"].append(AIMessage(content=ai_message))
                    current_user_message = None
                else:
                    # ユーザーメッセージがない場合はAIメッセージのみ追加
                    state["messages"].append(AIMessage(content=ai_message))

        # 最後のユーザーメッセージがあれば保存
        if current_user_message:
            state["messages"].append(
                HumanMessage(content=current_user_message)
            )
