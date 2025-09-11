"""
Module for processing articles including full article scraping and data handling
"""
import logging
import os
import json
import csv
import time
import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.scrapers.full_article_scraper import FullArticleScraper
from config.config import Config
from src.core.news_types import ArticleDict, FullArticleDict
from src.utils.validation import validate_path, validate_string, sanitize_filename
from src.utils.retry_utils import retry_for_file_operations, retry_for_parsing


def collect_full_articles(articles: List[ArticleDict], query: str, output_dir: Optional[str] = None, image_mode: str = Config.IMAGE_SCRAPE_MODE) -> List[ArticleDict]:
    """
    Collect full article content for top articles
    
    Args:
        articles (List[ArticleDict]): List of article dictionaries
        query (str): Search query used for naming files
        output_dir (Optional[str]): Output directory for saving files
        image_mode (str): Image scraping mode (url-only, download, both)
        
    Returns:
        List[ArticleDict]: Updated list of articles with full content
    """
    # Validate query
    try:
        validated_query = validate_string(query, "Search query", min_length=1, max_length=200)
    except ValueError as e:
        logging.error(f"Invalid query: {e}")
        return articles
    
    if not Config.SCRAPE_FULL_ARTICLES or not articles:
        return articles
    
    # Use provided output directory or default from config
    output_dir = output_dir or Config.OUTPUT_DIR
    
    # Validate output directory
    try:
        validated_output_dir = validate_path(output_dir, "Output directory")
    except ValueError as e:
        logging.error(f"Invalid output directory: {e}")
        return articles
    
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping full content for top {Config.FULL_ARTICLES_COUNT} articles...")
    
    # Initialize full article scraper
    full_scraper = FullArticleScraper(validated_output_dir)
    
    # Process top articles with improved error handling
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, article in enumerate(articles[:Config.FULL_ARTICLES_COUNT]):
        try:
            logger.info(f"Processing article {i+1}: {article['title'][:50]}...")
            full_data: Optional[FullArticleDict] = full_scraper.scrape_full_article(article['link'], article['title'], image_mode)
            
            if full_data:
                # Add full article data to the article dictionary
                article['full_content'] = create_full_article_data(full_data)
                # Transfer gnews_link and decoded_url to the main article structure
                if 'gnews_link' in full_data:
                    article['gnews_link'] = full_data['gnews_link']
                if 'decoded_url' in full_data:
                    article['decoded_url'] = full_data['decoded_url']
                logger.info(f"Successfully scraped full content for article {i+1}")
                successful_scrapes += 1
            else:
                logger.warning(f"Failed to scrape full content for article {i+1}")
                failed_scrapes += 1
                
        except requests.RequestException as e:
            logger.error(f"Network error scraping full content for article {i+1} ({article['title'][:50]}...): {e}")
            failed_scrapes += 1
            continue
        except ValueError as e:
            logger.error(f"Validation error scraping full content for article {i+1} ({article['title'][:50]}...): {e}")
            failed_scrapes += 1
            continue
        except Exception as e:
            logger.error(f"Unexpected error scraping full content for article {i+1} ({article['title'][:50]}...): {e}")
            failed_scrapes += 1
            continue
    
    logger.info(f"Full article scraping completed. Success: {successful_scrapes}, Failed: {failed_scrapes}")
    return articles


@retry_for_parsing
def create_full_article_data(full_data: FullArticleDict) -> FullArticleDict:
    """
    Create standardized full article data structure
    
    Args:
        full_data (FullArticleDict): Raw full article data from scraper
        
    Returns:
        FullArticleDict: Standardized full article data
    """
    return {
        'text': full_data['text'][:1000] + '...' if len(full_data['text']) > 1000 else full_data['text'],
        'authors': full_data['authors'],
        'publish_date': full_data['publish_date'],
        'summary': full_data['summary'],
        'keywords': full_data['keywords'],
        'top_image': full_data.get('top_image_local', full_data['top_image']),
        'local_images': full_data.get('local_images', []),
        'local_article_file': full_data.get('local_article_file', ''),
        'downloaded_at': full_data['downloaded_at'],
        'gnews_link': full_data.get('gnews_link', ''),
        'decoded_url': full_data.get('decoded_url', '')
    }


