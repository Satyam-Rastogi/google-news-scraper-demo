#!/usr/bin/env python3
"""
News Service - Main service for news scraping operations
"""

from typing import List, Dict, Any, Optional
from services.google_news_scraper import GoogleNewsScraper
from services.news_parser import ArticleParser
from common.config.mcp_config import OUTPUT_DIR, DEFAULT_MAX_RESULTS
from common.utils.logger import get_logger
from common.utils.exceptions import (
    handle_exceptions,
    NewsScrapingError,
    NewsParsingError,
    NewsFileError,
    create_error_response,
    create_success_response
)

logger = get_logger(__name__)

class NewsService:
    """Main service class for news operations"""
    
    def __init__(self):
        """Initialize news service with scraper and parser"""
        self.scraper = GoogleNewsScraper()
        self.parser = ArticleParser()
    
    @handle_exceptions(default_return={"articles": [], "error": "Search failed"})
    def search_news(self, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> Dict[str, Any]:
        """
        Search for news articles based on a query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing articles and any error
        """
        logger.info(f"Searching for news with query: {query}")
        
        # Get HTML content from scraper
        html_content = self.scraper.search(query)
        
        if not html_content:
            raise NewsScrapingError("Failed to retrieve HTML content from Google News")
        
        # Parse articles
        articles = self.parser.parse(html_content)
        
        if not articles:
            raise NewsParsingError("No articles found or parsed successfully")
        
        # Limit results
        limited_articles = articles[:max_results]
        
        logger.info(f"Successfully retrieved {len(limited_articles)} articles")
        return create_success_response(
            data={"articles": limited_articles},
            message=f"Retrieved {len(limited_articles)} articles"
        )
    
    @handle_exceptions(default_return={"titles": [], "error": "Failed to get titles"})
    def get_news_titles(self, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> Dict[str, Any]:
        """
        Get only news titles for a query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing titles and any error
        """
        # Get full articles first
        result = self.search_news(query, max_results)
        
        if not result.get("success", False):
            raise NewsParsingError(result.get("error", "Failed to search news"))
        
        # Extract only titles
        titles = []
        for article in result["data"]["articles"]:
            titles.append({
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "snippet": article.get("snippet", "")
            })
        
        logger.info(f"Extracted {len(titles)} titles")
        return create_success_response(
            data={"titles": titles},
            message=f"Extracted {len(titles)} titles"
        )
    
    @handle_exceptions(default_return={"success": False, "filepath": None, "error": "Save failed"})
    def save_news(self, articles: List[Dict], query: str, format_type: str = "json") -> Dict[str, Any]:
        """
        Save news articles to file
        
        Args:
            articles: List of article dictionaries
            query: Search query for naming files
            format_type: Output format (json or csv)
            
        Returns:
            Dict containing save status and any error
        """
        if not articles:
            raise NewsFileError("No articles to save")
        
        if format_type not in ['json', 'csv']:
            raise NewsFileError(f"Unsupported format: {format_type}")
        
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Create filename based on query and timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = query.replace(' ', '_')
        filename = f"{safe_query}_{timestamp}.{format_type}"
        filepath = OUTPUT_DIR / filename
        
        if format_type == 'json':
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        else:  # csv
            import csv
            fieldnames = ['title', 'link', 'snippet']
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(articles)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return create_success_response(
            data={"filepath": str(filepath)},
            message=f"Saved {len(articles)} articles to {filepath}"
        )

# Create a default service instance
news_service = NewsService()
