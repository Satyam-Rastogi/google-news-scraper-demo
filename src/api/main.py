"""
FastAPI application for Google News Scraper
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from src.common.config import config
from src.common.logger import setup_logging
from src.common.exceptions import NewsScraperException
from .routes import news, health, artifacts


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create FastAPI app
    app = FastAPI(
        title=config.api_title,
        version=config.api_version,
        description=config.api_description,
        debug=config.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Include versioned routers
    app.include_router(news.router)
    app.include_router(health.router)
    app.include_router(artifacts.router)
    
    # Include legacy routers for backward compatibility
    if config.enable_versioning:
        app.include_router(health.legacy_router)
    
    # Global exception handler
    @app.exception_handler(NewsScraperException)
    async def news_scraper_exception_handler(request: Request, exc: NewsScraperException):
        logger.error(f"News scraper exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "type": "NewsScraperException"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "type": "InternalError"}
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Google News Scraper API",
            "version": config.api_version,
            "docs": "/docs",
            "health": "/health",
            "api_prefix": config.api_prefix if config.enable_versioning else None,
            "supported_versions": config.supported_versions if config.enable_versioning else None
        }
    
    # Version info endpoint
    @app.get("/version")
    async def version_info():
        return {
            "api_version": config.api_version,
            "api_prefix": config.api_prefix,
            "enable_versioning": config.enable_versioning,
            "supported_versions": config.supported_versions,
            "endpoints": {
                "versioned": f"{config.api_prefix}/" if config.enable_versioning else None,
                "legacy": "/" if config.enable_versioning else None
            }
        }
    
    logger.info(f"FastAPI application created with version {config.api_version}")
    return app


# Create the app instance
app = create_app()
