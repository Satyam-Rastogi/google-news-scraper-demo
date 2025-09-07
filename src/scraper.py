import requests
from urllib.parse import urlencode
import time
import logging
from typing import Optional

class GoogleNewsScraper:
    BASE_URL: str = "https://news.google.com/search"

    def __init__(self) -> None:
        # Set up a session with headers to mimic a real browser
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search(self, query: str) -> Optional[str]:
        """
        Search for news articles based on a query
        
        Args:
            query (str): The search query
            
        Returns:
            Optional[str]: HTML content of the search results, or None if failed
        """
        params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
        url = f"{self.BASE_URL}?{urlencode(params)}"
        
        try:
            # Add a small delay to be respectful to the server
            time.sleep(1)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except Exception as e:
            logging.error(f"Error during requests: {e}")
            return None