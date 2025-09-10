#!/usr/bin/env python3
"""
Scheduler script for running news collection at fixed intervals
"""

import sys
import os
import argparse
import logging
from typing import List, Optional

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from src.core.scheduler import NewsScheduler
from src.scrapers.article_processor import collect_news
from config.config import Config
from src.utils.utils import setup_file_only_logging
from src.core.news_types import ArticleDict
from src.utils.validation import validate_string, validate_integer_range, validate_search_query

# Load configuration from file
try:
    Config.load_from_file()
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# Set up logging to file only (no console output to keep clean)
logger = setup_file_only_logging(Config.LOG_LEVEL)

def collect_news_task(query: str) -> List[ArticleDict]:
    """Task function to collect news for a specific query"""
    logger.info(f"Starting scheduled news collection for: {query}")
    
    try:
        # Validate query
        validated_query = validate_search_query(query)
        
        # Collect news using our unified function
        articles: List[ArticleDict] = collect_news(validated_query)
        
        if articles:
            logger.info(f"Collected {len(articles)} articles for '{validated_query}'")
        else:
            logger.warning(f"No articles found for '{validated_query}'")
            
        return articles
    except ValueError as e:
        logger.error(f"Invalid query '{query}': {e}")
        return []
    except Exception as e:
        logger.error(f"Error collecting news for '{query}': {e}")
    
    return []

def collect_news_for_all_topics() -> None:
    """Task function to collect news for all configured topics"""
    logger.info("Starting scheduled news collection for all configured topics")
    
    for topic in Config.TOPICS:
        collect_news_task(topic)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Schedule news collection tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/scheduler_main.py "artificial intelligence" --interval 30
  python src/scheduler_main.py "machine learning,data science" --daily --hour 9 --minute 0
  python src/scheduler_main.py --full-articles --full-count 5
        """
    )
    parser.add_argument("query", nargs="?", help="The search query for news articles (optional, uses config topics if not provided)")
    parser.add_argument("--interval", "-i", type=int, default=Config.SCHEDULER_INTERVAL_MINUTES, 
                        help=f"Interval in minutes (default: {Config.SCHEDULER_INTERVAL_MINUTES})")
    parser.add_argument("--daily", "-d", action="store_true",
                        help="Run daily instead of at intervals")
    parser.add_argument("--hour", type=int, default=Config.SCHEDULER_DAILY_HOUR,
                        help=f"Hour for daily run (0-23, default: {Config.SCHEDULER_DAILY_HOUR})")
    parser.add_argument("--minute", type=int, default=Config.SCHEDULER_DAILY_MINUTE,
                        help=f"Minute for daily run (0-59, default: {Config.SCHEDULER_DAILY_MINUTE})")
    parser.add_argument("--full-articles", action="store_true",
                        help="Enable full article scraping for top articles")
    parser.add_argument("--full-count", type=int, default=3,
                        help="Number of top articles to scrape fully (default: 3)")
    
    args = parser.parse_args()
    
    # Validate numeric arguments
    try:
        if args.hour is not None:
            args.hour = validate_integer_range(args.hour, "Hour", 0, 23)
        if args.minute is not None:
            args.minute = validate_integer_range(args.minute, "Minute", 0, 59)
        if args.interval is not None:
            args.interval = validate_integer_range(args.interval, "Interval", 1, 1440)
        if args.full_count is not None:
            args.full_count = validate_integer_range(args.full_count, "Full count", 1, 50)
    except ValueError as e:
        logger.error(f"Invalid argument: {e}")
        sys.exit(1)
    
    # Handle command-line arguments for full article scraping
    if args.full_articles:
        Config.SCRAPE_FULL_ARTICLES = True
    if args.full_count:
        Config.FULL_ARTICLES_COUNT = args.full_count
    
    # Determine which topics to collect news for
    if args.query:
        # Use provided query
        def task() -> None:
            collect_news_task(args.query)
    else:
        # Use all configured topics
        def task() -> None:
            collect_news_for_all_topics()
    
    # Set up scheduler
    scheduler = NewsScheduler()
    
    if args.daily:
        scheduler.schedule_daily_task(task, args.hour, args.minute)
    else:
        scheduler.schedule_task(task, args.interval)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unexpected error in scheduler: {e}")
        sys.exit(1)
