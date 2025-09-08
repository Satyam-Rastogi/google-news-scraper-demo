"""
Article Parser Module
Handles parsing of HTML content to extract article information
"""

from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
from dataclasses import dataclass


@dataclass
class ParsingConfig:
    """Configuration for parsing behavior"""
    max_articles: int = 100
    min_title_length: int = 5


class ArticleParser:
    """Parser for extracting article information from HTML content"""
    
    def __init__(self, config: Optional[ParsingConfig] = None) -> None:
        """
        Initialize the parser with configuration
        
        Args:
            config: Parsing configuration, uses default if None
        """
        self.config = config or ParsingConfig()
        self.logger = logging.getLogger(__name__)

    def parse(self, html_content: str) -> List[Dict]:
        """
        Parse HTML content to extract article information
        
        Args:
            html_content: HTML content from Google News search
            
        Returns:
            List of article dictionaries with title, link, and snippet
        """
        if not html_content:
            self.logger.warning("Empty HTML content provided")
            return []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # Find all article elements
            article_elements = soup.find_all('article')[:self.config.max_articles]
            
            for item in article_elements:
                article = self._extract_article(item)
                if article and self._is_valid_article(article):
                    articles.append(article)
            
            self.logger.info(f"Successfully parsed {len(articles)} articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML content: {e}")
            return []

    def _extract_article(self, item) -> Optional[Dict]:
        """Extract article information from a single article element"""
        try:
            # Try different possible selectors for title and link
            title_tag = (item.find('a', class_='DY5T1d') or 
                        item.find('a', class_='JtKRv') or
                        item.find('h3'))
            
            # Try different possible selectors for snippet
            snippet_tag = (item.find('div', class_='DaPVKc') or 
                          item.find('p') or 
                          item.find('div', class_='vr1PYe') or
                          item.find('div', class_='snippet'))
            
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'
            
            # Handle relative URLs
            link = self._extract_link(title_tag)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'N/A'

            return {
                'title': title,
                'link': link,
                'snippet': snippet
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting article: {e}")
            return None

    def _extract_link(self, title_tag) -> str:
        """Extract and normalize article link"""
        if not title_tag or not title_tag.get('href'):
            return 'N/A'
            
        href = title_tag['href']
        
        # Handle relative URLs
        if href.startswith('./'):
            return 'https://news.google.com' + href[1:]
        elif href.startswith('http'):
            return href
        else:
            return urljoin('https://news.google.com', href)

    def _is_valid_article(self, article: Dict) -> bool:
        """Check if article meets minimum quality criteria"""
        title = article.get('title', '')
        return (title != 'N/A' and 
                len(title) >= self.config.min_title_length and
                article.get('link') != 'N/A')
