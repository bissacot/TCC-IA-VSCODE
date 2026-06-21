"""
Robust, resilient, concurrent, and production-ready web scraper for books.toscrape.com.
Features: Type hints, logging, request pooling, retry mechanisms, concurrent processing,
and thread-safe batch CSV writing.
"""

import logging
import csv
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


# ============================================================================
# Configuration and Constants
# ============================================================================

BASE_URL: str = "http://books.toscrape.com/"
OUTPUT_CSV: str = "books_data.csv"
MAX_WORKERS: int = 5
BATCH_SIZE: int = 50
REQUEST_TIMEOUT: int = 10
RETRY_ATTEMPTS: int = 3
BACKOFF_FACTOR: float = 0.5

# HTTP status codes to retry on
RETRY_STATUS_CODES: Set[int] = {429, 500, 502, 503, 504}

# CSV headers
CSV_HEADERS: List[str] = ["title", "price", "availability", "rating", "url"]


# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class NetworkException(ScraperException):
    """Exception for network-related errors."""
    pass


class ParsingException(ScraperException):
    """Exception for parsing-related errors."""
    pass


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Book:
    """Represents a book with extracted metadata."""
    title: str
    price: str
    availability: str
    rating: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        """Convert book to dictionary for CSV writing."""
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "rating": self.rating,
            "url": self.url,
        }


# ============================================================================
# Session Factory with Retry Strategy
# ============================================================================

class SessionFactory:
    """Factory for creating HTTP sessions with retry strategy."""

    @staticmethod
    def create_session() -> requests.Session:
        """
        Create a requests.Session with configured retry strategy and connection pooling.

        Returns:
            requests.Session: Configured session with retry mechanism and TCP pooling.

        Raises:
            ScraperException: If session creation fails.
        """
        try:
            session = requests.Session()

            # Configure retry strategy with exponential backoff
            retry_strategy = Retry(
                total=RETRY_ATTEMPTS,
                status_forcelist=list(RETRY_STATUS_CODES),
                allowed_methods=["GET"],
                backoff_factor=BACKOFF_FACTOR,
            )

            # Attach retry strategy to HTTP and HTTPS adapters
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            # Configure connection pooling
            session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            })

            logger.info("HTTP session created with retry strategy configured")
            return session

        except Exception as e:
            logger.error(f"Failed to create HTTP session: {e}")
            raise ScraperException(f"Session creation failed: {e}") from e


# ============================================================================
# Web Scraper
# ============================================================================

