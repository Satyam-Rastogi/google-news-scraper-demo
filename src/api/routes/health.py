"""
Health check API routes
"""

from fastapi import APIRouter
from ...models.schemas import HealthResponse
from ...services.news_service import NewsService
from ...common.config import config
from ...common.logger import get_logger

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API service
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        version=config.api_version
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Returns whether the service is ready to handle requests
    """
    logger.info("Readiness check requested")
    try:
        # Test if the news service can be instantiated
        news_service = NewsService()
        health_status = news_service.get_health_status()
        
        if health_status["status"] == "healthy":
            return {"status": "ready", "message": "Service is ready"}
        else:
            return {"status": "not ready", "message": "Service is not healthy"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "message": f"Service error: {str(e)}"}


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint
    
    Returns whether the service is alive
    """
    logger.info("Liveness check requested")
    return {"status": "alive", "message": "Service is running"}
