#!/usr/bin/env python3
"""
Benchmark script to compare sync and async versions
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import both sync and async versions
from src.scrapers.article_processor import collect_news
from src.scrapers.async_article_processor import collect_news_async

def benchmark_sync(query, limit=5):
    """Benchmark sync version"""
    print(f"Benchmarking sync version with query: '{query}'")
    start_time = time.time()
    
    articles = collect_news(query, limit=limit)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Sync version completed in {duration:.2f} seconds")
    print(f"Articles collected: {len(articles) if articles else 0}")
    
    return duration

async def benchmark_async(query, limit=5):
    """Benchmark async version"""
    print(f"Benchmarking async version with query: '{query}'")
    start_time = time.time()
    
    articles = await collect_news_async(query, limit=limit)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Async version completed in {duration:.2f} seconds")
    print(f"Articles collected: {len(articles) if articles else 0}")
    
    return duration

async def run_benchmark():
    """Run benchmark comparison"""
    query = "Python programming"
    limit = 5
    
    print("=" * 50)
    print("NEWS COLLECTOR BENCHMARK")
    print("=" * 50)
    
    # Benchmark sync version
    sync_duration = benchmark_sync(query, limit)
    
    print("-" * 50)
    
    # Benchmark async version
    async_duration = await benchmark_async(query, limit)
    
    print("-" * 50)
    
    # Compare results
    improvement = ((sync_duration - async_duration) / sync_duration) * 100
    print(f"Performance comparison:")
    print(f"  Sync duration:  {sync_duration:.2f} seconds")
    print(f"  Async duration: {async_duration:.2f} seconds")
    print(f"  Improvement:    {improvement:.1f}%")
    
    if improvement > 0:
        print("[PASS] Async version is faster")
    else:
        print("[INFO] No significant improvement (might be due to network conditions)")

if __name__ == "__main__":
    asyncio.run(run_benchmark())