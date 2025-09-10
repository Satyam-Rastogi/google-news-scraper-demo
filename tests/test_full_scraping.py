#!/usr/bin/env python3
"""
Test script for full article scraping with improved URL decoding
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scrapers.full_article_scraper import FullArticleScraper
from src.scrapers.google_news_decoder import decode_google_news_url

def setup_test_logging():
    """Set up logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_url_decoding():
    """Test URL decoding with sample URLs from our CSV file"""
    # Sample Google News URLs from our CSV file
    test_urls = [
        "https://news.google.com/read/CBMitAFBVV95cUxQZW5WTzM2MmJxRlNxT0RMLUF4WVM1OXhiNlFhQ00wb1ZBMmRVamtrMVozMGswNmFvQVhWbzh5R0ZSUExJUjlBdXZ2SDdNeVRaQWdjQnNqSnVSNmJsRTZfNy03aU14WEZvQWdRT0NPY2FvRmNYdWppZkJETmRocTBxNHE3b2lkZkFSR1N6RGtEWEtWZ1dYQ3M5RG0wa2ZWVl9FZzVxd2Ruc3BmSHllallERGYzdlg?hl=en-US&gl=US&ceid=US%3Aen",
        "https://news.google.com/read/CBMi7AFBVV95cUxQOXlkMjM3RktIbXFoS0Mxc1djNVlfZ0hKd3Bsb3VaTlZBZGY2dEV3LWxGMEZTbXkyTlNlemdyV0FxOGVob0tpT0NqMVp0cE1BNDBhaEZEa2NwR2Uwa1piakZKZXctaUltU00zMVM3UEJ4MnQ0S1NoZ3NlZHZ2eFVXY044bHUyQVhURDBpSlpqMWpxNGhXMkNYNHVJcWhuS212Zi1CR1RyM21VTnFOR1M5RGJJM2xFX2oyNmVMNDdMZWhQc1VQVWdudUg1M0d1SDR6LUVhSk9UUHJHc1FzbVUwUmxBT0Q1TERIbUNRM9IB8gFBVV95cUxQejA1ZGg5MmFVSk9DTVRCdEwwOWh2azh5UnB0b29pc3o3NXJ4amxhOF9QdmswM0VmTlhjLVFYMVBMR1BVVVN2T01vLXBnYzFPS3V1bks0UVZTU2kwSmRIYUMyNGpteUE5SmRtdTZQS1hRZy15SGw0NEUxemo2MEZKU3I1UVJ5LU9kQ1g0Mkw4Wjd2MGdqQU9BRDV1VFAyNjBOYjQxQ2FYMTRFd0tRcE50UHRFd2VZNC1mOVVKNUQ2bXdUS2ZuVEs5LVFJeEVEREZ3NXZZUDE1QjdSbWJPMm5BM3dOQXk2Q3p2U1ZGNFRfVjVDQQ?hl=en-US&gl=US&ceid=US%3Aen"
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

def test_full_article_scraping():
    """Test full article scraping with sample URLs"""
    # Sample Google News URLs for testing
    test_urls = [
        "https://news.google.com/read/CBMi2AFBVV95cUxPd1ZCc1loODVVNHpnbFFTVHFkTG94eWh1NWhTeE9yT1RyNTRXMVV2S1VIUFM3ZlVkVjl6UHh3RkJ0bXdaTVRlcHBjMWFWTkhvZWVuM3pBMEtEdlllRDBveGdIUm9GUnJ4ajd1YWR5cWs3VFA5V2dsZnY1RDZhVDdORHRSSE9EalF2TndWdlh4bkJOWU5UMTdIV2RCc285Q2p3MFA4WnpodUNqN1RNREMwa3d5T2ZHS0JlX0MySGZLc01kWDNtUEkzemtkbWhTZXdQTmdfU1JJaXY?hl=en-US&gl=US&ceid=US%3Aen"
    ]
    
    print("\n\nTesting full article scraping with improved URL decoding...")
    print("=" * 60)
    
    # Initialize the scraper
    scraper = FullArticleScraper("data")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}:")
        print(f"Input URL: {url[:80]}...")
        
        try:
            # First test URL decoding
            decoded_url = decode_google_news_url(url)
            if decoded_url:
                print(f"Decoded URL: {decoded_url[:100]}...")
            else:
                print("FAILED: Could not decode URL")
                continue
                
            # Then test full article scraping
            print("Scraping full article...")
            article_data = scraper.scrape_full_article(url, f"Test Article {i}")
            
            if article_data:
                print("SUCCESS: Article scraped successfully")
                print(f"Title: {article_data.get('title', 'N/A')}")
                print(f"Text preview: {article_data.get('text', 'N/A')[:200]}...")
                print(f"Authors: {', '.join(article_data.get('authors', []))}")
            else:
                print("FAILED: Could not scrape full article")
                
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    setup_test_logging()
    test_url_decoding()
    test_full_article_scraping()
