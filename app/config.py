from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "DB Agent - Database Agnostic"
    app_version: str = "1.0.0"
    debug: bool = False
    llm_provider: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    max_retries: int = 3
    query_timeout: int = 30
    max_result_rows: int = 500

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
