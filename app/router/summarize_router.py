from fastapi import APIRouter

from app.controller.summarize_controller import SummarizeResponse, SummarizeRequest, summarize_controller

router = APIRouter(prefix="/summarize", tags=["summarize"])

@router.post("", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    result = summarize_controller.summarize_text(request.text)
    return SummarizeResponse(**result)
