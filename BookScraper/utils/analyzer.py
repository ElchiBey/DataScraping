"""
Data analysis tools for the book scraper.
"""
from typing import Dict, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import os

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraper.collector import WebCollector
from scraper.parser import BookParser
from models.data_models import Book, Category



class DataAnalyzer:
    """
    Performs analysis on book data.
    """
    
    def __init__(self, data_dir: str) -> None:
        """
        Initialize the DataAnalyzer.
        
        Args:
            data_dir: Directory path for data files and outputs
        """
        self.data_dir = data_dir
    
    def analyze_book_ratings(self, df: pd.DataFrame) -> Dict:
        """
        Analyze book ratings.
        
        Args:
            df: DataFrame containing book data
            
        Returns:
            Dictionary with rating statistics
        """
        # Convert rating to numeric if it's not already
        if df['rating'].dtype == object:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        rating_stats = {
            'average_rating': df['rating'].mean(),
            'rating_counts': df['rating'].value_counts().to_dict(),
            'highest_rated_books': df.nlargest(5, 'rating')[['title', 'rating', 'category']].to_dict('records'),
            'lowest_rated_books': df.nsmallest(5, 'rating')[['title', 'rating', 'category']].to_dict('records')
        }
        
        return rating_stats
    
    def analyze_prices(self, df: pd.DataFrame) -> Dict:
        """
        Analyze book prices.
        
        Args:
            df: DataFrame containing book data
            
        Returns:
            Dictionary with price statistics
        """
        # Convert price to numeric if it's not already
        if df['price'].dtype == object:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        price_stats = {
            'average_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'price_range': df['price'].max() - df['price'].min(),
            'standard_deviation': df['price'].std(),
            'most_expensive_books': df.nlargest(5, 'price')[['title', 'price', 'category']].to_dict('records'),
            'least_expensive_books': df.nsmallest(5, 'price')[['title', 'price', 'category']].to_dict('records')
        }
        
        return price_stats
    
    def analyze_categories(self, df: pd.DataFrame) -> Dict:
        """
        Analyze book categories.
        
        Args:
            df: DataFrame containing book data
            
        Returns:
            Dictionary with category statistics
        """
        category_counts = df['category'].value_counts()
        
        # Calculate average price and rating by category
        category_stats = df.groupby('category').agg({
            'price': 'mean',
            'rating': 'mean'
        }).reset_index()
        
        category_analysis = {
            'category_counts': category_counts.to_dict(),
            'most_common_category': category_counts.index[0],
            'least_common_category': category_counts.index[-1],
            'category_stats': category_stats.to_dict('records')
        }
        
        return category_analysis
    
    def create_visualizations(self, df: pd.DataFrame) -> None:
        """
        Create data visualizations and save them to files.
        
        Args:
            df: DataFrame containing book data
        """
        # Create visualizations directory
        viz_dir = os.path.join(self.data_dir, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        # Convert price and rating to numeric if needed
        if df['price'].dtype == object:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        if df['rating'].dtype == object:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # 1. Price distribution histogram
        plt.figure(figsize=(10, 6))
        plt.hist(df['price'], bins=20, color='skyblue', edgecolor='black')
        plt.title('Book Price Distribution')
        plt.xlabel('Price (£)')
        plt.ylabel('Number of Books')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(os.path.join(viz_dir, 'price_distribution.png'))
        plt.close()
        
        # 2. Rating distribution
        plt.figure(figsize=(10, 6))
        rating_counts = df['rating'].value_counts().sort_index()
        plt.bar(rating_counts.index, rating_counts.values, color='lightgreen', edgecolor='black')
        plt.title('Book Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Number of Books')
        plt.xticks(range(1, 6))
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(os.path.join(viz_dir, 'rating_distribution.png'))
        plt.close()
        
        # 3. Category counts - horizontal bar chart
        plt.figure(figsize=(12, 8))
        category_counts = df['category'].value_counts()
        category_counts.sort_values().plot(kind='barh', color='salmon')
        plt.title('Books per Category')
        plt.xlabel('Number of Books')
        plt.ylabel('Category')
        plt.grid(axis='x', alpha=0.75)
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'category_counts.png'))
        plt.close()
        
        # 4. Price vs Rating scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df['price'], df['rating'], alpha=0.5)
        plt.title('Price vs Rating')
        plt.xlabel('Price (£)')
        plt.ylabel('Rating')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(viz_dir, 'price_vs_rating.png'))
        plt.close()
        
        # 5. Average price by category
        plt.figure(figsize=(12, 8))
        category_avg_price = df.groupby('category')['price'].mean().sort_values()
        category_avg_price.plot(kind='barh', color='lightblue')
        plt.title('Average Price by Category')
        plt.xlabel('Average Price (£)')
        plt.ylabel('Category')
        plt.grid(axis='x', alpha=0.75)
        plt.tight_layout()
        plt.savefig(os.path.join(viz_dir, 'avg_price_by_category.png'))
        plt.close()
        
def test():
    # Step 1: Initialize WebCollector and BookParser
    base_url = "http://books.toscrape.com"
    collector = WebCollector(base_url, rate_limit=2.0)
    parser = BookParser(base_url)

    try:
        # Step 2: Fetch homepage content
        homepage_content = collector.get("/")
        if not homepage_content:
            print("Failed to fetch homepage content.")
            return

        # Step 3: Parse categories
        categories = parser.parse_categories(homepage_content)
        if not categories:
            print("No categories found.")
            return

        # Step 4: Scrape books from all categories
        books = []
        for category in categories:
            print(f"Fetching books for category: {category.name}")
            category_content = collector.get(category.url)
            if not category_content:
                print(f"Failed to fetch category page for: {category.name}")
                continue

            # Parse books in the category
            category_books = parser.parse_books_list(category_content, category.name)
            for book in category_books:
                # Fetch book detail page content
                book_detail_content = collector.get(book.url)
                if book_detail_content:
                    book = parser.parse_book_details(book_detail_content, book)
                else:
                    print(f"Failed to fetch details for book: {book.title}")
            books.extend(category_books)

        # Step 5: Convert books to a DataFrame
        books_data = [
            {
                "title": book.title,
                "price": book.price,
                "rating": book.rating,
                "availability": book.availability,
                "category": book.category,
                "url": book.url,
                "upc": book.upc,
                "description": book.description,
                "image_url": book.image_url,
            }
            for book in books
        ]
        df = pd.DataFrame(books_data)

        # Step 6: Analyze the data
        data_dir = "test_output"
        analyzer = DataAnalyzer(data_dir)

        print("\nAnalyzing book ratings...")
        rating_stats = analyzer.analyze_book_ratings(df)
        print(rating_stats)

        print("\nAnalyzing book prices...")
        price_stats = analyzer.analyze_prices(df)
        print(price_stats)

        print("\nAnalyzing book categories...")
        category_stats = analyzer.analyze_categories(df)
        print(category_stats)

        print("\nCreating visualizations...")
        analyzer.create_visualizations(df)
        print(f"Visualizations saved in {data_dir}/visualizations")

    finally:
        # Step 7: Close the WebCollector session
        collector.close()

if __name__ == "__main__":
    test()