"""Настройки приложения через pydantic-settings (v2).

Все секреты и окруж-зависимые значения читаются из переменных окружения
или .env — НЕ хардкодим и НЕ коммитим .env (он в .gitignore).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RAG Chat"

    # LLM
    llm_base_url: str = "http://localhost:8001"  # мок из [L] секции 1
    llm_model: str = "qwen2.5:3b"
    llm_connect_timeout: float = 5.0
    llm_read_timeout: float = 30.0

    # DB — на этапе 3 переедем на реальные значения
    database_url: str = "sqlite+aiosqlite:///./rag_chat.db"


settings = Settings()
