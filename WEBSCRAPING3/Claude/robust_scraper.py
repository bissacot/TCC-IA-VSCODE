"""
Robust, Resilient, and Concurrent Web Scraper for books.toscrape.com

A production-ready web scraper with:
- Modular design with Type Hints
- Native logging
- requests.Session for TCP reuse
- Retry mechanisms with exponential backoff
- Concurrent processing with ThreadPoolExecutor
- Thread-safe CSV batch writing
- Comprehensive error handling
"""

import csv
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "http://books.toscrape.com/"
OUTPUT_CSV = "books_data.csv"
BATCH_SIZE = 50
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5  # Exponential backoff multiplier


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(log_file: str = "scraper.log") -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers.
    
    Args:
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Book:
    """Data class representing a book from the website."""
    
    title: str
    price: str
    rating: str
    availability: str
    url: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert book to dictionary."""
        return {
            "title": self.title,
            "price": self.price,
            "rating": self.rating,
            "availability": self.availability,
            "url": self.url,
        }


# ============================================================================
# Session Management with Retry Strategy
# ============================================================================

def create_session_with_retries(
    max_retries: int = MAX_RETRIES,
    backoff_factor: float = BACKOFF_FACTOR,
) -> requests.Session:
    """
    Create a requests.Session with exponential backoff retry strategy.
    
    Args:
        max_retries: Maximum number of retries
        backoff_factor: Backoff factor for exponential backoff
        
    Returns:
        Configured requests.Session
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set headers to mimic a real browser
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
        }
    )
    
    return session


# ============================================================================
# Scraping Logic
# ============================================================================

