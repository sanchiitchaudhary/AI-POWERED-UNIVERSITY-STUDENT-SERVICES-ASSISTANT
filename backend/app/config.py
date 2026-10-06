"""Environment based application settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_PATH: str = "university.db"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    MOCK_LLM: bool = True
    CHROMA_PATH: str = "./chroma"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
