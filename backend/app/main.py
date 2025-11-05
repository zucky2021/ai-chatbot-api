"""
FastAPIアプリケーションのエントリーポイント
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.presentation.routers import chat, health
from app.infrastructure.config import settings
from app.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    print("🚀 AI Chatbot API is starting up...")
    await init_db()
    yield
    # シャットダウン時の処理
    print("👋 AI Chatbot API is shutting down...")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=(
        "AI Chatbot API with WebSocket, PostgreSQL, DynamoDB, and Vector Search"
    ),
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
