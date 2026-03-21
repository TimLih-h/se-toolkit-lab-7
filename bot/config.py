"""Configuration loading from environment variables."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = ""

    # LMS API
    lms_api_base_url: str = "http://backend:8000"
    lms_api_key: str = ""

    # LLM API
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = ""


def load_settings() -> BotSettings:
    """Load bot settings from environment."""
    # In Docker, environment variables take precedence
    settings = BotSettings()
    
    # Override with env vars if set (for Docker)
    if os.getenv("BOT_TOKEN"):
        settings.bot_token = os.getenv("BOT_TOKEN")
    if os.getenv("LMS_API_BASE_URL"):
        settings.lms_api_base_url = os.getenv("LMS_API_BASE_URL")
    if os.getenv("LMS_API_KEY"):
        settings.lms_api_key = os.getenv("LMS_API_KEY")
    if os.getenv("LLM_API_MODEL"):
        settings.llm_api_model = os.getenv("LLM_API_MODEL")
    if os.getenv("LLM_API_KEY"):
        settings.llm_api_key = os.getenv("LLM_API_KEY")
    if os.getenv("LLM_API_BASE_URL"):
        settings.llm_api_base_url = os.getenv("LLM_API_BASE_URL")
    
    return settings
