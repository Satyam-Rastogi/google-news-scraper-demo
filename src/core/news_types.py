"""
Type definitions for the News Collector application
"""
from typing import List, Dict, Optional, TypedDict, Any


class ArticleDict(TypedDict, total=False):
    """Type definition for basic article data"""
    title: str
    link: str
    snippet: str
    published_time: str
    publisher: str
    full_content: 'FullArticleDict'
    gnews_link: str
    decoded_url: str


class FullArticleDict(TypedDict, total=False):
    """Type definition for full article data"""
    text: str
    authors: List[str]
    publish_date: Optional[str]
    summary: str
    keywords: List[str]
    top_image: str
    local_images: List[str]
    local_article_file: str
    downloaded_at: str
    gnews_link: str
    decoded_url: str
    markdown_file: str
    top_image_local: str
    url: str
    movies: List[str]
    images: List[str]
    meta_description: str
    meta_lang: str


class ConfigDict(TypedDict, total=False):
    """Type definition for configuration data"""
    SEARCH_URL: str
    OUTPUT_FORMAT: str
    OUTPUT_DIR: str
    LOG_LEVEL: str
    SCHEDULER_INTERVAL_MINUTES: int
    SCHEDULER_DAILY_HOUR: int
    SCHEDULER_DAILY_MINUTE: int
    SCRAPE_FULL_ARTICLES: bool
    FULL_ARTICLES_COUNT: int
    SCRAPE_IMAGES: bool
    TOPICS: List[str]
    MAX_RETRIES: int
    BASE_DELAY: float
    MAX_DELAY: float
    FAILURE_THRESHOLD: int
    RECOVERY_TIMEOUT: int