"""
Async Google News scraper with connection pooling
"""
import asyncio
import logging
from typing import Optional
from src.utils.validation import validate_string, validate_search_query
from src.utils.async_http_client import get_global_async_http_client
from config.config import Config
from urllib.parse import urlencode

class AsyncGoogleNewsScraper:
    BASE_URL: str = Config.SEARCH_URL
    HOMEPAGE_URL: str = Config.HOMEPAGE_URL

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def search(self, query: str) -> Optional[str]:
        """
        Search for news articles based on a query asynchronously
        
        Args:
            query (str): The search query
            
        Returns:
            Optional[str]: HTML content of the search results, or None if failed
        """
        # Handle homepage case
        if query == Config.HOMEPAGE_URL:
            url = self.HOMEPAGE_URL
            try:
                # Get async HTTP client
                client = await get_global_async_http_client()
                response = await client.get(url)
                
                if response and response.status == 200:
                    content = await response.text()
                    return content
                else:
                    self.logger.error(f"Error fetching homepage: Status {response.status if response else 'Unknown'}")
                    return None
            except Exception as e:
                self.logger.error(f"Error during async requests to homepage: {e}")
                return None
        
        # Validate query
        try:
            validated_query = validate_search_query(query)
        except ValueError as e:
            self.logger.error(f"Invalid search query: {e}")
            return None
        
        params = {"q": validated_query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
        url = f"{self.BASE_URL}?{urlencode(params)}"
        
        try:
            # Get async HTTP client
            client = await get_global_async_http_client()
            response = await client.get(url)
            
            if response and response.status == 200:
                content = await response.text()
                return content
            else:
                self.logger.error(f"Error fetching search results: Status {response.status if response else 'Unknown'}")
                return None
        except Exception as e:
            self.logger.error(f"Error during async requests to search: {e}")
            return None