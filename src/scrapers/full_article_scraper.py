"""
Module for scraping full article content and images
"""

import os
import logging
import time
import requests
from datetime import datetime
from typing import Optional, List
from src.scrapers.google_news_decoder import decode_google_news_url
from src.utils.utils import (
    resolve_google_news_url_with_selenium,
    download_image,
    save_article_text
)
from src.utils.markdown_generator import generate_markdown
from src.scrapers.article_scraper import ArticleScraper
from src.core.news_types import FullArticleDict
from src.utils.validation import validate_url, validate_path

class FullArticleScraper:
    def __init__(self, output_dir: str = "data") -> None:
        # Validate output directory
        try:
            self.output_dir: str = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logging.error(f"Invalid output directory: {e}")
            self.output_dir = "data"  # fallback to default
            
        self.article_scraper: ArticleScraper = ArticleScraper()
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "articles"), exist_ok=True)
        
    def scrape_full_article(self, article_url: str, article_title: str = "") -> Optional[FullArticleDict]:
        """
        Scrape full article content and download images
        
        Args:
            article_url (str): URL of the article to scrape
            article_title (str): Title of the article (used for naming files)
            
        Returns:
            Optional[FullArticleDict]: Dictionary containing full article data or None if failed
        """
        # Validate URL
        try:
            validated_url = validate_url(article_url, "Article URL")
        except ValueError as e:
            logging.error(f"Invalid article URL: {e}")
            return None
        
        try:
            # First, try to decode the Google News URL to get the real URL
            real_url: Optional[str] = decode_google_news_url(validated_url)
            if not real_url:
                # If decoding fails, use Selenium to resolve the redirect
                real_url = resolve_google_news_url_with_selenium(validated_url)
            
            logging.info(f"Resolved URL: {real_url}")
            
            # Validate the resolved URL
            try:
                validated_real_url = validate_url(real_url, "Resolved article URL")
            except ValueError as e:
                logging.error(f"Invalid resolved URL: {e}")
                return None
            
            # Scrape the full article content with retry logic
            article_data: Optional[FullArticleDict] = self.article_scraper.scrape_article(validated_real_url, article_title)
            if not article_data:
                # If newspaper fails, try readability with retry logic
                article_data = self.article_scraper.scrape_article_with_readability(validated_real_url, article_title)
            
            # If readability also fails, try simplified parsing
            if not article_data:
                article_data = self.article_scraper.scrape_article_simplified(validated_real_url, article_title)
            
            if not article_data:
                logging.error(f"Failed to scrape article content from {validated_real_url}")
                return None
            
            # Add the original Google News URL and decoded URL to the article data
            article_data['gnews_link'] = validated_url
            article_data['decoded_url'] = real_url
            
            # Download top image with retry logic
            if article_data.get('top_image'):
                try:
                    validated_top_image_url = validate_url(article_data['top_image'], "Top image URL")
                    image_path: Optional[str] = download_image(
                        validated_top_image_url, 
                        self.output_dir, 
                        article_title, 
                        "top"
                    )
                    if image_path:
                        article_data['top_image_local'] = image_path
                except ValueError as e:
                    logging.warning(f"Invalid top image URL: {e}")
            
            # Download other images (limit to first 5 for performance) with retry logic
            local_images: List[str] = []
            for i, image_url in enumerate(list(article_data.get('images', []))[:5]):
                try:
                    validated_image_url = validate_url(image_url, f"Image {i+1} URL")
                    image_path = download_image(
                        validated_image_url, 
                        self.output_dir, 
                        article_title, 
                        f"img_{i+1}"
                    )
                    if image_path:
                        local_images.append(image_path)
                except ValueError as e:
                    logging.warning(f"Invalid image URL {image_url}: {e}")
            
            article_data['local_images'] = local_images
            
            # Save full article text to file
            article_path: Optional[str] = save_article_text(article_data, self.output_dir, article_title)
            if article_path:
                article_data['local_article_file'] = article_path
                
            # Generate Markdown file
            markdown_path: Optional[str] = generate_markdown(article_data, self.output_dir)
            if markdown_path:
                article_data['markdown_file'] = markdown_path
                
            logging.info(f"Successfully scraped full article: {article_data.get('title', '')[:50]}...")
            return article_data
            
        except requests.RequestException as e:
            logging.error(f"Network error scraping full article from {validated_url}: {e}")
            return None
        except ValueError as e:
            logging.error(f"Validation error scraping full article from {validated_url}: {e}")
            return None
        except OSError as e:
            logging.error(f"File system error scraping full article from {validated_url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error scraping full article from {validated_url}: {e}")
            return None
