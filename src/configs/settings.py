from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Brainy API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # PostgreSQL Database Settings
    POSTGRES_DB: str = "brainy_db"
    POSTGRES_USER: str = "brainy_user"
    POSTGRES_PASSWORD: str = "brainy_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "brainy_neo4j_password"

    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # RabbitMQ Settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    # MinIO Settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_admin"
    MINIO_SECRET_KEY: str = "minio_password"
    MINIO_SECURE: bool = False

    # LLM & AI Settings
    OPENAI_API_KEY: str = "mock-key"
    GEMINI_API_KEY: str = "mock-key"
    OLLAMA_HOST: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
