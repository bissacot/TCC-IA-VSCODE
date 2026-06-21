"""
Robust Web Scraper for http://books.toscrape.com/

A production-ready concurrent web scraper with:
- Modular design with Type Hints
- Native logging
- requests.Session for TCP reuse
- Retry mechanisms with exponential backoff
- ThreadPoolExecutor for parallel processing
- Thread-safe batch CSV writing
"""

import csv
import logging
import logging.handlers
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Optional, Generator, List, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(log_file: str = "scraper.log", level: int = logging.INFO) -> logging.Logger:
    """Configure logging with both file and console handlers."""
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create formatters
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ScraperConfig:
    """Configuration for the web scraper."""
    base_url: str = "http://books.toscrape.com/"
    output_file: str = "books.csv"
    batch_size: int = 50
    max_retries: int = 3
    backoff_factor: float = 0.5
    timeout: int = 10
    max_workers: int = 5
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class Book:
    """Data class representing a book."""
    title: str
    price: str
    availability: str
    rating: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        """Convert book data to dictionary."""
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "rating": self.rating,
            "url": self.url
        }


# ============================================================================
# SESSION MANAGEMENT WITH RETRY LOGIC
# ============================================================================

def create_session_with_retries(
    config: ScraperConfig,
) -> requests.Session:
    """
    Create a requests Session with retry strategy and exponential backoff.
    
    Args:
        config: ScraperConfig instance with retry settings
        
    Returns:
        Configured requests.Session object
    """
    session = requests.Session()

    # Configure retry strategy with exponential backoff
    retry_strategy = Retry(
        total=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET", "HEAD"]
    )

    # Mount adapter with retry strategy for both HTTP and HTTPS
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set user agent
    session.headers.update({"User-Agent": config.user_agent})

    return session


# ============================================================================
# WEB SCRAPING LOGIC
# ============================================================================

