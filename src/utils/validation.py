"""
Validation module for input validation functions used across the news collector
"""
import os
import re
import logging
from typing import Optional, List, Union
from urllib.parse import urlparse

# Set up logger
logger = logging.getLogger(__name__)

def validate_string(value: str, name: str, min_length: int = 1, max_length: int = 1000, 
                   allow_empty: bool = False, pattern: Optional[str] = None) -> str:
    """
    Validate a string input
    
    Args:
        value (str): The string to validate
        name (str): The name of the field for error messages
        min_length (int): Minimum length of the string
        max_length (int): Maximum length of the string
        allow_empty (bool): Whether empty strings are allowed
        pattern (str, optional): Regex pattern the string must match
        
    Returns:
        str: The validated string
        
    Raises:
        ValueError: If the string is invalid
    """
    # Check if empty strings are allowed
    if not value:
        if allow_empty:
            return value
        else:
            raise ValueError(f"{name} cannot be empty")
    
    # Check length
    if len(value) < min_length:
        raise ValueError(f"{name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValueError(f"{name} must be no more than {max_length} characters long")
    
    # Check pattern if provided
    if pattern:
        if not re.match(pattern, value):
            raise ValueError(f"{name} contains invalid characters")
    
    return value

def validate_integer_range(value: Union[int, str], name: str, min_val: int, max_val: int) -> int:
    """
    Validate an integer is within a specified range
    
    Args:
        value (Union[int, str]): The value to validate (can be string or int)
        name (str): The name of the field for error messages
        min_val (int): Minimum allowed value
        max_val (int): Maximum allowed value
        
    Returns:
        int: The validated integer
        
    Raises:
        ValueError: If the value is invalid or out of range
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a valid integer")
    
    if int_value < min_val:
        raise ValueError(f"{name} must be at least {min_val}")
    
    if int_value > max_val:
        raise ValueError(f"{name} must be no more than {max_val}")
    
    return int_value

def validate_boolean(value: Union[bool, str, int]) -> bool:
    """
    Validate a boolean value
    
    Args:
        value (Union[bool, str, int]): The value to validate
        
    Returns:
        bool: The validated boolean
        
    Raises:
        ValueError: If the value cannot be converted to boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'y')
    
    raise ValueError(f"Cannot convert {value} to boolean")

def validate_path(path: str, name: str, must_exist: bool = False, is_dir: bool = False) -> str:
    """
    Validate a file path
    
    Args:
        path (str): The path to validate
        name (str): The name of the field for error messages
        must_exist (bool): Whether the path must exist
        is_dir (bool): Whether the path should be a directory
        
    Returns:
        str: The validated path
        
    Raises:
        ValueError: If the path is invalid
    """
    if not path:
        raise ValueError(f"{name} cannot be empty")
    
    # Prevent directory traversal attacks
    if ".." in path:
        raise ValueError(f"{name} cannot contain directory traversal sequences")
    
    # Check for invalid characters (Windows)
    invalid_chars = '<>:"|?*'
    if any(char in path for char in invalid_chars):
        raise ValueError(f"{name} contains invalid characters")
    
    # Normalize path
    normalized_path = os.path.normpath(path)
    
    # Check if path must exist
    if must_exist:
        if is_dir and not os.path.isdir(normalized_path):
            raise ValueError(f"{name} directory does not exist: {normalized_path}")
        elif not is_dir and not os.path.exists(normalized_path):
            raise ValueError(f"{name} file does not exist: {normalized_path}")
    
    return normalized_path

def validate_url(url: str, name: str, require_https: bool = True) -> str:
    """
    Validate a URL
    
    Args:
        url (str): The URL to validate
        name (str): The name of the field for error messages
        require_https (bool): Whether HTTPS is required
        
    Returns:
        str: The validated URL
        
    Raises:
        ValueError: If the URL is invalid
    """
    if not url:
        raise ValueError(f"{name} cannot be empty")
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError(f"{name} is not a valid URL")
    
    # Check scheme
    if not parsed.scheme:
        raise ValueError(f"{name} must include a scheme (http:// or https://)")
    
    if require_https and parsed.scheme != 'https':
        raise ValueError(f"{name} must use HTTPS")
    
    # Check netloc
    if not parsed.netloc:
        raise ValueError(f"{name} must include a domain")
    
    # Check for javascript or data URLs (security risk)
    if parsed.scheme in ('javascript', 'data'):
        raise ValueError(f"{name} cannot be a javascript or data URL")
    
    # Check length
    if len(url) > 2048:
        raise ValueError(f"{name} is too long")
    
    return url

