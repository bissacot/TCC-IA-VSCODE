from __future__ import annotations

import csv
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "http://books.toscrape.com/"
CSV_FILE = "books.csv"
MAX_WORKERS = 10
BATCH_SIZE = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
)
LOGGER = logging.getLogger("robust_scraper")


@dataclass
class BookRecord:
    title: str
    price: str
    availability: str
    category: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "category": self.category,
            "url": self.url,
        }


class CSVBatchWriter:
    def __init__(self, path: Path, fieldnames: List[str], batch_size: int = 20) -> None:
        self.path = path
        self.fieldnames = fieldnames
        self.batch_size = batch_size
        self._lock = threading.Lock()
        self._buffer: List[Dict[str, str]] = []
        self._initialized = False

    def __enter__(self) -> "CSVBatchWriter":
        self._ensure_file()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.flush()

    def _ensure_file(self) -> None:
        if self._initialized:
            return
        is_new = not self.path.exists()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if is_new:
            with self.path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=self.fieldnames)
                writer.writeheader()
        self._initialized = True

    def write_batch(self, rows: List[Dict[str, str]]) -> None:
        if not rows:
            return
        with self._lock:
            self._buffer.extend(rows)
            if len(self._buffer) >= self.batch_size:
                self._flush_locked()

    def flush(self) -> None:
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self._buffer:
            return
        with self.path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fieldnames)
            writer.writerows(self._buffer)
        LOGGER.info("Flushed %d rows to %s", len(self._buffer), self.path)
        self._buffer.clear()


def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "robust-scraper/1.0"})
    return session


def retry_with_backoff(max_attempts: int = 5, initial_delay: float = 1.0) -> Any:
    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as exc:
                    if attempt == max_attempts:
                        LOGGER.error("Exceeded retries for %s: %s", func.__name__, exc)
                        raise
                    LOGGER.warning(
                        "Request failed (%s attempt %d/%d). Retrying in %.1f seconds...",
                        func.__name__,
                        attempt,
                        max_attempts,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator


@retry_with_backoff(max_attempts=5, initial_delay=1.0)
def fetch_url(session: requests.Session, url: str, timeout: int = 15) -> str:
    LOGGER.debug("Fetching %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_book_links(page_html: str, page_url: str) -> List[str]:
    matches = re.findall(r"<h3>\s*<a href=\"(.*?)\"", page_html)
    if not matches:
        LOGGER.debug("No book links found on page %s", page_url)
        return []
    return [urljoin(page_url, link.replace("../../../", "../")) for link in matches]


def parse_next_page(page_html: str, page_url: str) -> Optional[str]:
    match = re.search(r"<li class=\"next\">\s*<a href=\"(.*?)\"", page_html)
    if not match:
        return None
    return urljoin(page_url, match.group(1))


def parse_book_data(page_html: str, book_url: str) -> BookRecord:
    title_match = re.search(r"<div class=\"product_main\">.*?<h1>([^<]+)</h1>", page_html, re.S)
    price_match = re.search(r"<p class=\"price_color\">([^<]+)</p>", page_html)
    availability_match = re.search(
        r"<p class=\"instock availability\">\s*<i class=\"icon-ok\"></i>\s*([^<]+)",
        page_html,
    )
    category_match = re.search(
        r"<ul class=\"breadcrumb\">.*?<li><a href=\".*?\">Books</a></li>.*?<li><a href=\".*?\">([^<]+)</a></li>",
        page_html,
        re.S,
    )
    description_match = re.search(
        r"<div id=\"product_description\">.*?<p>(.*?)</p>", page_html, re.S,
    )

    title = title_match.group(1).strip() if title_match else "Unknown Title"
    price = price_match.group(1).strip() if price_match else "Unknown Price"
    availability = availability_match.group(1).strip() if availability_match else "Unknown Availability"
    category = category_match.group(1).strip() if category_match else "Unknown Category"
    if description_match:
        availability = f"{availability} | {description_match.group(1).strip()}"

    LOGGER.debug("Parsed book record %s", title)
    return BookRecord(title=title, price=price, availability=availability, category=category, url=book_url)


def discover_page_urls(session: requests.Session, start_url: str) -> List[str]:
    page_urls: List[str] = [start_url]
    current_url = start_url

    while True:
        html = fetch_url(session, current_url)
        next_page = parse_next_page(html, current_url)
        if not next_page:
            break
        LOGGER.info("Discovered page URL %s", next_page)
        page_urls.append(next_page)
        current_url = next_page

    LOGGER.info("Discovered %d total pages", len(page_urls))
    return page_urls


def scrape_book(session: requests.Session, book_url: str) -> Optional[BookRecord]:
    try:
        html = fetch_url(session, book_url)
        return parse_book_data(html, book_url)
    except requests.RequestException as exc:
        LOGGER.error("Failed to scrape book %s: %s", book_url, exc)
        return None


def scrape_page(session: requests.Session, page_url: str, executor: ThreadPoolExecutor) -> List[BookRecord]:
    html = fetch_url(session, page_url)
    book_links = parse_book_links(html, page_url)
    LOGGER.info("Page %s contains %d books", page_url, len(book_links))
    futures = [executor.submit(scrape_book, session, url) for url in book_links]
    books: List[BookRecord] = []

    for future in as_completed(futures):
        record = future.result()
        if record:
            books.append(record)

    LOGGER.info("Completed processing %d books from page %s", len(books), page_url)
    return books


def scrape_all_books(start_url: str, output_path: Path) -> None:
    session = create_session()
    page_urls = discover_page_urls(session, start_url)
    writer = CSVBatchWriter(output_path, ["title", "price", "availability", "category", "url"], batch_size=BATCH_SIZE)

    with writer, ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for page_url in page_urls:
            try:
                books = scrape_page(session, page_url, executor)
                writer.write_batch([book.to_dict() for book in books])
            except requests.RequestException as exc:
                LOGGER.error("Failed to scrape page %s: %s", page_url, exc)

    LOGGER.info("Scraping complete. Output written to %s", output_path)


def main() -> None:
    output_path = Path(CSV_FILE)
    LOGGER.info("Starting scraper for %s", BASE_URL)
    scrape_all_books(BASE_URL, output_path)


if __name__ == "__main__":
    main()
