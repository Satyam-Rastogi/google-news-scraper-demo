"""
Artifacts API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pathlib import Path

from src.services.news_service import NewsService
from src.common.logger import get_logger
from src.common.utils.router import create_versioned_router

router = create_versioned_router(prefix="/artifacts", tags=["artifacts"])
logger = get_logger(__name__)


def get_news_service() -> NewsService:
    """Dependency to get news service instance"""
    return NewsService()


@router.get("/scraped")
async def list_scraped_articles(
    format_type: Optional[str] = Query(None, description="Filter by format (json, csv)"),
    news_service: NewsService = Depends(get_news_service)
):
    """
    List scraped articles
    
    - **format_type**: Optional format filter
    """
    try:
        files = news_service.list_scraped_articles(format_type)
        return {
            "files": [str(f) for f in files],
            "count": len(files),
            "format_filter": format_type
        }
    except Exception as e:
        logger.error(f"Error listing scraped articles: {e}")
        raise HTTPException(status_code=500, detail="Failed to list articles")


@router.get("/stats")
async def get_artifacts_stats(
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get artifacts statistics
    
    Returns statistics about stored artifacts
    """
    try:
        stats = news_service.get_artifacts_stats()
        return {
            "artifacts": stats,
            "summary": {
                "total_files": sum(s["count"] for s in stats.values()),
                "total_size_bytes": sum(s["total_size"] for s in stats.values())
            }
        }
    except Exception as e:
        logger.error(f"Error getting artifacts stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.delete("/cleanup")
async def cleanup_old_articles(
    days_to_keep: int = Query(30, description="Number of days to keep articles"),
    news_service: NewsService = Depends(get_news_service)
):
    """
    Clean up old scraped articles
    
    - **days_to_keep**: Number of days to keep articles (default: 30)
    """
    try:
        removed_count = news_service.cleanup_old_articles(days_to_keep)
        return {
            "message": f"Cleaned up {removed_count} old articles",
            "days_kept": days_to_keep,
            "files_removed": removed_count
        }
    except Exception as e:
        logger.error(f"Error cleaning up articles: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup articles")


@router.get("/structure")
async def get_artifacts_structure():
    """
    Get artifacts directory structure
    
    Returns the current artifacts directory structure
    """
    try:
        from src.common.utils.artifacts import artifacts_manager
        
        structure = {
            "artifacts": {
                "headlines": {
                    "raw": {
                        "json": list(artifacts_manager.get_headlines_path("headlines_raw", "json").glob("*")),
                        "csv": list(artifacts_manager.get_headlines_path("headlines_raw", "csv").glob("*")),
                        "excel": list(artifacts_manager.get_headlines_path("headlines_raw", "excel").glob("*"))
                    },
                    "processed": {
                        "json": list(artifacts_manager.get_headlines_path("headlines_processed", "json").glob("*")),
                        "csv": list(artifacts_manager.get_headlines_path("headlines_processed", "csv").glob("*")),
                        "excel": list(artifacts_manager.get_headlines_path("headlines_processed", "excel").glob("*"))
                    }
                }
            },
            "logs": {
                "api": list(artifacts_manager.get_log_path("api").glob("*")),
                "scraper": list(artifacts_manager.get_log_path("scraper").glob("*")),
                "errors": list(artifacts_manager.get_log_path("errors").glob("*"))
            }
        }
        
        # Convert Path objects to strings for JSON serialization
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            else:
                return obj
        
        return convert_paths(structure)
        
    except Exception as e:
        logger.error(f"Error getting artifacts structure: {e}")
        raise HTTPException(status_code=500, detail="Failed to get structure")
