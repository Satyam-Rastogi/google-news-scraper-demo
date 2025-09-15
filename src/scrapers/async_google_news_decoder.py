"""
Async Google News URL decoder that combines the gnews library approach with our current implementation
"""
import asyncio
import logging
from typing import Optional, List, Tuple

try:
    from googlenewsdecoder import gnewsdecoder
    GNEWS_DECODER_AVAILABLE = True
except ImportError:
    GNEWS_DECODER_AVAILABLE = False
    logging.warning("gnewsdecoder not available. Will use fallback URL resolution methods.")

from src.scrapers.async_url_resolver import resolve_google_news_url_async

logger = logging.getLogger(__name__)

async def decode_google_news_url_async(google_news_url: str, use_fallback: bool = True) -> Optional[str]:
    """
    Decode a Google News URL to get the actual article URL using multiple approaches:
    1. Primary: gnewsdecoder library (more reliable)
    2. Fallback: Our current implementation using async requests
    3. Secondary fallback: Selenium-based resolution (kept synchronous for now)
    
    Args:
        google_news_url (str): The Google News redirect URL
        use_fallback (bool): Whether to use fallback methods if primary fails
        
    Returns:
        Optional[str]: The real article URL, or None if decoding fails
    """
    # Validate input
    if not google_news_url or not isinstance(google_news_url, str):
        logger.warning("Invalid Google News URL provided")
        return None
        
    logger.info(f"Attempting to decode Google News URL: {google_news_url[:100]}...")
    
    # Method 1: Try gnewsdecoder if available
    if GNEWS_DECODER_AVAILABLE:
        try:
            logger.debug("Attempting to decode with gnewsdecoder...")
            # Note: gnewsdecoder might not be async, so we run it in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, gnewsdecoder, google_news_url, 1)
            
            if result.get("status") and result.get("decoded_url"):
                decoded_url = result["decoded_url"]
                logger.info(f"gnewsdecoder successfully decoded URL to: {decoded_url[:100]}...")
                return decoded_url
            else:
                error_msg = result.get("message", "Unknown error")
                logger.warning(f"gnewsdecoder failed: {error_msg}")
        except Exception as e:
            logger.error(f"Error using gnewsdecoder: {e}")
    
    # Method 2: Try our current implementation as fallback
    if use_fallback:
        try:
            logger.debug("Attempting to decode with fallback resolver...")
            resolved_url = await resolve_google_news_url_async(google_news_url)
            
            # Check if the resolved URL is different from the original
            if resolved_url and resolved_url != google_news_url:
                logger.info(f"Fallback resolver successfully resolved URL to: {resolved_url[:100]}...")
                return resolved_url
            else:
                logger.warning("Fallback resolver returned the same URL")
        except Exception as e:
            logger.error(f"Error using fallback resolver: {e}")
    
    # If all methods fail, return None
    logger.error(f"All decoding methods failed for URL: {google_news_url[:100]}...")
    return None

async def decode_google_news_urls_batch_async(google_news_urls: List[str], use_fallback: bool = True, 
                                            max_concurrent: int = 10) -> List[Tuple[str, Optional[str]]]:
    """
    Decode multiple Google News URLs concurrently using batching to control concurrency
    
    Args:
        google_news_urls (List[str]): List of Google News redirect URLs
        use_fallback (bool): Whether to use fallback methods if primary fails
        max_concurrent (int): Maximum number of concurrent decoding operations
        
    Returns:
        List[Tuple[str, Optional[str]]]: List of (original_url, decoded_url) tuples
    """
    if not google_news_urls:
        return []
    
    logger.info(f"Starting batch decoding of {len(google_news_urls)} URLs with max concurrency {max_concurrent}")
    
    # Create semaphore to limit concurrent operations
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def decode_with_semaphore(url: str) -> Tuple[str, Optional[str]]:
        async with semaphore:
            decoded_url = await decode_google_news_url_async(url, use_fallback)
            return (url, decoded_url)
    
    # Create tasks for all URLs
    tasks = [decode_with_semaphore(url) for url in google_news_urls]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results, handling any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Exception during decoding of URL {google_news_urls[i]}: {result}")
            processed_results.append((google_news_urls[i], None))
        else:
            processed_results.append(result)
    
    logger.info(f"Completed batch decoding of {len(google_news_urls)} URLs")
    return processed_results