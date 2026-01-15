"""Configuration management for the agent."""

import os
from typing import Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_deepseek_api_key() -> Optional[str]:
    """Get DeepSeek API key from environment variable."""
    return os.getenv("DEEPSEEK_API_KEY", "sk-a4b393a1759b4a318bc56c65a87aea4c")


def get_deepseek_base_url() -> str:
    """Get DeepSeek API base URL."""
    return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def get_deepseek_model() -> str:
    """Get DeepSeek model name."""
    return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
