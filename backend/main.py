"""
MCQ Genie - Main FastAPI Application
A chatbot with MCQ test generation capabilities.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.config.database import Database
from app.views import chat_router, test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    await Database.connect_db()
    print("✅ All systems ready!")
    yield
    # Shutdown
    await Database.close_db()
    print("👋 Shutting down MCQ Genie")


# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered chatbot with MCQ test generation",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "chat": "/api/chat",
            "test": "/api/test"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2026-02-14",
        "database": "connected" if Database.db else "disconnected"
    }


# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(test_router, prefix="/api/test", tags=["Test"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )