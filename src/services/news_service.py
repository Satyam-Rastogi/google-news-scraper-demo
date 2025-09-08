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

    async def search_news(self, request: NewsSearchRequest) -> NewsSearchResponse:
        """
        Search for news articles based on the request
        
        Args:
            request: News search request
            
        Returns:
            News search response with articles
            
        Raises:
            ScrapingError: If scraping fails
            ParsingError: If parsing fails
        """
        try:
            self.logger.info(f"Searching for news with query: {request.query}")
            
            # Scrape HTML content
            html_content = self.scraper.search(request.query)
            if not html_content:
                raise ScrapingError(f"Failed to scrape news for query: {request.query}")
            
            # Parse articles
            articles_data = self.parser.parse(html_content)
            if not articles_data:
                raise ParsingError(f"No articles found for query: {request.query}")
            
            # Limit results
            max_results = min(request.max_results or config.default_max_results, 
                            config.max_results_limit)
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
            if request.format:
                await self._save_articles(articles_data, request.query, request.format)
            
            return NewsSearchResponse(
                query=request.query,
                total_results=len(articles),
                articles=articles,
                format=request.format or config.default_output_format
            )
            
        except Exception as e:
            self.logger.error(f"Error in news search: {e}")
            raise

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
