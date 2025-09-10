#!/usr/bin/env python3
"""
Unified News Collector CLI
A comprehensive command-line interface for collecting, processing, and scheduling news article collection.
"""

import sys
import os
import argparse
from datetime import datetime
import shutil
import logging
from typing import List, Optional

# Add the parent directory to the sys.path to allow imports from config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from src.scrapers.article_processor import collect_news
from config.config import Config
from src.utils.utils import setup_logging, setup_file_only_logging
from src.core.news_types import ArticleDict
from src.utils.validation import validate_string, validate_integer_range, validate_search_query
from src.core.scheduler import NewsScheduler

# Load configuration from file
try:
    Config.load_from_file()
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# Set up logging
logger = setup_logging(Config.LOG_LEVEL, log_to_console=True)

def get_terminal_width() -> int:
    """Get terminal width for formatting"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def print_header(title: str) -> None:
    """Print a formatted header"""
    width = get_terminal_width()
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def print_section_header(title: str) -> None:
    """Print a formatted section header"""
    width = get_terminal_width()
    print(f"\n{title}")
    print("-" * min(len(title), width))

def print_article_summary(index: int, article: ArticleDict) -> None:
    """Print a formatted article summary"""
    print(f"\n{index}. {article.get('title', 'N/A')}")
    
    # Print metadata
    snippet = article.get('snippet', 'N/A')
    if snippet and snippet != 'N/A':
        # Truncate snippet to fit terminal width
        width = get_terminal_width()
        max_snippet_length = width - 8  # Account for indentation
        if len(snippet) > max_snippet_length:
            snippet = snippet[:max_snippet_length-3] + "..."
        print(f"   Summary: {snippet}")
    
    # Print source and date
    source = article.get('source', 'N/A') if article.get('source') else 'N/A'
    published_time = article.get('published_time', 'N/A')
    if source != 'N/A' or published_time != 'N/A':
        source_info: List[str] = []
        if source != 'N/A':
            source_info.append(source)
        if published_time != 'N/A':
            source_info.append(published_time)
        if source_info:
            print(f"   Source: {' | '.join(source_info)}")
    
    # Print full content availability
    if 'full_content' in article:
        full_content = article['full_content']
        if isinstance(full_content, dict):
            print(f"   Full content: [Available]")
            if full_content.get('authors'):
                authors = ', '.join(full_content['authors'])
                print(f"   Authors: {authors}")
            if full_content.get('publish_date'):
                print(f"   Publish Date: {full_content['publish_date']}")
            if full_content.get('local_article_file'):
                print(f"   Saved to: {os.path.basename(full_content['local_article_file'])}")
        else:
            print(f"   Full content: [Not available]")

def display_articles_summary(articles: List[ArticleDict], query: str) -> None:
    """Display a formatted summary of articles"""
    if not articles:
        return
    
    print_section_header(f"Search Results for: '{query}'")
    print(f"Total articles found: {len(articles)}")
    
    # Display articles based on configuration
    display_count = min(10, len(articles))  # Show up to 10 articles
    
    if Config.SCRAPE_FULL_ARTICLES:
        display_count = min(Config.FULL_ARTICLES_COUNT, len(articles))
        logger.info(f"Full content scraped for top {display_count} articles")
    
    for i, article in enumerate(articles[:display_count]):
        print_article_summary(i+1, article)
    
    if len(articles) > display_count:
        remaining = len(articles) - display_count
        print(f"\n... and {remaining} more articles")
        print("(Check the saved files for complete results)")

def validate_queries(queries: List[str]) -> List[str]:
    """
    Validate a list of queries
    
    Args:
        queries (List[str]): List of queries to validate
        
    Returns:
        List[str]: List of validated queries
        
    Raises:
        ValueError: If any query is invalid
    """
    if not queries:
        raise ValueError("At least one query is required")
    
    validated_queries = []
    for i, query in enumerate(queries):
        try:
            validated_query = validate_search_query(query)
            validated_queries.append(validated_query)
        except ValueError as e:
            raise ValueError(f"Invalid query at position {i+1}: {str(e)}")
    
    return validated_queries

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
    except Exception as e:
        logger.error(f"Error collecting news for '{query}': {e}")
    
    return []

def collect_news_for_all_topics() -> None:
    """Task function to collect news for all configured topics"""
    logger.info("Starting scheduled news collection for all configured topics")
    
    for topic in Config.TOPICS:
        collect_news_task(topic)

def run_scheduler(query: Optional[str], interval_minutes: int, daily: bool, hour: int, minute: int) -> None:
    """
    Run the news collection scheduler
    
    Args:
        query: Specific query to collect news for (None for all configured topics)
        interval_minutes: Interval for periodic tasks
        daily: Whether to run daily instead of periodically
        hour: Hour for daily execution
        minute: Minute for daily execution
    """
    # Set up file-only logging for scheduler
    scheduler_logger = setup_file_only_logging(Config.LOG_LEVEL)
    
    # Determine which topics to collect news for
    if query:
        # Use provided query
        def task() -> None:
            collect_news_task(query)
    else:
        # Use all configured topics
        def task() -> None:
            collect_news_for_all_topics()
    
    # Set up scheduler
    scheduler = NewsScheduler()
    
    if daily:
        scheduler.schedule_daily_task(task, hour, minute)
    else:
        scheduler.schedule_task(task, interval_minutes)

def main_cli(queries: Optional[List[str]] = None, output_format: Optional[str] = None) -> None:
    """Main CLI function for interactive use"""
    # Validate queries
    try:
        validated_queries = validate_queries(queries or [])
    except ValueError as e:
        logger.error(f"Invalid queries: {e}")
        return
    
    width = get_terminal_width()
    print_header("NEWS COLLECTOR")
    print(f"{'Starting news collection process':^{width}}")
    
    # Collect news for each query
    all_articles: List[ArticleDict] = []
    for query in validated_queries:
        logger.info(f"\nProcessing query: '{query}'")
        articles: List[ArticleDict] = collect_news(query, output_format)
        display_articles_summary(articles, query)
        all_articles.extend(articles)
    
    # Print final summary
    print_header("COMPLETED")
    total_articles = len(all_articles)
    print(f"{'Final Summary':^{width}}")
    print(f"{'':^{width}}")
    print(f"{'Total Queries Processed:':<30} {len(validated_queries)}")
    print(f"{'Total Articles Collected:':<30} {total_articles}")
    if Config.SCRAPE_FULL_ARTICLES:
        full_articles = sum(1 for article in all_articles if 'full_content' in article)
        print(f"{'Full Articles Scraped:':<30} {full_articles}")
    print(f"{'Output Format:':<30} {output_format or Config.OUTPUT_FORMAT}")
    print(f"{'Output Directory:':<30} {Config.OUTPUT_DIR}")
    print(f"{'':^{width}}")
    print(f"{'News collection completed successfully!':^{width}}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect news articles from Google News with optional scheduling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive collection
  python news_collector.py "artificial intelligence"
  python news_collector.py "AI,ML,Data Science" --format csv
  python news_collector.py "climate change" --full-articles --full-count 5
  
  # Scheduled collection
  python news_collector.py "machine learning" --schedule --interval 30
  python news_collector.py --schedule --daily --hour 9 --minute 0
  python news_collector.py "technology" --schedule --daily --hour 10 --minute 30 --full-articles --full-count 2
        """
    )
    
    # Query arguments
    parser.add_argument("queries", nargs="*", help="The search query/queries for news articles (comma-separated for multiple)")
    
    # Output format arguments
    parser.add_argument("--format", "-f", choices=['json', 'csv'], 
                        help="Output format (json or csv)")
    
    # Full article scraping arguments
    parser.add_argument("--full-articles", action="store_true",
                        help="Enable full article scraping for top articles")
    parser.add_argument("--no-full-articles", action="store_false", dest="full_articles",
                        help="Disable full article scraping")
    parser.add_argument("--full-count", type=int, default=3,
                        help="Number of top articles to scrape fully (default: 3)")
    
    # Scheduling arguments
    parser.add_argument("--schedule", "-s", action="store_true",
                        help="Run as a scheduled task instead of one-time collection")
    parser.add_argument("--interval", "-i", type=int, default=Config.SCHEDULER_INTERVAL_MINUTES, 
                        help=f"Interval in minutes for periodic tasks (default: {Config.SCHEDULER_INTERVAL_MINUTES})")
    parser.add_argument("--daily", "-d", action="store_true",
                        help="Run daily instead of at intervals")
    parser.add_argument("--hour", type=int, default=Config.SCHEDULER_DAILY_HOUR,
                        help=f"Hour for daily run (0-23, default: {Config.SCHEDULER_DAILY_HOUR})")
    parser.add_argument("--minute", type=int, default=Config.SCHEDULER_DAILY_MINUTE,
                        help=f"Minute for daily run (0-59, default: {Config.SCHEDULER_DAILY_MINUTE})")
    
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
    if hasattr(args, 'full_articles') and args.full_articles:
        Config.SCRAPE_FULL_ARTICLES = True
    if args.full_count:
        Config.FULL_ARTICLES_COUNT = args.full_count
    if args.format:
        Config.OUTPUT_FORMAT = args.format
    
    # Handle both space-separated and comma-separated queries
    queries: List[str] = []
    if args.queries:
        for query in args.queries:
            # Split by comma if there are multiple queries in one argument
            queries.extend([q.strip() for q in query.split(',')])
    
    # Run as scheduler or one-time collection
    if args.schedule:
        # Scheduler mode
        query = queries[0] if queries else None
        run_scheduler(query, args.interval, args.daily, args.hour, args.minute)
    else:
        # One-time collection mode
        main_cli(queries, args.format)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("News collection interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
