"""
FastAPIアプリケーションのエントリーポイント
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.infrastructure.config import settings
from app.infrastructure.database import init_db
from app.infrastructure.langchain_logging import configure_langchain_logging
from app.infrastructure.logging import configure_logging, get_logger
from app.presentation.middleware.error_handler import (
    AppError,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.presentation.middleware.request_id import RequestIDMiddleware
from app.presentation.routers import chat, health

# ログ設定
configure_logging(log_level=settings.LOG_LEVEL, json_logs=settings.JSON_LOGS)
configure_langchain_logging()  # LangChainのログも統合
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    logger.info("startup", message="AI Chatbot API is starting up")
    try:
        await init_db()
        logger.info(
            "database_initialized", message="Database initialized successfully"
        )
    except Exception as e:
        logger.error(
            "database_initialization_failed",
            message="Database initialization failed",
            error=str(e),
            exc_info=True,
        )
        raise
    yield
    # シャットダウン時の処理
    logger.info("shutdown", message="AI Chatbot API is shutting down")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "AI Chatbot API with WebSocket, PostgreSQL, DynamoDB, and Vector Search"
    ),
    lifespan=lifespan,
)

# ミドルウェアの登録（登録順が重要：最初に登録したものが最初に実行される）
# 1. リクエストIDミドルウェア（ログコンテキストを設定）
app.add_middleware(RequestIDMiddleware)

# 2. CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 例外ハンドラーの登録
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ルーターの登録
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "message": "AI Chatbot API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }
