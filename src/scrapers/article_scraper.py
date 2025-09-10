"""
Module for scraping full article content using readability and newspaper libraries
"""

import logging
import re
import time
from typing import Dict, List, Optional
from readability import Document
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from newspaper import Article
from datetime import datetime
from src.core.news_types import FullArticleDict
from src.utils.retry_utils import retry_for_network, CircuitBreaker
from config.config import Config

# Verification messages that indicate the content requires human verification
VERIFY_MESSAGES: List[str] = [
    "you are human",
    "are you human", 
    "i'm not a robot",
    "recaptcha"
]

# Unwanted keywords that indicate promotional/content farm content
UNWANTED_KEYWORDS: List[str] = [
    "subscribe now",
    "sign up",
    "newsletter",
    "subscribe now",
    "sign up for our newsletter",
    "exclusive offer",
    "limited time offer",
    "free trial",
    "download now",
    "join now",
    "register today",
    "special promotion",
    "promotional offer",
    "discount code",
    "early access",
    "sneak peek",
    "save now",
    "don't miss out",
    "act now",
    "last chance",
    "expires soon",
    "giveaway",
    "free access",
    "premium access",
    "unlock full access",
    "buy now",
    "learn more",
    "click here",
    "follow us on",
    "share this article",
    "connect with us",
    "advertisement",
    "sponsored content",
    "partner content",
    "affiliate links",
    "click here",
    "for more information",
    "you may also like",
    "we think you'll like",
    "from our network"
]

# User agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

