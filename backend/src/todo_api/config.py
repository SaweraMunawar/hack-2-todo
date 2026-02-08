"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = "*"
    OPENAI_API_KEY: str = ""
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    EVENTS_ENABLED: bool = False


settings = Settings()
