from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # AWS (LocalStack)
    AWS_ENDPOINT_URL: str = "http://localstack:4566"
    AWS_REGION: str = "ap-northeast-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"

    # Google AI
    GOOGLE_AI_API_KEY: str = ""
    GOOGLE_AI_MODEL: str = "gemini-flash-latest"  # デフォルトはgemini-flash-latest（常に最新のFlashモデルを使用）

    # LangChain Settings
    LANGCHAIN_MEMORY_TYPE: str = "buffer"  # buffer, summary, summary_buffer
    LANGCHAIN_MAX_TOKENS: int = 4000
    LANGCHAIN_TEMPERATURE: float = 0.7
    LANGCHAIN_SYSTEM_PROMPT: str = "あなたは親切で丁寧なAIアシスタントです。ユーザーの質問に分かりやすく答えてください。"

    # LangGraph Settings
    LANGGRAPH_ENABLED: bool = False
    LANGGRAPH_DEBUG: bool = False

    # LangFuse Settings
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"
    LANGFUSE_ENABLED: bool = False

    # API Settings
    API_TITLE: str = "AI Chatbot API"
    API_VERSION: str = "1.0.0"

    # Logging Settings
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    JSON_LOGS: bool = True  # 本番環境ではTrue、開発環境ではFalse

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
