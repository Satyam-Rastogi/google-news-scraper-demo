"""
Logging configuration
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from .config import config


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    log_level = level or config.log_level
    
    # Ensure logs directory exists
    logs_dir = Path(config.logs_directory)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Create file handler for general logs
    file_handler = logging.FileHandler(logs_dir / "api" / "app.log")
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Remove default handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        if not isinstance(handler, (logging.StreamHandler, logging.FileHandler)):
            root_logger.removeHandler(handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
