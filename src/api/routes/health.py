"""
Health check API routes
"""

from fastapi import APIRouter
from src.models.schemas import HealthResponse
from src.services.news_service import NewsService
from src.common.config import config
from src.common.logger import get_logger
from src.common.router import create_versioned_router, create_legacy_router

# Health routes can be both versioned and legacy for backward compatibility
router = create_versioned_router(prefix="/health", tags=["health"])
legacy_router = create_legacy_router(prefix="/health", tags=["health"])
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


# Legacy endpoints for backward compatibility
@legacy_router.get("/", response_model=HealthResponse)
async def legacy_health_check():
    """Legacy health check endpoint"""
    return await health_check()


@legacy_router.get("/ready")
async def legacy_readiness_check():
    """Legacy readiness check endpoint"""
    return await readiness_check()


@legacy_router.get("/live")
async def legacy_liveness_check():
    """Legacy liveness check endpoint"""
    return await liveness_check()
