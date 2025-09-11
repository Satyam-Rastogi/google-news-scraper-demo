"""
Module for converting full articles to Markdown format.
"""
import os
import logging
from typing import Dict, Any, Optional
from src.utils.validation import validate_path, sanitize_filename


def generate_markdown(article_data: Dict[str, Any], output_dir: str) -> Optional[str]:
    """
    Generate a Markdown file for a full article.
    
    Args:
        article_data (Dict[str, Any]): Dictionary containing full article data
        output_dir (str): Directory to save the Markdown file
        
    Returns:
        Optional[str]: Path to the generated Markdown file, or None if failed
    """
    try:
        # Validate output directory
        try:
            validated_output_dir = validate_path(output_dir, "Output directory")
        except ValueError as e:
            logging.warning(f"Invalid output directory: {e}")
            return None
            
        # Create articles directory if it doesn't exist
        articles_dir = os.path.join(validated_output_dir, "articles")
        os.makedirs(articles_dir, exist_ok=True)
        
        # Get article title
        title = article_data.get('title', 'Untitled')
        
        # Create a safe filename
        safe_title = sanitize_filename(title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.md"
        filepath = os.path.join(articles_dir, filename)
        
        # Create Markdown content
        content = f"# {title}\n\n"
        
        # Add metadata
        authors = article_data.get('authors', [])
        if authors:
            content += f"**Authors**: {', '.join(authors)}\n\n"
            
        publish_date = article_data.get('publish_date', '')
        if publish_date:
            content += f"**Publish Date**: {publish_date}\n\n"
            
        keywords = article_data.get('keywords', [])
        if keywords:
            content += f"**Keywords**: {', '.join(keywords)}\n\n"
            
        summary = article_data.get('summary', '')
        if summary:
            content += f"**Summary**: {summary}\n\n"
            
        # Add top image if available
        top_image = article_data.get('top_image_local', article_data.get('top_image', ''))
        if top_image and os.path.exists(top_image):
            # Convert to relative path
            rel_path = os.path.relpath(top_image, articles_dir)
            content += f"![Top Image]({rel_path})\n\n"
            
        # Add main content
        text = article_data.get('text', '')
        if text:
            content += f"{text}\n\n"
            
        # Add source URL
        url = article_data.get('url', '')
        if url:
            content += f"**Source**: [{url}]({url})\n\n"
            
        # Save content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logging.info(f"Generated Markdown file: {filename}")
        return filepath
        
    except Exception as e:
        logging.error(f"Error generating Markdown for article '{title}': {e}")
        return None
