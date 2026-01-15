"""MCP Server implementation with addition tool."""

import asyncio
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建 MCP 服务器实例
server = Server("addition-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具."""
    return [
        Tool(
            name="add",
            description="计算两个数字 a 和 b 的和",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字",
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字",
                    },
                },
                "required": ["a", "b"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用."""
    if name == "add":
        a = arguments.get("a")
        b = arguments.get("b")

        if a is None or b is None:
            return [
                TextContent(
                    type="text",
                    text="错误: 参数 'a' 和 'b' 是必需的",
                )
            ]

        try:
            result = float(a) + float(b)
            return [
                TextContent(
                    type="text",
                    text=f"结果: {result}",
                )
            ]
        except (ValueError, TypeError) as e:
            return [
                TextContent(
                    type="text",
                    text=f"错误: 无效的输入 - {str(e)}",
                )
            ]
    else:
        return [
            TextContent(
                type="text",
                text=f"错误: 未知的工具 '{name}'",
            )
        ]


async def main():
    """运行 MCP 服务器."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
