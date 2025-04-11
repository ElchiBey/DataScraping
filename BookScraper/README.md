# Books to Scrape - Web Scraping Project

This project is a Python web scraper that collects book data from [Books to Scrape](http://books.toscrape.com/), processes the information, saves it to files, and performs basic analysis on the collected data.

## Features

- Scrapes book data including titles, prices, ratings, and availability
- Processes books by category
- Respects rate limiting and follows ethical scraping principles
- Implements error handling and robust HTML parsing
- Saves data in both CSV and JSON formats
- Performs data analysis and creates visualizations
- Uses object-oriented design principles

## Project Structure

```
BookScraper/
├── main.py                 # Application entry point
├── scraper/                # Web scraping modules
│   ├── __init__.py
│   ├── collector.py        # HTTP requests handling
│   └── parser.py           # HTML parsing utilities
├── models/                 # Data models
│   ├── __init__.py
│   └── data_models.py      # Object representations of data
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── file_handler.py     # File operations
│   └── analyzer.py         # Data analysis tools
├── data/                   # Directory for output files
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
└── CONTRIBUTIONS.md        # Team member contributions
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/BookScraper.git
   cd BookScraper
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the scraper with default settings:

```
python main.py
```

This will scrape all books from all categories and save the data to the `data` directory.

### Command Line Arguments

The scraper supports several command line arguments:

- `--max-books`: Maximum number of books to scrape per category (default: no limit)
- `--data-dir`: Directory to store output files (default: `data`)
- `--analyze-only`: Skip scraping and only analyze existing data

Examples:

```
# Scrape up to 10 books per category
python main.py --max-books 10

# Save data to a custom directory
python main.py --data-dir my_book_data

# Only analyze previously scraped data
python main.py --analyze-only
```

## Output Files

The scraper generates the following files in the data directory:

- `books.csv`: All book data in CSV format
- `books.json`: All book data in JSON format
- `categories.json`: Category information including book lists
- `analysis_results.json`: Results of data analysis
- `visualizations/`: Directory containing data visualizations:
  - `price_distribution.png`: Histogram of book prices
  - `rating_distribution.png`: Bar chart of book ratings
  - `category_counts.png`: Bar chart of books per category
  - `price_vs_rating.png`: Scatter plot of price vs. rating
  - `avg_price_by_category.png`: Bar chart of average price by category

## Ethical Considerations

This scraper:

- Respects the website's `robots.txt` policy
- Implements rate limiting to prevent server overload
- Does not scrape copyrighted content for commercial purposes
- Uses clear user-agent headers to identify itself

## License

This project is licensed under the MIT License - see the LICENSE file for details.