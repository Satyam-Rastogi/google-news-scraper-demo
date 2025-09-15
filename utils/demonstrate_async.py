#!/usr/bin/env python3
"""
Test script to clearly demonstrate async concurrent processing
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.scrapers.async_scraper import AsyncGoogleNewsScraper
from src.scrapers.async_google_news_decoder import decode_google_news_url_async

async def demonstrate_concurrent_search():
    """Demonstrate concurrent Google News searches"""
    print("=== Demonstrating Concurrent Google News Searches ===")
    
    scraper = AsyncGoogleNewsScraper()
    
    # Start time
    start_time = time.time()
    
    # Run multiple searches concurrently
    queries = ["Python programming", "Machine learning", "Data science"]
    tasks = [scraper.search(query) for query in queries]
    
    # Wait for all searches to complete
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Completed {len(queries)} searches concurrently in {duration:.2f} seconds")
    
    for i, (query, result) in enumerate(zip(queries, results)):
        if result:
            print(f"  Search {i+1} ('{query}'): Success ({len(result)} characters)")
        else:
            print(f"  Search {i+1} ('{query}'): Failed")
    
    return duration

async def demonstrate_concurrent_decoding():
    """Demonstrate concurrent URL decoding"""
    print("\n=== Demonstrating Concurrent URL Decoding ===")
    
    # Sample Google News URLs (these are real URLs from our previous tests)
    urls = [
        "https://news.google.com/read/CBMifEFVX3lxTE4tS0RQdHlWakhZWGVwY1BrYkpMUWZnQnp1OFE0WEdkSUJoQXB5anpnTUl...",
        "https://news.google.com/read/CBMihwFBVV95cUxPMVl2OF95UjQzZjlTRFhMSVBwaXBraHlzQnJqN0FJdEEtSE5ESURubTR...",
        "https://news.google.com/read/CBMijAFBVV95cUxNVVJpMTNxYmZ2WDVpSTFrLU9sV1kyd0lSM0o0aUJEbktTZzZSVU5tZHB..."
    ]
    
    # Truncate URLs for display (they're very long)
    display_urls = [url[:80] + "..." for url in urls]
    
    start_time = time.time()
    
    # Run multiple decodings concurrently
    tasks = [decode_google_news_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Completed {len(urls)} URL decodings concurrently in {duration:.2f} seconds")
    
    for i, (url, result) in enumerate(zip(display_urls, results)):
        if result:
            print(f"  Decode {i+1}: Success -> {result[:80]}...")
        else:
            print(f"  Decode {i+1}: Failed")
    
    return duration

async def main():
    """Main function to demonstrate async concurrent processing"""
    print("ASYNC CONCURRENT PROCESSING DEMONSTRATION")
    print("=" * 50)
    
    # Demonstrate concurrent searches
    search_time = await demonstrate_concurrent_search()
    
    # Demonstrate concurrent decoding
    decode_time = await demonstrate_concurrent_decoding()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Concurrent searches completed in: {search_time:.2f} seconds")
    print(f"Concurrent decoding completed in: {decode_time:.2f} seconds")
    print("\nThe async implementation processes multiple operations simultaneously,")
    print("rather than waiting for each operation to complete before starting the next.")

if __name__ == "__main__":
    asyncio.run(main())