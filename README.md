# langgraph-cursor-base

基于 LangGraph 的 Agent 基础项目，提供控制台交互界面。

## 核心技术栈

- **uv** - 进行依赖版本管理
- **Python 3.13** - 作为默认语言
- **LangGraph** - 作为默认 agent 框架
- **LangChain** - LLM 应用开发框架
- **DeepSeek API** - 默认使用的 LLM 服务（兼容 OpenAI SDK）
- **MCP (Model Context Protocol)** - 模型上下文协议，提供工具扩展能力
- **Console** - 默认使用控制台作为用户交互窗口

## 项目结构

```
langgraph-cursor-base/
├── agent/              # Agent 核心模块
│   ├── __init__.py    # 模块导出
│   ├── config.py      # 配置管理（API Key 等）
│   ├── graph.py       # LangGraph 图定义（已集成 MCP 工具）
│   ├── console.py     # 控制台交互接口
│   └── mcp/           # MCP 服务器模块
│       ├── __init__.py
│       ├── server.py  # MCP 服务器（实现 a+b 工具）
│       ├── client.py  # MCP 客户端封装
│       ├── tools.py   # MCP 工具转换（转换为 LangChain 工具）
│       └── test.py    # MCP 服务器测试脚本
├── test_mcp_integration.py  # MCP 与 Graph 集成测试
├── main.py            # 应用入口
├── pyproject.toml     # 项目配置和依赖
├── Makefile          # 常用命令
├── .env              # 环境变量配置（需要创建）
└── README.md         # 项目说明
```

## 快速开始

### 1. 安装依赖

使用 `uv` 创建虚拟环境并安装依赖：

```bash
make setup
```

或者手动执行：

```bash
uv venv --python 3.13
uv pip install -e .
```

### 2. 配置 DeepSeek API

创建 `.env` 文件并配置 DeepSeek API Key：

```bash
# 复制示例文件（如果存在）
# cp .env.example .env

# 编辑 .env 文件，添加以下配置
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

可选配置（使用默认值时可省略）：

```bash
# DeepSeek API 基础 URL（默认: https://api.deepseek.com）
DEEPSEEK_BASE_URL=https://api.deepseek.com

# DeepSeek 模型名称（默认: deepseek-chat）
DEEPSEEK_MODEL=deepseek-chat
```

**获取 API Key：**

1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册账号并获取 API Key
3. 将 API Key 配置到 `.env` 文件中

### 3. 运行 Agent

启动控制台交互界面：

```bash
make run
```

或者：

```bash
uv run python main.py
```

### 4. 使用说明

启动后会进入交互式控制台：

- 直接输入消息与 Agent 对话（支持多轮对话，会保留上下文）
- 输入 `exit` 或 `quit` 退出
- 输入 `clear` 清空对话历史
- 使用 `Ctrl+C` 也可以退出

## 开发

### 代码格式化

```bash
make format
```

### 代码检查

```bash
make lint
```

### 运行测试

```bash
make test
```

### 查看所有可用命令

```bash
make help
```

## MCP Server

项目包含一个 MCP (Model Context Protocol) 服务器，实现了 `a+b` 加法工具。

### 启动 MCP Server

```bash
make mcp-server
```

或者：

```bash
uv run python -m agent.mcp.server
```

### 测试 MCP Server

```bash
make mcp-test
```

或者：

```bash
uv run python -m agent.mcp.test
```

### MCP Server 功能

当前实现的工具：

- **add**: 计算两个数字 a 和 b 的和
  - 参数：
    - `a` (number): 第一个数字
    - `b` (number): 第二个数字
  - 返回：两个数字的和

### 扩展 MCP Server

要添加更多工具，编辑 `agent/mcp/server.py`：

1. 在 `list_tools()` 函数中添加新工具的定义
2. 在 `call_tool()` 函数中添加新工具的处理逻辑

参考 [MCP 文档](https://modelcontextprotocol.io/) 了解更多信息。

### MCP Server 与 Graph 集成

MCP server 已经集成到 LangGraph 中，Agent 可以自动调用 MCP 工具：

1. **自动工具发现**：启动时自动从 MCP server 加载所有可用工具
2. **工具绑定**：工具自动绑定到 LLM，LLM 可以根据需要调用工具
3. **工具执行**：当 LLM 决定调用工具时，会自动执行并返回结果

**工作流程：**

```
用户输入 → Agent (LLM) → 判断是否需要工具 → Tools (MCP) → Agent (LLM) → 返回结果
```

**测试集成：**

```bash
make mcp-integration-test
```

或者：

```bash
uv run python test_mcp_integration.py
```

**使用示例：**
在 console 中，你可以直接要求 Agent 使用工具：

- "请帮我计算 15 加 27 等于多少？使用 add 工具来计算。"
- "用 add 工具计算 100 + 200"

Agent 会自动识别需要使用工具，调用 MCP server 的 add 工具，并返回结果。

## 自定义 Agent

当前已集成 DeepSeek API，可以直接使用。如需自定义：

1. **修改 LLM 配置**：编辑 `agent/config.py` 调整 API 配置
2. **修改模型参数**：在 `agent/graph.py` 中调整 `ChatOpenAI` 的参数（如 `temperature`）
3. **调整图结构**：在 `agent/graph.py` 中添加更多节点和边，实现复杂的 agent 工作流
4. **参考文档**：
   - [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
   - [LangChain 文档](https://python.langchain.com/)
   - [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)

## 许可证

查看 [LICENSE](LICENSE) 文件了解详情。