@retry_for_file_operations
def save_articles(articles: List[ArticleDict], query: str, format_type: str, output_dir: Optional[str] = None) -> None:
    """
    Save articles to a file in the specified format
    
    Args:
        articles (List[ArticleDict]): List of article dictionaries
        query (str): Search query used for naming files
        format_type (str): Output format (json or csv)
        output_dir (Optional[str]): Output directory for saving files
        
    Returns:
        None
    """
    # Validate query
    try:
        validated_query = validate_string(query, "Search query", min_length=1, max_length=200)
    except ValueError as e:
        logging.error(f"Invalid query: {e}")
        return
    
    # Validate format type
    if format_type not in ('json', 'csv'):
        logging.error(f"Unsupported output format: {format_type}")
        return
    
    # Use provided output directory or default from config
    output_dir = output_dir or Config.OUTPUT_DIR
    
    # Validate output directory
    try:
        validated_output_dir = validate_path(output_dir, "Output directory")
    except ValueError as e:
        logging.error(f"Invalid output directory: {e}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(validated_output_dir, exist_ok=True)
    
    # Create a filename based on the query and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize query for filename
    safe_query = sanitize_filename(validated_query)
    safe_query = safe_query.replace(' ', '_')
    
    if format_type == 'json':
        filename = f"{safe_query}_{timestamp}.json"
        filepath = os.path.join(validated_output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved {len(articles)} articles to {filepath}")
        
    elif format_type == 'csv':
        filename = f"{safe_query}_{timestamp}.csv"
        filepath = os.path.join(validated_output_dir, filename)
        
        if articles:
            # Define standard fieldnames for CSV including new fields
            standard_fieldnames = [
                'serial_number', 'title', 'gnews_link', 'decoded_url', 'publisher', 'published_time',
                'date', 'time', 'image_url', 'image_path', 'full_text', 'authors', 'publish_date', 
                'summary', 'keywords', 'top_image'
            ]
            
            # Process articles to handle nested dictionaries for CSV
            processed_articles = []
            for article in articles:
                # Create a new article dict with all standard fields
                processed_article = {}
                
                # Map fields properly
                field_mapping = {
                    'gnews_link': 'link',  # Map original 'link' to 'gnews_link'
                    'decoded_url': 'decoded_url',  # This will be added by full article scraper
                    'publisher': 'snippet',  # This is extracted by the parser
                    'image_path': 'top_image_local'  # Map top_image_local to image_path
                }
                
                for field in standard_fieldnames:
                    # Handle special field mappings
                    if field in field_mapping:
                        source_field = field_mapping[field]
                        processed_article[field] = article.get(source_field, '')
                    elif field in article:
                        processed_article[field] = article[field]
                    else:
                        processed_article[field] = ''
                
                # Handle full_content field if it exists
                if 'full_content' in article and article['full_content']:
                    # Flatten the full_content field
                    full_content = article['full_content']
                    processed_article['full_text'] = full_content.get('text', '')[:500] + '...' if len(full_content.get('text', '')) > 500 else full_content.get('text', '')
                    processed_article['authors'] = ', '.join(full_content.get('authors', []))
                    processed_article['publish_date'] = full_content.get('publish_date', '')
                    processed_article['summary'] = full_content.get('summary', '')
                    processed_article['keywords'] = ', '.join(full_content.get('keywords', []))
                    processed_article['top_image'] = full_content.get('top_image', '')
                    
                    # Add decoded_url and gnews_link from full_content if available
                    if 'decoded_url' in full_content:
                        processed_article['decoded_url'] = full_content['decoded_url']
                    if 'gnews_link' in full_content:
                        processed_article['gnews_link'] = full_content['gnews_link']
                
                processed_articles.append(processed_article)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=standard_fieldnames)
                writer.writeheader()
                writer.writerows(processed_articles)
            
            logging.info(f"Saved {len(processed_articles)} articles to {filepath}")
    else:
        logging.error(f"Unsupported output format: {format_type}")


def collect_images(articles: List[ArticleDict], query: str, output_dir: Optional[str] = None, image_mode: str = Config.IMAGE_SCRAPE_MODE) -> List[ArticleDict]:
    """
    Collect images for all articles
    
    Args:
        articles (List[ArticleDict]): List of article dictionaries
        query (str): Search query used for naming files
        output_dir (Optional[str]): Output directory for saving files
        image_mode (str): Image scraping mode (url-only, download, both)
        
    Returns:
        List[ArticleDict]: Updated list of articles with image data
    """
    # Validate query
    try:
        validated_query = validate_string(query, "Search query", min_length=1, max_length=200)
    except ValueError as e:
        logging.error(f"Invalid query: {e}")
        return articles
    
    if not Config.SCRAPE_IMAGES or not articles:
        return articles
    
    # Use provided output directory or default from config
    output_dir = output_dir or Config.OUTPUT_DIR
    
    # Validate output directory
    try:
        validated_output_dir = validate_path(output_dir, "Output directory")
    except ValueError as e:
        logging.error(f"Invalid output directory: {e}")
        return articles
    
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping images for {len(articles)} articles...")
    
    # Process all articles for image scraping
    successful_image_scrapes = 0
    failed_image_scrapes = 0
    
    for i, article in enumerate(articles):
        try:
            # Extract image URL from the article if available
            image_url = article.get('image_url')
            if image_url and image_url != 'N/A':
                # Handle image scraping based on mode
                if image_mode == 'url-only':
                    # For url-only mode, ensure we have the image URL but no local path
                    article.pop('image_path', None)
                    successful_image_scrapes += 1
                elif image_mode in ['download', 'both']:
                    # Download the image
                    try:
                        from src.utils.utils import download_image
                        image_path: Optional[str] = download_image(
                            image_url, 
                            validated_output_dir, 
                            article.get('title', f'article_{i+1}'), 
                            "main"
                        )
                        if image_path:
                            article['image_path'] = image_path
                            # If mode is 'download', replace the URL with the local path
                            if image_mode == 'download':
                                article['image_url'] = image_path
                            successful_image_scrapes += 1
                        else:
                            failed_image_scrapes += 1
                    except Exception as e:
                        logging.warning(f"Error downloading image for article {i+1}: {e}")
                        failed_image_scrapes += 1
                else:
                    successful_image_scrapes += 1
            else:
                # No image URL available for this article
                failed_image_scrapes += 1
                
        except Exception as e:
            logging.error(f"Unexpected error scraping image for article {i+1} ({article.get('title', '')[:50]}...): {e}")
            failed_image_scrapes += 1
    
    logger.info(f"Image scraping completed. Success: {successful_image_scrapes}, Failed: {failed_image_scrapes}")
    return articles


def collect_news(query: str, output_format: Optional[str] = None, output_dir: Optional[str] = None,
                 limit: Optional[int] = None, image_mode: Optional[str] = None) -> List[ArticleDict]:
    """
    Collect news for a specific query with optional full article scraping
    
    Args:
        query (str): Search query
        output_format (Optional[str]): Output format (json or csv)
        output_dir (Optional[str]): Output directory for saving files
        limit (Optional[int]): Maximum number of articles to collect
        image_mode (Optional[str]): Image scraping mode (url-only, download, both)
        
    Returns:
        List[ArticleDict]: List of collected articles
    """
    from src.scrapers.scraper import GoogleNewsScraper
    from src.scrapers.parser import ArticleParser
    
    # Validate query
    try:
        validated_query = validate_string(query, "Search query", min_length=1, max_length=200)
    except ValueError as e:
        logging.error(f"Invalid query: {e}")
        return []
    
    # Use provided output directory or default from config
    output_dir = output_dir or Config.OUTPUT_DIR
    
    # Validate output directory
    try:
        validated_output_dir = validate_path(output_dir, "Output directory")
    except ValueError as e:
        logging.error(f"Invalid output directory: {e}")
        return []
    
    # Use provided output format or default from config
    format_type = output_format or Config.OUTPUT_FORMAT
    
    # Validate format type
    if format_type not in ('json', 'csv'):
        logging.error(f"Unsupported output format: {format_type}")
        return []

    # Use provided limit or default from config
    article_limit = limit or Config.DEFAULT_ARTICLE_LIMIT
    
    # Use provided image mode or default from config
    image_scrape_mode = image_mode or Config.IMAGE_SCRAPE_MODE

    scraper = GoogleNewsScraper()
    parser = ArticleParser()

    logger = logging.getLogger(__name__)
    logger.info(f"Searching for news related to: {validated_query}")
    html_content: Optional[str] = scraper.search(validated_query)

    if html_content:
        logger.info("Parsing search results...")
        articles: List[ArticleDict] = parser.parse(html_content, article_limit)
        if articles:
            logger.info(f"Found {len(articles)} articles.")
            
            # Collect images for all articles if enabled
            if Config.SCRAPE_IMAGES:
                articles = collect_images(articles, validated_query, validated_output_dir, image_scrape_mode)
            
            # Collect full article content for top articles if enabled
            if Config.SCRAPE_FULL_ARTICLES:
                articles = collect_full_articles(articles, validated_query, validated_output_dir, image_scrape_mode)
            
            # Save articles to file
            save_articles(articles, validated_query, format_type, validated_output_dir)
            
            return articles
        else:
            logger.warning("No articles found or parsed.")
    else:
        logger.error("Failed to retrieve HTML content.")
    
    return []