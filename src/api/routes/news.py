"""
News API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ...models.schemas import NewsSearchRequest, NewsSearchResponse, ErrorResponse
from ...services.news_service import NewsService
from ...common.exceptions import ScrapingError, ParsingError
from ...common.logger import get_logger

router = APIRouter(prefix="/news", tags=["news"])
logger = get_logger(__name__)


def get_news_service() -> NewsService:
    """Dependency to get news service instance"""
    return NewsService()


@router.post("/search", response_model=NewsSearchResponse)
async def search_news(
    request: NewsSearchRequest,
    news_service: NewsService = Depends(get_news_service)
):
    """
    Search for news articles
    
    - **query**: Search query (required)
    - **format**: Output format (json or csv, default: json)
    - **max_results**: Maximum number of results (1-100, default: 50)
    """
    try:
        logger.info(f"Received news search request: {request.query}")
        result = await news_service.search_news(request)
        return result
    except ScrapingError as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=503, detail=f"Scraping failed: {str(e)}")
    except ParsingError as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=422, detail=f"Parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=NewsSearchResponse)
async def search_news_get(
    query: str,
    format: str = "json",
    max_results: int = 50,
    news_service: NewsService = Depends(get_news_service)
):
    """
    Search for news articles (GET endpoint)
    
    - **query**: Search query (required)
    - **format**: Output format (json or csv, default: json)
    - **max_results**: Maximum number of results (1-100, default: 50)
    """
    request = NewsSearchRequest(
        query=query,
        format=format,
        max_results=max_results
    )
    
    try:
        logger.info(f"Received news search request (GET): {query}")
        result = await news_service.search_news(request)
        return result
    except ScrapingError as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=503, detail=f"Scraping failed: {str(e)}")
    except ParsingError as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=422, detail=f"Parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
