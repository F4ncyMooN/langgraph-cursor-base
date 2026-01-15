"""LangGraph agent graph definition."""

from agent.config import (
    get_deepseek_api_key,
    get_deepseek_base_url,
    get_deepseek_model,
)
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import logging
from langgraph.graph.message import add_messages
logger = logging.getLogger(__name__)


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

    # 创建 DeepSeek LLM 实例
    # DeepSeek 使用与 OpenAI 兼容的 API
    llm = ChatOpenAI(
        model=get_deepseek_model(),
        base_url=get_deepseek_base_url(),
        api_key=api_key,
        temperature=0.7,
    )

    def call_model(state: AgentState) -> AgentState:
        """Call DeepSeek LLM with conversation history."""
        # 调用 LLM，传入所有消息历史
        response = llm.invoke(state["messages"])
        # logger.info(f"Response: {response}")
        # print(f"Response: {response}")
        # print(f"State: {state}")
        # 返回新消息（LangGraph 会自动追加到现有消息列表）
        return {"messages": [response]}

    # 创建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", call_model)

    # 设置入口点
    workflow.set_entry_point("agent")

    # 添加边
    workflow.add_edge("agent", END)

    # 编译图
    app = workflow.compile()

    return app
