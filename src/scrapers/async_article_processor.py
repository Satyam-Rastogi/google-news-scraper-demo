"""
Async module for processing articles including full article scraping and data handling
"""
import asyncio
import logging
import os
import json
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.scrapers.async_full_article_scraper import AsyncFullArticleScraper
from config.config import Config
from src.core.news_types import ArticleDict, FullArticleDict
from src.utils.validation import validate_path, validate_string, sanitize_filename
from src.utils.retry_utils import retry_for_file_operations, retry_for_parsing

async def collect_full_articles_async(articles: List[ArticleDict], query: str, output_dir: Optional[str] = None, image_mode: str = Config.IMAGE_SCRAPE_MODE) -> List[ArticleDict]:
    """
    Collect full article content for top articles asynchronously
    
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
    
    # Initialize async full article scraper
    full_scraper = AsyncFullArticleScraper(validated_output_dir)
    
    # Prepare data for batch processing
    top_articles = articles[:Config.FULL_ARTICLES_COUNT]
    article_data_list = [
        (article['link'], article['title'], article['link']) 
        for article in top_articles
    ]
    
    # Use batch processing for better performance
    if len(article_data_list) > 1:
        logger.info(f"Using batch processing for {len(article_data_list)} articles")
        full_articles_data = await full_scraper.scrape_full_articles_batch(article_data_list, image_mode)
    else:
        # For single article, use individual processing
        logger.info("Using individual processing for single article")
        full_articles_data = []
        for i, article in enumerate(top_articles):
            try:
                full_data: Optional[FullArticleDict] = await full_scraper.scrape_full_article(article['link'], article['title'], image_mode)
                full_articles_data.append(full_data)
            except Exception as e:
                logger.error(f"Error scraping full content for article {i+1} ({article['title'][:50]}...): {e}")
                full_articles_data.append(None)
    
    # Update articles with full content data
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, (article, full_data) in enumerate(zip(top_articles, full_articles_data)):
        if full_data:
            try:
                # Add full article data to the article dictionary
                article['full_content'] = create_full_article_data(full_data)
                # Transfer gnews_link and decoded_url to the main article structure
                if 'gnews_link' in full_data:
                    article['gnews_link'] = full_data['gnews_link']
                if 'decoded_url' in full_data:
                    article['decoded_url'] = full_data['decoded_url']
                successful_scrapes += 1
                logger.info(f"Successfully scraped full content for article {i+1}")
            except Exception as e:
                logger.error(f"Error updating article {i+1} with full content: {e}")
                failed_scrapes += 1
        else:
            logger.warning(f"Failed to scrape full content for article {i+1}")
            failed_scrapes += 1
    
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
async def save_articles_async(articles: List[ArticleDict], query: str, format_type: str, output_dir: Optional[str] = None) -> None:
    """
    Save articles to a file in the specified format asynchronously
    
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
        
        # Use aiofiles for async file operations
        try:
            import aiofiles
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(articles, indent=2, ensure_ascii=False))
            logging.info(f"Saved {len(articles)} articles to {filepath}")
        except Exception as e:
            logging.error(f"Error saving JSON file: {e}")
        
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
            
            # Use aiofiles for async file operations
            try:
                import aiofiles
                import io
                import csv as csv_module
                
                # Create CSV content in memory
                output = io.StringIO()
                writer = csv_module.DictWriter(output, fieldnames=standard_fieldnames)
                writer.writeheader()
                writer.writerows(processed_articles)
                
                # Write to file asynchronously
                async with aiofiles.open(filepath, 'w', newline='', encoding='utf-8') as f:
                    await f.write(output.getvalue())
                
                logging.info(f"Saved {len(processed_articles)} articles to {filepath}")
            except Exception as e:
                logging.error(f"Error saving CSV file: {e}")
        else:
            # Handle case with no articles
            try:
                import aiofiles
                import io
                import csv as csv_module
                
                # Create empty CSV with headers
                output = io.StringIO()
                standard_fieldnames = [
                    'serial_number', 'title', 'gnews_link', 'decoded_url', 'publisher', 'published_time',
                    'date', 'time', 'image_url', 'image_path', 'full_text', 'authors', 'publish_date', 
                    'summary', 'keywords', 'top_image'
                ]
                writer = csv_module.DictWriter(output, fieldnames=standard_fieldnames)
                writer.writeheader()
                
                # Write to file asynchronously
                async with aiofiles.open(filepath, 'w', newline='', encoding='utf-8') as f:
                    await f.write(output.getvalue())
                
                logging.info(f"Saved empty CSV file with headers to {filepath}")
            except Exception as e:
                logging.error(f"Error saving empty CSV file: {e}")
    else:
        logging.error(f"Unsupported output format: {format_type}")

