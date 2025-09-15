"""
Async module for scraping full article content and images
"""
import asyncio
import os
import logging
import time
from datetime import datetime
from typing import Optional, List, Tuple
from src.scrapers.async_google_news_decoder import decode_google_news_url_async, decode_google_news_urls_batch_async
from src.utils.utils import (
    resolve_google_news_url_with_selenium,
    download_image,
    save_article_text
)
from src.utils.async_utils import download_image_async, save_article_text_async
from src.utils.markdown_generator import generate_markdown
from src.scrapers.async_article_scraper import AsyncArticleScraper
from src.core.news_types import FullArticleDict
from src.utils.validation import validate_url, validate_path
from config.config import Config

class AsyncFullArticleScraper:
    def __init__(self, output_dir: str = "data") -> None:
        # Validate output directory
        try:
            self.output_dir: str = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logging.error(f"Invalid output directory: {e}")
            self.output_dir = "data"  # fallback to default
            
        self.article_scraper: AsyncArticleScraper = AsyncArticleScraper()
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "articles"), exist_ok=True)
        
    async def scrape_full_article(self, article_url: str, article_title: str = "", image_mode: str = Config.IMAGE_SCRAPE_MODE) -> Optional[FullArticleDict]:
        """
        Scrape full article content and download images asynchronously
        
        Args:
            article_url (str): URL of the article to scrape
            article_title (str): Title of the article (used for naming files)
            image_mode (str): Image scraping mode (url-only, download, both)
            
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
            real_url: Optional[str] = await decode_google_news_url_async(validated_url)
            if not real_url:
                # If decoding fails, use Selenium to resolve the redirect (keep synchronous)
                real_url = resolve_google_news_url_with_selenium(validated_url)
            
            logging.info(f"Resolved URL: {real_url}")
            
            # Validate the resolved URL
            try:
                validated_real_url = validate_url(real_url, "Resolved article URL")
            except ValueError as e:
                logging.error(f"Invalid resolved URL: {e}")
                return None
                
            # Scrape the full article content with retry logic
            article_data: Optional[FullArticleDict] = await self.article_scraper.scrape_article(validated_real_url, article_title)
            if not article_data:
                # If newspaper fails, try readability with retry logic
                article_data = await self.article_scraper.scrape_article_with_readability(validated_real_url, article_title)
            
            # If readability also fails, try simplified parsing
            if not article_data:
                article_data = await self.article_scraper.scrape_article_simplified(validated_real_url, article_title)
            
            if not article_data:
                logging.error(f"Failed to scrape article content from {validated_real_url}")
                return None
                
            # Add the original Google News URL and decoded URL to the article data
            article_data['gnews_link'] = validated_url
            article_data['decoded_url'] = real_url
            
            # Handle image downloading based on image mode
            if image_mode in ['download', 'both'] and article_data.get('top_image'):
                try:
                    validated_top_image_url = validate_url(article_data['top_image'], "Top image URL")
                    # Use async image download
                    image_path: Optional[str] = await download_image_async(
                        validated_top_image_url,
                        self.output_dir,
                        article_title,
                        "top"
                    )
                    if image_path:
                        article_data['top_image_local'] = image_path
                        # If mode is 'download', replace the URL with the local path
                        if image_mode == 'download':
                            article_data['top_image'] = image_path
                except ValueError as e:
                    logging.warning(f"Invalid top image URL: {e}")
            elif image_mode == 'url-only' and article_data.get('top_image'):
                # For url-only mode, ensure we have the image URL but no local path
                article_data.pop('top_image_local', None)
            
            # Download other images (limit to first 5 for performance) with parallel processing
            local_images: List[str] = []
            if image_mode in ['download', 'both']:
                image_urls = list(article_data.get('images', []))[:5]
                if image_urls:
                    try:
                        # Validate all image URLs first
                        validated_image_urls = []
                        for i, image_url in enumerate(image_urls):
                            try:
                                validated_url = validate_url(image_url, f"Image {i+1} URL")
                                validated_image_urls.append((i, validated_url))
                            except ValueError as e:
                                logging.warning(f"Invalid image URL {image_url}: {e}")
                        
                        if validated_image_urls:
                            # Create tasks for concurrent image downloads
                            image_download_tasks = [
                                download_image_async(
                                    validated_url,
                                    self.output_dir,
                                    article_title,
                                    f"img_{i+1}"
                                )
                                for i, validated_url in validated_image_urls
                            ]
                            
                            # Execute all image downloads concurrently
                            image_paths = await asyncio.gather(*image_download_tasks, return_exceptions=True)
                            
                            # Process results
                            for i, (index, _) in enumerate(validated_image_urls):
                                result = image_paths[i]
                                if isinstance(result, Exception):
                                    logging.warning(f"Error downloading image {index+1}: {result}")
                                elif result:
                                    local_images.append(result)
                                    # If mode is 'download', replace the URL with the local path
                                    if image_mode == 'download':
                                        article_data['images'][index] = result
                    except Exception as e:
                        logging.warning(f"Error processing multiple images: {e}")
            
            article_data['local_images'] = local_images
            
            # Save full article text to file asynchronously
            article_path: Optional[str] = await save_article_text_async(article_data, self.output_dir, article_title)
            if article_path:
                article_data['local_article_file'] = article_path
                
            # Generate Markdown file asynchronously
            try:
                from src.utils.markdown_generator import generate_markdown_async
                markdown_path: Optional[str] = await generate_markdown_async(article_data, self.output_dir)
                if markdown_path:
                    article_data['markdown_file'] = markdown_path
            except Exception as e:
                logging.warning(f"Error generating markdown: {e}")
                
            logging.info(f"Successfully scraped full article: {article_data.get('title', '')[:50]}...")
            return article_data
            
        except Exception as e:
            logging.error(f"Unexpected error scraping full article from {validated_url}: {e}")
            return None
            
    async def scrape_full_articles_batch(self, article_data_list: List[Tuple[str, str, str]], image_mode: str = Config.IMAGE_SCRAPE_MODE) -> List[Optional[FullArticleDict]]:
        """
        Scrape multiple full articles concurrently with batch URL decoding
        
        Args:
            article_data_list (List[Tuple[str, str, str]]): List of (article_url, article_title, gnews_link) tuples
            image_mode (str): Image scraping mode (url-only, download, both)
            
        Returns:
            List[Optional[FullArticleDict]]: List of article data dictionaries or None for failed articles
        """
        if not article_data_list:
            return []
            
        logger = logging.getLogger(__name__)
        logger.info(f"Starting batch scraping of {len(article_data_list)} articles")
        
        # Extract URLs for batch decoding
        gnews_urls = [gnews_link for _, _, gnews_link in article_data_list]
        
        # Batch decode URLs
        logger.info(f"Batch decoding {len(gnews_urls)} URLs")
        decoded_urls_results = await decode_google_news_urls_batch_async(gnews_urls)
        
        # Create mapping of original URLs to decoded URLs
        url_mapping = {original: decoded for original, decoded in decoded_urls_results}
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(Config.CONCURRENT_ARTICLES_PROCESSING)
        
        async def scrape_article_with_semaphore(article_url: str, article_title: str, gnews_link: str, index: int) -> Optional[FullArticleDict]:
            async with semaphore:
                try:
                    logger.info(f"Processing article {index+1}: {article_title[:50]}...")
                    # Get decoded URL from mapping
                    real_url = url_mapping.get(gnews_link)
                    if not real_url:
                        # Fallback to individual decoding
                        real_url = await decode_google_news_url_async(gnews_link)
                        if not real_url:
                            real_url = resolve_google_news_url_with_selenium(gnews_link)
                    
                    # Validate the resolved URL
                    try:
                        validated_real_url = validate_url(real_url, "Resolved article URL")
                    except ValueError as e:
                        logging.error(f"Invalid resolved URL for article {index+1}: {e}")
                        return None
                    
                    # Scrape the full article content
                    article_data: Optional[FullArticleDict] = await self.article_scraper.scrape_article(validated_real_url, article_title)
                    if not article_data:
                        article_data = await self.article_scraper.scrape_article_with_readability(validated_real_url, article_title)
                    
                    if not article_data:
                        article_data = await self.article_scraper.scrape_article_simplified(validated_real_url, article_title)
                    
                    if not article_data:
                        logging.error(f"Failed to scrape article content from {validated_real_url}")
                        return None
                    
                    # Add the original Google News URL and decoded URL to the article data
                    article_data['gnews_link'] = gnews_link
                    article_data['decoded_url'] = real_url
                    
                    # Handle image downloading based on image mode
                    if image_mode in ['download', 'both'] and article_data.get('top_image'):
                        try:
                            validated_top_image_url = validate_url(article_data['top_image'], "Top image URL")
                            image_path: Optional[str] = await download_image_async(
                                validated_top_image_url,
                                self.output_dir,
                                article_title,
                                "top"
                            )
                            if image_path:
                                article_data['top_image_local'] = image_path
                                if image_mode == 'download':
                                    article_data['top_image'] = image_path
                        except ValueError as e:
                            logging.warning(f"Invalid top image URL for article {index+1}: {e}")
                    elif image_mode == 'url-only' and article_data.get('top_image'):
                        article_data.pop('top_image_local', None)
                    
                    # Download other images with parallel processing
                    local_images: List[str] = []
                    if image_mode in ['download', 'both']:
                        image_urls = list(article_data.get('images', []))[:5]
                        if image_urls:
                            try:
                                validated_image_urls = []
                                for i, image_url in enumerate(image_urls):
                                    try:
                                        validated_url = validate_url(image_url, f"Image {i+1} URL")
                                        validated_image_urls.append((i, validated_url))
                                    except ValueError as e:
                                        logging.warning(f"Invalid image URL {image_url}: {e}")
                                
                                if validated_image_urls:
                                    image_download_tasks = [
                                        download_image_async(
                                            validated_url,
                                            self.output_dir,
                                            article_title,
                                            f"img_{i+1}"
                                        )
                                        for i, validated_url in validated_image_urls
                                    ]
                                    
                                    image_paths = await asyncio.gather(*image_download_tasks, return_exceptions=True)
                                    
                                    for i, (index_img, _) in enumerate(validated_image_urls):
                                        result = image_paths[i]
                                        if isinstance(result, Exception):
                                            logging.warning(f"Error downloading image {index_img+1} for article {index+1}: {result}")
                                        elif result:
                                            local_images.append(result)
                                            if image_mode == 'download':
                                                article_data['images'][index_img] = result
                            except Exception as e:
                                logging.warning(f"Error processing multiple images for article {index+1}: {e}")
                    
                    article_data['local_images'] = local_images
                    
                    # Save full article text to file asynchronously
                    article_path: Optional[str] = await save_article_text_async(article_data, self.output_dir, article_title)
                    if article_path:
                        article_data['local_article_file'] = article_path
                    
                    # Generate Markdown file asynchronously
                    try:
                        from src.utils.markdown_generator import generate_markdown_async
                        markdown_path: Optional[str] = await generate_markdown_async(article_data, self.output_dir)
                        if markdown_path:
                            article_data['markdown_file'] = markdown_path
                    except Exception as e:
                        logging.warning(f"Error generating markdown for article {index+1}: {e}")
                    
                    logger.info(f"Successfully scraped full article {index+1}: {article_data.get('title', '')[:50]}...")
                    return article_data
                    
                except Exception as e:
                    logger.error(f"Error scraping full article {index+1} ({article_title[:50]}...): {e}")
                    return None
        
        # Process all articles concurrently
        tasks = [
            scrape_article_with_semaphore(article_url, article_title, gnews_link, i)
            for i, (article_url, article_title, gnews_link) in enumerate(article_data_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception during batch scraping of article {i+1}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        logger.info(f"Completed batch scraping of {len(article_data_list)} articles")
        return processed_results