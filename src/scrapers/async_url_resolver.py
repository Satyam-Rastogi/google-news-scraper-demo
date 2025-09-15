"""
Async URL resolver for Google News URLs

This module resolves Google News "read" URLs to get the actual article URLs
by following redirects asynchronously.
"""
import asyncio
import logging
from typing import Optional
from src.utils.async_http_client import get_global_async_http_client
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

async def resolve_google_news_url_async(google_news_url: str, timeout: int = 30) -> str:
    """
    Resolve a Google News URL to get the actual article URL by following redirects asynchronously
    
    Args:
        google_news_url (str): The Google News URL to resolve
        timeout (int): Request timeout in seconds
        
    Returns:
        str: The resolved actual URL or the original URL if resolution fails
    """
    try:
        # Get async HTTP client
        client = await get_global_async_http_client()
        
        # Make a HEAD request with redirect following disabled to get redirect info
        response = await client.head(google_news_url)
        
        # Follow redirects manually to get the final URL
        redirect_count = 0
        max_redirects = 10
        current_url = google_news_url
        
        while response and (response.status in [301, 302, 303, 307, 308] or 
                           str(response.status).startswith('3')):
            if redirect_count >= max_redirects:
                logger.warning(f"Max redirects reached for {google_news_url}")
                break
                
            # Get the redirect location
            location = response.headers.get('Location')
            if not location:
                break
                
            # Resolve relative URLs
            if location.startswith('/'):
                parsed_current = urlparse(current_url)
                location = f"{parsed_current.scheme}://{parsed_current.netloc}{location}"
            elif not location.startswith('http'):
                location = urljoin(current_url, location)
                
            current_url = location
            logger.debug(f"Redirect {redirect_count + 1}: {current_url}")
            
            # Make next request
            try:
                response = await client.head(current_url)
                redirect_count += 1
            except Exception as e:
                logger.warning(f"Error following redirect to {current_url}: {e}")
                # Try GET request as fallback
                try:
                    response = await client.get(current_url)
                except Exception as e2:
                    logger.warning(f"Error with GET request to {current_url}: {e2}")
                    break
        
        # Return the final URL
        logger.info(f"Resolved {google_news_url} to {current_url}")
        return current_url
        
    except Exception as e:
        logger.error(f"Error resolving Google News URL {google_news_url}: {e}")
        # Try a simple GET request as fallback
        try:
            client = await get_global_async_http_client()
            response = await client.get(google_news_url)
            if response:
                # For aiohttp, we need to get the URL from the response
                # This is a simplified approach - in practice, you might need to check history
                final_url = str(response.url)
                logger.info(f"Fallback resolved {google_news_url} to {final_url}")
                return final_url
            else:
                return google_news_url
        except Exception as e2:
            logger.error(f"Fallback also failed for {google_news_url}: {e2}")
            return google_news_url