def fetch_page(session: requests.Session, url: str) -> Optional[str]:
    """
    Fetch a page with error handling.
    
    Args:
        session: requests.Session instance
        url: URL to fetch
        
    Returns:
        HTML content or None if failed
    """
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} for {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {url}: {e}")
        return None


def parse_book(article_element: Any) -> Optional[Book]:
    """
    Parse a book from a BeautifulSoup article element.
    
    Args:
        article_element: BeautifulSoup article element
        
    Returns:
        Book instance or None if parsing fails
    """
    try:
        title = article_element.find("h3").find("a")["title"]
        price = article_element.find("p", class_="price_color").text.strip()
        rating = article_element.find("p", class_="star-rating")["class"][1]
        availability = article_element.find("p", class_="instock availability").text.strip()
        url = article_element.find("h3").find("a")["href"]
        
        return Book(
            title=title,
            price=price,
            rating=rating,
            availability=availability,
            url=urljoin(BASE_URL, url),
        )
    except (AttributeError, KeyError, IndexError) as e:
        logger.warning(f"Error parsing book element: {e}")
        return None


def scrape_page_books(session: requests.Session, url: str) -> List[Book]:
    """
    Scrape all books from a single page.
    
    Args:
        session: requests.Session instance
        url: URL of the page to scrape
        
    Returns:
        List of Book instances
    """
    html_content = fetch_page(session, url)
    if not html_content:
        return []
    
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.find_all("article", class_="product_pod")
        
        books = []
        for article in articles:
            book = parse_book(article)
            if book:
                books.append(book)
        
        logger.info(f"Scraped {len(books)} books from {url}")
        return books
    except Exception as e:
        logger.error(f"Error parsing page {url}: {e}")
        return []


def get_page_urls(session: requests.Session, max_pages: Optional[int] = None) -> List[str]:
    """
    Get all page URLs from the website.
    
    Args:
        session: requests.Session instance
        max_pages: Maximum number of pages to scrape (None = all)
        
    Returns:
        List of page URLs
    """
    urls = [BASE_URL + "catalogue/page-1.html"]
    page_number = 2
    
    while True:
        if max_pages and page_number > max_pages:
            break
        
        next_url = BASE_URL + f"catalogue/page-{page_number}.html"
        response = fetch_page(session, next_url)
        
        if not response:
            logger.info(f"Reached last page at page {page_number}")
            break
        
        urls.append(next_url)
        page_number += 1
    
    logger.info(f"Found {len(urls)} pages to scrape")
    return urls


# ============================================================================
# CSV Writing with Thread Safety
# ============================================================================

class ThreadSafeCSVWriter:
    """Thread-safe CSV writer using context managers."""
    
    def __init__(self, filepath: str, fieldnames: List[str]) -> None:
        """
        Initialize CSV writer.
        
        Args:
            filepath: Path to CSV file
            fieldnames: Column names
        """
        self.filepath = filepath
        self.fieldnames = fieldnames
        self._lock = Lock()
        self._initialized = False
    
    def write_batch(self, rows: List[Dict[str, str]]) -> None:
        """
        Write a batch of rows to CSV in a thread-safe manner.
        
        Args:
            rows: List of dictionaries to write
        """
        with self._lock:
            file_exists = Path(self.filepath).exists()
            
            try:
                with open(self.filepath, "a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                    
                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()
                        self._initialized = True
                    
                    writer.writerows(rows)
                
                logger.info(f"Wrote {len(rows)} rows to {self.filepath}")
            except IOError as e:
                logger.error(f"Error writing to CSV: {e}")


# ============================================================================
# Main Scraper Class
# ============================================================================

class RobustBookScraper:
    """
    Main scraper class orchestrating the scraping process.
    """
    
    def __init__(
        self,
        output_file: str = OUTPUT_CSV,
        batch_size: int = BATCH_SIZE,
        max_workers: int = MAX_WORKERS,
        max_pages: Optional[int] = None,
    ) -> None:
        """
        Initialize the scraper.
        
        Args:
            output_file: Output CSV file path
            batch_size: Number of books per batch before writing
            max_workers: Number of concurrent threads
            max_pages: Maximum number of pages to scrape (None = all)
        """
        self.output_file = output_file
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.max_pages = max_pages
        self.session = create_session_with_retries()
        self.csv_writer = ThreadSafeCSVWriter(output_file, list(Book(
            title="", price="", rating="", availability="", url=""
        ).to_dict().keys()))
        self.all_books: List[Book] = []
    
    def scrape(self) -> Dict[str, Any]:
        """
        Execute the scraping process.
        
        Returns:
            Dictionary with scraping statistics
        """
        logger.info("Starting scraper...")
        start_time = time.time()
        
        try:
            # Get all page URLs
            page_urls = self.get_page_urls(self.max_pages)
            
            if not page_urls:
                logger.warning("No pages found to scrape")
                return {
                    "total_books": 0,
                    "total_pages": 0,
                    "duration_seconds": time.time() - start_time,
                    "success": False,
                }
            
            # Scrape pages concurrently
            self.scrape_pages_concurrent(page_urls)
            
            # Write remaining books
            self.flush_remaining_books()
            
            duration = time.time() - start_time
            logger.info(f"Scraping completed in {duration:.2f} seconds")
            
            return {
                "total_books": len(self.all_books),
                "total_pages": len(page_urls),
                "duration_seconds": duration,
                "success": True,
            }
        
        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return {
                "total_books": 0,
                "total_pages": 0,
                "duration_seconds": time.time() - start_time,
                "success": False,
                "error": str(e),
            }
        
        finally:
            self.session.close()
            logger.info("Session closed")
    
    def get_page_urls(self, max_pages: Optional[int] = None) -> List[str]:
        """Get all page URLs."""
        return get_page_urls(self.session, max_pages)
    
    def scrape_pages_concurrent(self, page_urls: List[str]) -> None:
        """
        Scrape multiple pages concurrently.
        
        Args:
            page_urls: List of page URLs to scrape
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(scrape_page_books, self.session, url): url
                for url in page_urls
            }
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    books = future.result()
                    self.all_books.extend(books)
                    
                    # Write batch if threshold reached
                    if len(self.all_books) >= self.batch_size:
                        self.write_batch()
                
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
    
    def write_batch(self) -> None:
        """Write accumulated books to CSV."""
        if self.all_books:
            batch = [book.to_dict() for book in self.all_books[:self.batch_size]]
            self.csv_writer.write_batch(batch)
            self.all_books = self.all_books[self.batch_size:]
    
    def flush_remaining_books(self) -> None:
        """Write any remaining books to CSV."""
        if self.all_books:
            batch = [book.to_dict() for book in self.all_books]
            self.csv_writer.write_batch(batch)
            self.all_books = []


# ============================================================================
# CLI Interface
# ============================================================================

def main() -> None:
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Robust Web Scraper for books.toscrape.com")
    logger.info("=" * 70)
    
    scraper = RobustBookScraper(
        output_file=OUTPUT_CSV,
        batch_size=BATCH_SIZE,
        max_workers=MAX_WORKERS,
        max_pages=None,  # Change to integer to limit pages (e.g., 2 for testing)
    )
    
    results = scraper.scrape()
    
    logger.info("=" * 70)
    logger.info("Scraping Results:")
    logger.info(f"  Total Books: {results['total_books']}")
    logger.info(f"  Total Pages: {results['total_pages']}")
    logger.info(f"  Duration: {results['duration_seconds']:.2f} seconds")
    logger.info(f"  Success: {results['success']}")
    logger.info(f"  Output File: {OUTPUT_CSV}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
