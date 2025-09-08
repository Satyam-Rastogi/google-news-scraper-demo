"""
Custom exceptions for the application
"""


class NewsScraperException(Exception):
    """Base exception for news scraper"""
    pass


class ScrapingError(NewsScraperException):
    """Exception raised when scraping fails"""
    pass


class ParsingError(NewsScraperException):
    """Exception raised when parsing fails"""
    pass


class ConfigurationError(NewsScraperException):
    """Exception raised when configuration is invalid"""
    pass


class RateLimitError(NewsScraperException):
    """Exception raised when rate limit is exceeded"""
    pass
