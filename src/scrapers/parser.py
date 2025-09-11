
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
from src.core.news_types import ArticleDict
from datetime import datetime

class ArticleParser:
    def parse(self, html_content: Optional[str], limit: Optional[int] = None) -> List[ArticleDict]:
        """
        Parse HTML content and extract article information
        
        Args:
            html_content (Optional[str]): HTML content to parse
            limit (Optional[int]): Maximum number of articles to parse
            
        Returns:
            List[ArticleDict]: List of parsed articles
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles: List[ArticleDict] = []

        # Updated selectors based on Google News HTML structure
        # The main container for news articles when using requests
        article_items = soup.find_all('article')
        
        # Apply limit if specified
        if limit:
            article_items = article_items[:limit]
        
        for i, item in enumerate(article_items):
            # Try different possible selectors for title and link
            title_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            link_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            
            # Try different possible selectors for snippet
            snippet_tag = item.find('div', class_='DaPVKc') or item.find('p') or item.find('div', class_='vr1PYe')
            
            # Try different possible selectors for time
            time_tag = item.find('time') or item.find('div', class_='hvbAAd')
            
            # Try to find publisher/source information
            publisher_tag = item.find('div', class_='QmrVtf') or item.find('span', class_='wE4Mu') or item.find('a', class_='wE4Mu')
            
            # Try to find image information - look for actual article images, not favicons
            # Google News often uses data-src or data-lazy-src for actual images
            image_tag = None
            # Try to find actual article images (not favicons)
            img_candidates = item.find_all('img')
            for img in img_candidates:
                src = img.get('src', '')
                data_src = img.get('data-src', '')
                data_lazy_src = img.get('data-lazy-src', '')
                
                # Skip favicons (they contain 'favicon' in the URL)
                if 'favicon' not in src and 'favicon' not in data_src and 'favicon' not in data_lazy_src:
                    # Prefer data-src or data-lazy-src over src for actual images
                    if data_src:
                        image_tag = img
                        image_tag['src'] = data_src  # Override src with data-src
                        break
                    elif data_lazy_src:
                        image_tag = img
                        image_tag['src'] = data_lazy_src  # Override src with data-lazy-src
                        break
                    elif src and src.startswith('http') and 'gstatic.com' not in src:
                        # If it's a regular HTTP URL and not a Google static asset, use it
                        image_tag = img
                        break
            
            # If we still don't have an image tag, fall back to any img tag (but this will likely be favicons)
            if not image_tag and img_candidates:
                image_tag = img_candidates[0]

            title = title_tag.text.strip() if title_tag else 'N/A'
            # Google News links are relative, so we need to prepend the base URL
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                # Handle relative URLs
                if href.startswith('./'):
                    link = 'https://news.google.com' + href[1:]
                elif href.startswith('http'):
                    link = href
                else:
                    link = 'https://news.google.com' + href
            else:
                link = 'N/A'
                
            snippet = snippet_tag.text.strip() if snippet_tag else 'N/A'
            
            # Extract time information
            if time_tag:
                if time_tag.name == 'time' and time_tag.has_attr('datetime'):
                    published_time = time_tag['datetime']
                else:
                    published_time = time_tag.text.strip() if time_tag.text else 'N/A'
            else:
                published_time = 'N/A'
                
            # Extract publisher information
            publisher = publisher_tag.text.strip() if publisher_tag else 'N/A'
            
            # Extract image URL
            image_url = 'N/A'
            if image_tag and image_tag.has_attr('src'):
                image_src = image_tag['src']
                # Handle relative image URLs
                if image_src.startswith('./'):
                    image_url = 'https://news.google.com' + image_src[1:]
                elif image_src.startswith('http'):
                    image_url = image_src
                else:
                    image_url = 'https://news.google.com' + image_src

            # Only add articles with at least a title
            if title != 'N/A':
                article: ArticleDict = {
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'published_time': published_time,
                    'publisher': publisher,
                    'serial_number': i + 1,  # Add sequential numbering
                    'image_url': image_url
                }
                
                # Split timestamp into date and time if it exists
                if published_time != 'N/A':
                    try:
                        # Try to parse the timestamp
                        if 'T' in published_time and 'Z' in published_time:
                            # ISO format like "2025-09-09T16:57:48Z"
                            dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%SZ")
                            article['date'] = dt.strftime("%Y-%m-%d")
                            article['time'] = dt.strftime("%H:%M:%S")
                        elif 'T' in published_time:
                            # ISO format without Z like "2025-09-09T16:57:48"
                            dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%S")
                            article['date'] = dt.strftime("%Y-%m-%d")
                            article['time'] = dt.strftime("%H:%M:%S")
                    except ValueError:
                        # If parsing fails, keep the original timestamp
                        pass
                
                articles.append(article)
        
        logging.info(f"Parsed {len(articles)} articles")
        return articles


