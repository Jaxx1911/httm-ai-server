import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException

class VnExpressCrawler:
    def scrape(self, url: str):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Không thể truy cập URL: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')

        title_element = soup.select_one('h1.title-detail')
        title = title_element.get_text(strip=True) if title_element else ""

        description_element = soup.select_one('p.description')
        target_summary = description_element.get_text(strip=True) if description_element else ""

        content_paragraphs = soup.select('article.fck_detail p.Normal')
        
        if not content_paragraphs:
            content_paragraphs = soup.select('article.fck_detail p')

        input_text = "\n".join([p.get_text(strip=True) for p in content_paragraphs if p.get_text(strip=True)])

        if not input_text:
            raise HTTPException(status_code=404)

        return {
            "title": title,
            "target_summary": target_summary,
            "input_text": input_text,
            "source": "VNExpress",
            "category": "",
            "language": "vi"
        }

vnexpress_service = VnExpressCrawler()
