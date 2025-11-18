"""LangGraph AIサービス実装"""

from collections.abc import AsyncGenerator
import logging
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from app.domain.services import IAIService
from app.domain.value_objects.message import Message
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)


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

    def __init__(self):
        """LangGraph AIサービスを初期化"""
        model_name = settings.GOOGLE_AI_MODEL
        logger.info(f"LangGraph AIモデルを初期化: {model_name}")

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

        logger.info("LangGraph AIサービスが初期化されました")

    def _build_graph(self) -> StateGraph:
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
        logger.debug(f"入力ノード: session_id={state['session_id']}")
        return state

    async def _intent_classifier(self, state: GraphState) -> GraphState:
        """意図判定ノード: ユーザーの意図を判定"""
        messages = state["messages"]
        if not messages:
            state["next_action"] = "normal"
            return state

        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            content = last_message.content.lower()

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

        logger.debug(f"意図判定: {state['next_action']}")
        return state

    def _route_after_intent(self, state: GraphState) -> str:
        """意図判定後のルーティング"""
        return state.get("next_action", "normal")

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
            logger.error(f"通常会話ノードエラー: {str(e)}")
            state["messages"].append(
                AIMessage(content=f"エラーが発生しました: {str(e)}")
            )

        return state

    async def _rag_chat(self, state: GraphState) -> GraphState:
        """RAGノード: ベクトル検索を使用した情報検索（将来の実装）"""
        # 現在は通常会話と同じ処理
        logger.info("RAGノード: 将来の実装予定")
        return await self._normal_chat(state)

    async def _tool_execution(self, state: GraphState) -> GraphState:
        """ツール実行ノード: 外部ツールの実行（将来の実装）"""
        # 現在は通常会話と同じ処理
        logger.info("ツール実行ノード: 将来の実装予定")
        return await self._normal_chat(state)

    async def _output_node(self, state: GraphState) -> GraphState:
        """出力ノード: レスポンスの最終処理"""
        logger.debug("出力ノード: 処理完了")
        return state

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

            # グラフを実行
            result = await self._graph.ainvoke(state)

            # 最後のAIメッセージを取得
            ai_messages = [
                msg for msg in result["messages"] if isinstance(msg, AIMessage)
            ]
            if ai_messages:
                return ai_messages[-1].content

            return "レスポンスを生成できませんでした。"
        except Exception as e:
            logger.error(f"LangGraph AIレスポンス生成エラー: {str(e)}")
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

            # グラフをストリーミング実行
            full_response = ""
            async for chunk in self._graph.astream(state):
                # 各ノードの出力を処理
                for node_name, node_output in chunk.items():
                    if node_name == "normal_chat" or node_name == "rag_chat":
                        messages = node_output.get("messages", [])
                        for msg in messages:
                            if isinstance(msg, AIMessage) and msg.content:
                                # 新しい部分のみを取得
                                new_content = msg.content[len(full_response) :]
                                if new_content:
                                    full_response = msg.content
                                    yield new_content

            # 最終的なレスポンスを確認
            if not full_response:
                # ストリーミングで取得できなかった場合は通常実行
                result = await self._graph.ainvoke(state)
                ai_messages = [
                    msg
                    for msg in result["messages"]
                    if isinstance(msg, AIMessage)
                ]
                if ai_messages:
                    yield ai_messages[-1].content
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LangGraph AIストリーム生成エラー: {error_msg}")
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