class ArticleScraper:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        # Initialize circuit breaker for this scraper
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=Config.FAILURE_THRESHOLD,
            recovery_timeout=Config.RECOVERY_TIMEOUT
        )
        self.request_count = 0
        self.last_request_time = 0
    
    def _delay_request(self) -> None:
        """Add delay between requests to avoid rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Minimum delay between requests (in seconds)
        min_delay = 2.0
        
        if time_since_last_request < min_delay:
            sleep_time = min_delay - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    @retry_for_network
    def _scrape_with_newspaper(self, article_url: str) -> Optional[FullArticleDict]:
        """Scrape article using newspaper library with retry logic"""
        # Add delay before making request
        self._delay_request()
        
        # Create newspaper Article object
        article = Article(article_url)
        article.download()
        article.parse()
        
        # Extract article data
        article_data: FullArticleDict = {
            'title': article.title,
            'url': article_url,
            'authors': article.authors,
            'publish_date': article.publish_date.isoformat() if article.publish_date else None,
            'text': article.text,
            'summary': article.summary,
            'keywords': article.keywords,
            'top_image': article.top_image,
            'images': list(article.images),
            'movies': list(article.movies),
            'meta_description': article.meta_description,
            'meta_lang': article.meta_lang,
            'downloaded_at': datetime.now().isoformat()
        }
        
        return article_data
    
    def scrape_article(self, article_url: str, article_title: str = "") -> Optional[FullArticleDict]:
        """
        Scrape full article content using newspaper library
        
        Args:
            article_url (str): URL of the article to scrape
            article_title (str): Title of the article (used for naming files)
            
        Returns:
            Optional[FullArticleDict]: Dictionary containing full article data or None if failed
        """
        try:
            # Scrape with retry logic and circuit breaker
            article_data = self.circuit_breaker.call(self._scrape_with_newspaper, article_url)
            return article_data
        except Exception as e:
            self.logger.error(f"Error scraping article from {article_url}: {e}")
            return None
    
    @retry_for_network
    def _fetch_with_requests(self, article_url: str) -> requests.Response:
        """Fetch article content with requests and retry logic"""
        # Add delay before making request
        self._delay_request()
        
        # Rotate user agents
        user_agent = USER_AGENTS[self.request_count % len(USER_AGENTS)]
        headers: Dict[str, str] = {
            'User-Agent': user_agent
        }
        
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
    
    @retry_for_network
    def _scrape_with_readability(self, article_url: str) -> Optional[FullArticleDict]:
        """Scrape article using readability library with retry logic"""
        # Fetch the article content
        response = self._fetch_with_requests(article_url)
        
        # Use readability to parse the article
        doc = Document(response.text)
        title = doc.title()
        content = doc.summary()
        
        # Parse the content with BeautifulSoup to clean it further
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text_content = soup.get_text()
        
        # Clean the text
        cleaned_text = self.clean_text(text_content, UNWANTED_KEYWORDS)
        
        # Check if content is too short
        if len(cleaned_text.split()) < 100:  # Less than 100 words
            self.logger.warning(f"Article content is too short and likely not valuable: {article_title}")
            return None
        
        # Check for verification messages
        has_verify_message = any(msg in cleaned_text.lower() for msg in VERIFY_MESSAGES)
        if has_verify_message:
            self.logger.warning(f"Article requires human verification: {article_title}")
            return None
        
        # Extract additional metadata
        meta_description: str = ""
        meta_lang: str = "en"
        
        # Try to extract meta description
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag and meta_desc_tag.get('content'):
            meta_description = meta_desc_tag['content']
        
        # Try to extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            meta_lang = html_tag['lang']
        
        # Extract article data
        article_data: FullArticleDict = {
            'title': title,
            'url': article_url,
            'authors': [],
            'publish_date': None,
            'text': cleaned_text,
            'summary': "",
            'keywords': [],
            'top_image': "",
            'images': [],
            'movies': [],
            'meta_description': meta_description,
            'meta_lang': meta_lang,
            'downloaded_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"SUCCESSFULLY SCRAPED ARTICLE CONTENT: {cleaned_text[:100]}...")
        return article_data
    
    def scrape_article_with_readability(self, article_url: str, article_title: str = "") -> Optional[FullArticleDict]:
        """
        Scrape full article content using readability library
        
        Args:
            article_url (str): URL of the article to scrape
            article_title (str): Title of the article (used for naming files)
            
        Returns:
            Optional[FullArticleDict]: Dictionary containing full article data or None if failed
        """
        try:
            # Scrape with retry logic and circuit breaker
            article_data = self.circuit_breaker.call(self._scrape_with_readability, article_url)
            return article_data
        except Exception as e:
            self.logger.error(f"Error scraping article with readability from {article_url}: {e}")
            return None
    
    @retry_for_network
    def _scrape_with_simplified_parsing(self, article_url: str) -> Optional[FullArticleDict]:
        """Scrape article using simplified parsing with retry logic"""
        # Fetch the article content
        response = self._fetch_with_requests(article_url)
        
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Try to extract title
        title = ""
        title_tag = soup.find('title') or soup.find('h1')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Try to extract main content
        # Look for common content containers
        content_selectors = [
            'article', 
            '.article-content', 
            '.content', 
            '.post-content',
            '.entry-content',
            'main',
            '.main-content'
        ]
        
        content_div = None
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                break
        
        # If no specific content container found, use body
        if not content_div:
            content_div = soup.find('body')
        
        # Get text content
        if content_div:
            # Remove navigation links and other unwanted elements
            for nav_element in content_div.find_all(['nav', 'footer', 'header', 'aside', 'form']):
                nav_element.decompose()
            
            text_content = content_div.get_text()
        else:
            text_content = soup.get_text()
        
        # Clean the text
        cleaned_text = self.clean_text(text_content, UNWANTED_KEYWORDS)
        
        # Check if content is too short
        if len(cleaned_text.split()) < 50:  # Less than 50 words
            self.logger.warning(f"Simplified parsing yielded too little content for: {title[:50]}...")
            return None
        
        # Extract article data
        article_data: FullArticleDict = {
            'title': title,
            'url': article_url,
            'authors': [],
            'publish_date': None,
            'text': cleaned_text,
            'summary': "",
            'keywords': [],
            'top_image': "",
            'images': [],
            'movies': [],
            'meta_description': "",
            'meta_lang': "en",
            'downloaded_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"SUCCESSFULLY SCRAPED ARTICLE WITH SIMPLIFIED PARSING: {cleaned_text[:100]}...")
        return article_data
    
    def scrape_article_simplified(self, article_url: str, article_title: str = "") -> Optional[FullArticleDict]:
        """
        Scrape full article content using simplified parsing
        
        Args:
            article_url (str): URL of the article to scrape
            article_title (str): Title of the article (used for naming files)
            
        Returns:
            Optional[FullArticleDict]: Dictionary containing full article data or None if failed
        """
        try:
            # Scrape with retry logic and circuit breaker
            article_data = self.circuit_breaker.call(self._scrape_with_simplified_parsing, article_url)
            return article_data
        except Exception as e:
            self.logger.error(f"Error scraping article with simplified parsing from {article_url}: {e}")
            return None
    
    def clean_text(self, text: str, filter_words: List[str]) -> str:
        """
        Clean text by removing unwanted content and formatting
        
        Args:
            text (str): Text to clean
            filter_words (List[str]): Words/phrases to filter out
            
        Returns:
            str: Cleaned text
        """
        try:
            # Split into lines and trim whitespace
            lines: List[str] = [line.strip() for line in text.split('\n')]
            
            # Filter out lines with fewer than 5 words (likely headers/navigation)
            lines = [line for line in lines if len(line.split()) > 4]
            
            # Filter out lines containing unwanted keywords
            filtered_lines: List[str] = []
            for line in lines:
                line_lower = line.lower()
                if not any(keyword.lower() in line_lower for keyword in filter_words):
                    filtered_lines.append(line)
            
            # Join lines back together
            cleaned_text = '\n'.join(filtered_lines)
            
            return cleaned_text
        except Exception as e:
            return text
