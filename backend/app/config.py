"""Environment based application settings."""
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_PATH: str = "university.db"
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("OLLAMA_URL", "OLLAMA_HOST"),
    )
    OLLAMA_MODEL: str = "llama3"
    MOCK_LLM: bool = True
    CHROMA_PATH: str = "./chroma"
    CLOUD_FALLBACK: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
