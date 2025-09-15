"""
Async HTTP client with connection pooling for the news collector
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
from config.config import Config

class AsyncHTTPClient:
    """Async HTTP client with connection pooling"""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 30) -> None:
        """
        Initialize the async HTTP client with connection pooling
        
        Args:
            max_connections: Maximum number of simultaneous connections
            max_connections_per_host: Maximum connections per host
        """
        self.logger = logging.getLogger(__name__)
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self) -> 'AsyncHTTPClient':
        """Async context manager entry"""
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_connections_per_host,
            ttl_dns_cache=300,  # DNS cache TTL
            keepalive_timeout=30,  # Keep-alive timeout
            enable_cleanup_closed=True  # Enable cleanup of closed connections
        )
        
        # Create session with connector and default headers
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30, connect=10),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def get(self, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """
        Make an async GET request
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            aiohttp.ClientResponse or None if failed
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
            
        try:
            response = await self.session.get(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Error making GET request to {url}: {e}")
            return None
            
    async def head(self, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """
        Make an async HEAD request
        
        Args:
            url: URL to request
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            aiohttp.ClientResponse or None if failed
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
            
        try:
            response = await self.session.head(url, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"Error making HEAD request to {url}: {e}")
            return None

# Global instance for the application
async_http_client: Optional[AsyncHTTPClient] = None

async def get_global_async_http_client() -> AsyncHTTPClient:
    """
    Get or create a global async HTTP client instance
    
    Returns:
        AsyncHTTPClient: Global async HTTP client instance
    """
    global async_http_client
    
    if async_http_client is None:
        async_http_client = AsyncHTTPClient(
            max_connections=Config.CONCURRENT_REQUESTS_LIMIT,
            max_connections_per_host=Config.CONCURRENT_REQUESTS_PER_HOST
        )
        # Initialize the session
        await async_http_client.__aenter__()
        
    return async_http_client

async def close_global_async_http_client() -> None:
    """Close the global async HTTP client instance"""
    global async_http_client
    
    if async_http_client is not None:
        await async_http_client.__aexit__(None, None, None)
        async_http_client = None