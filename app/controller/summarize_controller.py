from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

from app.models import SessionLocal
from app.repositories.model_repository import ModelRepository
from app.service.summarize_service import SummarizeService

# Request/Response models
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    title: str
    summary: str

class SummarizeController:
    def __init__(self, summarize_service: SummarizeService):
        self.summarize_service = summarize_service

    def summarize_text(self, text: str) -> Dict[str, str]:
        result = self.summarize_service.summarize(text)
        return {
            "title": result["title"],
            "summary": result["summary"],
            "model_version": result["model_version"]
        }

summarize_controller = SummarizeController(SummarizeService(ModelRepository(SessionLocal())))
