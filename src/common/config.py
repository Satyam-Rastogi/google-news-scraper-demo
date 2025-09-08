# Common package
"""
Configuration management
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AppConfig:
    """Application configuration"""
    # API Configuration
    api_title: str = "Google News Scraper API"
    api_version: str = "1.0.0"
    api_description: str = "A FastAPI-based Google News scraper service"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Scraping Configuration
    default_max_results: int = 50
    max_results_limit: int = 100
    request_timeout: int = 30
    request_delay: float = 1.0
    
    # Output Configuration
    default_output_format: str = "json"
    output_directory: str = "data"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            default_max_results=int(os.getenv("DEFAULT_MAX_RESULTS", "50")),
            max_results_limit=int(os.getenv("MAX_RESULTS_LIMIT", "100")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            request_delay=float(os.getenv("REQUEST_DELAY", "1.0")),
            default_output_format=os.getenv("DEFAULT_OUTPUT_FORMAT", "json"),
            output_directory=os.getenv("OUTPUT_DIRECTORY", "data"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Global configuration instance
config = AppConfig.from_env()
