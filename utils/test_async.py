#!/usr/bin/env python3
"""
Simple test script to verify async functionality
"""

import asyncio
import sys
import os

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.scrapers.async_scraper import AsyncGoogleNewsScraper
from src.scrapers.async_google_news_decoder import decode_google_news_url_async
from src.scrapers.async_article_processor import collect_news_async

async def test_async_functionality():
    """Test async functionality"""
    print("Testing async Google News search...")
    
    # Test Google News search
    scraper = AsyncGoogleNewsScraper()
    html_content = await scraper.search("Python programming")
    
    if html_content:
        print("[PASS] Google News search successful")
        print(f"  Content length: {len(html_content)} characters")
    else:
        print("[FAIL] Google News search failed")
        return
    
    # Test async news collection
    print("\nTesting async news collection...")
    articles = await collect_news_async("Python programming", limit=5)
    
    if articles:
        print("[PASS] Async news collection successful")
        print(f"  Articles collected: {len(articles)}")
        for i, article in enumerate(articles[:3]):  # Show first 3 articles
            print(f"  {i+1}. {article.get('title', 'N/A')[:50]}...")
    else:
        print("[FAIL] Async news collection failed")
    
    print("\nAsync functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_async_functionality())
