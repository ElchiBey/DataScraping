"""
HTML parsing utilities for the book scraper.
"""
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import re

from collector import WebCollector

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from models.data_models import Book, Category

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
        Parse all book categories from the homepage.
        
        Args:
            html_content: HTML content of the homepage
            
        Returns:
            List of Category objects
        """
        categories = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # The category navigation is in the sidebar
        nav_element = soup.select_one('.side_categories')
        if not nav_element:
            return categories
        
        # Get all category links
        category_links = nav_element.select('ul > li > ul > li > a')
        for link in category_links:
            name = link.text.strip()
            url = link.get('href', '')
            if url:
                full_url = f"{self.base_url}/{url.lstrip('/')}"
                categories.append(Category(name, full_url))
        
        return categories
    
    def _extract_rating(self, element: Tag) -> int:
        """
        Extract star rating from a book element.
        
        Args:
            element: HTML element containing the rating
            
        Returns:
            Integer rating from 1-5
        """
        rating_class = element.select_one('p.star-rating')
        if not rating_class:
            return 0
        
        # Rating is encoded in the class name
        rating_map = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }
        
        for class_name in rating_class['class']:
            if class_name in rating_map:
                return rating_map[class_name]
        
        return 0
    
    def _extract_price(self, element: Tag) -> float:
        """
        Extract price from a book element.
        
        Args:
            element: HTML element containing the price
            
        Returns:
            Price as float
        """
        price_element = element.select_one('p.price_color')
        if not price_element:
            return 0.0
        
        # Remove currency symbol and convert to float
        price_text = price_element.text.strip()
        price_match = re.search(r'£(\d+\.\d+)', price_text)
        if price_match:
            return float(price_match.group(1))
        
        return 0.0
    
    def _extract_availability(self, element: Tag) -> str:
        """
        Extract availability info from a book element.
        
        Args:
            element: HTML element containing availability
            
        Returns:
            Availability as string
        """
        availability_element = element.select_one('p.availability')
        if availability_element:
            return availability_element.text.strip()
        return "Unknown"
    
    def parse_books_list(self, html_content: str, category: str) -> List[Book]:
        """
        Parse book listings from a category page.
        
        Args:
            html_content: HTML content of the category page
            category: Name of the category
            
        Returns:
            List of Book objects
        """
        books = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all book elements
        book_elements = soup.select('article.product_pod')
        for element in book_elements:
            # Extract basic book info
            title_element = element.select_one('h3 > a')
            title = title_element.get('title', 'Unknown') if title_element else 'Unknown'
            
            url_path = title_element.get('href', '') if title_element else ''
            url = f"{self.base_url}/{"catalogue"}/{url_path.lstrip('../../..')}" if url_path else ''   
            # print("book url: ",url)   
                  
            image_element = element.select_one('img')
            image_url = image_element.get('src', '') if image_element else ''
            if image_url and not image_url.startswith('http'):
                image_url = f"{self.base_url}/{image_url.lstrip('/')}"
            
            # Get rating and price
            rating = self._extract_rating(element)
            price = self._extract_price(element)
            availability = self._extract_availability(element)
            
            # Create Book object with basic info
            book = Book(
                title=title,
                price=price,
                rating=rating,
                availability=availability,
                category=category,
                url=url,
                image_url=image_url
            )
            books.append(book)
        
        return books
    
    def parse_book_details(self, html_content: str, book: Book) -> Book:
        """
        Parse detailed information for a specific book.
        
        Args:
            html_content: HTML content of the book page
            book: Existing Book object to update
            
        Returns:
            Updated Book object
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract description
        description_element = soup.select_one('#product_description + p')
        if description_element:
            book.description = description_element.text.strip()
        
        # Extract UPC from product information table
        info_table = soup.select_one('table.table-striped')
        if info_table:
            rows = info_table.select('tr')
            for row in rows:
                header = row.select_one('th')
                data = row.select_one('td')
                if header and data and header.text.strip() == 'UPC':
                    book.upc = data.text.strip()
        
        return book
    
    def check_next_page(self, html_content: str) -> Optional[str]:
        """
        Check if there's a next page of results and return its URL.
        
        Args:
            html_content: HTML content of the current page
            
        Returns:
            URL of the next page or None if there isn't one
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        next_button = soup.select_one('li.next > a')
        
        if next_button:
            next_url = next_button.get('href', '')
            if next_url:
                return next_url
        
        return None
    
    
# Example usage:
# if __name__ == "__main__":
#     # Initialize the parser with default selectors
#     parser = BookParser("http://books.toscrape.com")
#
#     # Example HTML content (this would be fetched from a real request)
#     html_content = """
#     <html>
#         <body>
#             <div class="side_categories">
#                 <ul>
#                     <li><ul><li><a href="/category/books_1/index.html">Books</a></li></ul></li>
#                 </ul>
#             </div>

#             <article class="product_pod">
#                 <h3><a href="/catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
#                 <p class="star-rating Three"></p>
#                 <p class="price_color">£51.77</p>
#                 <p class="availability in-stock availability">In stock (21 available)</p>
#                 <img src="../media/cache/6c/6c1b8f7e9a4a2b5d5f9e4e7c0d3f3b1d.jpg" alt="A Light in the Attic" class="thumbnail">
#             </article>
#         </body>
#     </html>
#     """
#
#     # Parse categories
#     categories = parser.parse_categories(html_content)

#     for category in categories:
#         print(f"Category: {category.name}, URL: {category.url}")
#         # Parse books in the category
#         books = parser.parse_books_list(html_content, category.name)
#         for book in books:
#             print(f"  Book: {book.title}, Price: {book.price}, Rating: {book.rating}")

#             # Parse book details
#             book_detail_html = """
#             <html>
#                 <body>
#                     <div id="product_description">
#                         <p>A great book about...</p>
#                     </div>
#                     <table class="table-striped">
#                         <tr><th>UPC</th><td>1234567890</td></tr>
#                     </table>
#                 </body>
#             </html>
#             """
#             book = parser.parse_book_details(book_detail_html, book)
#             print(f"    Description: {book.description}, UPC: {book.upc}")
#
#             print(f"    Image URL: {book.image_url}")
#         print()
#     # Check for next page (example, not functional without real HTML)
#     next_page_url = parser.check_next_page(html_content)
#     if next_page_url:
#         print(f"Next page URL: {next_page_url}")
#     else:
#         print("No next page found.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
from collector import WebCollector
from models.data_models import Book, Category

# Initialize the WebCollector with the base URL and rate limit
collector = WebCollector("http://books.toscrape.com", rate_limit=2.0)

try:
    # Attempt to fetch the content from the homepage
    html_content = collector.get("/")
    if html_content:
        print("Content fetched successfully.")
        print("Fetched Content:")
        # print(html_content)  # Print the raw HTML content just to varify correctness
    else:
        print("Failed to fetch content or resource not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    collector.close()
    print("Collector closed.")#         parser.close()
#         print("Parser closed.")
#     # Note: The example HTML content is not functional and is just for demonstration purposes.
#     # In a real scenario, you would fetch the HTML content from the website using the WebCollector class.


"""
now let's test the real scenario and fetch from the website using the WebCollector class.
"""
if __name__ == "__main__": 
    collector = WebCollector("http://books.toscrape.com", rate_limit=2.0)

    try:
        # Fetch the homepage content
        homepage_content = collector.get("/")
        if homepage_content:
            print("Homepage content fetched successfully.")
            
            # Initialize the parser with default selectors
            parser = BookParser("http://books.toscrape.com")
            
            # Parse categories from the homepage
            categories = parser.parse_categories(homepage_content)
            
            
            if categories:
                # Test the first category
                first_category = categories[0]
                print(f"Category: {first_category.name}, URL: {first_category.url}")
                
                # Fetch the first category page content
                category_content = collector.get(first_category.url)
                if category_content:
                    print(f"Fetched category page for: {first_category.name}")
                    
                    # Parse books in the first category
                    books = parser.parse_books_list(category_content, first_category.name)
                    for book in books:
                        # print(f"  Book: {book.title}, Price: {book.price}, Rating: {book.rating}")
                        # print()
                        # print(f"  Book : {book}")
                        # print("book ulr: ",book.url)
                        
                        # Fetch book detail page content
                        book_detail_content = collector.get(book.url)
                        print()
                        if book_detail_content:
                            print(f"Fetched details for book: {book.title}")
                            
                            # Parse book details
                            book = parser.parse_book_details(book_detail_content, book)
                            print(f"    Description: {book.description}, UPC: {book.upc}")
                            print(f"    Image URL: {book.image_url}")
                        else:
                            print(f"Failed to fetch details for book: {book.title}")
                    
                    # Check for the next page in the category
                    next_page_url = parser.check_next_page(category_content)
                    if next_page_url:
                        print(f"Next page URL: {next_page_url}")
                        next_page_content = collector.get(next_page_url)
                        if next_page_content:
                            print("Fetched second page of the category.")
                            # Parse books from the second page
                            books = parser.parse_books_list(next_page_content, first_category.name)
                            for book in books:
                                print(f"  Book: {book.title}, Price: {book.price}, Rating: {book.rating}")
                        else:
                            print("Failed to fetch the second page of the category.")
                    else:
                        print("No next page found for the category.")
                else:
                    print(f"Failed to fetch category page for: {first_category.name}")
            else:
                print("No categories found on the homepage.")
        
        else:
            print("Failed to fetch homepage content.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        collector.close()
        print("Web collector session closed.")