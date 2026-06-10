"""
Installation:
    pip install requests beautifulsoup4 tenacity

Robust, resilient, and concurrent web scraper for books.toscrape.com.
Implements modular architecture with proper concurrency, retry logic, and persistence.
"""

import logging
import csv
import threading
import queue
import time
from typing import Optional, List, Dict, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import random

import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as UrlRetry


# Configure logging with timestamp, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


class UserAgentRotator:
    """
    Manages rotation of User-Agent strings for request headers.
    
    This class provides a pool of modern User-Agent strings and randomly
    selects one for each request to avoid detection as a bot.
    """
    
    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    @staticmethod
    def get_random_user_agent() -> str:
        """
        Get a random User-Agent string.
        
        Returns:
            str: A randomly selected User-Agent string.
        """
        return random.choice(UserAgentRotator.USER_AGENTS)


class SessionManager:
    """
    Manages HTTP session with connection pooling, retry strategy, and timeouts.
    
    Features:
    - TCP connection reuse via requests.Session
    - Exponential backoff retry with jitter
    - Configurable timeout (10 seconds)
    - Automatic retry on connection errors and specific HTTP status codes
    """
    
    TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    RETRY_CODES: tuple = (429, 500, 502, 503, 504)
    
    def __init__(self) -> None:
        """Initialize the session manager with configured session."""
        self.session: requests.Session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy and connection pooling.
        
        Returns:
            requests.Session: A configured session object with retry strategy.
        """
        session = requests.Session()
        
        # Configure urllib3 retry strategy for connection pooling
        retry_strategy = UrlRetry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=list(self.RETRY_CODES),
            allowed_methods=["GET", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        logger.debug("Session created with retry strategy")
        return session
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ))
    )
    def _fetch_with_retry(self, url: str, headers: Dict[str, str]) -> requests.Response:
        """
        Fetch URL with exponential backoff retry.
        
        Implements exponential backoff with jitter for resilience against
        temporary network failures and rate limiting.
        
        Args:
            url (str): The URL to fetch.
            headers (Dict[str, str]): HTTP headers to include in the request.
            
        Returns:
            requests.Response: The HTTP response object.
            
        Raises:
            requests.exceptions.RequestException: If request fails after retries.
            requests.exceptions.HTTPError: If HTTP status code indicates an error.
        """
        response = self.session.get(url, headers=headers, timeout=self.TIMEOUT)
        
        # Treat certain status codes as errors to trigger retry
        if response.status_code in self.RETRY_CODES:
            logger.warning(
                f"Received status {response.status_code} for {url}, "
                f"will retry with exponential backoff"
            )
            response.raise_for_status()
        
        response.raise_for_status()
        return response
    
    def get(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a URL with retry logic and exponential backoff.
        
        Args:
            url (str): The URL to fetch.
            
        Returns:
            Optional[requests.Response]: The response object, or None if all retries failed.
        """
        headers = {"User-Agent": UserAgentRotator.get_random_user_agent()}
        
        try:
            response = self._fetch_with_retry(url, headers)
            logger.info(f"Successfully fetched {url}")
            return response
        except Exception as e:
            logger.error(f"Failed to fetch {url} after {self.MAX_RETRIES} retries: {e}")
            return None
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        self.session.close()
        logger.debug("Session closed")


