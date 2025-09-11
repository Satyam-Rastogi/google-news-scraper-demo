"""
Google News URL decoder that combines the gnews library approach with our current implementation
"""

import logging
from typing import Optional

try:
    from googlenewsdecoder import gnewsdecoder
    GNEWS_DECODER_AVAILABLE = True
except ImportError:
    GNEWS_DECODER_AVAILABLE = False
    logging.warning("gnewsdecoder not available. Will use fallback URL resolution methods.")

from src.scrapers.url_resolver import resolve_google_news_url as fallback_resolver

logger = logging.getLogger(__name__)

def decode_google_news_url(google_news_url: str, use_fallback: bool = True) -> Optional[str]:
    """
    Decode a Google News URL to get the actual article URL using multiple approaches:
    1. Primary: gnewsdecoder library (more reliable)
    2. Fallback: Our current implementation using requests
    3. Secondary fallback: Selenium-based resolution
    
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
            result = gnewsdecoder(google_news_url, interval=1)
            
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
            resolved_url = fallback_resolver(google_news_url)
            
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

# Test function
if __name__ == "__main__":
    # Test with a sample URL
    test_url = "https://news.google.com/read/CBMi2AFBVV95cUxPd1ZCc1loODVVNHpnbFFTVHFkTG94eWh1NWhTeE9yT1RyNTRXMVV2S1VIUFM3ZlVkVjl6UHh3RkJ0bXdaTVRlcHBjMWFWTkhvZWVuM3pBMEtEdlllRDBveGdIUm9GUnJ4ajd1YWR5cWs3VFA5V2dsZnY1RDZhVDdORHRSSE9EalF2TndWdlh4bkJOWU5UMTdIV2RCc285Q2p3MFA4WnpodUNqN1RNREMwa3d5T2ZHS0JlX0MySGZLc01kWDNtUEkzemtkbWhTZXdQTmdfU1JJaXY?hl=en-US&gl=US&ceid=US%3Aen"
    
    print("Testing Google News URL decoder...")
    print(f"Input URL: {test_url}")
    
    try:
        decoded_url = decode_google_news_url(test_url)
        if decoded_url:
            print(f"Decoded URL: {decoded_url}")
        else:
            print("Failed to decode URL")
    except Exception as e:
        print(f"Error: {e}")
