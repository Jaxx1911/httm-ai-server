"""Summarize routes - API endpoints for summarization"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from ..models.vit5_model import vit5_model

router = APIRouter(prefix="/summarize", tags=["summarize"])

# Request/Response models
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    title: str
    summary: str

# --- Logic được di chuyển từ summarize_controller ---
def summarize_text(text: str) -> Dict[str, str]:
    """
    Tóm tắt văn bản
    
    Args:
        text: Văn bản cần tóm tắt
        
    Returns:
        Dict chứa title và summary
    """
    result = vit5_model.summarize_text(text)
    return {
        "title": result["title"],
        "summary": result["summary"]
    }
# --- Kết thúc logic từ controller ---

@router.post("", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    """
    Endpoint để tóm tắt văn bản
    Nhận văn bản đầu vào, trả về title và summary
    Không lưu vào database
    """
    result = summarize_text(request.text)
    return SummarizeResponse(**result)
