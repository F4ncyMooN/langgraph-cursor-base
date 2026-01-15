"""简单的 MCP server 测试脚本."""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_add_tool():
    """测试 add 工具."""
    print("=" * 60)
    print("MCP Server 简单测试")
    print("=" * 60)

    # 配置服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "agent.mcp.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()

            # 列出工具
            print("\n1. 列出可用工具...")
            tools = await session.list_tools()
            print(f"   工具数量: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # 测试 add 工具
            print("\n2. 测试 add 工具...")
            test_cases = [
                (5, 3, 8),
                (10, 20, 30),
                (-5, 10, 5),
                (3.14, 2.86, 6.0),
            ]

            for a, b, expected in test_cases:
                print(f"\n   测试: {a} + {b} = ?")
                result = await session.call_tool("add", {"a": a, "b": b})
                print(f"   结果: {result.content[0].text}")
                if str(expected) in result.content[0].text:
                    print(f"   ✓ 通过 (期望: {expected})")
                else:
                    print(f"   ✗ 失败 (期望: {expected})")

            # 测试错误情况
            print("\n3. 测试错误情况（缺少参数）...")
            try:
                result = await session.call_tool("add", {"a": 5})
                print(f"   结果: {result.content[0].text}")
            except Exception as e:
                print(f"   错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_add_tool())
