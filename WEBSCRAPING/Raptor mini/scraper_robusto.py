# pip install requests beautifulsoup4
"""Robust web scraper for books.toscrape.com."""

import argparse
import csv
import logging
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, RequestException, Timeout

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
LOGGER = logging.getLogger(__name__)


def build_headers() -> Dict[str, str]:
    """Build request headers with a randomized User-Agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


class RequestManager:
    """Manage HTTP requests with connection reuse and retry logic."""

    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 5,
        backoff_factor: float = 0.5,
        jitter: float = 0.5,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._jitter = jitter
        self._session = requests.Session()
        self._session_lock = threading.Lock()

    def __enter__(self) -> "RequestManager":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._session.close()

    def get(self, url: str) -> str:
        """Perform a GET request with retries and exponential backoff."""
        for attempt in range(1, self._max_retries + 1):
            headers = build_headers()
            try:
                with self._session_lock:
                    response = self._session.get(url, headers=headers, timeout=self._timeout)
                self._raise_for_retry(response)
                return response.text
            except (ConnectionError, Timeout, ReadTimeout, HTTPError) as exc:
                should_retry = self._should_retry(exc)
                if not should_retry or attempt == self._max_retries:
                    LOGGER.error("Request failed for %s after %s attempts: %s", url, attempt, exc)
                    raise
                delay = self._get_backoff_delay(attempt)
                LOGGER.warning(
                    "Retrying %s after %.2f seconds (attempt %s/%s): %s",
                    url,
                    delay,
                    attempt,
                    self._max_retries,
                    exc,
                )
                time.sleep(delay)
            except RequestException as exc:
                LOGGER.error("Non-retriable request error for %s: %s", url, exc)
                raise
        raise RuntimeError("Exceeded maximum retry attempts")

    def _raise_for_retry(self, response: Response) -> None:
        response.raise_for_status()
        if response.status_code in RETRY_STATUS_CODES:
            raise HTTPError(f"Retryable status code: {response.status_code}", response=response)

    def _should_retry(self, exc: Exception) -> bool:
        if isinstance(exc, HTTPError):
            response = getattr(exc, "response", None)
            return bool(response and response.status_code in RETRY_STATUS_CODES)
        return isinstance(exc, (ConnectionError, Timeout, ReadTimeout))

    def _get_backoff_delay(self, attempt: int) -> float:
        base = self._backoff_factor * (2 ** (attempt - 1))
        return min(60.0, base) + random.uniform(0, self._jitter)


class CsvWriter:
    """Thread-safe CSV writer for streaming product records."""

    def __init__(self, file_path: str, field_names: Iterable[str]) -> None:
        self._file_path = file_path
        self._field_names = list(field_names)
        self._lock = threading.Lock()
        self._file = None
        self._writer = None

    def __enter__(self) -> "CsvWriter":
        self._file = open(self._file_path, mode="w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self._field_names)
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._file:
            self._file.close()

    def write_rows(self, rows: List[Dict[str, str]]) -> None:
        """Write rows to CSV in a thread-safe way."""
        with self._lock:
            for row in rows:
                self._writer.writerow(row)
            self._file.flush()


def parse_rating(class_list: List[str]) -> int:
    """Convert the star-rating class name into an integer rating."""
    mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }
    for class_name in class_list:
        if class_name in mapping:
            return mapping[class_name]
    return 0


def parse_book_tag(book_tag: BeautifulSoup, page_url: str) -> Dict[str, str]:
    """Extract book information from a product card."""
    title_tag = book_tag.find("h3").find("a")
    title = title_tag["title"].strip() if title_tag and title_tag.has_attr("title") else title_tag.text.strip()
    price_tag = book_tag.find("p", class_="price_color")
    availability_tag = book_tag.find("p", class_="instock availability")
    image_tag = book_tag.find("img")
    rating_tag = book_tag.find("p", class_="star-rating")

    raw_image_src = image_tag["src"].strip() if image_tag and image_tag.has_attr("src") else ""
    image_url = urljoin(page_url, raw_image_src)
    rating = parse_rating(rating_tag.get("class", []) if rating_tag else [])

    return {
        "title": title,
        "price": price_tag.text.strip() if price_tag else "",
        "availability": availability_tag.text.strip() if availability_tag else "",
        "rating": str(rating),
        "image_url": image_url,
    }


def get_book_rows(html: str, page_url: str) -> List[Dict[str, str]]:
    """Parse product rows from a single page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    product_tags = soup.select("article.product_pod")
    return [parse_book_tag(tag, page_url) for tag in product_tags]


def find_next_page_url(html: str, current_url: str) -> Optional[str]:
    """Return the absolute URL to the next page when available."""
    soup = BeautifulSoup(html, "html.parser")
    next_element = soup.select_one("li.next > a")
    if not next_element or not next_element.has_attr("href"):
        return None
    return urljoin(current_url, next_element["href"].strip())


def discover_page_urls(request_manager: RequestManager, start_url: str) -> List[str]:
    """Discover all paginated page URLs by following the Next button."""
    page_urls: List[str] = []
    current_url = start_url

    while current_url:
        LOGGER.info("Discovering page URL: %s", current_url)
        html = request_manager.get(current_url)
        page_urls.append(current_url)
        next_url = find_next_page_url(html, current_url)
        if not next_url:
            break
        current_url = next_url

    LOGGER.info("Discovered %s pages for scraping.", len(page_urls))
    return page_urls


def process_page(page_url: str, request_manager: RequestManager, writer: CsvWriter) -> int:
    """Fetch, parse, and persist products for a single page."""
    try:
        html = request_manager.get(page_url)
        rows = get_book_rows(html, page_url)
        writer.write_rows(rows)
        LOGGER.info("Processed %s products from %s", len(rows), page_url)
        return len(rows)
    except Exception as exc:
        LOGGER.exception("Failed to process page %s: %s", page_url, exc)
        return 0


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Robust concurrent scraper for books.toscrape.com")
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent worker threads.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="produtos.csv",
        help="Output CSV file path.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        default="http://books.toscrape.com/",
        help="Starting URL for the scraper.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the scraping workflow."""
    args = parse_arguments()
    field_names = ["title", "price", "availability", "rating", "image_url"]

    with RequestManager() as request_manager, CsvWriter(args.output, field_names) as writer:
        page_urls = discover_page_urls(request_manager, args.start_url)

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(process_page, url, request_manager, writer) for url in page_urls]
            total_products = sum(future.result() for future in as_completed(futures))

    LOGGER.info("Scraping completed. Total products written: %s", total_products)


if __name__ == "__main__":
    main()
