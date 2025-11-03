from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.service.crawler_service import vnexpress_service
from ..controller.auth_controllers import get_current_user as get_current_admin
from ..models.database import Admin

router = APIRouter()

class CrawlRequest(BaseModel):
    url: str

@router.post("/api/crawler/vnexpress", summary="Crawl VnExpres")
def crawl_vnexpress_article(
    request: CrawlRequest,
    admin: Admin = Depends(get_current_admin)
):
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if "vnexpress.net" not in request.url:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ vnexpress")

    try:
        crawled_data = vnexpress_service.scrape(request.url)
        return crawled_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