async def collect_images_async(articles: List[ArticleDict], query: str, output_dir: Optional[str] = None, image_mode: str = Config.IMAGE_SCRAPE_MODE) -> List[ArticleDict]:
    """
    Collect images for all articles asynchronously
    
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
    
    # Import async image download function
    from src.utils.async_utils import download_image_async
    
    # Create semaphore to limit concurrent image downloads
    semaphore = asyncio.Semaphore(Config.CONCURRENT_ARTICLES_PROCESSING)
    
    # Create tasks for concurrent image downloading
    async def download_image_with_semaphore(article: ArticleDict, index: int) -> Optional[tuple[int, str]]:
        async with semaphore:
            try:
                # Extract image URL from the article if available
                image_url = article.get('image_url')
                if image_url and image_url != 'N/A':
                    # Handle image scraping based on mode
                    if image_mode == 'url-only':
                        # For url-only mode, ensure we have the image URL but no local path
                        article.pop('image_path', None)
                        return (index, "success")
                    elif image_mode in ['download', 'both']:
                        # Download the image
                        image_path: Optional[str] = await download_image_async(
                            image_url, 
                            validated_output_dir, 
                            article.get('title', f'article_{index+1}'), 
                            "main"
                        )
                        if image_path:
                            article['image_path'] = image_path
                            # If mode is 'download', replace the URL with the local path
                            if image_mode == 'download':
                                article['image_url'] = image_path
                            return (index, "success")
                        else:
                            return (index, "failed")
                    else:
                        return (index, "success")
                else:
                    # No image URL available for this article
                    return (index, "failed")
            except Exception as e:
                logger.error(f"Error downloading image for article {index+1} ({article.get('title', '')[:50]}...): {e}")
                return (index, "failed")
    
    # Process all articles for image scraping concurrently
    tasks = [
        download_image_with_semaphore(article, i) 
        for i, article in enumerate(articles)
    ]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_image_scrapes = 0
    failed_image_scrapes = 0
    
    for result in results:
        if isinstance(result, Exception):
            failed_image_scrapes += 1
            logger.error(f"Exception in image downloading: {result}")
            continue
            
        if result is None:
            failed_image_scrapes += 1
            continue
            
        index, status = result
        if status == "success":
            successful_image_scrapes += 1
        else:
            failed_image_scrapes += 1
    
    logger.info(f"Image scraping completed. Success: {successful_image_scrapes}, Failed: {failed_image_scrapes}")
    return articles

async def collect_news_async(query: str, output_format: Optional[str] = None, output_dir: Optional[str] = None,
                            limit: Optional[int] = None, image_mode: Optional[str] = None) -> List[ArticleDict]:
    """
    Collect news for a specific query with optional full article scraping asynchronously
    
    Args:
        query (str): Search query
        output_format (Optional[str]): Output format (json or csv)
        output_dir (Optional[str]): Output directory for saving files
        limit (Optional[int]): Maximum number of articles to collect
        image_mode (Optional[str]): Image scraping mode (url-only, download, both)
        
    Returns:
        List[ArticleDict]: List of collected articles
    """
    from src.scrapers.async_scraper import AsyncGoogleNewsScraper
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

    scraper = AsyncGoogleNewsScraper()
    parser = ArticleParser()

    logger = logging.getLogger(__name__)
    logger.info(f"Searching for news related to: {validated_query}")
    html_content: Optional[str] = await scraper.search(validated_query)

    if html_content:
        logger.info("Parsing search results...")
        articles: List[ArticleDict] = parser.parse(html_content, article_limit)
        if articles:
            logger.info(f"Found {len(articles)} articles.")
            
            # Collect images for all articles if enabled
            if Config.SCRAPE_IMAGES:
                articles = await collect_images_async(articles, validated_query, validated_output_dir, image_scrape_mode)
            
            # Collect full article content for top articles if enabled
            if Config.SCRAPE_FULL_ARTICLES:
                articles = await collect_full_articles_async(articles, validated_query, validated_output_dir, image_scrape_mode)
            
            # Save articles to file
            await save_articles_async(articles, validated_query, format_type, validated_output_dir)
            
            return articles
        else:
            logger.warning("No articles found or parsed.")
    else:
        logger.error("Failed to retrieve HTML content.")
    
    return []