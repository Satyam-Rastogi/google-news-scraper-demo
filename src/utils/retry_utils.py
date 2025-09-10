"""
Retry utilities for handling network operations with robust error recovery
"""
import time
import random
import logging
from typing import Callable, Any, Optional, Type, Tuple, Set
from functools import wraps
import requests
from requests.exceptions import RequestException
import json
import csv

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker implementation to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection"""
        if self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

def is_rate_limit_error(exception: Exception) -> bool:
    """Check if an exception is a rate limiting error"""
    if isinstance(exception, requests.exceptions.HTTPError):
        return exception.response.status_code == 429
    return False

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    rate_limit_delay: float = 10.0,  # Additional delay for rate limiting
    exceptions: Tuple[Type[Exception], ...] = (RequestException, ConnectionError, TimeoutError),
    circuit_breaker: Optional[CircuitBreaker] = None
) -> Callable:
    """
    Decorator that implements retry logic with exponential backoff and jitter
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        rate_limit_delay: Additional delay for rate limiting errors
        exceptions: Tuple of exceptions to catch and retry on
        circuit_breaker: Optional circuit breaker instance
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use circuit breaker if provided
            if circuit_breaker:
                def call_func():
                    return func(*args, **kwargs)
                return circuit_breaker.call(call_func)
            
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # If this was the last attempt, re-raise the exception
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e
                    
                    # Calculate delay
                    if is_rate_limit_error(e):
                        # For rate limiting errors, use a longer delay
                        delay = rate_limit_delay
                        logger.warning(
                            f"Rate limiting detected for {func.__name__}: {str(e)}. "
                            f"Waiting {delay} seconds before retry..."
                        )
                    else:
                        # For other errors, use exponential backoff
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter if requested
                    if jitter and not is_rate_limit_error(e):
                        delay *= (0.5 + random.random() * 0.5)  # 0.5 to 1.0 multiplier
                    
                    logger.warning(
                        f"Attempt {attempt + 1} of {func.__name__} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Sleep for the calculated delay
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

# Pre-configured retry policies for different use cases
retry_default = retry_with_backoff(max_retries=3, base_delay=1.0)
retry_aggressive = retry_with_backoff(max_retries=5, base_delay=0.5)
retry_conservative = retry_with_backoff(max_retries=2, base_delay=2.0, max_delay=30.0)
retry_for_network = retry_with_backoff(
    max_retries=3, 
    base_delay=1.0,
    rate_limit_delay=15.0,  # Wait 15 seconds for rate limiting
    exceptions=(RequestException, ConnectionError, TimeoutError)
)

# Additional specific retry policies
retry_for_parsing = retry_with_backoff(
    max_retries=2,
    base_delay=0.5,
    exceptions=(ValueError, TypeError, json.JSONDecodeError, csv.Error)  # Specific parsing errors
)

retry_for_file_operations = retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=10.0,
    exceptions=(OSError, IOError)  # File operation errors
)

retry_for_validation = retry_with_backoff(
    max_retries=1,
    base_delay=0.1,
    exceptions=(ValueError,)  # Validation errors
)