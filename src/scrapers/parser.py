
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
from src.core.news_types import ArticleDict

class ArticleParser:
    def parse(self, html_content: Optional[str]) -> List[ArticleDict]:
        """
        Parse HTML content and extract article information
        
        Args:
            html_content (Optional[str]): HTML content to parse
            
        Returns:
            List[ArticleDict]: List of parsed articles
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles: List[ArticleDict] = []

        # Updated selectors based on Google News HTML structure
        # The main container for news articles when using requests
        for item in soup.find_all('article'):
            # Try different possible selectors for title and link
            title_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            link_tag = item.find('a', class_='DY5T1d') or item.find('a', class_='JtKRv')
            
            # Try different possible selectors for snippet
            snippet_tag = item.find('div', class_='DaPVKc') or item.find('p') or item.find('div', class_='vr1PYe')
            
            # Try different possible selectors for time
            time_tag = item.find('time') or item.find('div', class_='hvbAAd')
            
            # Try to find publisher/source information
            publisher_tag = item.find('div', class_='QmrVtf') or item.find('span', class_='wE4Mu') or item.find('a', class_='wE4Mu')

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

            # Only add articles with at least a title
            if title != 'N/A':
                article: ArticleDict = {
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'published_time': published_time,
                    'publisher': publisher
                }
                articles.append(article)
        
        logging.info(f"Parsed {len(articles)} articles")
        return articles


