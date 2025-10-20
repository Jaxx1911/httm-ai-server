"""Summarize routes - API endpoints for summarization"""

from fastapi import APIRouter
from pydantic import BaseModel
from ..controllers.summarize_controller import SummarizeController

router = APIRouter(prefix="/summarize", tags=["summarize"])

# Request/Response models
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    title: str
    summary: str

@router.post("", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    """
    Endpoint để tóm tắt văn bản
    Nhận văn bản đầu vào, trả về title và summary
    Không lưu vào database
    """
    result = SummarizeController.summarize_text(request.text)
    return SummarizeResponse(**result)
