"""
Router utilities for API versioning
"""

from fastapi import APIRouter
from typing import Optional
from .config import config
from .logger import get_logger

logger = get_logger(__name__)


def create_versioned_router(
    prefix: str = "",
    tags: Optional[list] = None,
    version: str = "v1"
) -> APIRouter:
    """
    Create a versioned API router
    
    Args:
        prefix: Router prefix (without version)
        tags: Router tags
        version: API version (v1, v2, etc.)
        
    Returns:
        Configured APIRouter with versioning
    """
    if not config.enable_versioning:
        # If versioning is disabled, use direct prefix
        router_prefix = prefix
    else:
        # Create versioned prefix
        if version not in config.supported_versions:
            logger.warning(f"Version {version} not in supported versions: {config.supported_versions}")
            version = config.supported_versions[0]  # Use first supported version
        
        # Build versioned prefix
        if prefix.startswith("/"):
            prefix = prefix[1:]  # Remove leading slash
        
        router_prefix = f"{config.api_prefix}/{prefix}" if prefix else config.api_prefix
    
    logger.info(f"Creating versioned router: {router_prefix} (version: {version})")
    
    return APIRouter(
        prefix=router_prefix,
        tags=tags or [],
        responses={
            404: {"description": "Not found"},
            500: {"description": "Internal server error"}
        }
    )


def get_version_from_request(request) -> str:
    """
    Extract version from request path
    
    Args:
        request: FastAPI request object
        
    Returns:
        API version string
    """
    if not config.enable_versioning:
        return "v1"
    
    path = request.url.path
    if config.api_prefix in path:
        # Extract version from path like /api/v1/news
        parts = path.split("/")
        try:
            api_index = parts.index("api")
            if api_index + 1 < len(parts):
                version = parts[api_index + 1]
                if version in config.supported_versions:
                    return version
        except (ValueError, IndexError):
            pass
    
    # Default to first supported version
    return config.supported_versions[0]


def create_legacy_router(
    prefix: str = "",
    tags: Optional[list] = None
) -> APIRouter:
    """
    Create a legacy router without versioning (for backward compatibility)
    
    Args:
        prefix: Router prefix
        tags: Router tags
        
    Returns:
        Configured APIRouter without versioning
    """
    logger.info(f"Creating legacy router: {prefix}")
    
    return APIRouter(
        prefix=prefix,
        tags=tags or [],
        responses={
            404: {"description": "Not found"},
            500: {"description": "Internal server error"}
        }
    )