class BookScraper:
    """Modular book scraper with concurrent processing capabilities."""

    def __init__(self, config: ScraperConfig):
        """
        Initialize the scraper.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
        self.session = create_session_with_retries(config)
        self.csv_lock = Lock()
        self.books_batch: List[Book] = []
        self.batch_lock = Lock()
        logger.info(f"BookScraper initialized with config: {config}")

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page with built-in error handling and retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if fetch fails
        """
        try:
            logger.debug(f"Fetching URL: {url}")
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url} (Status: {response.status_code})")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}", exc_info=True)
            return None

    def parse_books_from_html(self, html: str, page_url: str) -> List[Book]:
        """
        Parse book information from HTML content.
        
        Args:
            html: HTML content
            page_url: URL of the page being parsed
            
        Returns:
            List of Book objects
        """
        books = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            book_containers = soup.find_all("article", class_="product_pod")
            logger.debug(f"Found {len(book_containers)} books in HTML")

            for container in book_containers:
                try:
                    title_elem = container.find("h3").find("a")
                    title = title_elem.get("title", "N/A") if title_elem else "N/A"

                    price_elem = container.find("p", class_="price_color")
                    price = price_elem.get_text(strip=True) if price_elem else "N/A"

                    availability_elem = container.find("p", class_="instock availability")
                    availability = availability_elem.get_text(strip=True) if availability_elem else "N/A"

                    rating_elem = container.find("p", class_="star-rating")
                    rating = rating_elem.get("class")[1] if rating_elem else "N/A"

                    # Extract relative URL and build full URL
                    href = title_elem.get("href", "") if title_elem else ""
                    book_url = self._build_absolute_url(href, page_url)

                    book = Book(
                        title=title,
                        price=price,
                        availability=availability,
                        rating=rating,
                        url=book_url
                    )
                    books.append(book)
                    logger.debug(f"Parsed book: {title}")

                except (AttributeError, IndexError) as e:
                    logger.warning(f"Failed to parse individual book: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing HTML: {e}", exc_info=True)

        logger.info(f"Successfully parsed {len(books)} books from page")
        return books

    def _build_absolute_url(self, relative_url: str, page_url: str) -> str:
        """Build absolute URL from relative URL."""
        if relative_url.startswith("http"):
            return relative_url
        
        base = self.config.base_url.rstrip("/")
        relative_url = relative_url.lstrip("./")
        return f"{base}/{relative_url}"

    def get_all_page_urls(self) -> List[str]:
        """
        Discover all page URLs from the catalogue.
        
        Returns:
            List of all page URLs to scrape
        """
        urls = [self.config.base_url]
        page_num = 2

        while True:
            next_url = f"{self.config.base_url}catalogue/page-{page_num}.html"
            html = self.fetch_page(next_url)

            if html is None:
                logger.info(f"Reached end of pagination at page {page_num}")
                break

            if "404 Not Found" in html or "Page not found" in html:
                logger.info(f"Reached end of pagination at page {page_num}")
                break

            urls.append(next_url)
            logger.info(f"Found page {page_num}")
            page_num += 1
            time.sleep(0.5)  # Be respectful to the server

        logger.info(f"Total pages discovered: {len(urls)}")
        return urls

    @contextmanager
    def _csv_writer_context(self) -> Generator[csv.DictWriter, None, None]:
        """
        Thread-safe context manager for CSV writing.
        
        Yields:
            csv.DictWriter object
        """
        with self.csv_lock:
            output_path = Path(self.config.output_file)
            file_exists = output_path.exists()

            with open(output_path, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["title", "price", "availability", "rating", "url"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    logger.info(f"Creating new CSV file: {self.config.output_file}")
                    writer.writeheader()

                yield writer

    def save_books_to_csv(self, books: List[Book]) -> None:
        """
        Save books to CSV file in a thread-safe manner.
        
        Args:
            books: List of Book objects to save
        """
        if not books:
            logger.debug("No books to save")
            return

        try:
            with self._csv_writer_context() as writer:
                for book in books:
                    writer.writerow(book.to_dict())
            logger.info(f"Saved {len(books)} books to CSV")
        except IOError as e:
            logger.error(f"Failed to write to CSV: {e}", exc_info=True)

    def scrape_page(self, page_url: str) -> int:
        """
        Scrape a single page and save books.
        
        Args:
            page_url: URL to scrape
            
        Returns:
            Number of books scraped
        """
        html = self.fetch_page(page_url)
        if html is None:
            return 0

        books = self.parse_books_from_html(html, page_url)
        self.save_books_to_csv(books)
        return len(books)

    def scrape_concurrent(self) -> None:
        """
        Perform concurrent scraping of all pages using ThreadPoolExecutor.
        """
        logger.info("Starting concurrent scraping...")
        start_time = datetime.now()

        # Get all page URLs
        page_urls = self.get_all_page_urls()
        logger.info(f"Starting to scrape {len(page_urls)} pages concurrently")

        total_books = 0
        failed_pages = 0

        # Use ThreadPoolExecutor for concurrent page scraping
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.scrape_page, url): url
                for url in page_urls
            }

            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    books_count = future.result()
                    total_books += books_count
                    logger.info(f"Completed: {url} - {books_count} books scraped")
                except Exception as e:
                    failed_pages += 1
                    logger.error(f"Exception occurred while scraping {url}: {e}", exc_info=True)

        elapsed_time = datetime.now() - start_time
        logger.info(
            f"Scraping completed in {elapsed_time.total_seconds():.2f}s - "
            f"Total books: {total_books}, Failed pages: {failed_pages}"
        )

    def close(self) -> None:
        """Clean up resources."""
        self.session.close()
        logger.info("Scraper session closed")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> None:
    """Main execution function."""
    try:
        logger.info("=" * 80)
        logger.info("ROBUST WEB SCRAPER STARTED")
        logger.info("=" * 80)

        # Initialize configuration
        config = ScraperConfig()
        logger.info(f"Configuration: {config}")

        # Initialize scraper
        scraper = BookScraper(config)

        # Perform concurrent scraping
        scraper.scrape_concurrent()

        # Clean up
        scraper.close()

        logger.info("=" * 80)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY")
        logger.info(f"Results saved to: {config.output_file}")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
    except Exception as e:
        logger.critical(f"Critical error in main execution: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
