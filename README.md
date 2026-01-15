# langgraph-cursor-base

基于 LangGraph 的 Agent 基础项目，提供控制台交互界面。

## 核心技术栈

- **uv** - 进行依赖版本管理
- **Python 3.13** - 作为默认语言
- **LangGraph** - 作为默认 agent 框架
- **LangChain** - LLM 应用开发框架
- **DeepSeek API** - 默认使用的 LLM 服务（兼容 OpenAI SDK）
- **Console** - 默认使用控制台作为用户交互窗口

## 项目结构

```
langgraph-cursor-base/
├── agent/              # Agent 核心模块
│   ├── __init__.py    # 模块导出
│   ├── config.py      # 配置管理（API Key 等）
│   ├── graph.py       # LangGraph 图定义
│   └── console.py     # 控制台交互接口
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
