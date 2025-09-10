"""
Utility module for common functions used across the news collector
"""

import os
import logging
import requests
from urllib.parse import urlparse, urljoin
import base64
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import sys
from typing import Optional, Dict, List, Any
from src.core.news_types import FullArticleDict
from .validation import validate_path, validate_url, sanitize_filename
from .retry_utils import retry_for_network, CircuitBreaker
from config.config import Config

def setup_logging(log_level: str = "INFO", log_to_console: bool = True) -> logging.Logger:
    """
    Set up logging configuration to both file and console
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_console (bool): Whether to log to console (default: True)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Validate log level
    valid_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
    
    # Create logs directory if it doesn't exist
    log_dir = "data/logs"
    try:
        validated_log_dir = validate_path(log_dir, "Log directory")
        os.makedirs(validated_log_dir, exist_ok=True)
    except ValueError:
        # Fallback to current directory if validation fails
        validated_log_dir = "."
        os.makedirs(validated_log_dir, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    log_file = os.path.join(validated_log_dir, 'app.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    
    # Console handler with proper encoding (optional)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.stream.reconfigure(encoding='utf-8')
        root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

def setup_console_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up console logging for the application (deprecated - use setup_logging with log_to_console=True)
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logging(log_level, log_to_console=True)

def setup_file_only_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up file-only logging for scheduled tasks
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logging(log_level, log_to_console=False)

# Removed decode_google_news_url function as it's now in google_news_decoder.py
# Import the new decoder instead
from src.scrapers.google_news_decoder import decode_google_news_url

# Circuit breaker for Selenium operations
selenium_circuit_breaker = CircuitBreaker(
    failure_threshold=Config.FAILURE_THRESHOLD,
    recovery_timeout=Config.RECOVERY_TIMEOUT
)

@retry_for_network
def _resolve_url_with_selenium(google_news_url: str, logger: Optional[logging.Logger] = None) -> str:
    """
    Internal function to resolve Google News redirect URL using Selenium with retry logic
    """
    if logger is None:
        logger = logging.getLogger(__name__)
        
    driver: Optional[webdriver.Chrome] = None
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Create WebDriver instance
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Navigate to the Google News URL
        logger.info(f"Navigating to Google News URL: {google_news_url}")
        driver.get(google_news_url)
        
        # Wait for page to load and redirect to complete
        try:
            WebDriverWait(driver, 10).until(
                lambda d: "news.google.com" not in d.current_url or 
                          len(d.find_elements(By.TAG_NAME, "noscript")) > 0
            )
        except TimeoutException:
            pass  # Continue even if timeout occurs
        
        # Get the final URL after redirects
        final_url = driver.current_url
        logger.info(f"Final URL after redirects: {final_url}")
        
        return final_url
        
    except WebDriverException as e:
        logger.error(f"WebDriver error while resolving Google News URL {google_news_url}: {e}")
        # If Selenium fails, return the original URL
        return google_news_url
    except Exception as e:
        logger.error(f"Error resolving Google News URL {google_news_url}: {e}")
        # If resolution fails, return the original URL
        return google_news_url
    finally:
        # Clean up WebDriver
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

def resolve_google_news_url_with_selenium(google_news_url: str, logger: Optional[logging.Logger] = None) -> str:
    """
    Resolve Google News redirect URL to get the real article URL using Selenium
    
    Args:
        google_news_url (str): Google News redirect URL
        logger: Optional logger instance
        
    Returns:
        str: Real article URL
    """
    if logger is None:
        logger = logging.getLogger(__name__)
        
    # Validate URL
    try:
        validated_url = validate_url(google_news_url, "Google News URL", require_https=False)
    except ValueError as e:
        logger.warning(f"Invalid Google News URL: {e}")
        return google_news_url
    
    try:
        # Resolve URL with retry logic and circuit breaker
        final_url = selenium_circuit_breaker.call(_resolve_url_with_selenium, validated_url, logger)
        return final_url
    except Exception as e:
        logger.error(f"Error resolving Google News URL with Selenium {validated_url}: {e}")
        return google_news_url

# Circuit breaker for image downloading
image_circuit_breaker = CircuitBreaker(
    failure_threshold=Config.FAILURE_THRESHOLD,
    recovery_timeout=Config.RECOVERY_TIMEOUT
)

@retry_for_network
def _download_image_with_retry(image_url: str, timeout: int = 10) -> bytes:
    """
    Download image with retry logic
    """
    response = requests.get(image_url, timeout=timeout)
    response.raise_for_status()
    return response.content

def download_image(image_url: str, output_dir: str, article_title: str = "", prefix: str = "img") -> Optional[str]:
    """
    Download an image and save it locally
    
    Args:
        image_url (str): URL of the image to download
        output_dir (str): Directory to save the image
        article_title (str): Title of the article (used for naming files)
        prefix (str): Prefix for the image filename
        
    Returns:
        Optional[str]: Local path to the downloaded image, or None if failed
    """
    try:
        # Validate URL
        try:
            validated_url = validate_url(image_url, "Image URL")
        except ValueError as e:
            logging.warning(f"Invalid image URL: {e}")
            return None
            
        # Skip if image URL is empty
        if not validated_url:
            return None
            
        # Validate output directory
        try:
            validated_output_dir = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logging.warning(f"Invalid output directory: {e}")
            return None
            
        # Create output directory if it doesn't exist
        image_dir = os.path.join(validated_output_dir, "images")
        os.makedirs(image_dir, exist_ok=True)
            
        # Create a safe filename
        safe_title = sanitize_filename(article_title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
        # Get file extension from URL
        parsed_url = urlparse(validated_url)
        ext = os.path.splitext(parsed_url.path)[1]
        if not ext:
            ext = '.jpg'  # Default extension
                
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{prefix}_{timestamp}{ext}"
        filepath = os.path.join(image_dir, filename)
            
        # Download image with retry logic and circuit breaker
        image_content = image_circuit_breaker.call(_download_image_with_retry, validated_url)
            
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_content)
                
        logging.info(f"Downloaded image: {filename}")
        return filepath
            
    except Exception as e:
        logging.error(f"Error downloading image from {image_url}: {e}")
        return None

def save_article_text(article_data: Dict[str, Any], output_dir: str, article_title: str = "") -> Optional[str]:
    """
    Save the full article text to a file
    
    Args:
        article_data (Dict[str, Any]): Dictionary containing article data
        output_dir (str): Directory to save the article
        article_title (str): Title of the article (used for naming files)
        
    Returns:
        Optional[str]: Local path to the saved article file, or None if failed
    """
    try:
        # Validate output directory
        try:
            validated_output_dir = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logging.warning(f"Invalid output directory: {e}")
            return None
        
        # Create output directory if it doesn't exist
        article_dir = os.path.join(validated_output_dir, "articles")
        os.makedirs(article_dir, exist_ok=True)
        
        # Create a safe filename
        safe_title = sanitize_filename(article_title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = safe_title + "_" + timestamp + ".txt"
        filepath = os.path.join(article_dir, filename)
            
        # Create article content
        content = ""
        content += "Title: " + str(article_data.get('title', 'N/A')) + "\n"
        content += "URL: " + str(article_data.get('url', 'N/A')) + "\n"
        content += "Authors: " + ', '.join(article_data.get('authors', [])) + "\n"
        content += "Publish Date: " + str(article_data.get('publish_date', 'N/A')) + "\n"
        content += "Downloaded At: " + str(article_data.get('downloaded_at', 'N/A')) + "\n"
        content += "Keywords: " + ', '.join(article_data.get('keywords', [])) + "\n"
        content += "Summary: " + str(article_data.get('summary', 'N/A')) + "\n"
        content += "Meta Description: " + str(article_data.get('meta_description', 'N/A')) + "\n"
        content += "Meta Language: " + str(article_data.get('meta_lang', 'N/A')) + "\n"
        content += "\n" + "="*50 + "\n\n"
        content += str(article_data.get('text', 'N/A'))
            
        # Save content to file with proper encoding
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
                
        logging.info("Saved article text: " + filename)
        return filepath
            
    except Exception as e:
        logging.error("Error saving article text for " + article_title + ": " + str(e))
        return None
