"""
News API routes with Celery async task processing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from celery.result import AsyncResult

from src.models.schemas import NewsSearchRequest, NewsSearchResponse, ErrorResponse
from src.workers.tasks.news_tasks import (
    scrape_news_async,
    scrape_multiple_queries,
    export_articles,
    get_task_status
)
from src.common.logger import get_logger
from src.common.router import create_versioned_router
from src.common.config import config

router = create_versioned_router(prefix="/news", tags=["news"])
logger = get_logger(__name__)


@router.post("/search/async")
async def search_news_async(
    request: NewsSearchRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Start async news scraping task
    
    - **query**: Search query (required)
    - **format**: Output format (json or csv, default: json)
    - **max_results**: Maximum number of results (1-100, default: 50)
    - **language**: Language code (default: en)
    - **country**: Country code (default: US)
    - **time_period**: Time period for search (default: 24h)
    
    Returns task ID for tracking progress
    """
    try:
        logger.info(f"Starting async news search for query: {request.query}")
        
        # Start Celery task
        task = scrape_news_async.delay(
            query=request.query,
            max_results=request.max_results,
            format_type=request.format,
            language=request.language,
            country=request.country,
            time_period=request.time_period
        )
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": f"News scraping task started for query: {request.query}",
            "query": request.query,
            "track_url": f"/api/v1/news/tasks/{task.id}/status"
        }
        
    except Exception as e:
        logger.error(f"Failed to start async news search: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get("/search/async")
async def search_news_async_get(
    query: str,
    format: str = None,
    max_results: int = None,
    language: str = None,
    country: str = None,
    time_period: str = None
) -> Dict:
    """
    Start async news scraping task (GET endpoint)
    
    - **query**: Search query (required)
    - **format**: Output format (json or csv, default: json)
    - **max_results**: Maximum number of results (1-100, default: 50)
    - **language**: Language code (default: en)
    - **country**: Country code (default: US)
    - **time_period**: Time period for search (default: 24h)
    
    Returns task ID for tracking progress
    """
    try:
        logger.info(f"Starting async news search (GET) for query: {query}")
        
        # Start Celery task
        task = scrape_news_async.delay(
            query=query,
            max_results=max_results,
            format_type=format,
            language=language,
            country=country,
            time_period=time_period
        )
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": f"News scraping task started for query: {query}",
            "query": query,
            "track_url": f"/api/v1/news/tasks/{task.id}/status"
        }
        
    except Exception as e:
        logger.error(f"Failed to start async news search: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.post("/search/batch")
async def search_news_batch(
    queries: List[str],
    max_results: int = None,
    format_type: str = None,
    language: str = None,
    country: str = None,
    time_period: str = None
) -> Dict:
    """
    Start batch news scraping for multiple queries
    
    - **queries**: List of search queries
    - **max_results**: Maximum number of results per query (1-100, default: 10)
    - **format_type**: Output format (json or csv, default: json)
    - **language**: Language code (default: en)
    - **country**: Country code (default: US)
    - **time_period**: Time period for search (default: 24h)
    
    Returns task ID for tracking progress
    """
    try:
        logger.info(f"Starting batch news search for {len(queries)} queries")
        
        # Start Celery task
        task = scrape_multiple_queries.delay(
            queries=queries,
            max_results=max_results,
            format_type=format_type,
            language=language,
            country=country,
            time_period=time_period
        )
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": f"Batch news scraping started for {len(queries)} queries",
            "queries": queries,
            "track_url": f"/api/v1/news/tasks/{task.id}/status"
        }
        
    except Exception as e:
        logger.error(f"Failed to start batch news search: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch task: {str(e)}")


@router.post("/export")
async def export_articles_task(
    articles: List[Dict],
    query: str,
    format_type: str = None
) -> Dict:
    """
    Start async article export task
    
    - **articles**: List of article dictionaries
    - **query**: Search query for naming
    - **format_type**: Export format (json, csv, excel)
    
    Returns task ID for tracking progress
    """
    try:
        logger.info(f"Starting article export for query: {query}")
        
        # Start Celery task
        task = export_articles.delay(
            articles=articles,
            query=query,
            format_type=format_type
        )
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": f"Article export started for query: {query}",
            "query": query,
            "articles_count": len(articles),
            "track_url": f"/api/v1/news/tasks/{task.id}/status"
        }
        
    except Exception as e:
        logger.error(f"Failed to start export task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start export task: {str(e)}")


@router.get("/tasks/{task_id}/status")
async def get_task_status_endpoint(task_id: str) -> Dict:
    """
    Get the status of a specific task
    
    - **task_id**: Celery task ID
    
    Returns task status and result if completed
    """
    try:
        logger.info(f"Getting status for task: {task_id}")
        
        # Get task status using Celery task
        result = get_task_status.delay(task_id)
        status_info = result.get(timeout=5)  # 5 second timeout
        
        return status_info
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Dict:
    """
    Get the result of a completed task
    
    - **task_id**: Celery task ID
    
    Returns task result if completed, error if not ready
    """
    try:
        logger.info(f"Getting result for task: {task_id}")
        
        # Get task result directly
        result = AsyncResult(task_id)
        
        if not result.ready():
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is still running"
            }
        
        if result.failed():
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(result.result),
                "message": "Task failed"
            }
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result.result,
            "message": "Task completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get task result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task result: {str(e)}")


# Legacy synchronous endpoints (commented out - use async versions instead)
"""
@router.post("/search", response_model=NewsSearchResponse)
async def search_news_legacy(
    request: NewsSearchRequest,
    news_service: NewsService = Depends(get_news_service)
):
    # Legacy synchronous endpoint - use /search/async instead
    pass

@router.get("/search", response_model=NewsSearchResponse)
async def search_news_get_legacy(
    query: str,
    format: str = "json",
    max_results: int = 50,
    news_service: NewsService = Depends(get_news_service)
):
    # Legacy synchronous endpoint - use /search/async instead
    pass
"""
