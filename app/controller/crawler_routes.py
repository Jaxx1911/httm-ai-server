from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services.crawler_service import crawler_service
from ..controller.auth_controllers import get_current_user as get_current_admin
from ..models.database import Admin

router = APIRouter()

class CrawlRequest(BaseModel):
    url: str

@router.post("/api/crawler/vnexpress", summary="Crawl a VnExpress article")
def crawl_vnexpress_article(
    request: CrawlRequest,
    admin: Admin = Depends(get_current_admin)
):
    """
    Takes a VnExpress URL, crawls the article, and returns the extracted
    title, summary, and content.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if "vnexpress.net" not in request.url:
        raise HTTPException(status_code=400, detail="URL không hợp lệ. Chỉ hỗ trợ link từ vnexpress.net")

    try:
        crawled_data = crawler_service.scrape(request.url)
        return crawled_data
    except HTTPException as e:
        # Re-raise HTTPException to let FastAPI handle it
        raise e
    except Exception as e:
        # Catch any other unexpected errors during crawling
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định khi crawl: {str(e)}")
