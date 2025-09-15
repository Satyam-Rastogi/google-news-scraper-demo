"""
Async utility functions for the news collector
"""
import asyncio
import aiohttp
import aiofiles
import os
import logging
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional
from src.utils.validation import validate_path, validate_url, sanitize_filename
from src.utils.async_http_client import get_global_async_http_client

logger = logging.getLogger(__name__)

async def download_image_async(image_url: str, output_dir: str, article_title: str = "", prefix: str = "img") -> Optional[str]:
    """
    Download an image and save it locally asynchronously
    
    Args:
        image_url (str): URL of the image to download
        output_dir (str): Directory to save the image
        article_title (str): Title of the article (used for naming files)
        prefix (str): Prefix for the image filename
        
    Returns:
        Optional[str]: Local path to the downloaded image, or None if failed
    """
    try:
        # Validate URL
        try:
            validated_url = validate_url(image_url, "Image URL")
        except ValueError as e:
            logger.warning(f"Invalid image URL: {e}")
            return None
            
        # Skip if image URL is empty
        if not validated_url:
            return None
            
        # Validate output directory
        try:
            validated_output_dir = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logger.warning(f"Invalid output directory: {e}")
            return None
            
        # Create output directory if it doesn't exist
        image_dir = os.path.join(validated_output_dir, "images")
        os.makedirs(image_dir, exist_ok=True)
            
        # Create a safe filename
        safe_title = sanitize_filename(article_title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
        # Get file extension from URL
        parsed_url = urlparse(validated_url)
        ext = os.path.splitext(parsed_url.path)[1]
        if not ext:
            ext = '.jpg'  # Default extension
                
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{prefix}_{timestamp}{ext}"
        filepath = os.path.join(image_dir, filename)
            
        # Download image using async HTTP client
        client = await get_global_async_http_client()
        response = await client.get(validated_url)
        
        if response and response.status == 200:
            # Read image content
            image_content = await response.read()
            
            # Save image using aiofiles for async file operations
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(image_content)
                
            logger.info(f"Downloaded image: {filename}")
            return filepath
        else:
            logger.error(f"Failed to download image from {validated_url}: Status {response.status if response else 'Unknown'}")
            return None
            
    except Exception as e:
        logger.error(f"Error downloading image from {image_url}: {e}")
        return None

async def save_article_text_async(article_data: dict, output_dir: str, article_title: str = "") -> Optional[str]:
    """
    Save the full article text to a file asynchronously
    
    Args:
        article_data (dict): Dictionary containing article data
        output_dir (str): Directory to save the article
        article_title (str): Title of the article (used for naming files)
        
    Returns:
        Optional[str]: Local path to the saved article file, or None if failed
    """
    try:
        # Validate output directory
        try:
            validated_output_dir = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logger.warning(f"Invalid output directory: {e}")
            return None
            
        # Create output directory if it doesn't exist
        article_dir = os.path.join(validated_output_dir, "articles")
        os.makedirs(article_dir, exist_ok=True)
        
        # Create a safe filename
        safe_title = sanitize_filename(article_title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = safe_title + "_" + timestamp + ".txt"
        filepath = os.path.join(article_dir, filename)
            
        # Create article content
        content = ""
        content += "Title: " + str(article_data.get('title', 'N/A')) + "\n"
        content += "URL: " + str(article_data.get('url', 'N/A')) + "\n"
        content += "Authors: " + ', '.join(article_data.get('authors', [])) + "\n"
        content += "Publish Date: " + str(article_data.get('publish_date', 'N/A')) + "\n"
        content += "Downloaded At: " + str(article_data.get('downloaded_at', 'N/A')) + "\n"
        content += "Keywords: " + ', '.join(article_data.get('keywords', [])) + "\n"
        content += "Summary: " + str(article_data.get('summary', 'N/A')) + "\n"
        content += "Meta Description: " + str(article_data.get('meta_description', 'N/A')) + "\n"
        content += "Meta Language: " + str(article_data.get('meta_lang', 'N/A')) + "\n"
        content += "\n" + "="*50 + "\n\n"
        content += str(article_data.get('text', 'N/A'))
            
        # Save content to file with proper encoding using aiofiles
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)
                
        logger.info("Saved article text: " + filename)
        return filepath
            
    except Exception as e:
        logger.error("Error saving article text for " + article_title + ": " + str(e))
        return None