"""
Google News Scraper Module
Handles web scraping from Google News
"""

import requests
from urllib.parse import urlencode
import time
import logging
from typing import Optional
from dataclasses import dataclass


@dataclass
class ScrapingConfig:
    """Configuration for scraping behavior"""
    base_url: str = "https://news.google.com/search"
    timeout: int = 30
    delay: float = 1.0
    max_retries: int = 3


class GoogleNewsScraper:
    """Google News scraper with rate limiting and error handling"""
    
    def __init__(self, config: Optional[ScrapingConfig] = None) -> None:
        """
        Initialize the scraper with configuration
        
        Args:
            config: Scraping configuration, uses default if None
        """
        self.config = config or ScrapingConfig()
        self.session = self._create_session()
        self.logger = logging.getLogger(__name__)

    def _create_session(self) -> requests.Session:
        """Create a configured requests session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session

    def search(self, query: str) -> Optional[str]:
        """
        Search for news articles based on a query
        
        Args:
            query: The search query
            
        Returns:
            HTML content of the search results, or None if failed
        """
        params = {
            "q": query, 
            "hl": "en-US", 
            "gl": "US", 
            "ceid": "US:en"
        }
        url = f"{self.config.base_url}?{urlencode(params)}"
        
        for attempt in range(self.config.max_retries):
            try:
                # Add delay to be respectful to the server
                time.sleep(self.config.delay)
                
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                
                self.logger.info(f"Successfully scraped news for query: {query}")
                return response.text
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"All {self.config.max_retries} attempts failed for query: {query}")
                    return None
                time.sleep(self.config.delay * (attempt + 1))  # Exponential backoff
        
        return None

    def close(self) -> None:
        """Close the session"""
        self.session.close()
