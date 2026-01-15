"""将 MCP 工具转换为 LangChain 工具."""

import asyncio
from typing import Any, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from agent.mcp.client import call_mcp_tool_sync


async def load_mcp_tools():
    """从 MCP server 加载工具并转换为 LangChain 工具."""
    from agent.mcp.client import MCPClient

    tools = []
    async with MCPClient() as client:
        mcp_tools = await client.list_tools()

        for mcp_tool in mcp_tools.tools:
            # 从 inputSchema 提取参数信息
            schema = mcp_tool.inputSchema
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            # 创建 Pydantic 模型用于参数验证
            fields = {}
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "string")
                prop_desc = prop_info.get("description", "")

                # 映射 JSON Schema 类型到 Python 类型
                if prop_type == "number":
                    python_type = float
                elif prop_type == "integer":
                    python_type = int
                elif prop_type == "boolean":
                    python_type = bool
                else:
                    python_type = str

                # 创建字段
                field_kwargs = {"description": prop_desc}
                if prop_name in required:
                    field_kwargs["..."] = ...  # 必需字段
                else:
                    field_kwargs["default"] = None

                fields[prop_name] = (python_type, Field(**field_kwargs))

            # 动态创建 Pydantic 模型
            ToolInput = type(
                f"{mcp_tool.name.capitalize()}Input",
                (BaseModel,),
                {
                    "__annotations__": {k: v[0] for k, v in fields.items()},
                    **{k: v[1] for k, v in fields.items()},
                }
            )

            # 创建工具调用函数
            def make_tool_func(tool_name: str):
                def tool_func(**kwargs: Any) -> str:
                    """调用 MCP 工具."""
                    return call_mcp_tool_sync(tool_name, kwargs)
                return tool_func

            # 创建 LangChain 工具
            langchain_tool = StructuredTool.from_function(
                func=make_tool_func(mcp_tool.name),
                name=mcp_tool.name,
                description=mcp_tool.description,
                args_schema=ToolInput,
            )

            tools.append(langchain_tool)

    return tools


def get_mcp_tools_sync():
    """同步获取 MCP 工具."""
    return asyncio.run(load_mcp_tools())
