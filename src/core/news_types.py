"""
Type definitions for the News Collector application
"""
from typing import List, Dict, Optional, TypedDict, Any


class ArticleDict(TypedDict, total=False):
    """Type definition for basic article data"""
    # Core article fields
    title: str
    link: str
    snippet: str
    published_time: str
    publisher: str
    
    # New fields for enhanced functionality
    serial_number: int  # Sequential numbering for easier processing
    image_url: str      # URL of the headline/main article image
    image_path: str     # Local file path (when images are downloaded)
    date: str           # Extracted date portion (YYYY-MM-DD format)
    time: str           # Extracted time portion (HH:MM:SS format)
    
    # Full article content (when scraping is enabled)
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


class WeatherDict(TypedDict, total=False):
    """Type definition for weather data"""
    # Core weather fields
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: float
    pressure: float
    description: str
    wind_speed: float
    visibility: float
    collected_at: str
    
    # Additional weather data
    sunrise: str
    sunset: str
    timezone: int
    
    # Forecast data (list of forecast entries)
    forecast: List[Dict[str, Any]]
    
    # Hourly forecast data
    hourly_forecast: List[Dict[str, Any]]


class ConfigDict(TypedDict, total=False):
    """Type definition for configuration data"""
    SEARCH_URL: str
    HOMEPAGE_URL: str
    OUTPUT_FORMAT: str
    OUTPUT_DIR: str
    LOG_LEVEL: str
    SCHEDULER_INTERVAL_MINUTES: int
    SCHEDULER_DAILY_HOUR: int
    SCHEDULER_DAILY_MINUTE: int
    DEFAULT_ARTICLE_LIMIT: int
    MAX_ARTICLE_LIMIT: int
    SCRAPE_FULL_ARTICLES: bool
    FULL_ARTICLES_COUNT: int
    SCRAPE_IMAGES: bool
    IMAGE_SCRAPE_MODE: str
    TOPICS: List[str]
    MAX_RETRIES: int
    BASE_DELAY: float
    MAX_DELAY: float
    FAILURE_THRESHOLD: int
    RECOVERY_TIMEOUT: int
    
    # Weather settings
    WEATHER_API_KEY: str
