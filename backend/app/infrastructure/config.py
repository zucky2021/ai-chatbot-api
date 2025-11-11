from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # AWS (LocalStack)
    AWS_ENDPOINT_URL: str = "http://localstack:4566"
    AWS_REGION: str = "ap-northeast-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # Google AI
    GOOGLE_AI_API_KEY: str
    GOOGLE_AI_MODEL: str = "gemini-flash-latest"  # デフォルトはgemini-flash-latest（常に最新のFlashモデルを使用）

    # API Settings
    API_TITLE: str = "AI Chatbot API"
    API_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ],
        description="CORS origins",
    )


settings = Settings()