class BooksScraper:
    """Main scraper class for books.toscrape.com."""

    def __init__(self, base_url: str = BASE_URL, output_file: str = OUTPUT_CSV):
        """
        Initialize the scraper.

        Args:
            base_url: The base URL of the website to scrape.
            output_file: Path to the output CSV file.
        """
        self.base_url: str = base_url
        self.output_file: str = output_file
        self.session: requests.Session = SessionFactory.create_session()
        self.csv_lock: Lock = Lock()
        self.scraped_urls: Set[str] = set()
        self.books: List[Book] = []

        logger.info(f"BooksScraper initialized with base_url={base_url}, output_file={output_file}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure session is closed."""
        self.close()

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            logger.info("HTTP session closed")

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page with error handling and retry logic.

        Args:
            url: URL to fetch.

        Returns:
            HTML content of the page or None if fetching fails.

        Raises:
            NetworkException: If all retry attempts fail.
        """
        try:
            logger.debug(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url}")
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url} after retries: {e}")
            raise NetworkException(f"Network error fetching {url}: {e}") from e

    def parse_book(self, book_element, page_url: str) -> Optional[Book]:
        """
        Parse a book element from the page.

        Args:
            book_element: BeautifulSoup element representing a book.
            page_url: URL of the page containing the book.

        Returns:
            Book object or None if parsing fails.
        """
        try:
            title: str = book_element.h3.a.get("title", "N/A")
            price_text: str = book_element.find("p", class_="price_color").get_text()
            price: str = price_text.replace("£", "").strip() if price_text else "N/A"
            availability: str = book_element.find("p", class_="instock availability").get_text().strip()
            rating_text: str = book_element.find("p", class_="star-rating").get("class", ["N/A"])[1]
            url: str = urljoin(self.base_url, book_element.h3.a.get("href", ""))

            book = Book(
                title=title,
                price=price,
                availability=availability,
                rating=rating_text,
                url=url,
            )
            logger.debug(f"Parsed book: {title}")
            return book

        except (AttributeError, IndexError, ValueError) as e:
            logger.warning(f"Failed to parse book element from {page_url}: {e}")
            return None

    def scrape_page(self, url: str) -> List[Book]:
        """
        Scrape all books from a single page.

        Args:
            url: URL of the page to scrape.

        Returns:
            List of Book objects found on the page.
        """
        try:
            if url in self.scraped_urls:
                logger.debug(f"URL already scraped: {url}")
                return []

            html_content: str = self.fetch_page(url)
            soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

            books: List[Book] = []
            book_elements = soup.find_all("article", class_="product_pod")

            for book_element in book_elements:
                book = self.parse_book(book_element, url)
                if book:
                    books.append(book)

            self.scraped_urls.add(url)
            logger.info(f"Scraped {len(books)} books from {url}")
            return books

        except ParsingException as e:
            logger.error(f"Parsing error for {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return []

    def get_all_page_urls(self) -> List[str]:
        """
        Get all page URLs to scrape.

        Returns:
            List of all page URLs.
        """
        try:
            urls: List[str] = [self.base_url]
            page: int = 1

            while True:
                if page == 1:
                    url = self.base_url
                else:
                    url = urljoin(self.base_url, f"catalogue/page-{page}.html")

                try:
                    html_content: str = self.fetch_page(url)
                    soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

                    # Check if next page exists
                    next_button = soup.find("li", class_="next")
                    if not next_button:
                        break

                    if page > 1:
                        urls.append(url)

                    page += 1

                except NetworkException:
                    logger.warning(f"Failed to fetch page {page}, stopping pagination")
                    break

            logger.info(f"Found {len(urls)} pages to scrape")
            return urls

        except Exception as e:
            logger.error(f"Error discovering pages: {e}")
            return [self.base_url]

    def write_batch_to_csv(self, books_batch: List[Book]) -> None:
        """
        Write a batch of books to CSV file in a thread-safe manner.

        Args:
            books_batch: List of Book objects to write.
        """
        if not books_batch:
            return

        try:
            with self.csv_lock:
                file_exists: bool = Path(self.output_file).exists()

                with open(self.output_file, mode="a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)

                    # Write header only if file is new
                    if not file_exists:
                        writer.writeheader()
                        logger.info(f"Created new CSV file: {self.output_file}")

                    for book in books_batch:
                        writer.writerow(book.to_dict())

                logger.info(f"Wrote {len(books_batch)} books to CSV")

        except IOError as e:
            logger.error(f"Failed to write batch to CSV: {e}")
        except Exception as e:
            logger.error(f"Unexpected error writing to CSV: {e}")

    def scrape_concurrent(self) -> None:
        """
        Scrape all pages concurrently using ThreadPoolExecutor.
        """
        try:
            logger.info("Starting concurrent scraping...")
            page_urls: List[str] = self.get_all_page_urls()

            if not page_urls:
                logger.warning("No pages to scrape")
                return

            start_time: float = time.time()
            books_batch: List[Book] = []

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit all scraping tasks
                future_to_url: Dict = {
                    executor.submit(self.scrape_page, url): url
                    for url in page_urls
                }

                # Process completed tasks
                for future in as_completed(future_to_url):
                    url: str = future_to_url[future]

                    try:
                        books: List[Book] = future.result()
                        books_batch.extend(books)

                        # Write batch to CSV when batch size is reached
                        if len(books_batch) >= BATCH_SIZE:
                            self.write_batch_to_csv(books_batch)
                            books_batch = []

                    except Exception as e:
                        logger.error(f"Task failed for {url}: {e}")

                # Write remaining books
                if books_batch:
                    self.write_batch_to_csv(books_batch)

            elapsed_time: float = time.time() - start_time
            total_books: int = len(self.scraped_urls)
            logger.info(
                f"Scraping completed in {elapsed_time:.2f}s. "
                f"Total pages: {len(self.scraped_urls)}"
            )

        except Exception as e:
            logger.error(f"Critical error during concurrent scraping: {e}")
            raise

    def run(self) -> None:
        """Main execution method."""
        try:
            logger.info("Starting web scraper for books.toscrape.com")
            self.scrape_concurrent()
            logger.info("Scraping completed successfully")

        except Exception as e:
            logger.critical(f"Scraper failed: {e}")
            raise

        finally:
            self.close()


# ============================================================================
# Entry Point
# ============================================================================

def main() -> None:
    """Main entry point for the scraper."""
    try:
        logger.info("=" * 80)
        logger.info("Robust Web Scraper - Starting Execution")
        logger.info("=" * 80)

        with BooksScraper(base_url=BASE_URL, output_file=OUTPUT_CSV) as scraper:
            scraper.run()

        logger.info("=" * 80)
        logger.info("Scraper execution completed successfully")
        logger.info(f"Results saved to: {OUTPUT_CSV}")
        logger.info("=" * 80)

    except ScraperException as e:
        logger.error(f"Scraper error: {e}")
        exit(1)

    except KeyboardInterrupt:
        logger.warning("Scraper interrupted by user")
        exit(0)

    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
