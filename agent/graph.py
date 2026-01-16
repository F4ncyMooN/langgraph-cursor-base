"""LangGraph agent graph definition."""

from agent.mcp.tools import get_mcp_tools_sync
from agent.config import (
    get_deepseek_api_key,
    get_deepseek_base_url,
    get_deepseek_model,
    get_langfuse_public_key,
    get_langfuse_secret_key,
    get_langfuse_host,
)
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import logging
import sys
from pathlib import Path
from langgraph.graph.message import add_messages

# Langfuse 集成
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None

# 配置 logger 写入 agent.log 文件
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 如果 logger 还没有 handler，添加 FileHandler（写入文件）
if not logger.handlers:
    # 创建日志文件路径
    log_file = Path("agent.log")

    # 添加 FileHandler（写入文件）
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 防止日志传播到根 logger（避免重复输出）
    logger.propagate = False


# 初始化 Langfuse 客户端
_langfuse_client: Langfuse | None = None


def get_langfuse_client() -> Langfuse | None:
    """获取 Langfuse 客户端实例."""
    global _langfuse_client
    if _langfuse_client is None:
        public_key = get_langfuse_public_key()
        secret_key = get_langfuse_secret_key()
        if public_key and secret_key:
            _langfuse_client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=get_langfuse_host(),
            )
            logger.info("Langfuse 客户端初始化成功")
        else:
            logger.warning("Langfuse 配置未设置，将不使用 tracing 功能")
    return _langfuse_client


class AgentState(TypedDict):
    """Agent state definition."""
    messages: Annotated[list[BaseMessage], add_messages]


def create_agent_graph():
    """Create and return the agent graph."""
    # 获取配置
    api_key = get_deepseek_api_key()
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY 环境变量未设置。"
            "请在 .env 文件中设置 DEEPSEEK_API_KEY，或通过环境变量设置。"
        )

    # 加载 MCP 工具
    try:
        mcp_tools = get_mcp_tools_sync()
        logger.info(f"加载了 {len(mcp_tools)} 个 MCP 工具")
    except Exception as e:
        logger.warning(f"加载 MCP 工具失败: {e}，将不使用工具调用功能")
        mcp_tools = []

    # 创建 DeepSeek LLM 实例
    # DeepSeek 使用与 OpenAI 兼容的 API
    llm = ChatOpenAI(
        model=get_deepseek_model(),
        base_url=get_deepseek_base_url(),
        api_key=api_key,
        temperature=0.7,
    )

    # 如果有工具，绑定到 LLM
    if mcp_tools:
        llm_with_tools = llm.bind_tools(mcp_tools)
    else:
        llm_with_tools = llm

    def call_model(state: AgentState) -> AgentState:
        """Call DeepSeek LLM with conversation history."""
        langfuse = get_langfuse_client()

        # 使用 Langfuse 包装 LLM 调用
        if langfuse and LANGFUSE_AVAILABLE:
            # 准备输入消息
            input_messages = []
            for msg in state["messages"]:
                if hasattr(msg, "content"):
                    input_messages.append(msg.content)
                else:
                    input_messages.append(str(msg))

            # 使用 context manager 创建 generation span，自动嵌套到当前 trace
            with langfuse.start_as_current_observation(
                as_type="generation",
                name="llm_call",
                model=get_deepseek_model(),
                input={"messages": input_messages},
            ) as generation:
                try:
                    # 调用 LLM
                    response = llm_with_tools.invoke(state["messages"])

                    # 更新 generation 的输出
                    output_content = response.content if hasattr(response, "content") else str(response)
                    generation.update(output={"content": output_content})

                    # 如果有 token 使用信息，可以添加
                    if hasattr(response, "response_metadata"):
                        metadata = response.response_metadata
                        if "token_usage" in metadata:
                            generation.update(usage=metadata["token_usage"])
                except Exception as e:
                    # 记录错误
                    generation.update(
                        output={"error": str(e)},
                        level="ERROR",
                    )
                    raise
        else:
            # 没有 Langfuse 时，直接调用
            response = llm_with_tools.invoke(state["messages"])

        # 返回新消息（LangGraph 会自动追加到现有消息列表）
        return {"messages": [response]}

    # 创建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", call_model)

    # 如果有工具，添加工具调用节点
    if mcp_tools:
        tool_node = ToolNode(mcp_tools)
        workflow.add_node("tools", tool_node)

        # 添加条件边：根据是否有工具调用来决定下一步
        def should_continue(state: AgentState) -> str:
            """决定下一步是调用工具还是结束."""
            messages = state["messages"]
            last_message = messages[-1]
            # 如果最后一条消息包含工具调用，则调用工具
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return "end"

        # 设置入口点
        workflow.set_entry_point("agent")

        # 从 agent 节点添加条件边
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END,
            },
        )

        # 从 tools 节点返回到 agent 节点
        workflow.add_edge("tools", "agent")
    else:
        # 没有工具时，直接连接 agent 到 END
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)

    # 编译图
    app = workflow.compile()

    return app
