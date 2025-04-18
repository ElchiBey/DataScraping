"""
File operation utilities for the book scraper.
"""
import json
import csv
import os
from typing import Dict, List, Any, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraper.collector import WebCollector
from scraper.parser import BookParser
from models.data_models import Book, Category


class FileHandler:
    """
    Handles file operations for saving and loading scraped data.
    """
    
    def __init__(self, data_dir: str) -> None:
        """
        Initialize the FileHandler.
        
        Args:
            data_dir: Directory path for data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_to_json(self, data: List[Dict], filename: str) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename (without path)
            
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def save_to_csv(self, data: List[Dict], filename: str) -> bool:
        """
        Save data to a CSV file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename (without path)
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            print("No data to save")
            return False
        
        filepath = os.path.join(self.data_dir, filename)
        try:
            # Get the fieldnames from the first dictionary
            fieldnames = data[0].keys()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def load_json(self, filename: str) -> List[Dict]:
        """
        Load data from a JSON file.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            List of dictionaries from the JSON file
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return []
    
    def load_csv(self, filename: str) -> List[Dict]:
        """
        Load data from a CSV file.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            List of dictionaries from the CSV file
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
    
    def load_as_dataframe(self, filename: str) -> pd.DataFrame:
        """
        Load data into a pandas DataFrame.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            DataFrame containing the data
        """
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if filename.endswith('.csv'):
                return pd.read_csv(filepath)
            elif filename.endswith('.json'):
                return pd.read_json(filepath)
            else:
                print(f"Unsupported file format: {filename}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading data into DataFrame: {e}")
            return pd.DataFrame()
        
        
def fetch_book_details(book, parser, collector):
    book_html = collector.get(book.url)
    if book_html:
        return parser.parse_book_details(book_html, book)
    return None

def scrape_all_books(base_url: str, max_books_per_category: Optional[int] = None) -> List[Category]:
    collector = WebCollector(base_url, rate_limit=2.0)
    try:
        homepage_content = collector.get("/")
        if not homepage_content:
            print("Failed to fetch homepage content.")
            return []

        parser = BookParser(base_url)
        categories = parser.parse_categories(homepage_content)
        if not categories:
            print("No categories found.")
            return []

        for category in categories:
            print(f"Fetching books for category: {category.name}")
            category_content = collector.get(category.url)
            if not category_content:
                print(f"Failed to fetch category page for: {category.name}")
                continue

            with ThreadPoolExecutor(max_workers=5) as executor:
                category_books = parser.parse_books_list(category_content, category.name)
                detailed_books = list(executor.map(
                    lambda book: fetch_book_details(book, parser, collector),
                    category_books
                ))
                category.books.extend(filter(None, detailed_books))

        return categories
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        collector.close()
        
def test():
    # Create a FileHandler instance
    data_dir = "test_data"
    file_handler = FileHandler(data_dir)
    
    # Scrape all books
    categories = scrape_all_books("http://books.toscrape.com")
    if not categories:
        print("No categories or books found.")
        return
    
    # Prepare data for saving
    books_data = []
    for category in categories:
        for book in category.books:
            books_data.append({
                "title": book.title,
                "price": book.price,
                "rating": book.rating,
                "availability": book.availability,
                "category": book.category,
                "url": book.url,
                "upc": book.upc,
                "description": book.description,
                "image_url": book.image_url
            })
    
    # Save to JSON and CSV
    if books_data:
        if file_handler.save_to_json(books_data, "books.json"):
            print("Books data saved to books.json")
        if file_handler.save_to_csv(books_data, "books.csv"):
            print("Books data saved to books.csv")
    else:
        print("No books data to save.")
    
    # Load from JSON and CSV
    loaded_json = file_handler.load_json("books.json")
    loaded_csv = file_handler.load_csv("books.csv")

    print("Loaded JSON:", loaded_json)
    print("Loaded CSV:", loaded_csv)

# test FileHandler class functionality using collected data from the scraper
if __name__ == "__main__":
    test()
