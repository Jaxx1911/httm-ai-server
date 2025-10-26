"""Routes package - API endpoints"""

from .model_controller import router as model_router

# Keep backward compatibility
train_router = model_router

__all__ = ['model_router', 'train_router']
