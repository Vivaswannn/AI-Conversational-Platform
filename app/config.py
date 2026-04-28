from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    SECRET_KEY: str  # Required — set via SECRET_KEY env var
    APP_NAME: str = "AI Conversational Support Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_support"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI
    OPENAI_API_KEY: str = "sk-placeholder"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # RAG
    VECTOR_STORE_PATH: str = "./vector_store"
    KNOWLEDGE_BASE_PATH: str = "./knowledge_base/documents"

    # Crisis
    CRISIS_SIMILARITY_THRESHOLD: float = 0.85

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
