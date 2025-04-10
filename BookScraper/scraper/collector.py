"""
HTTP request handling for the book scraper.
"""
import time
from typing import Dict, Optional, Union
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


class WebCollector:
    """
    Handles HTTP requests for web scraping with rate limiting and error handling.
    """
    
    def __init__(self, base_url: str, rate_limit: float = 1.0) -> None:
        """
        Initialize the WebCollector.
        
        Args:
            base_url: The base URL for the website
            rate_limit: Minimum time between requests in seconds
        """
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
    
    def _respect_rate_limit(self) -> None:
        """
        Enforce rate limiting between requests.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """
        Perform a GET request with rate limiting and error handling.
        
        Args:
            url: The URL to request
            params: Optional query parameters
            
        Returns:
            The HTML content as string if successful, None otherwise
        """
        full_url = url if url.startswith('http') else f"{self.base_url}/{url.lstrip('/')}"
        
        try:
            self._respect_rate_limit()
            response = self.session.get(full_url, params=params)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except RequestException as e:
            print(f"Error fetching {full_url}: {e}")
            return None
    
    def close(self) -> None:
        """
        Close the session.
        """
        self.session.close()
        # print("Session closed.")
        
if __name__ == "__main__":
    # Initialize the WebCollector with the base URL and rate limit
    collector = WebCollector("http://books.toscrape.com", rate_limit=2.0)
    
    # Fetch the content of the books
    books_url = "/catalogue/category/books_1/index.html"
    books_content = collector.get(books_url)

    if books_content:
        print("Books content fetched successfully.")
        print("Books Page Content:")
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(books_content, 'html.parser')

        # Find all book containers
        books = soup.find_all('article', class_='product_pod')

        # Extract and print the title and price of each book
        for book in books:
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            print(f"Title: {title}, Price: {price}")
    else:
        print("Failed to fetch books content or resource not found.")
    
    try:
        # Attempt to fetch the content from the homepage
        html_content = collector.get("/")
        if html_content:
            print("Content fetched successfully.")
            print("Fetched Content:")
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all category links in the sidebar
            categories = soup.find('div', class_='side_categories').find_all('a')

            # Extract and print the category names
            print("Categories:")
            for category in categories:
                category_name = category.text.strip()
                print(f"- {category_name}")
        else:
            print("Failed to fetch content or resource not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the session is closed properly
        collector.close()
        print("Collector closed.")