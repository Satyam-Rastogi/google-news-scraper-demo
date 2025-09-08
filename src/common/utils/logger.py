#!/usr/bin/env python3
"""
Logger utility for the News MCP Server
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

from src.common.config.mcp_config import LOGGING_CONFIG

class NewsLogger:
    """Centralized logging utility for the News MCP Server"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance
        
        Args:
            name: Logger name (usually __name__)
            level: Optional log level override
            
        Returns:
            Configured logger instance
        """
        if name not in cls._loggers:
            # Configure logging if not already done
            if not logging.getLogger().handlers:
                logging.config.dictConfig(LOGGING_CONFIG)
            
            # Create logger
            logger = logging.getLogger(name)
            
            # Set level if provided
            if level:
                logger.setLevel(getattr(logging, level.upper(), logging.INFO))
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def setup_file_logging(cls, log_file: str, logger_name: str = 'news_mcp') -> None:
        """
        Setup file logging for a specific logger
        
        Args:
            log_file: Path to log file
            logger_name: Name of the logger to configure
        """
        logger = cls.get_logger(logger_name)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    @classmethod
    def log_function_call(cls, logger: logging.Logger, func_name: str, args: dict = None, kwargs: dict = None):
        """
        Log function call with parameters
        
        Args:
            logger: Logger instance
            func_name: Name of the function being called
            args: Function arguments
            kwargs: Function keyword arguments
        """
        params = []
        if args:
            params.extend([f"arg{i}={arg}" for i, arg in enumerate(args)])
        if kwargs:
            params.extend([f"{k}={v}" for k, v in kwargs.items()])
        
        param_str = ", ".join(params) if params else "no parameters"
        logger.debug(f"Calling {func_name}({param_str})")
    
    @classmethod
    def log_function_result(cls, logger: logging.Logger, func_name: str, result: any, success: bool = True):
        """
        Log function result
        
        Args:
            logger: Logger instance
            func_name: Name of the function
            result: Function result
            success: Whether the function succeeded
        """
        if success:
            logger.debug(f"{func_name} completed successfully")
            if hasattr(result, '__len__') and not isinstance(result, str):
                logger.debug(f"{func_name} returned {len(result)} items")
        else:
            logger.error(f"{func_name} failed: {result}")

# Convenience function for getting loggers
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a logger instance"""
    return NewsLogger.get_logger(name, level)

# Default logger for the module
logger = get_logger(__name__)
