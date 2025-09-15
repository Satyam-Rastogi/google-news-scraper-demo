#!/usr/bin/env python3
"""
Side-by-side comparison to demonstrate async vs sync concurrent processing
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import both sync and async versions
from src.scrapers.scraper import GoogleNewsScraper
from src.scrapers.async_scraper import AsyncGoogleNewsScraper

def sync_multiple_searches(queries):
    """Perform multiple searches synchronously (one after another)"""
    print("=== SYNC VERSION: Sequential Processing ===")
    scraper = GoogleNewsScraper()
    start_time = time.time()
    
    results = []
    for i, query in enumerate(queries):
        print(f"  Starting search {i+1}: '{query}'")
        start_search = time.time()
        result = scraper.search(query)
        end_search = time.time()
        duration = end_search - start_search
        print(f"  Completed search {i+1} in {duration:.2f} seconds")
        results.append(result is not None)
    
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"Sync version completed {len(queries)} searches in {total_duration:.2f} seconds")
    return total_duration

async def async_multiple_searches(queries):
    """Perform multiple searches asynchronously (concurrently)"""
    print("\n=== ASYNC VERSION: Concurrent Processing ===")
    scraper = AsyncGoogleNewsScraper()
    start_time = time.time()
    
    # Create tasks for concurrent execution
    print(f"  Starting all {len(queries)} searches simultaneously...")
    tasks = [scraper.search(query) for query in queries]
    
    # Wait for all searches to complete
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"Async version completed {len(queries)} searches in {total_duration:.2f} seconds")
    return total_duration

async def main():
    """Main function to demonstrate the difference"""
    print("ASYNC vs SYNC CONCURRENT PROCESSING COMPARISON")
    print("=" * 60)
    
    # Test queries
    queries = ["Python programming", "Machine learning", "Data science", "Artificial intelligence"]
    
    # Run sync version
    sync_time = sync_multiple_searches(queries)
    
    # Run async version
    async_time = await async_multiple_searches(queries)
    
    # Calculate improvement
    if sync_time > 0:
        improvement = ((sync_time - async_time) / sync_time) * 100
    else:
        improvement = 0
    
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"Sync version time:  {sync_time:.2f} seconds")
    print(f"Async version time: {async_time:.2f} seconds")
    print(f"Performance improvement: {improvement:.1f}%")
    print()
    print("KEY DIFFERENCES:")
    print("1. SYNC: Each search waits for the previous one to complete")
    print("2. ASYNC: All searches start at the same time and run concurrently")
    print("3. ASYNC: Better resource utilization (network, CPU)")
    print("4. ASYNC: Connection pooling reduces overhead")
    print()
    print("This is the 'async nature' you were looking for - concurrent execution!")

if __name__ == "__main__":
    asyncio.run(main())