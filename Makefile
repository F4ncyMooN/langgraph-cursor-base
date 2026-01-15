.PHONY: help install dev test lint format clean run setup

help: ## 显示帮助信息
	@echo "LangGraph Agent Base - 可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## 初始设置（创建虚拟环境并安装依赖）
	uv venv
	uv pip install -e .

install: ## 安装依赖
	uv pip install -e .

dev: ## 启动开发模式（运行 agent console）
	uv run python main.py

run: ## 运行 agent console
	uv run python main.py

test: ## 运行测试
	uv run pytest

test-cov: ## 运行测试并显示覆盖率
	uv run pytest --cov=agent --cov-report=html

lint: ## 运行代码检查
	uv run ruff check agent/ main.py
	uv run mypy agent/ main.py

format: ## 格式化代码
	uv run ruff format agent/ main.py

clean: ## 清理缓存文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage 