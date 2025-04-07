"""
Data models for the book scraper application.
"""
from typing import Dict, List, Optional


class Book:
    """
    Represents a book with its details.
    """
    
    def __init__(self, title: str, price: float, rating: int, availability: str, 
                 category: str, url: str, upc: str = None, description: str = None,
                 image_url: str = None) -> None:
        """
        Initialize a Book object.
        
        Args:
            title: The title of the book
            price: The price in pounds
            rating: The rating from 1-5
            availability: The availability status
            category: The book's category/genre
            url: URL of the book's page
            upc: Universal Product Code (optional)
            description: Book description (optional)
            image_url: URL of the book's image (optional)
        """
        self.title = title
        self.price = price
        self.rating = rating
        self.availability = availability
        self.category = category
        self.url = url
        self.upc = upc
        self.description = description
        self.image_url = image_url
    
    def __str__(self) -> str:
        """String representation of the book."""
        return f"{self.title} - £{self.price} - {self.rating}★"
    
    def to_dict(self) -> Dict:
        """Convert the book object to a dictionary."""
        return {
            'title': self.title,
            'price': self.price,
            'rating': self.rating,
            'availability': self.availability,
            'category': self.category,
            'url': self.url,
            'upc': self.upc,
            'description': self.description,
            'image_url': self.image_url
        }


class Category:
    """
    Represents a book category with its books.
    """
    
    def __init__(self, name: str, url: str) -> None:
        """
        Initialize a Category object.
        
        Args:
            name: The name of the category
            url: The URL for the category page
        """
        self.name = name
        self.url = url
        self.books: List[Book] = []
    
    def add_book(self, book: Book) -> None:
        """
        Add a book to this category.
        
        Args:
            book: The Book object to add
        """
        self.books.append(book)
    
    def book_count(self) -> int:
        """Return the number of books in this category."""
        return len(self.books)
    
    def __str__(self) -> str:
        """String representation of the category."""
        return f"{self.name} ({self.book_count()} books)"
    
    def to_dict(self) -> Dict:
        """Convert the category to a dictionary."""
        return {
            'name': self.name,
            'url': self.url,
            'book_count': self.book_count(),
            'books': [book.to_dict() for book in self.books]
        }
        
    def get_books(self) -> List[Book]:
        """
        Get the list of books in this category.
        
        Returns:
            List of Book objects
        """
        return self.books
     
def test():        
    # get_books = Category.get_books
    book1 = Book("Sample Book", 9.99, 5, "In stock", "Fiction", "http://example.com/book1")
    book2 = Book("Another Book", 12.99, 4, "Out of stock", "Non-Fiction", "http://example.com/book2")
    category = Category("Sample Category", "http://example.com/category")
    category.add_book(book1)
    category.add_book(book2)
    print(category) # Output: Sample Category (2 books)

    category_dict = category.to_dict()
    print(category_dict)  # Output: Dictionary representation of the category
    
if __name__ == "__main__":
    test()