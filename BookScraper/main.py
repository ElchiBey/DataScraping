"""
Book Scraper - Web scraping application for 'Books to Scrape'.

This application collects data from the Books to Scrape website,
processes it, saves it to files, and performs basic analysis.
"""
import os
import argparse
import time
from typing import Dict, List, Optional

import pandas as pd

from scraper.collector import WebCollector
from scraper.parser import BookParser
from models.data_models import Book, Category
from utils.file_handler import FileHandler
from utils.analyzer import DataAnalyzer


def scrape_all_books(base_url: str, max_books_per_category: Optional[int] = None) -> List[Category]:
    """
    Scrape all books from all categories.
    
    Args:
        base_url: The base URL of the website
        max_books_per_category: Optional limit of books per category
        
    Returns:
        List of Category objects with their books
    """
    print(f"Starting scraper for {base_url}")
    
    # Initialize components
    collector = WebCollector(base_url)
    parser = BookParser(base_url)
    
    # Get the homepage content
    homepage_html = collector.get("/")
    if not homepage_html:
        print("Failed to fetch homepage")
        return []
    
    # Parse categories
    categories = parser.parse_categories(homepage_html)
    print(f"Found {len(categories)} categories")
    
    # Process each category
    for category in categories:
        print(f"Processing category: {category.name}")
        html_content = collector.get(category.url)
        if not html_content:
            print(f"Failed to fetch category page: {category.name}")
            continue
        
        # Process all pages of the category
        current_url = category.url
        book_count = 0
        
        while html_content and (max_books_per_category is None or book_count < max_books_per_category):
            # Parse books from current page
            books = parser.parse_books_list(html_content, category.name)
            print(f"  Found {len(books)} books on current page")
            
            # Process each book
            for book in books:
                # Check if we've reached the limit
                if max_books_per_category is not None and book_count >= max_books_per_category:
                    break
                
                # Get detailed book information
                book_html = collector.get(book.url)
                if book_html:
                    book = parser.parse_book_details(book_html, book)
                
                # Add the book to the category
                category.add_book(book)
                book_count += 1
            
            # Check if there's a next page
            next_page = parser.check_next_page(html_content)
            if next_page and (max_books_per_category is None or book_count < max_books_per_category):
                # Construct full URL if it's relative
                if not next_page.startswith('http'):
                    # Extract the directory part of the current URL
                    current_dir = '/'.join(current_url.split('/')[:-1])
                    next_page = f"{current_dir}/{next_page}"
                
                current_url = next_page
                html_content = collector.get(next_page)
            else:
                break
        
        print(f"  Total books scraped for {category.name}: {category.book_count()}")
    
    collector.close()
    return categories

def save_data(categories: List[Category], file_handler: FileHandler) -> None:
    """
    Save scraped data to files.
    
    Args:
        categories: List of Category objects with their books
        file_handler: FileHandler instance for saving data
    """
    # Save all books to CSV
    all_books = []
    for category in categories:
        for book in category.books:
            all_books.append(book.to_dict())
    
    if all_books:
        print(f"Saving {len(all_books)} books to CSV and JSON...")
        file_handler.save_to_csv(all_books, "books.csv")
        file_handler.save_to_json(all_books, "books.json")
    
    # Save categories to JSON
    categories_data = [category.to_dict() for category in categories]
    if categories_data:
        print(f"Saving {len(categories_data)} categories to JSON...")
        file_handler.save_to_json(categories_data, "categories.json")


def analyze_data(file_handler: FileHandler, data_analyzer: DataAnalyzer) -> None:
    """
    Analyze the collected data.
    
    Args:
        file_handler: FileHandler instance for loading data
        data_analyzer: DataAnalyzer instance for analysis
    """
    print("Analyzing scraped data...")
    
    # Load the data into a DataFrame
    df = file_handler.load_as_dataframe("books.csv")
    if df.empty:
        print("No data available for analysis")
        return
    
    # Convert columns to numeric types if necessary
    if df['price'].dtype == object:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    if df['rating'].dtype == object:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Perform analyses
    print("Performing book ratings analysis...")
    rating_stats = data_analyzer.analyze_book_ratings(df)

    print("Performing book prices analysis...")
    price_stats = data_analyzer.analyze_prices(df)

    print("Performing book categories analysis...")
    category_stats = data_analyzer.analyze_categories(df)

    # Save analysis results
    analysis_results = {
        "rating_analysis": rating_stats,
        "price_analysis": price_stats,
        "category_analysis": category_stats
    }
    file_handler.save_to_json(analysis_results, "analysis_results.json")
    print("Analysis results saved to analysis_results.json")

    # Create visualizations
    print("Creating visualizations...")
    data_analyzer.create_visualizations(df)
    print("Visualizations saved in the visualizations directory.")


def main() -> None:
    """
    Main function to run the book scraper.
    """
    arg_parser = argparse.ArgumentParser(description="Book Scraper for Books to Scrape website")
    arg_parser.add_argument("--max-books", type=int, default=None, 
                            help="Maximum number of books to scrape per category")
    arg_parser.add_argument("--data-dir", type=str, default="../data",
                            help="Directory to store output files")
    arg_parser.add_argument("--analyze-only", action="store_true",
                            help="Skip scraping and only analyze existing data")
    args = arg_parser.parse_args()
    
    # Set base URL for the website
    base_url = "http://books.toscrape.com"
    
    # Initialize file handler and data analyzer
    file_handler = FileHandler(args.data_dir)
    data_analyzer = DataAnalyzer(args.data_dir)
    
    if not args.analyze_only:
        # Perform web scraping
        start_time = time.time()
        categories = scrape_all_books(base_url, args.max_books)
        end_time = time.time()
        
        print(f"Scraping completed in {end_time - start_time:.2f} seconds")
        
        if categories:
            # Save the scraped data
            save_data(categories, file_handler)
    
    # Analyze the data
    analyze_data(file_handler, data_analyzer)
    
    print("Book scraper program completed successfully.")


if __name__ == "__main__":
    main()