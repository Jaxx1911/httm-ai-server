"""
HTTM - ViT5 Text Summarization Server
Main application entry point
"""

from fastapi import FastAPI
from app.routes import train_router, summarize_router
from app.config.settings import settings
import uvicorn

# Khởi tạo FastAPI app
app = FastAPI(
    title="HTTM - ViT5 Text Summarization API",
    description="API for training ViT5 model and text summarization",
    version="1.0.0"
)

# Đăng ký routes
app.include_router(train_router)
app.include_router(summarize_router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "HTTM - ViT5 Text Summarization API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "train": "/train",
            "summarize": "/summarize"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