class BookParser:
    """
    Parses book data from HTML content using BeautifulSoup.
    
    Handles extraction of:
    - Book title
    - Price
    - Availability status
    - Star rating (converted to 1-5 integer)
    - Absolute image URL
    - Next page URL for pagination
    """
    
    @staticmethod
    def parse_books(html: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Parse books from HTML content.
        
        Extracts all book information from the provided HTML using CSS selectors.
        Handles parsing errors gracefully by logging warnings.
        
        Args:
            html (str): The HTML content to parse.
            base_url (str): The base URL for resolving relative image links.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing book data.
        """
        soup = BeautifulSoup(html, 'html.parser')
        books: List[Dict[str, Any]] = []
        
        for article in soup.find_all('article', class_='product_pod'):
            try:
                # Extract title
                title_elem = article.find('h3')
                if title_elem:
                    title_link = title_elem.find('a')
                    title = title_link.get('title', 'N/A') if title_link else 'N/A'
                else:
                    title = 'N/A'
                
                # Extract price
                price_elem = article.find('p', class_='price_color')
                price: str = price_elem.text if price_elem else 'N/A'
                
                # Extract availability
                availability_elem = article.find('p', class_='instock availability')
                availability: str = availability_elem.text.strip() if availability_elem else 'N/A'
                
                # Extract and convert star rating
                rating_elem = article.find('p', class_='star-rating')
                rating_text: str = rating_elem.get('class')[1] if rating_elem else 'N/A'
                rating: int = BookParser._convert_rating(rating_text)
                
                # Extract and resolve absolute image URL
                image_elem = article.find('img')
                image_url: str = urljoin(base_url, image_elem.get('src', '')) if image_elem else 'N/A'
                
                books.append({
                    'title': title,
                    'price': price,
                    'availability': availability,
                    'rating': rating,
                    'image_url': image_url
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse book article: {e}")
        
        logger.debug(f"Parsed {len(books)} books from page")
        return books
    
    @staticmethod
    def _convert_rating(rating_text: str) -> int:
        """
        Convert rating text to integer (1-5).
        
        Maps text representation of ratings (One, Two, Three, Four, Five)
        to numeric values.
        
        Args:
            rating_text (str): The rating text (e.g., 'Three').
            
        Returns:
            int: An integer from 1 to 5, or 0 if conversion fails.
        """
        rating_map: Dict[str, int] = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }
        return rating_map.get(rating_text, 0)
    
    @staticmethod
    def get_next_page_url(html: str, base_url: str) -> Optional[str]:
        """
        Extract the URL for the next page from pagination controls.
        
        Follows the "Next" button link if present to discover pagination.
        
        Args:
            html (str): The HTML content to parse.
            base_url (str): The base URL for resolving relative links.
            
        Returns:
            Optional[str]: The URL of the next page, or None if there's no next page.
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_button = soup.find('li', class_='next')
        
        if next_button:
            link_elem = next_button.find('a')
            if link_elem and link_elem.get('href'):
                next_url: str = link_elem.get('href')
                full_url: str = urljoin(base_url, next_url)
                logger.debug(f"Found next page: {full_url}")
                return full_url
        
        return None


class CSVWriter:
    """
    Thread-safe CSV writer for persistent data storage.
    
    Implements mutex-based locking to ensure safe concurrent writes from
    multiple threads. Uses context managers for resource management.
    """
    
    def __init__(self, filename: str) -> None:
        """
        Initialize the CSV writer.
        
        Args:
            filename (str): The output CSV filename.
        """
        self.filename: str = filename
        self.lock: threading.Lock = threading.Lock()
        self.fieldnames: List[str] = [
            'title',
            'price',
            'availability',
            'rating',
            'image_url'
        ]
        self._initialize_file()
    
    def _initialize_file(self) -> None:
        """
        Initialize the CSV file with headers.
        
        Creates the output file and writes the header row with column names.
        Thread-safe operation.
        """
        with self.lock:
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
        
        logger.info(f"CSV file initialized: {self.filename}")
    
    def write_rows(self, rows: List[Dict[str, Any]]) -> None:
        """
        Write rows to the CSV file in a thread-safe manner.
        
        Uses a lock to ensure that only one thread writes at a time,
        preventing data corruption or interleaving.
        
        Args:
            rows (List[Dict[str, Any]]): List of dictionaries to write.
        """
        if not rows:
            return
        
        with self.lock:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerows(rows)
        
        logger.info(f"Wrote {len(rows)} rows to {self.filename}")


class Scraper:
    """
    Main scraper orchestrator with concurrent processing.
    
    Manages:
    - URL discovery through pagination
    - Concurrent page fetching and processing
    - Thread-safe data persistence
    - Exponential backoff retry logic
    - Resource cleanup
    """
    
    def __init__(
        self,
        base_url: str,
        num_workers: int = 5,
        output_file: str = 'products.csv'
    ) -> None:
        """
        Initialize the scraper.
        
        Args:
            base_url (str): The starting URL to scrape.
            num_workers (int): The number of worker threads for concurrent fetching.
            output_file (str): The output CSV filename.
        """
        self.base_url: str = base_url
        self.num_workers: int = num_workers
        self.output_file: str = output_file
        self.session_manager: SessionManager = SessionManager()
        self.csv_writer: CSVWriter = CSVWriter(output_file)
        self.visited_urls: Set[str] = set()
        self.url_lock: threading.Lock = threading.Lock()
        
        logger.info(
            f"Scraper initialized: base_url={base_url}, "
            f"workers={num_workers}, output={output_file}"
        )
    
    def _process_page(self, url: str) -> Optional[str]:
        """
        Process a single page: fetch, parse, and write data.
        
        This method is executed by worker threads. It fetches a page,
        parses book data, writes to CSV, and returns the next page URL.
        Implements thread-safe visited URL tracking.
        
        Args:
            url (str): The URL to process.
            
        Returns:
            Optional[str]: The URL of the next page if it exists, None otherwise.
        """
        # Check if already visited (thread-safe)
        with self.url_lock:
            if url in self.visited_urls:
                logger.debug(f"URL already processed, skipping: {url}")
                return None
            self.visited_urls.add(url)
        
        logger.info(f"Worker thread processing: {url}")
        
        # Fetch page with retry logic
        response = self.session_manager.get(url)
        if response is None:
            logger.error(f"Failed to fetch {url}, skipping")
            return None
        
        # Parse books from page
        books = BookParser.parse_books(response.text, url)
        logger.info(f"Extracted {len(books)} books from {url}")
        
        # Write to CSV immediately (not accumulating in memory)
        self.csv_writer.write_rows(books)
        
        # Discover next page
        next_url = BookParser.get_next_page_url(response.text, url)
        return next_url
    
    def scrape(self) -> None:
        """
        Execute the scraping operation with concurrent processing.
        
        Uses ThreadPoolExecutor to fetch and process pages concurrently.
        Dynamically discovers pages by following the "Next" button and adds
        them to a queue for concurrent processing. Implements graceful
        shutdown of thread pool and resource cleanup.
        """
        logger.info(f"Starting scraper with {self.num_workers} worker threads")
        
        # Use a queue to manage URLs to process
        url_queue: queue.Queue = queue.Queue()
        url_queue.put(self.base_url)
        
        total_pages: int = 0
        
        try:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures: Dict[Any, str] = {}
                
                # Process URLs from queue and submit to thread pool
                while not url_queue.empty() or futures:
                    # Submit new tasks while we have URLs in the queue
                    # and haven't reached the worker limit
                    while not url_queue.empty() and len(futures) < self.num_workers:
                        url = url_queue.get()
                        future = executor.submit(self._process_page, url)
                        futures[future] = url
                    
                    # Wait for at least one task to complete
                    if futures:
                        try:
                            # Process completed futures
                            for future in as_completed(futures.keys(), timeout=30):
                                url = futures.pop(future)
                                
                                try:
                                    next_url = future.result()
                                    total_pages += 1
                                    
                                    # If there's a next page, add to queue
                                    if next_url:
                                        logger.info(f"Discovered next page: {next_url}")
                                        url_queue.put(next_url)
                                    else:
                                        logger.info(f"No next page found for: {url}")
                                        
                                except Exception as e:
                                    logger.error(f"Error processing {url}: {e}")
                        except Exception as e:
                            logger.warning(f"Timeout waiting for futures: {e}")
                            continue
        
        except Exception as e:
            logger.error(f"Scraping interrupted: {e}")
        
        finally:
            # Cleanup resources
            self.session_manager.close()
            logger.info(
                f"Scraping completed. Total pages processed: {total_pages}. "
                f"Data saved to: {self.output_file}"
            )


def main() -> None:
    """
    Main entry point for the scraper.
    
    Configures and starts the scraping operation for books.toscrape.com.
    """
    base_url = 'http://books.toscrape.com/'
    num_workers = 5
    output_file = 'products.csv'
    
    logger.info("=" * 80)
    logger.info("Starting Books Scraper")
    logger.info("=" * 80)
    
    scraper = Scraper(
        base_url=base_url,
        num_workers=num_workers,
        output_file=output_file
    )
    
    start_time = time.time()
    scraper.scrape()
    elapsed_time = time.time() - start_time
    
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
