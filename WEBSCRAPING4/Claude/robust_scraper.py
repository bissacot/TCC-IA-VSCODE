"""
Robust Web Scraper for books.toscrape.com

A production-ready web scraper with concurrent processing, retry logic,
and batch CSV export capabilities.
"""

import csv
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import List, Optional, Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ============================================================================
# Configuration and Constants
# ============================================================================

@dataclass
class Config:
    """Application configuration."""
    base_url: str = "http://books.toscrape.com/"
    max_retries: int = 3
    backoff_factor: float = 0.5
    timeout: int = 10
    batch_size: int = 50
    max_workers: int = 4
    output_file: str = "books_data.csv"


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(log_file: str = "scraper.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging with both file and console handlers.
    
    Args:
        log_file: Path to the log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()


# ============================================================================
# Custom Exceptions
# ============================================================================

class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class FetchException(ScraperException):
    """Exception raised when fetching a page fails."""
    pass


class ParseException(ScraperException):
    """Exception raised when parsing HTML fails."""
    pass


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Book:
    """Represents a book with its metadata."""
    title: str
    price: str
    availability: str
    rating: str
    url: str
    
    def to_dict(self) -> dict:
        """Convert book to dictionary for CSV export."""
        return asdict(self)


# ============================================================================
# Web Scraper Implementation
# ============================================================================

class BookScraper:
    """
    Robust web scraper for books.toscrape.com with retry logic and concurrency.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the scraper.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.session = self._create_session()
        self.csv_lock = Lock()
        self.books: List[Book] = []
        logger.info(f"Scraper initialized with config: {self.config}")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests Session with TCP connection pooling.
        
        Returns:
            Configured requests.Session instance
        """
        session = requests.Session()
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=self.config.max_workers,
            pool_maxsize=self.config.max_workers,
            max_retries=0  # We handle retries manually for better control
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        })
        
        logger.info("HTTP Session created with connection pooling")
        return session
    
    def _fetch_with_retry(self, url: str) -> str:
        """
        Fetch a URL with exponential backoff retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            Response text
            
        Raises:
            FetchException: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                logger.debug(f"Successfully fetched {url} on attempt {attempt + 1}")
                return response.text
                
            except requests.RequestException as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    wait_time = self.config.backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {url}. "
                        f"Retrying in {wait_time:.2f}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {self.config.max_retries} attempts")
        
        raise FetchException(f"Failed to fetch {url}: {str(last_exception)}")
    
    def _parse_book(self, book_element) -> Optional[Book]:
        """
        Parse a book element from the HTML.
        
        Args:
            book_element: BeautifulSoup element representing a book
            
        Returns:
            Book object or None if parsing fails
            
        Raises:
            ParseException: If parsing fails
        """
        try:
            title = book_element.select_one("h3 a")
            if not title:
                raise ParseException("Could not find book title")
            
            title_text = title.get("title")
            url = urljoin(self.config.base_url, title.get("href"))
            
            price_elem = book_element.select_one(".price_color")
            price = price_elem.get_text(strip=True) if price_elem else "N/A"
            
            availability_elem = book_element.select_one(".instock.availability")
            availability = availability_elem.get_text(strip=True) if availability_elem else "N/A"
            
            rating_elem = book_element.select_one(".star-rating")
            rating = rating_elem.get("class")[-1] if rating_elem else "N/A"
            
            book = Book(
                title=title_text,
                price=price,
                availability=availability,
                rating=rating,
                url=url
            )
            logger.debug(f"Parsed book: {book.title}")
            return book
            
        except (AttributeError, IndexError) as e:
            logger.error(f"Error parsing book element: {str(e)}")
            raise ParseException(f"Failed to parse book: {str(e)}")
    
    def _scrape_page(self, page_num: int) -> List[Book]:
        """
        Scrape a single page of books.
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            List of Book objects
        """
        url = urljoin(self.config.base_url, f"catalogue/page-{page_num}.html")
        books_on_page = []
        
        try:
            html = self._fetch_with_retry(url)
            soup = BeautifulSoup(html, "html.parser")
            
            book_elements = soup.select("article.product_pod")
            logger.info(f"Found {len(book_elements)} books on page {page_num}")
            
            for book_elem in book_elements:
                try:
                    book = self._parse_book(book_elem)
                    if book:
                        books_on_page.append(book)
                except ParseException as e:
                    logger.warning(f"Skipping book on page {page_num}: {str(e)}")
                    continue
            
            return books_on_page
            
        except FetchException as e:
            logger.error(f"Failed to scrape page {page_num}: {str(e)}")
            return []
    
    def _save_batch_to_csv(self, books: List[Book], append: bool = True) -> None:
        """
        Save a batch of books to CSV file with thread safety.
        
        Args:
            books: List of Book objects to save
            append: If True, append to existing file; if False, overwrite
        """
        if not books:
            return
        
        with self.csv_lock:
            mode = "a" if append and Path(self.config.output_file).exists() else "w"
            
            try:
                with open(
                    self.config.output_file,
                    mode,
                    newline="",
                    encoding="utf-8"
                ) as csvfile:
                    fieldnames = ["title", "price", "availability", "rating", "url"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header only if file is new
                    if mode == "w":
                        writer.writeheader()
                    
                    for book in books:
                        writer.writerow(book.to_dict())
                
                logger.info(f"Saved batch of {len(books)} books to {self.config.output_file}")
                
            except IOError as e:
                logger.error(f"Failed to write to CSV file: {str(e)}")
    
    def scrape_all_pages(self) -> List[Book]:
        """
        Scrape all pages from the website.
        
        Returns:
            List of all Book objects scraped
        """
        logger.info("Starting scrape of all pages...")
        start_time = datetime.now()
        
        try:
            # First, fetch the main page to determine total pages
            html = self._fetch_with_retry(self.config.base_url)
            soup = BeautifulSoup(html, "html.parser")
            
            pager = soup.select_one("li.current")
            if pager:
                total_pages = int(pager.get_text().split()[-2])
            else:
                logger.warning("Could not determine total pages, defaulting to 1")
                total_pages = 1
            
            logger.info(f"Total pages to scrape: {total_pages}")
            
            # Use ThreadPoolExecutor for concurrent page scraping
            all_books = []
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_page = {
                    executor.submit(self._scrape_page, page): page
                    for page in range(1, total_pages + 1)
                }
                
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        books = future.result()
                        all_books.extend(books)
                        
                        # Save batch when it reaches batch_size
                        if len(all_books) >= self.config.batch_size:
                            self._save_batch_to_csv(all_books[:self.config.batch_size])
                            all_books = all_books[self.config.batch_size:]
                            
                    except Exception as e:
                        logger.error(f"Error scraping page {page}: {str(e)}")
            
            # Save remaining books
            if all_books:
                self._save_batch_to_csv(all_books, append=True)
            
            elapsed = datetime.now() - start_time
            total_books = self._count_csv_rows()
            
            logger.info(
                f"Scraping completed in {elapsed.total_seconds():.2f}s. "
                f"Total books saved: {total_books}"
            )
            
            return all_books
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {str(e)}")
            raise ScraperException(f"Scraping failed: {str(e)}")
    
    def _count_csv_rows(self) -> int:
        """
        Count the number of data rows in the CSV file.
        
        Returns:
            Number of rows (excluding header)
        """
        if not Path(self.config.output_file).exists():
            return 0
        
        try:
            with open(self.config.output_file, "r", encoding="utf-8") as f:
                return sum(1 for _ in f) - 1  # Subtract 1 for header
        except IOError as e:
            logger.error(f"Error counting CSV rows: {str(e)}")
            return 0
    
    def close(self) -> None:
        """Close the HTTP session and cleanup resources."""
        self.session.close()
        logger.info("Scraper session closed")


# ============================================================================
# Main Execution
# ============================================================================

def main() -> None:
    """Main execution function."""
    config = Config(
        max_workers=4,
        batch_size=50,
        output_file="books_data.csv"
    )
    
    scraper = BookScraper(config)
    
    try:
        scraper.scrape_all_pages()
        logger.info("Web scraping completed successfully")
    except ScraperException as e:
        logger.error(f"Scraping failed: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
