"""
Simple URL resolver for Google News URLs

This module resolves Google News "read" URLs to get the actual article URLs
by following redirects.
"""
import requests
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

def resolve_google_news_url(google_news_url: str, timeout: int = 30) -> str:
    """
    Resolve a Google News URL to get the actual article URL by following redirects
    
    Args:
        google_news_url (str): The Google News URL to resolve
        timeout (int): Request timeout in seconds
        
    Returns:
        str: The resolved actual URL or the original URL if resolution fails
    """
    try:
        # Create a session with appropriate headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Make a HEAD request with redirect following disabled to get redirect info
        response = session.head(google_news_url, allow_redirects=False, timeout=timeout)
        
        # Follow redirects manually to get the final URL
        redirect_count = 0
        max_redirects = 10
        current_url = google_news_url
        
        while response.is_redirect or response.status_code in [301, 302, 303, 307, 308]:
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
                response = session.head(current_url, allow_redirects=False, timeout=timeout)
                redirect_count += 1
            except Exception as e:
                logger.warning(f"Error following redirect to {current_url}: {e}")
                # Try GET request as fallback
                try:
                    response = session.get(current_url, allow_redirects=False, timeout=timeout)
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
            response = requests.get(google_news_url, allow_redirects=True, timeout=timeout)
            final_url = response.url
            logger.info(f"Fallback resolved {google_news_url} to {final_url}")
            return final_url
        except Exception as e2:
            logger.error(f"Fallback also failed for {google_news_url}: {e2}")
            return google_news_url

# Test function
if __name__ == "__main__":
    # Test with a sample URL
    test_url = "https://news.google.com/read/CBMiiAFBVV95cUxQcWMwVk52M3ZZM3J1T2RpQktGaFpkYWRNa0Q1Y25lVTZOZVhvU3VOUWtybThDRVIzQklvamt4azZMTnkxTTVQRUpNWmlHTTVBTE1FLVE4YkFvU3lKTzJnNTROTkdhTmYzSTVvQnlUTF8yRTVyRkg1Q0UzaDV0ZkZMaTQyTTdneTBt0gGOAUFVX3lxTE1pNnlNZ19jcVp0anBqd0h5ajV5TThKSXo3UUV1b1Itd2hQUGtFWHVGckFkUVFtYTdOQldvek1NREc3Sm0taHVXSWRYYTVXR2hmMmI2eW5vRHlseFhrTlBvNkdJYXRURnJFMGtGbFpYdThQMm1YenQzTkFKaGE1dUgzUzBIRkdXOUgxX0hzaWc?hl=en-US&gl=US&ceid=US%3Aen"
    print("Testing URL resolution...")
    print(f"Input URL: {test_url}")
    try:
        resolved_url = resolve_google_news_url(test_url)
        print(f"Resolved URL: {resolved_url}")
    except Exception as e:
        print(f"Error: {e}")