"""Console interaction module for the agent."""

from typing import Any

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from agent.config import (
    get_langfuse_public_key,
    get_langfuse_secret_key,
    get_langfuse_host,
)

# Langfuse 集成
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None


class ConsoleInterface:
    """Console interface for agent interaction."""

    def __init__(self, agent_app: Any):
        """Initialize console interface with agent app."""
        self.agent_app = agent_app
        self.running = False

        # 初始化 Langfuse 客户端（如果配置了）
        self.langfuse = None
        if LANGFUSE_AVAILABLE:
            public_key = get_langfuse_public_key()
            secret_key = get_langfuse_secret_key()
            if public_key and secret_key:
                self.langfuse = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=get_langfuse_host(),
                )

    def start(self):
        """Start the console interaction loop."""
        self.running = True
        print("=" * 60)
        print("LangGraph Agent Console (DeepSeek)")
        print("=" * 60)
        print("输入 'exit' 或 'quit' 退出")
        print("输入 'clear' 清空对话历史")
        print("-" * 60)

        config = {"configurable": {"thread_id": "1"}}
        # 维护消息历史
        messages = []

        while self.running:
            try:
                # 获取用户输入
                user_input = input("\n你: ").strip()

                if not user_input:
                    continue

                # 处理退出命令
                if user_input.lower() in ["exit", "quit"]:
                    print("\n再见！")
                    break

                # 处理清空命令
                if user_input.lower() == "clear":
                    messages = []
                    print("对话历史已清空")
                    continue

                # 添加用户消息到历史
                user_message = HumanMessage(content=user_input)
                messages.append(user_message)

                # 创建包含完整消息历史的状态
                state = {"messages": messages}

                # 使用 Langfuse 包装整个流程为一个 trace
                if self.langfuse and LANGFUSE_AVAILABLE:
                    # 创建根 span，包装从用户输入到输出的整个过程
                    with self.langfuse.start_as_current_observation(
                        as_type="span",
                        name="user_query_to_response",
                        input={"user_input": user_input},
                    ) as root_span:
                        # 更新 trace 的 user_id 和 session_id
                        root_span.update_trace(
                            user_id="console_user",
                            session_id=config.get("configurable", {}).get("thread_id", "default"),
                        )
                        try:
                            # 调用 agent（LLM 调用会在 graph 中自动记录为 generation）
                            result = self.agent_app.invoke(state, config)

                            # 更新消息历史（包含新的响应）
                            if result.get("messages"):
                                # 获取新添加的消息（通常是最后一条）
                                new_messages = result["messages"][len(messages):]
                                messages.extend(new_messages)

                                # 显示 agent 响应
                                if new_messages:
                                    last_message = new_messages[-1]
                                    last2message = None if len(new_messages) < 2 else new_messages[-2]
                                    if last2message and isinstance(last2message, ToolMessage):
                                        print(f"\nTool call: {last2message.to_json()} {last2message.content}")

                                    output_content = last_message.content if hasattr(
                                        last_message, "content") else str(last_message)
                                    print(f"\nAgent: {output_content}")

                                    # 更新根 span 和 trace 的输出
                                    root_span.update(output={"response": output_content})
                                    root_span.update_trace(
                                        input={"user_input": user_input},
                                        output={"response": output_content},
                                    )
                            else:
                                root_span.update(output={"response": "No response"})
                                root_span.update_trace(
                                    input={"user_input": user_input},
                                    output={"response": "No response"},
                                )
                        except Exception as e:
                            # 记录错误
                            root_span.update(
                                output={"error": str(e)},
                                level="ERROR",
                            )
                            root_span.update_trace(
                                input={"user_input": user_input},
                                output={"error": str(e)},
                            )
                            raise
                else:
                    # 没有 Langfuse 时，直接调用
                    result = self.agent_app.invoke(state, config)

                    # 更新消息历史（包含新的响应）
                    if result.get("messages"):
                        # 获取新添加的消息（通常是最后一条）
                        new_messages = result["messages"][len(messages):]
                        messages.extend(new_messages)

                        # 显示 agent 响应
                        if new_messages:
                            last_message = new_messages[-1]
                            last2message = None if len(new_messages) < 2 else new_messages[-2]
                            if last2message and isinstance(last2message, ToolMessage):
                                print(f"\nTool call: {last2message.to_json()} {last2message.content}")
                            print(f"\nAgent: {last_message.content}")

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except EOFError:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {e}")
                continue
