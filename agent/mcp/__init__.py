"""MCP server module."""

__all__ = ["main", "server"]


def _lazy_import():
    """延迟导入以避免循环依赖."""
    from agent.mcp.server import main, server
    return main, server


def __getattr__(name: str):
    """延迟加载模块属性."""
    if name in ("main", "server"):
        main, server = _lazy_import()
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
