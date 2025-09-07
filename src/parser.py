from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from urllib.parse import urljoin

class ArticleParser:
    def parse(self, html_content: str) -> List[Dict]:
        """
        Parse HTML content to extract article information
        
        Args:
            html_content (str): HTML content from Google News search
            
        Returns:
            List[Dict]: List of article dictionaries with title, link, and snippet
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []

        # Find all article elements
        for item in soup.find_all('article'):
            # Try different possible selectors for title and link
            title_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            link_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            
            # Try different possible selectors for snippet
            snippet_tag = item.find('div', class_='DaPVKc') or item.find('p') or item.find('div', class_='vr1PYe')
            
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'
            
            # Handle relative URLs
            if link_tag and link_tag.get('href'):
                href = link_tag['href']
                # Handle relative URLs
                if href.startswith('./'):
                    link = 'https://news.google.com' + href[1:]
                elif href.startswith('http'):
                    link = href
                else:
                    link = urljoin('https://news.google.com', href)
            else:
                link = 'N/A'
                
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'N/A'

            # Only add articles with at least a title
            if title != 'N/A':
                articles.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })
        
        logging.info(f"Parsed {len(articles)} articles")
        return articles