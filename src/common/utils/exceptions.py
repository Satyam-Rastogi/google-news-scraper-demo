#!/usr/bin/env python3
"""
Exception handling utilities for the News MCP Server
"""

import traceback
from typing import Any, Dict, Optional, Union
from functools import wraps

from src.common.utils.logger import get_logger

logger = get_logger(__name__)

class NewsMCPError(Exception):
    """Base exception for News MCP Server"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class NewsScrapingError(NewsMCPError):
    """Exception raised during news scraping operations"""
    pass

class NewsParsingError(NewsMCPError):
    """Exception raised during news parsing operations"""
    pass

class NewsValidationError(NewsMCPError):
    """Exception raised during data validation"""
    pass

class NewsConfigurationError(NewsMCPError):
    """Exception raised during configuration operations"""
    pass

class NewsNetworkError(NewsMCPError):
    """Exception raised during network operations"""
    pass

class NewsFileError(NewsMCPError):
    """Exception raised during file operations"""
    pass

def handle_exceptions(
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    error_class: type = NewsMCPError
):
    """
    Decorator to handle exceptions in functions
    
    Args:
        default_return: Value to return if an exception occurs
        log_error: Whether to log the error
        reraise: Whether to reraise the exception after logging
        error_class: Custom exception class to raise
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    if isinstance(e, error_class):
                        raise
                    else:
                        raise error_class(f"Error in {func.__name__}: {str(e)}")
                
                return default_return
        return wrapper
    return decorator

def safe_execute(
    func,
    *args,
    default_return: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    error_class: type = NewsMCPError,
    **kwargs
) -> Any:
    """
    Safely execute a function with exception handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return if an exception occurs
        log_error: Whether to log the error
        reraise: Whether to reraise the exception after logging
        error_class: Custom exception class to raise
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return if exception occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        if reraise:
            if isinstance(e, error_class):
                raise
            else:
                raise error_class(f"Error in {func.__name__}: {str(e)}")
        
        return default_return

def create_error_response(
    error: Union[str, Exception],
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error: Error message or exception
        error_code: Optional error code
        details: Optional additional details
        
    Returns:
        Standardized error response dictionary
    """
    if isinstance(error, Exception):
        message = str(error)
        if hasattr(error, 'error_code'):
            error_code = error.error_code
        if hasattr(error, 'details'):
            details = error.details
    else:
        message = str(error)
    
    return {
        "success": False,
        "error": message,
        "error_code": error_code,
        "details": details or {}
    }

def create_success_response(
    data: Any = None,
    message: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Optional success message
        **kwargs: Additional response fields
        
    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    response.update(kwargs)
    return response

class ExceptionContext:
    """Context manager for exception handling"""
    
    def __init__(
        self,
        default_return: Any = None,
        log_error: bool = True,
        reraise: bool = False,
        error_class: type = NewsMCPError
    ):
        self.default_return = default_return
        self.log_error = log_error
        self.reraise = reraise
        self.error_class = error_class
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val
            
            if self.log_error:
                logger.error(f"Exception occurred: {str(exc_val)}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            if self.reraise:
                if not isinstance(exc_val, self.error_class):
                    raise self.error_class(f"Exception occurred: {str(exc_val)}")
                return False  # Don't suppress the exception
            
            return True  # Suppress the exception
        
        return False
