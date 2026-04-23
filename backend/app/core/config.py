from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = "sk-placeholder"
    OPENAI_CHAT_MODEL: str = "gpt-4o"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "saju_db"
    POSTGRES_USER: str = "saju_user"
    POSTGRES_PASSWORD: str = "saju_pass"

    # Embedding
    EMBEDDING_MODEL_NAME: str = "nlpai-lab/KURE-v1"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_DIMENSION: int = 1024

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy + asyncpg URL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def PSYCOPG_URL(self) -> str:
        """psycopg3 (LangGraph Checkpoint용) URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
