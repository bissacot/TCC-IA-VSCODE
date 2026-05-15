#!/usr/bin/env python3
"""
Robust Production-Ready Web Scraper for books.toscrape.com

Installation Requirements:
    pip install requests beautifulsoup4 tenacity

Usage:
    python scraper_robusto.py
"""

import csv
import logging
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging with timestamp, level, and message.

    Args:
        log_file: Optional file path to write logs. Defaults to console only.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ============================================================================
# USER-AGENTS ROTATION
# ============================================================================

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]


def get_random_user_agent() -> str:
    """
    Get a random modern User-Agent string.

    Returns:
        Random User-Agent string.
    """
    return random.choice(USER_AGENTS)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Book:
    """
    Data model representing a book product.

    Attributes:
        title: Complete book title.
        price: Book price as string (with currency symbol).
        availability: Availability status text.
        rating: Rating in stars (1-5 as integer).
        image_url: Absolute URL of the book cover image.
    """
    title: str
    price: str
    availability: str
    rating: int
    image_url: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert book to dictionary.

        Returns:
            Dictionary representation of the book.
        """
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "rating": self.rating,
            "image_url": self.image_url,
        }


# ============================================================================
# HTTP REQUEST HANDLER WITH RETRY
# ============================================================================

class HTTPClient:
    """
    HTTP client with connection pooling, retry logic, and user-agent rotation.
    """

    def __init__(self, timeout: float = 10.0) -> None:
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.session = requests.Session()
        logger.info(f"HTTP client initialized with {timeout}s timeout")

    def _is_retryable_status(self, response: requests.Response) -> bool:
        """
        Check if response status code is retryable.

        Args:
            response: Response object to check.

        Returns:
            True if status code is retryable (429, 500, 502, 503, 504).
        """
        return response.status_code in (429, 500, 502, 503, 504)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(requests.RequestException)
            | retry_if_exception_type(requests.Timeout)
            | retry_if_result(lambda r: isinstance(r, requests.Response) and 429 <= r.status_code <= 599)
        ),
    )
    def get(self, url: str) -> requests.Response:
        """
        Perform GET request with exponential backoff retry.

        Args:
            url: URL to request.

        Returns:
            Response object.

        Raises:
            requests.RequestException: If all retries are exhausted.
        """
        headers = {"User-Agent": get_random_user_agent()}
        logger.debug(f"GET request to {url}")

        response = self.session.get(
            url,
            headers=headers,
            timeout=self.timeout,
            allow_redirects=True,
        )

        if self._is_retryable_status(response):
            logger.warning(f"Retryable status {response.status_code} for {url}")
            response.raise_for_status()

        response.raise_for_status()
        logger.debug(f"Successfully fetched {url}")
        return response

    def close(self) -> None:
        """Close HTTP session and release resources."""
        self.session.close()
        logger.debug("HTTP session closed")

    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


# ============================================================================
# HTML PARSER
# ============================================================================

class BookParser:
    """
    Parser for extracting book data from HTML.
    """

    BASE_URL = "http://books.toscrape.com"

    @staticmethod
    def parse_rating(rating_text: str) -> int:
        """
        Convert rating text to integer (1-5).

        Args:
            rating_text: Rating text (e.g., "Three", "Four").

        Returns:
            Rating as integer (1-5).

        Raises:
            ValueError: If rating text is invalid.
        """
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        rating = rating_map.get(rating_text.strip())
        if rating is None:
            raise ValueError(f"Invalid rating: {rating_text}")
        return rating

    @staticmethod
    def parse_books(html: str, page_url: str) -> List[Book]:
        """
        Extract book data from HTML.

        Args:
            html: HTML content as string.
            page_url: Current page URL for relative URL resolution.

        Returns:
            List of Book objects.
        """
        soup = BeautifulSoup(html, "html.parser")
        books: List[Book] = []

        book_elements = soup.select("article.product_pod")
        logger.debug(f"Found {len(book_elements)} books on page")

        for book_elem in book_elements:
            try:
                # Extract title
                title_elem = book_elem.select_one("h3 a")
                title = title_elem.get("title", "") if title_elem else ""

                # Extract price
                price_elem = book_elem.select_one("p.price_color")
                price = price_elem.text if price_elem else "N/A"

                # Extract availability
                availability_elem = book_elem.select_one("p.instock.availability")
                availability = availability_elem.text.strip() if availability_elem else "N/A"

                # Extract rating (in stars)
                rating_elem = book_elem.select_one("p.star-rating")
                rating_class = rating_elem.get("class", []) if rating_elem else []
                rating_text = next((c for c in rating_class if c != "star-rating"), "Zero")
                rating = BookParser.parse_rating(rating_text)

                # Extract image URL (absolute)
                image_elem = book_elem.select_one("img")
                image_relative_url = image_elem.get("src", "") if image_elem else ""
                image_url = urljoin(BookParser.BASE_URL, image_relative_url)

                book = Book(
                    title=title,
                    price=price,
                    availability=availability,
                    rating=rating,
                    image_url=image_url,
                )
                books.append(book)

            except (ValueError, AttributeError, IndexError) as e:
                logger.warning(f"Error parsing book element: {e}")
                continue

        logger.info(f"Successfully parsed {len(books)} books")
        return books

    @staticmethod
    def get_next_page_url(html: str) -> Optional[str]:
        """
        Extract next page URL from pagination.

        Args:
            html: HTML content as string.

        Returns:
            Next page URL or None if no next page exists.
        """
        soup = BeautifulSoup(html, "html.parser")
        next_btn = soup.select_one("li.next a")

        if next_btn:
            next_href = next_btn.get("href", "")
            next_url = urljoin("http://books.toscrape.com/catalogue/page-1.html", next_href)
            logger.debug(f"Found next page: {next_url}")
            return next_url

        logger.debug("No next page found")
        return None


# ============================================================================
# THREAD-SAFE CSV WRITER
# ============================================================================

class CSVWriter:
    """
    Thread-safe CSV writer for persisting book data.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize CSV writer.

        Args:
            file_path: Path to output CSV file.
        """
        self.file_path = Path(file_path)
        self.lock = threading.Lock()
        self.fieldnames = ["title", "price", "availability", "rating", "image_url"]

        # Initialize file with header if it doesn't exist
        if not self.file_path.exists():
            with self.lock:
                with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
            logger.info(f"Created CSV file: {self.file_path}")

    def write_books(self, books: List[Book]) -> None:
        """
        Write books to CSV file (thread-safe).

        Args:
            books: List of Book objects to write.
        """
        with self.lock:
            with open(self.file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                for book in books:
                    writer.writerow(book.to_dict())
            logger.info(f"Wrote {len(books)} books to {self.file_path}")


# ============================================================================
# SCRAPER ORCHESTRATOR
# ============================================================================

class BookScraper:
    """
    Main scraper orchestrator with pagination and concurrency support.
    """

    def __init__(
        self,
        base_url: str,
        output_file: str = "produtos.csv",
        timeout: float = 10.0,
        batch_size: int = 10,
    ) -> None:
        """
        Initialize scraper.

        Args:
            base_url: Base URL to start scraping from.
            output_file: Output CSV file path.
            timeout: HTTP request timeout in seconds.
            batch_size: Number of books to write per batch.
        """
        self.base_url = base_url
        self.http_client = HTTPClient(timeout=timeout)
        self.csv_writer = CSVWriter(output_file)
        self.batch_size = batch_size
        self.pages_to_scrape: List[str] = []
        self.total_books = 0
        logger.info(f"Scraper initialized for {base_url}")

    def discover_pages(self) -> List[str]:
        """
        Discover all pages by following pagination.

        Returns:
            List of page URLs to scrape.
        """
        logger.info("Starting page discovery")
        pages = [self.base_url]
        current_url = self.base_url

        while True:
            try:
                response = self.http_client.get(current_url)
                response.encoding = "utf-8"
                html = response.text

                next_url = BookParser.get_next_page_url(html)
                if not next_url:
                    break

                current_url = next_url
                pages.append(current_url)
                logger.debug(f"Discovered page {len(pages)}: {current_url}")

            except requests.RequestException as e:
                logger.error(f"Error discovering pages at {current_url}: {e}")
                break

        logger.info(f"Discovered {len(pages)} pages total")
        return pages

    def scrape_page(self, page_url: str) -> List[Book]:
        """
        Scrape a single page.

        Args:
            page_url: URL of the page to scrape.

        Returns:
            List of Book objects from the page.
        """
        try:
            response = self.http_client.get(page_url)
            response.encoding = "utf-8"
            html = response.text

            books = BookParser.parse_books(html, page_url)
            logger.info(f"Scraped {len(books)} books from {page_url}")

            # Write to CSV immediately (continuous write)
            if books:
                self.csv_writer.write_books(books)

            return books

        except requests.RequestException as e:
            logger.error(f"Error scraping page {page_url}: {e}")
            return []

    def run(self, max_workers: int = 4) -> int:
        """
        Run full scraping workflow with concurrent page processing.

        Args:
            max_workers: Maximum number of worker threads.

        Returns:
            Total number of books scraped.
        """
        logger.info(f"Starting scraper with {max_workers} workers")
        start_time = time.time()

        # Discover all pages
        self.pages_to_scrape = self.discover_pages()

        if not self.pages_to_scrape:
            logger.error("No pages discovered")
            return 0

        # Scrape pages concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(self.scrape_page, page): page
                for page in self.pages_to_scrape
            }

            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    books = future.result()
                    self.total_books += len(books)
                except Exception as e:
                    logger.error(f"Exception while processing {page}: {e}")

        elapsed_time = time.time() - start_time
        logger.info(
            f"Scraping completed: {self.total_books} books in {elapsed_time:.2f}s "
            f"({self.total_books / elapsed_time:.1f} books/sec)"
        )

        return self.total_books

    def close(self) -> None:
        """Close resources."""
        self.http_client.close()
        logger.debug("Scraper resources closed")

    def __enter__(self) -> "BookScraper":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Main entry point for the scraper.
    """
    logger.info("=" * 70)
    logger.info(f"Starting scraper at {datetime.now().isoformat()}")
    logger.info("=" * 70)

    try:
        with BookScraper(
            base_url="http://books.toscrape.com/catalogue/",
            output_file="produtos.csv",
            timeout=10.0,
            batch_size=10,
        ) as scraper:
            total_books = scraper.run(max_workers=4)
            logger.info(f"Total books scraped: {total_books}")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise

    logger.info("=" * 70)
    logger.info(f"Scraper finished at {datetime.now().isoformat()}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
