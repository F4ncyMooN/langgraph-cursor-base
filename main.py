"""Main entry point for the LangGraph agent application."""

from agent import create_agent_graph
from agent.console import ConsoleInterface


def main():
    """Main function to start the agent console interface."""
    # 创建 agent graph
    agent_app = create_agent_graph()

    # 创建并启动 console 接口
    console = ConsoleInterface(agent_app)
    console.start()


if __name__ == "__main__":
    main()
