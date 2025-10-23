from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

from app.service.summarize_service import SummarizeService

router = APIRouter(prefix="/summarize", tags=["summarize"])

# Request/Response models
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    title: str
    summary: str

@router.post("", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    result = summarize_text(request.text)
    return SummarizeResponse(**result)


def summarize_text(text: str) -> Dict[str, str]:
    result = SummarizeService.summarize(text)
    return {
        "title": result["title"],
        "summary": result["summary"],
        "model_version": result["model_version"]
    }
