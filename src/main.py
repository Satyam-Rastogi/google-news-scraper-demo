#!/usr/bin/env python3
"""
Simplified News Collector CLI
A basic command-line interface for collecting news articles from Google News.
"""

import sys
import os
import argparse
import logging
from datetime import datetime
import json
import csv
from typing import List, Optional

# Add the parent directory to the sys.path to allow imports from config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from src.scraper import GoogleNewsScraper
from src.parser import ArticleParser
from config.config import Config

# Load configuration from file
try:
    Config.load_from_file()
except ValueError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

def save_articles(articles: List[dict], query: str, format_type: str) -> None:
    """
    Save articles to a file in the specified format
    
    Args:
        articles (List[dict]): List of article dictionaries
        query (str): Search query used for naming files
        format_type (str): Output format (json or csv)
    """
    # Create output directory if it doesn't exist
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    # Create a filename based on the query and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(' ', '_')
    
    if format_type == 'json':
        filename = f"{safe_query}_{timestamp}.json"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        # Only include basic fields in the output
        basic_articles = []
        for article in articles:
            basic_article = {
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'snippet': article.get('snippet', '')
            }
            basic_articles.append(basic_article)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(basic_articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(basic_articles)} articles to {filepath}")
        
    elif format_type == 'csv':
        filename = f"{safe_query}_{timestamp}.csv"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        if articles:
            # Only include basic fields in the output
            basic_articles = []
            for article in articles:
                basic_article = {
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'snippet': article.get('snippet', '')
                }
                basic_articles.append(basic_article)
            
            fieldnames = ['title', 'link', 'snippet']
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(basic_articles)
            
            logger.info(f"Saved {len(basic_articles)} articles to {filepath}")

def collect_news(query: str, output_format: Optional[str] = None) -> List[dict]:
    """
    Collect news for a specific query without full article scraping
    
    Args:
        query (str): Search query
        output_format (Optional[str]): Output format (json or csv)
        
    Returns:
        List[dict]: List of collected articles
    """
    scraper = GoogleNewsScraper()
    parser = ArticleParser()

    logger.info(f"Searching for news related to: {query}")
    html_content = scraper.search(query)

    if html_content:
        logger.info("Parsing search results...")
        articles = parser.parse(html_content)
        if articles:
            logger.info(f"Found {len(articles)} articles.")
            
            # Save articles to file
            format_type = output_format or Config.OUTPUT_FORMAT
            save_articles(articles, query, format_type)
            
            return articles
        else:
            logger.warning("No articles found or parsed.")
    else:
        logger.error("Failed to retrieve HTML content.")
    
    return []

def main():
    parser = argparse.ArgumentParser(
        description="Collect news articles from Google News",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python news_collector.py "E20 Fuel"
  python news_collector.py "artificial intelligence" --format csv
        """
    )
    
    parser.add_argument("query", help="The search query for news articles")
    parser.add_argument("--format", "-f", choices=['json', 'csv'], 
                        help="Output format (json or csv)")
    
    args = parser.parse_args()
    
    # Use provided output format or default from config
    format_type = args.format or Config.OUTPUT_FORMAT
    
    # Collect news
    articles = collect_news(args.query, format_type)
    
    # Print summary
    print(f"\nCollected {len(articles)} articles for query: '{args.query}'")
    print(f"Output format: {format_type}")
    print(f"Output directory: {Config.OUTPUT_DIR}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("News collection interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)