#!/usr/bin/env python3
"""
Demonstrate concurrent full article scraping
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import both sync and async article processors
from src.scrapers.article_processor import collect_full_articles
from src.scrapers.async_article_processor import collect_full_articles_async

def create_sample_articles():
    """Create sample articles for testing"""
    return [
        {
            'title': 'Python Programming Basics',
            'link': 'https://news.google.com/read/CBMifEFVX3lxTE4tS0RQdHlWakhZWGVwY1BrYkpMUWZnQnp1OFE0WEdkSUJoQXB5anpnTUl...',
            'snippet': 'Learn the basics of Python programming',
            'serial_number': 1
        },
        {
            'title': 'Machine Learning Fundamentals',
            'link': 'https://news.google.com/read/CBMihwFBVV95cUxPMVl2OF95UjQzZjlTRFhMSVBwaXBraHlzQnJqN0FJdEEtSE5ESURubTR...',
            'snippet': 'Introduction to machine learning concepts',
            'serial_number': 2
        },
        {
            'title': 'Data Science Techniques',
            'link': 'https://news.google.com/read/CBMijAFBVV95cUxNVVJpMTNxYmZ2WDVpSTFrLU9sV1kyd0lSM0o0aUJEbktTZzZSVU5tZHB...',
            'snippet': 'Advanced data science methodologies',
            'serial_number': 3
        }
    ]

def sync_full_article_processing(articles):
    """Process full articles synchronously"""
    print("=== SYNC VERSION: Sequential Full Article Processing ===")
    start_time = time.time()
    
    # Process articles one by one
    processed_articles = []
    for i, article in enumerate(articles):
        print(f"  Starting processing of article {i+1}: '{article['title']}'")
        start_process = time.time()
        # In a real scenario, this would actually process the article
        # For demo purposes, we'll just simulate the processing time
        time.sleep(0.5)  # Simulate processing time
        end_process = time.time()
        duration = end_process - start_process
        print(f"  Completed processing article {i+1} in {duration:.2f} seconds")
        processed_articles.append(article)
    
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"Sync version completed processing {len(articles)} articles in {total_duration:.2f} seconds")
    return total_duration

async def async_full_article_processing(articles):
    """Process full articles asynchronously"""
    print("\n=== ASYNC VERSION: Concurrent Full Article Processing ===")
    start_time = time.time()
    
    async def process_article(article, index):
        """Process a single article asynchronously"""
        print(f"  Starting processing of article {index+1}: '{article['title']}'")
        start_process = time.time()
        # Simulate processing time
        await asyncio.sleep(0.5)
        end_process = time.time()
        duration = end_process - start_process
        print(f"  Completed processing article {index+1} in {duration:.2f} seconds")
        return article
    
    # Create tasks for concurrent execution
    print(f"  Starting processing of all {len(articles)} articles simultaneously...")
    tasks = [process_article(article, i) for i, article in enumerate(articles)]
    
    # Wait for all articles to be processed
    processed_articles = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"Async version completed processing {len(articles)} articles in {total_duration:.2f} seconds")
    return total_duration

async def main():
    """Main function to demonstrate full article processing"""
    print("ASYNC vs SYNC FULL ARTICLE PROCESSING COMPARISON")
    print("=" * 60)
    
    # Create sample articles
    articles = create_sample_articles()
    
    # Run sync version
    sync_time = sync_full_article_processing(articles)
    
    # Run async version
    async_time = await async_full_article_processing(articles)
    
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
    print("THE 'ASYNC NATURE' IN ACTION:")
    print("1. SYNC: Article 2 starts ONLY after Article 1 completes")
    print("2. ASYNC: All articles start processing at the same time")
    print("3. ASYNC: Articles process in parallel, not sequentially")
    print("4. ASYNC: Better utilization of system resources")
    print()
    print("This demonstrates concurrent execution - the core of async processing!")

if __name__ == "__main__":
    asyncio.run(main())