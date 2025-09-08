#!/usr/bin/env python3
"""
Configuration settings for News Scraping MCP tools
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# News Scraping settings
DEFAULT_MAX_RESULTS = int(os.getenv("DEFAULT_MAX_RESULTS", "10"))
DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")
OUTPUT_DIR = BASE_DIR / "data"

# MCP Server settings
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
NEWS_MCP_PORT = int(os.getenv("NEWS_MCP_PORT", "3006"))
NEWS_MCP_URL = f"http://{MCP_HOST}:{NEWS_MCP_PORT}/sse"

# Agent settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'news_mcp_server': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'news_mcp_agent': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# System prompts
SYSTEM_PROMPTS = {
    'agent': """
    You are a helpful news analysis assistant. Your job is to analyze news articles and provide insights.
    Focus on these key elements:
    
    1. Article titles and main topics
    2. Key information and summaries
    3. Source credibility and relevance
    4. Trends and patterns in the news
    
    Provide a concise analysis of the news articles, highlighting important information and trends.
    """
}

# Error messages
ERROR_MESSAGES = {
    'missing_api_key': "ERROR: OPENAI_API_KEY not found in environment variables",
    'server_connection': "Error connecting to MCP server: {error}",
    'server_not_running': "Make sure the News MCP server is running at {url}",
    'news_retrieval': "Could not retrieve news articles",
    'news_analysis': "Error analyzing news articles: {error}"
}