#!/usr/bin/env python3
"""
Command Line Interface for Google News Scraper
A CLI tool for collecting news articles from Google News.
"""

import sys
import os
import argparse
import asyncio
from typing import Optional

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.services.news_service import NewsService
from src.models.schemas import NewsSearchRequest
from src.common.logger import setup_logging, get_logger


async def collect_news(query: str, output_format: Optional[str] = None, max_results: Optional[int] = None) -> None:
    """
    Collect news for a specific query
    
    Args:
        query: Search query
        output_format: Output format (json or csv)
        max_results: Maximum number of results
    """
    logger = get_logger(__name__)
    
    try:
        # Create news service
        news_service = NewsService()
        
        # Create search request
        request = NewsSearchRequest(
            query=query,
            format=output_format or "json",
            max_results=max_results or 50
        )
        
        logger.info(f"Searching for news related to: {query}")
        
        # Search for news
        result = await news_service.search_news(request)
        
        # Print summary
        print(f"\n✅ Collected {result.total_results} articles for query: '{query}'")
        print(f"📄 Output format: {result.format}")
        print(f"📁 Output directory: data/")
        
        if result.articles:
            print(f"\n📰 Sample articles:")
            for i, article in enumerate(result.articles[:3], 1):
                print(f"  {i}. {article.title}")
                print(f"     {article.link}")
                print()
        
    except Exception as e:
        logger.error(f"Error collecting news: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Collect news articles from Google News",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli.news_cli "E20 Fuel"
  python -m src.cli.news_cli "artificial intelligence" --format csv --max-results 20
        """
    )
    
    parser.add_argument("query", help="The search query for news articles")
    parser.add_argument("--format", "-f", choices=['json', 'csv'], 
                        help="Output format (json or csv, default: json)")
    parser.add_argument("--max-results", "-m", type=int, 
                        help="Maximum number of results (default: 50)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Run the async function
    asyncio.run(collect_news(args.query, args.format, args.max_results))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  News collection interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
