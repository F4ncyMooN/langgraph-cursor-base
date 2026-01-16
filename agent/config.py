"""Configuration management for the agent."""

import os
from typing import Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_deepseek_api_key() -> Optional[str]:
    """Get DeepSeek API key from environment variable."""
    return os.getenv("DEEPSEEK_API_KEY")


def get_deepseek_base_url() -> str:
    """Get DeepSeek API base URL."""
    return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def get_deepseek_model() -> str:
    """Get DeepSeek model name."""
    return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def get_langfuse_public_key() -> Optional[str]:
    """Get Langfuse public key from environment variable."""
    return os.getenv("LANGFUSE_PUBLIC_KEY")


def get_langfuse_secret_key() -> Optional[str]:
    """Get Langfuse secret key from environment variable."""
    return os.getenv("LANGFUSE_SECRET_KEY")


def get_langfuse_host() -> str:
    """Get Langfuse host URL."""
    return os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
