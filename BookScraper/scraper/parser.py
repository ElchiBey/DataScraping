"""
HTML parsing utilities for the book scraper.
"""

from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import re

from models.data_models import Book, Category


class BookParser:
    """
    Parser for extracting book data from HTML content.
    """
    
    def __init__(self, base_url: str) -> None:
        """
        Initialize the BookParser.
        
        Args:
            base_url: The base URL of the website
        """
        self.base_url = base_url
        
    def parse_categories(self, html_content: str) -> List[Category]:
        """
        Parse the HTML content to extract book categories and their URLs.
        
        Args:
            html_content: The HTML content of the homepage
        
        Returns:
            list of Category objects
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []
        
        # Find all category links
        for link in soup.select('a[href^="/category/books/"]'):
            category_name = link.text.strip()
            category_url = self.base_url + link['href']
            categories.append(Category(category_name, category_url))
        
        return categories
    