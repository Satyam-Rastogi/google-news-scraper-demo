#!/usr/bin/env python3
"""
Integration test for the new Google News URL decoder with the main application
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scrapers.article_processor import collect_news
from config.config import Config

def setup_test_logging():
    """Set up logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_integration():
    """Test the integration of the new URL decoder with the main application"""
    print("Testing integration of new Google News URL decoder with main application...")
    print("=" * 80)
    
    # Configure for a simple test
    Config.SCRAPE_FULL_ARTICLES = True
    Config.FULL_ARTICLES_COUNT = 1
    Config.OUTPUT_FORMAT = "json"
    Config.OUTPUT_DIR = "data"
    
    # Use a simple query related to the articles in our CSV
    query = "E20 fuel"
    
    print(f"Collecting news for query: '{query}'")
    print("This will test both the URL decoding and full article scraping functionality.")
    
    try:
        # Collect news using our main function
        articles = collect_news(query, output_format="json")
        
        if articles:
            print(f"SUCCESS: Collected {len(articles)} articles")
            
            # Check if we have any articles with full content
            articles_with_full_content = [a for a in articles if 'full_content' in a]
            print(f"Articles with full content: {len(articles_with_full_content)}")
            
            # Display information about the first article
            if articles:
                first_article = articles[0]
                print(f"\nFirst article:")
                print(f"  Title: {first_article.get('title', 'N/A')}")
                print(f"  URL: {first_article.get('link', 'N/A')}")
                print(f"  Snippet: {first_article.get('snippet', 'N/A')[:100]}...")
                
                if 'full_content' in first_article:
                    full_content = first_article['full_content']
                    print(f"  Full content available: Yes")
                    print(f"  Full text preview: {full_content.get('text', 'N/A')[:100]}...")
                    print(f"  Authors: {', '.join(full_content.get('authors', []))}")
                else:
                    print(f"  Full content available: No")
        else:
            print("No articles collected")
            
    except Exception as e:
        print(f"ERROR: {e}")
        logging.exception("Error during integration test")

if __name__ == "__main__":
    setup_test_logging()
    test_integration()
