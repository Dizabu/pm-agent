from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    llm_provider: Literal["anthropic", "ollama", "fake"] = "ollama"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"


settings = Settings()
