"""MCP client wrapper for connecting to MCP server."""

import asyncio
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """MCP 客户端，用于连接和调用 MCP server 的工具."""

    def __init__(self, server_command: str = "python", server_args: Optional[list[str]] = None):
        """初始化 MCP 客户端.

        Args:
            server_command: 启动 MCP server 的命令
            server_args: MCP server 的命令参数
        """
        if server_args is None:
            server_args = ["-m", "agent.mcp.server"]

        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
        )
        self._session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._client_context = None

    async def __aenter__(self):
        """异步上下文管理器入口."""
        self._client_context = stdio_client(self.server_params)
        self._read, self._write = await self._client_context.__aenter__()
        self._session = ClientSession(self._read, self._write)
        await self._session.__aenter__()
        await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出."""
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client_context:
            await self._client_context.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self):
        """列出所有可用的工具."""
        if not self._session:
            raise RuntimeError("MCP client not initialized. Use async context manager.")
        return await self._session.list_tools()

    async def call_tool(self, name: str, arguments: dict[str, Any]):
        """调用指定的工具.

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具调用的结果
        """
        if not self._session:
            raise RuntimeError("MCP client not initialized. Use async context manager.")
        result = await self._session.call_tool(name, arguments)
        # 提取文本内容
        if result.content and len(result.content) > 0:
            return result.content[0].text
        return ""


# 全局 MCP 客户端实例（用于同步调用）
_mcp_client: Optional[MCPClient] = None
_mcp_client_lock = asyncio.Lock()


async def get_mcp_client() -> MCPClient:
    """获取全局 MCP 客户端实例."""
    global _mcp_client
    async with _mcp_client_lock:
        if _mcp_client is None:
            _mcp_client = MCPClient()
        return _mcp_client


def call_mcp_tool_sync(name: str, arguments: dict[str, Any]) -> str:
    """同步调用 MCP 工具（用于 LangChain 工具包装）.

    Args:
        name: 工具名称
        arguments: 工具参数

    Returns:
        工具调用的结果文本
    """
    async def _call():
        async with MCPClient() as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(_call())
