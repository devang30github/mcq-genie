"""Views module containing API routes."""
from .chat_routes import router as chat_router
from .test_routes import router as test_router

__all__ = [
    "chat_router",
    "test_router"
]