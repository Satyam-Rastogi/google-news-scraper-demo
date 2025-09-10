#!/usr/bin/env python3
"""
Test script for verifying scheduled news collection with full article extraction
"""

import sys
import os
import logging
from datetime import datetime
from typing import List, Optional

# Add the parent directory to the sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from config.config import Config
from src.core.scheduler import NewsScheduler
from src.scrapers.scraper import GoogleNewsScraper
from src.scrapers.parser import ArticleParser
from src.scrapers.full_article_scraper import FullArticleScraper
from src.utils.utils import setup_logging
from src.core.news_types import ArticleDict, FullArticleDict

# Load configuration from file
Config.load_from_file()

# Set up logging to both file and console
logger = setup_logging(Config.LOG_LEVEL)

def test_scheduled_collection() -> bool:
    """Test function to verify scheduled collection works correctly"""
    print("=== SCHEDULED NEWS COLLECTION TEST ===")
    print(f"Test started at: {datetime.now().isoformat()}")
    print(f"Topics to collect: {Config.TOPICS}")
    print(f"Full article scraping enabled: {Config.SCRAPE_FULL_ARTICLES}")
    print(f"Full articles count: {Config.FULL_ARTICLES_COUNT}")
    print("=" * 50)
    
    logger.info("=== SCHEDULED NEWS COLLECTION TEST ===")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    logger.info(f"Topics to collect: {Config.TOPICS}")
    logger.info(f"Full article scraping enabled: {Config.SCRAPE_FULL_ARTICLES}")
    logger.info(f"Full articles count: {Config.FULL_ARTICLES_COUNT}")
    logger.info("=" * 50)
    
    try:
        # Test with the first configured topic
        if Config.TOPICS:
            topic = Config.TOPICS[0]
            print(f"Testing collection for topic: {topic}")
            logger.info(f"Testing collection for topic: {topic}")
            
            # Initialize components
            scraper = GoogleNewsScraper()
            parser = ArticleParser()
            
            # Search for news
            print(f"Searching for news related to: {topic}")
            logger.info(f"Searching for news related to: {topic}")
            html_content: Optional[str] = scraper.search(topic)
            
            if html_content:
                # Parse results
                print("Parsing search results...")
                logger.info("Parsing search results...")
                articles: List[ArticleDict] = parser.parse(html_content)
                
                if articles:
                    print(f"Found {len(articles)} articles.")
                    logger.info(f"Found {len(articles)} articles.")
                    
                    # Test full article scraping if enabled
                    if Config.SCRAPE_FULL_ARTICLES:
                        print(f"Scraping full content for top {Config.FULL_ARTICLES_COUNT} articles...")
                        logger.info(f"Scraping full content for top {Config.FULL_ARTICLES_COUNT} articles...")
                        full_scraper = FullArticleScraper(Config.OUTPUT_DIR)
                        
                        success_count = 0
                        for i, article in enumerate(articles[:Config.FULL_ARTICLES_COUNT]):
                            try:
                                print(f"Processing article {i+1}: {article['title'][:50]}...")
                                logger.info(f"Processing article {i+1}: {article['title'][:50]}...")
                                full_data: Optional[FullArticleDict] = full_scraper.scrape_full_article(article['link'], article['title'])
                                
                                if full_data:
                                    print(f"✅ Successfully scraped full content for article {i+1}")
                                    logger.info(f"✅ Successfully scraped full content for article {i+1}")
                                    success_count += 1
                                else:
                                    print(f"⚠️ Failed to scrape full content for article {i+1}")
                                    logger.warning(f"⚠️ Failed to scrape full content for article {i+1}")
                                    
                            except Exception as e:
                                print(f"❌ Error scraping full content for article {i+1}: {e}")
                                logger.error(f"❌ Error scraping full content for article {i+1}: {e}")
                                continue
                        
                        print(f"Full article scraping completed. Success: {success_count}/{Config.FULL_ARTICLES_COUNT}")
                        logger.info(f"Full article scraping completed. Success: {success_count}/{Config.FULL_ARTICLES_COUNT}")
                    else:
                        print("Full article scraping is disabled in configuration.")
                        logger.info("Full article scraping is disabled in configuration.")
                else:
                    print("No articles found or parsed.")
                    logger.warning("No articles found or parsed.")
            else:
                print("Failed to retrieve HTML content.")
                logger.error("Failed to retrieve HTML content.")
        else:
            print("No topics configured for testing.")
            logger.error("No topics configured for testing.")
            
    except Exception as e:
        print(f"Error in scheduled collection test: {e}")
        logger.error(f"Error in scheduled collection test: {e}")
        return False
    
    print("=" * 50)
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=== END SCHEDULED NEWS COLLECTION TEST ===")
    
    logger.info("=" * 50)
    logger.info(f"Test completed at: {datetime.now().isoformat()}")
    logger.info("=== END SCHEDULED NEWS COLLECTION TEST ===")
    return True

def main() -> bool:
    """Main function for testing scheduled collection"""
    print("Starting scheduled news collection test...")
    logger.info("Starting scheduled news collection test...")
    
    # Run the test
    success = test_scheduled_collection()
    
    if success:
        print("Scheduled news collection test completed successfully!")
        logger.info("Scheduled news collection test completed successfully!")
    else:
        print("Scheduled news collection test failed!")
        logger.error("Scheduled news collection test failed!")
    
    return success

if __name__ == "__main__":
    main()
