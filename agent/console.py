"""Console interaction module for the agent."""

from typing import Any

from langchain_core.messages import HumanMessage


class ConsoleInterface:
    """Console interface for agent interaction."""

    def __init__(self, agent_app: Any):
        """Initialize console interface with agent app."""
        self.agent_app = agent_app
        self.running = False

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

                # 调用 agent
                result = self.agent_app.invoke(state, config)

                # 更新消息历史（包含新的响应）
                if result.get("messages"):
                    # 获取新添加的消息（通常是最后一条）
                    new_messages = result["messages"][len(messages):]
                    messages.extend(new_messages)

                    # 显示 agent 响应
                    if new_messages:
                        last_message = new_messages[-1]
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
