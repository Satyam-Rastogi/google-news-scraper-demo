"""
News Service
Business logic for news scraping and processing
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from ..core.scraper import GoogleNewsScraper, ScrapingConfig
from ..core.parser import ArticleParser, ParsingConfig
from ..models.schemas import Article, NewsSearchRequest, NewsSearchResponse
from ..common.config import config
from ..common.exceptions import ScrapingError, ParsingError
from ..common.logger import get_logger
from ..common.utils.artifacts import artifacts_manager, ArtifactType


class NewsService:
    """Service for handling news scraping operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.scraper = GoogleNewsScraper(ScrapingConfig(
            timeout=config.request_timeout,
            delay=config.request_delay
        ))
        self.parser = ArticleParser(ParsingConfig(
            max_articles=config.max_results_limit
        ))
        self.artifacts = artifacts_manager

    # Legacy synchronous method - commented out, use Celery tasks instead
    """
    async def search_news(self, request: NewsSearchRequest) -> NewsSearchResponse:
        # This method is replaced by Celery async tasks
        # Use scrape_news_async task instead
        pass
    """

    async def _save_articles(self, articles: List[Dict], query: str, format_type: str) -> None:
        """
        Save articles to file using artifacts manager
        
        Args:
            articles: List of article dictionaries
            query: Search query for filename
            format_type: Output format (json or csv)
        """
        try:
            # Save to scraped data directory
            file_path = self.artifacts.save_artifact(
                data=articles,
                query=query,
                format_type=format_type,
                artifact_type="scraped"
            )
            
            self.logger.info(f"Saved {len(articles)} articles to {file_path}")
            
            # Also save a copy to exports directory for easy access
            export_path = self.artifacts.save_artifact(
                data=articles,
                query=query,
                format_type=format_type,
                artifact_type="exports"
            )
            
            self.logger.info(f"Saved export copy to {export_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving articles: {e}")
            # Don't raise exception as this is not critical

    def get_health_status(self) -> Dict[str, str]:
        """
        Get service health status
        
        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "service": "news-scraper",
            "version": config.api_version
        }
    
    def list_scraped_articles(self, format_type: Optional[str] = None) -> List[Path]:
        """
        List scraped articles
        
        Args:
            format_type: Optional format filter (json, csv)
            
        Returns:
            List of scraped article file paths
        """
        return self.artifacts.list_artifacts("scraped", format_type)
    
    def cleanup_old_articles(self, days_to_keep: int = 30) -> int:
        """
        Clean up old scraped articles
        
        Args:
            days_to_keep: Number of days to keep articles
            
        Returns:
            Number of files removed
        """
        return self.artifacts.cleanup_old_artifacts("scraped", days_to_keep)
    
    def get_artifacts_stats(self) -> Dict[str, any]:
        """
        Get artifacts statistics
        
        Returns:
            Dictionary with artifacts statistics
        """
        stats = {}
        
        for artifact_type in ["scraped", "processed", "raw"]:
            files = self.artifacts.list_artifacts(artifact_type)
            stats[artifact_type] = {
                "count": len(files),
                "total_size": sum(f.stat().st_size for f in files if f.exists()),
                "latest_file": files[0] if files else None
            }
        
        return stats
    
    async def scrape_news_async(
        self,
        query: str,
        max_results: int = None,
        format_type: str = None,
        language: str = None,
        country: str = None,
        time_period: str = None
    ) -> Dict:
        """
        Asynchronously scrape news articles (for Celery tasks)
        
        Args:
            query: Search query
            max_results: Maximum number of results (uses config default if None)
            format_type: Output format (uses config default if None)
            language: Language code (uses config default if None)
            country: Country code (uses config default if None)
            time_period: Time period for search (uses config default if None)
        
        Returns:
            Dict with articles and metadata
        """
        try:
            # Use config defaults if not provided
            max_results = max_results or config.default_max_results
            format_type = format_type or config.default_format_type
            language = language or config.default_language
            country = country or config.default_country
            time_period = time_period or config.default_time_period
            
            self.logger.info(f"Starting async news scraping for query: {query}")
            
            # Scrape HTML content
            html_content = self.scraper.search(query)
            if not html_content:
                raise ScrapingError(f"Failed to scrape news for query: {query}")
            
            # Parse articles
            articles_data = self.parser.parse(html_content)
            if not articles_data:
                raise ParsingError(f"No articles found for query: {query}")
            
            # Limit results
            max_results = min(max_results, config.max_results_limit)
            articles_data = articles_data[:max_results]
            
            # Convert to Article models
            articles = [
                Article(
                    title=article['title'],
                    link=article['link'],
                    snippet=article['snippet']
                )
                for article in articles_data
            ]
            
            # Save to file if requested
            if format_type:
                await self._save_articles(articles_data, query, format_type)
            
            # Convert to dict format for return
            articles_dict = [article.dict() for article in articles]
            
            return {
                "articles": articles_dict,
                "total_count": len(articles),
                "query": query,
                "language": language,
                "country": country,
                "time_period": time_period,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Async news scraping failed: {e}")
            raise
    
    async def scrape_multiple_queries_async(
        self,
        queries: List[str],
        max_results: int = None,
        format_type: str = None,
        language: str = None,
        country: str = None,
        time_period: str = None
    ) -> Dict[str, Dict]:
        """
        Asynchronously scrape news for multiple queries
        
        Args:
            queries: List of search queries
            max_results: Maximum number of results per query (uses config default if None)
            format_type: Output format (uses config default if None)
            language: Language code (uses config default if None)
            country: Country code (uses config default if None)
            time_period: Time period for search (uses config default if None)
        
        Returns:
            Dict with results for each query
        """
        results = {}
        
        for query in queries:
            try:
                result = await self.scrape_news_async(
                    query=query,
                    max_results=max_results,
                    format_type=format_type,
                    language=language,
                    country=country,
                    time_period=time_period
                )
                results[query] = result
                
            except Exception as e:
                self.logger.error(f"Failed to scrape query '{query}': {e}")
                results[query] = {
                    "error": str(e),
                    "articles": [],
                    "total_count": 0
                }
        
        return results
    
    async def export_articles_async(
        self,
        articles: List[Dict],
        query: str,
        format_type: str = None
    ) -> Dict:
        """
        Asynchronously export articles to specified format
        
        Args:
            articles: List of article dictionaries
            query: Search query for naming
            format_type: Export format (uses config default if None)
        
        Returns:
            Dict with export result and file path
        """
        try:
            # Use config default if not provided
            format_type = format_type or config.default_format_type
            
            self.logger.info(f"Starting async export for query: {query}")
            
            # Save to artifacts
            file_path = self.artifacts.save_artifact(
                data=articles,
                query=query,
                format_type=format_type,
                artifact_type="exports"
            )
            
            return {
                "file_path": str(file_path),
                "articles_count": len(articles),
                "format_type": format_type,
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Async export failed: {e}")
            raise
