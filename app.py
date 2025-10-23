"""
HTTM - ViT5 Text Summarization Server
Main application entry point
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.routes import train_router, summarize_router
from app.routes.auth_routes import router as auth_router
from app.routes.sample_routes import router as sample_router
from app.config.settings import settings
import uvicorn
import os

app = FastAPI(
    title="HTTM - ViT5 Text Summarization API & Sample Management",
    description="API for training ViT5 model, text summarization and sample management",
    version="1.0.0"
)


app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "a-very-secret-key"))

app.include_router(train_router)
app.include_router(summarize_router)
app.include_router(auth_router)
app.include_router(sample_router)

app.mount("/manage", StaticFiles(directory="app/views", html=True), name="webapp")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "HTTM - ViT5 Text Summarization API",
        "version": "1.0.0",
        "docs": "/docs",
        "webapp": "/manage"
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
