"""
Celery tasks for news scraping operations
"""
import asyncio
from typing import List, Dict, Optional
from celery import Task
from src.workers.celery_app import celery_app
from src.services.news_service import NewsService
from src.common.logger import get_logger
from src.common.exceptions import NewsScraperException

logger = get_logger(__name__)


class CallbackTask(Task):
    """Custom task class with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} succeeded: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {task_id} retrying: {exc}")


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="scrape_news_async",
    queue="news_scraping",
    max_retries=3,
    default_retry_delay=60,
)
def scrape_news_async(
    self,
    query: str,
    max_results: int = None,
    format_type: str = None,
    language: str = None,
    country: str = None,
    time_period: str = None
) -> Dict:
    """
    Asynchronously scrape news articles
    
    Args:
        query: Search query
        max_results: Maximum number of results (uses config default if None)
        format_type: Output format (uses config default if None)
        language: Language code (uses config default if None)
        country: Country code (uses config default if None)
        time_period: Time period for search (uses config default if None)
    
    Returns:
        Dict with task result and file paths
    """
    try:
        logger.info(f"Starting news scraping task for query: {query}")
        
        # Create news service instance
        news_service = NewsService()
        
        # Run the async scraping operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                news_service.scrape_news_async(
                    query=query,
                    max_results=max_results,
                    format_type=format_type,
                    language=language,
                    country=country,
                    time_period=time_period
                )
            )
            
            logger.info(f"News scraping completed for query: {query}")
            return {
                "status": "success",
                "task_id": self.request.id,
                "query": query,
                "articles_count": len(result.get("articles", [])),
                "result": result,
                "message": f"Successfully scraped {len(result.get('articles', []))} articles"
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"News scraping task failed: {exc}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task {self.request.id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "query": query,
            "error": str(exc),
            "message": f"Failed to scrape news for query: {query}"
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="scrape_multiple_queries",
    queue="news_scraping",
    max_retries=2,
    default_retry_delay=120,
)
def scrape_multiple_queries(
    self,
    queries: List[str],
    max_results: int = None,
    format_type: str = None,
    language: str = None,
    country: str = None,
    time_period: str = None
) -> Dict:
    """
    Scrape news for multiple queries in parallel
    
    Args:
        queries: List of search queries
        max_results: Maximum number of results per query
        format_type: Output format
        language: Language code
        country: Country code
        time_period: Time period for search
    
    Returns:
        Dict with results for all queries
    """
    try:
        logger.info(f"Starting batch news scraping for {len(queries)} queries")
        
        # Create news service instance
        news_service = NewsService()
        
        # Run the async batch operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                news_service.scrape_multiple_queries_async(
                    queries=queries,
                    max_results=max_results,
                    format_type=format_type,
                    language=language,
                    country=country,
                    time_period=time_period
                )
            )
            
            total_articles = sum(len(result.get("articles", [])) for result in results.values())
            logger.info(f"Batch news scraping completed: {total_articles} total articles")
            
            return {
                "status": "success",
                "task_id": self.request.id,
                "queries": queries,
                "total_articles": total_articles,
                "results": results,
                "message": f"Successfully scraped news for {len(queries)} queries"
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Batch news scraping task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying batch task {self.request.id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=120 * (self.request.retries + 1))
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "queries": queries,
            "error": str(exc),
            "message": f"Failed to scrape news for {len(queries)} queries"
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="export_articles",
    queue="news_scraping",
    max_retries=2,
    default_retry_delay=30,
)
def export_articles(
    self,
    articles: List[Dict],
    query: str,
    format_type: str = None
) -> Dict:
    """
    Export articles to specified format
    
    Args:
        articles: List of article dictionaries
        query: Search query for naming
        format_type: Export format (json, csv, excel)
    
    Returns:
        Dict with export result and file path
    """
    try:
        logger.info(f"Starting article export for query: {query}")
        
        # Create news service instance
        news_service = NewsService()
        
        # Run the async export operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                news_service.export_articles_async(
                    articles=articles,
                    query=query,
                    format_type=format_type
                )
            )
            
            logger.info(f"Article export completed for query: {query}")
            return {
                "status": "success",
                "task_id": self.request.id,
                "query": query,
                "format_type": format_type,
                "articles_count": len(articles),
                "file_path": result.get("file_path"),
                "message": f"Successfully exported {len(articles)} articles to {format_type}"
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Article export task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying export task {self.request.id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30 * (self.request.retries + 1))
        
        return {
            "status": "error",
            "task_id": self.request.id,
            "query": query,
            "format_type": format_type,
            "error": str(exc),
            "message": f"Failed to export articles for query: {query}"
        }


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="get_task_status",
    queue="default",
)
def get_task_status(self, task_id: str) -> Dict:
    """
    Get the status of a specific task
    
    Args:
        task_id: Celery task ID
    
    Returns:
        Dict with task status information
    """
    try:
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id, app=celery_app)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }
        
    except Exception as exc:
        logger.error(f"Failed to get task status for {task_id}: {exc}")
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(exc),
            "message": f"Failed to get status for task: {task_id}"
        }