def validate_config_values(config_dict: dict) -> dict:
    """
    Validate configuration values
    
    Args:
        config_dict (dict): Dictionary of configuration values
        
    Returns:
        dict: The validated configuration dictionary
        
    Raises:
        ValueError: If any configuration values are invalid
    """
    validated = config_dict.copy()
    
    # Validate OUTPUT_FORMAT
    if 'OUTPUT_FORMAT' in validated:
        output_format = validated['OUTPUT_FORMAT']
        if output_format not in ('json', 'csv'):
            raise ValueError(f"OUTPUT_FORMAT must be 'json' or 'csv', got '{output_format}'")
    
    # Validate OUTPUT_DIR
    if 'OUTPUT_DIR' in validated:
        validated['OUTPUT_DIR'] = validate_path(validated['OUTPUT_DIR'], "OUTPUT_DIR")
    
    # Validate LOG_LEVEL
    if 'LOG_LEVEL' in validated:
        valid_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        if validated['LOG_LEVEL'] not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, got '{validated['LOG_LEVEL']}'")
    
    # Validate scheduler settings
    if 'SCHEDULER_INTERVAL_MINUTES' in validated:
        validated['SCHEDULER_INTERVAL_MINUTES'] = validate_integer_range(
            validated['SCHEDULER_INTERVAL_MINUTES'], "SCHEDULER_INTERVAL_MINUTES", 1, 1440)
    
    if 'SCHEDULER_DAILY_HOUR' in validated:
        validated['SCHEDULER_DAILY_HOUR'] = validate_integer_range(
            validated['SCHEDULER_DAILY_HOUR'], "SCHEDULER_DAILY_HOUR", 0, 23)
    
    if 'SCHEDULER_DAILY_MINUTE' in validated:
        validated['SCHEDULER_DAILY_MINUTE'] = validate_integer_range(
            validated['SCHEDULER_DAILY_MINUTE'], "SCHEDULER_DAILY_MINUTE", 0, 59)
    
    # Validate full article settings
    if 'FULL_ARTICLES_COUNT' in validated:
        validated['FULL_ARTICLES_COUNT'] = validate_integer_range(
            validated['FULL_ARTICLES_COUNT'], "FULL_ARTICLES_COUNT", 1, 50)
    
    # Validate boolean values
    if 'SCRAPE_FULL_ARTICLES' in validated:
        validated['SCRAPE_FULL_ARTICLES'] = validate_boolean(validated['SCRAPE_FULL_ARTICLES'])
    
    if 'SCRAPE_IMAGES' in validated:
        validated['SCRAPE_IMAGES'] = validate_boolean(validated['SCRAPE_IMAGES'])
    
    # Validate retry mechanism settings
    if 'MAX_RETRIES' in validated:
        validated['MAX_RETRIES'] = validate_integer_range(
            validated['MAX_RETRIES'], "MAX_RETRIES", 0, 10)
    
    if 'BASE_DELAY' in validated:
        try:
            validated['BASE_DELAY'] = float(validated['BASE_DELAY'])
            if validated['BASE_DELAY'] < 0:
                raise ValueError("BASE_DELAY must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("BASE_DELAY must be a valid number")
    
    if 'MAX_DELAY' in validated:
        try:
            validated['MAX_DELAY'] = float(validated['MAX_DELAY'])
            if validated['MAX_DELAY'] < 0:
                raise ValueError("MAX_DELAY must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("MAX_DELAY must be a valid number")
    
    if 'FAILURE_THRESHOLD' in validated:
        validated['FAILURE_THRESHOLD'] = validate_integer_range(
            validated['FAILURE_THRESHOLD'], "FAILURE_THRESHOLD", 1, 20)
    
    if 'RECOVERY_TIMEOUT' in validated:
        validated['RECOVERY_TIMEOUT'] = validate_integer_range(
            validated['RECOVERY_TIMEOUT'], "RECOVERY_TIMEOUT", 10, 3600)
    
    # Validate TOPICS
    if 'TOPICS' in validated:
        topics = validated['TOPICS']
        if not isinstance(topics, list):
            raise ValueError("TOPICS must be a list")
        
        if len(topics) == 0:
            raise ValueError("TOPICS cannot be empty")
        
        validated_topics = []
        for i, topic in enumerate(topics):
            try:
                validated_topic = validate_string(topic, f"Topic {i+1}", min_length=1, max_length=200)
                validated_topics.append(validated_topic)
            except ValueError as e:
                raise ValueError(f"Invalid topic at index {i}: {str(e)}")
        
        validated['TOPICS'] = validated_topics
    
    return validated

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing unsafe characters
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(ch for ch in filename if ord(ch) >= 32)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def validate_search_query(query: str) -> str:
    """
    Validate a search query
    
    Args:
        query (str): The search query to validate
        
    Returns:
        str: The validated search query
        
    Raises:
        ValueError: If the query is invalid
    """
    return validate_string(query, "Search query", min_length=1, max_length=200)