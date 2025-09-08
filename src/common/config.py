# Common package
"""
Configuration management
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


"""
Constants
"""

# Load environment variables from .env file
load_dotenv()


@dataclass
class AppConfig:
    """Application configuration"""
    # API Configuration
    api_title: str = "Google News Scraper API"
    api_version: str = "1.0.0"
    api_description: str = "A FastAPI-based Google News scraper service"
    
    # Router Configuration
    api_prefix: str = "/api/v1"
    enable_versioning: bool = True
    supported_versions: list = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.supported_versions is None:
            self.supported_versions = ["v1"]
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Scraping Configuration
    default_max_results: int = 50
    max_results_limit: int = 100
    request_timeout: int = 30
    request_delay: float = 1.0
    
    # Default values for news scraping
    default_language: str = "en"
    default_country: str = "US"
    default_time_period: str = "24h"
    default_format_type: str = "json"
    
    # Output Configuration
    default_output_format: str = "json"
    output_directory: str = "artifacts/data/scraped"
    logs_directory: str = "logs"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    enable_cache: bool = False
    cache_ttl: int = 3600
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        # Parse supported versions from environment
        supported_versions_str = os.getenv("SUPPORTED_VERSIONS", "v1")
        supported_versions = [v.strip() for v in supported_versions_str.split(",")]
        
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            api_prefix=os.getenv("API_PREFIX", "/api/v1"),
            enable_versioning=os.getenv("ENABLE_VERSIONING", "true").lower() == "true",
            supported_versions=supported_versions,
            default_max_results=int(os.getenv("DEFAULT_MAX_RESULTS", "50")),
            max_results_limit=int(os.getenv("MAX_RESULTS_LIMIT", "100")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            request_delay=float(os.getenv("REQUEST_DELAY", "1.0")),
            default_output_format=os.getenv("DEFAULT_OUTPUT_FORMAT", "json"),
            output_directory=os.getenv("OUTPUT_DIRECTORY", "artifacts/data/scraped"),
            logs_directory=os.getenv("LOGS_DIRECTORY", "logs"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            enable_cache=os.getenv("ENABLE_CACHE", "false").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
        )


# Global configuration instance
config = AppConfig.from_env()
