#!/usr/bin/env python3
"""
Test script for the new Google News URL decoder
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scrapers.google_news_decoder import decode_google_news_url

def setup_test_logging():
    """Set up logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_url_decoding():
    """Test URL decoding with sample URLs"""
    # Sample Google News URLs for testing
    test_urls = [
        "https://news.google.com/read/CBMi2AFBVV95cUxPd1ZCc1loODVVNHpnbFFTVHFkTG94eWh1NWhTeE9yT1RyNTRXMVV2S1VIUFM3ZlVkVjl6UHh3RkJ0bXdaTVRlcHBjMWFWTkhvZWVuM3pBMEtEdlllRDBveGdIUm9GUnJ4ajd1YWR5cWs3VFA5V2dsZnY1RDZhVDdORHRSSE9EalF2TndWdlh4bkJOWU5UMTdIV2RCc285Q2p3MFA4WnpodUNqN1RNREMwa3d5T2ZHS0JlX0MySGZLc01kWDNtUEkzemtkbWhTZXdQTmdfU1JJaXY?hl=en-US&gl=US&ceid=US%3Aen",
        "https://news.google.com/read/CBMilgFBVV95cUxOM0JJaFRwV2dqRDk5dEFpWmF1cC1IVml5WmVtbHZBRXBjZHBfaUsyalRpa1I3a2lKM1ZnZUI4MHhPU2sydi1nX3JrYU0xWjhLaHNfU0N6cEhOYVE2TEptRnRoZGVTU3kzZGJNQzc2aDZqYjJOR0xleTdsemdRVnJGLTVYTEhzWGw4Z19lR3AwR0F1bXlyZ0HSAYwBQVVfeXFMTXlLRDRJUFN5WHg3ZTI0X1F4SjN6bmFIck1IaGxFVVZyOFQxdk1JT3JUbl91SEhsU0NpQzkzRFdHSEtjVGhJNzY4ZTl6eXhESUQ3XzdWVTBGOGgwSmlXaVRmU3BsQlhPVjV4VWxET3FQVzJNbm5CUDlUOHJUTExaME5YbjZCX1NqOU9Ta3U?hl=en-US&gl=US&ceid=US%3Aen",
        "https://news.google.com/read/CBMiiAFBVV95cUxQOXZLdC1hSzFqQVVLWGJVZzlPaDYyNjdWTURScV9BbVp0SWhFNzZpSWZxSzdhc0tKbVlHMU13NmZVOFdidFFkajZPTm9SRnlZMWFRZ01CVHh0dXU0TjNVMUxZNk9Ibk5DV3hrYlRiZ20zYkIzSFhMQVVpcTFPc00xQjhhcGV1aXM00gF_QVVfeXFMTmtFQXMwMlY1el9WY0VRWEh5YkxXbHF0SjFLQVByNk1xS3hpdnBuUDVxOGZCQXl1QVFXaUVpbk5lUGgwRVVVT25tZlVUVWZqQzc4cm5MSVlfYmVlclFTOUFmTHF4eTlfemhTa2JKeG14bmNabENkSmZaeHB4WnZ5dw?hl=en-US&gl=US&ceid=US%3Aen"
    ]
    
    print("Testing Google News URL decoder...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}:")
        print(f"Input URL: {url[:80]}...")
        
        try:
            decoded_url = decode_google_news_url(url)
            if decoded_url:
                print(f"SUCCESS: {decoded_url[:100]}...")
            else:
                print("FAILED: Could not decode URL")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    setup_test_logging()
    test_url_decoding()
