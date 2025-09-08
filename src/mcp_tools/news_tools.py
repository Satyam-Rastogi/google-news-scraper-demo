#!/usr/bin/env python3
"""
News MCP Tools - MCP tool definitions for news scraping
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.common.utils.news_helper import news_helper
from src.common.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------------------------------------------
# News Search Tool
# -------------------------------------------------------------------------

class NewsSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for news articles")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class NewsSearchResponse(BaseModel):
    articles: List[Dict[str, Any]]
    error: Optional[str] = None

def search_news(request: NewsSearchRequest) -> NewsSearchResponse:
    """
    Search for news articles based on a query
    
    Args:
        request: Contains the search query and max results
        
    Returns:
        List of news articles with title, link, and snippet
    """
    try:
        logger.info(f"Searching news with query: {request.query}")
        
        result = news_helper.search_news(
            query=request.query,
            max_results=request.max_results
        )
        
        if not result.get("success", False):
            logger.error(result.get("error", "Unknown error"))
            return NewsSearchResponse(
                articles=[],
                error=result.get("error", "Search failed")
            )
        
        articles = result["data"]["articles"]
        logger.info(f"Successfully retrieved {len(articles)} articles")
        return NewsSearchResponse(
            articles=articles,
            error=None
        )
        
    except Exception as e:
        error_msg = f"Error in search_news: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return NewsSearchResponse(
            articles=[],
            error=error_msg
        )

# -------------------------------------------------------------------------
# News Titles Tool
# -------------------------------------------------------------------------

class NewsTitlesRequest(BaseModel):
    query: str = Field(..., description="Search query for news articles")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class NewsTitlesResponse(BaseModel):
    titles: List[Dict[str, Any]]
    error: Optional[str] = None

def get_news_titles(request: NewsTitlesRequest) -> NewsTitlesResponse:
    """
    Get only news titles for a query
    
    Args:
        request: Contains the search query and max results
        
    Returns:
        List of news titles with title, link, and snippet
    """
    try:
        logger.info(f"Getting news titles with query: {request.query}")
        
        result = news_helper.get_news_titles(
            query=request.query,
            max_results=request.max_results
        )
        
        if not result.get("success", False):
            logger.error(result.get("error", "Unknown error"))
            return NewsTitlesResponse(
                titles=[],
                error=result.get("error", "Failed to get titles")
            )
        
        titles = result["data"]["titles"]
        logger.info(f"Successfully retrieved {len(titles)} titles")
        return NewsTitlesResponse(
            titles=titles,
            error=None
        )
        
    except Exception as e:
        error_msg = f"Error in get_news_titles: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return NewsTitlesResponse(
            titles=[],
            error=error_msg
        )

# -------------------------------------------------------------------------
# Save News Tool
# -------------------------------------------------------------------------

class SaveNewsRequest(BaseModel):
    articles: List[Dict[str, Any]] = Field(..., description="List of articles to save")
    query: str = Field(..., description="Search query for naming the file")
    format_type: Optional[str] = Field("json", description="Output format (json or csv)")

class SaveNewsResponse(BaseModel):
    success: bool
    filepath: Optional[str] = None
    error: Optional[str] = None

def save_news(request: SaveNewsRequest) -> SaveNewsResponse:
    """
    Save news articles to a file
    
    Args:
        request: Contains articles, query, and format type
        
    Returns:
        Success status and file path
    """
    try:
        logger.info(f"Saving {len(request.articles)} articles for query: {request.query}")
        
        result = news_helper.save_news(
            articles=request.articles,
            query=request.query,
            format_type=request.format_type
        )
        
        if not result.get("success", False):
            logger.error(result.get("error", "Unknown error"))
            return SaveNewsResponse(
                success=False,
                filepath=None,
                error=result.get("error", "Save failed")
            )
        
        filepath = result["data"]["filepath"]
        logger.info(f"Successfully saved articles to {filepath}")
        return SaveNewsResponse(
            success=True,
            filepath=filepath,
            error=None
        )
        
    except Exception as e:
        error_msg = f"Error in save_news: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return SaveNewsResponse(
            success=False,
            filepath=None,
            error=error_msg
        )
