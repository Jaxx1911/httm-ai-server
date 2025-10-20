"""Routes package - API endpoints"""

from .train_routes import router as train_router
from .summarize_routes import router as summarize_router

__all__ = ['train_router', 'summarize_router']
