"""LangGraph agent graph definition."""

from agent.mcp.tools import get_mcp_tools_sync
from agent.config import (
    get_deepseek_api_key,
    get_deepseek_base_url,
    get_deepseek_model,
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
        # 调用 LLM，传入所有消息历史
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
