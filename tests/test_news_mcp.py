#!/usr/bin/env python3
"""
Test script for News MCP Server
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.common.utils.news_helper import news_helper
from src.common.utils.logger import get_logger

logger = get_logger(__name__)

def test_news_search():
    """Test news search functionality"""
    print("Testing news search...")
    
    # Test search
    result = news_helper.search_news("artificial intelligence", max_results=3)
    
    if result.get("success"):
        articles = result["data"]["articles"]
        print(f"✅ Found {len(articles)} articles")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. {article.get('title', 'No title')}")
    else:
        print(f"❌ Search failed: {result.get('error')}")

def test_news_titles():
    """Test news titles functionality"""
    print("\nTesting news titles...")
    
    # Test titles
    result = news_helper.get_news_titles("technology", max_results=2)
    
    if result.get("success"):
        titles = result["data"]["titles"]
        print(f"✅ Found {len(titles)} titles")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title.get('title', 'No title')}")
    else:
        print(f"❌ Titles failed: {result.get('error')}")

def test_save_news():
    """Test save news functionality"""
    print("\nTesting save news...")
    
    # Sample articles
    sample_articles = [
        {"title": "Test Article 1", "link": "https://example.com/1", "snippet": "Test snippet 1"},
        {"title": "Test Article 2", "link": "https://example.com/2", "snippet": "Test snippet 2"}
    ]
    
    result = news_helper.save_news(sample_articles, "test_query", "json")
    
    if result.get("success"):
        print(f"✅ Saved articles to: {result['data']['filepath']}")
    else:
        print(f"❌ Save failed: {result.get('error')}")

if __name__ == "__main__":
    print("🧪 Testing News MCP Server Components")
    print("=" * 50)
    
    try:
        test_news_search()
        test_news_titles()
        test_save_news()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
