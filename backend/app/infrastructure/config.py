from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://chatbot:chatbot_password@postgres:5432/chatbot_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # AWS (LocalStack)
    AWS_ENDPOINT_URL: str = "http://localstack:4566"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # Google AI
    GOOGLE_AI_API_KEY: str

    # API Settings
    API_TITLE: str = "AI Chatbot API"
    API_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")


settings = Settings()
