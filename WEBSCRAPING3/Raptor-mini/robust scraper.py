from __future__ import annotations

import csv
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html import unescape
from queue import Queue
from typing import Iterator, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "http://books.toscrape.com/"
CSV_FILE = "books.csv"
BATCH_SIZE = 25
MAX_WORKERS = 8
TIMEOUT_SECONDS = 10
RETRY_TOTAL = 5
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_FORCELIST = (429, 500, 502, 503, 504)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s %(message)s",
)
logger = logging.getLogger(__name__)

_write_lock = threading.Lock()


@dataclass(frozen=True)
class Book:
    title: str
    price: str
    availability: str
    rating: str
    product_page_url: str

    def to_csv_row(self) -> List[str]:
        return [self.title, self.price, self.availability, self.rating, self.product_page_url]


def create_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_FORCELIST,
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "robust-scraper/1.0"})
    return session


def parse_total_pages(html: str) -> int:
    match = re.search(r"Page 1 of (\d+)", html)
    if match:
        total_pages = int(match.group(1))
        logger.debug("Total pages detected: %d", total_pages)
        return total_pages
    return 1


def normalize_url(relative_url: str) -> str:
    if relative_url.startswith("http"):
        return relative_url
    return BASE_URL.rstrip("/") + "/" + relative_url.lstrip("./")


def parse_books_from_page(html: str) -> List[Book]:
    books: List[Book] = []
    for item in re.finditer(r"<article class=\"product_pod\">(.*?)</article>", html, re.S):
        block = item.group(1)
        title_match = re.search(r"title=\"([^\"]+)\"", block)
        price_match = re.search(r"<p class=\"price_color\">([^<]+)</p>", block)
        availability_match = re.search(r"<p class=\"instock availability\">\s*([^<]+)", block)
        rating_match = re.search(r"<p class=\"star-rating ([A-Za-z]+)\">", block)
        href_match = re.search(r"<a href=\"([^\"]+)\">", block)

        if not (title_match and price_match and availability_match and rating_match and href_match):
            logger.debug("Skipped incomplete book entry")
            continue

        title = unescape(title_match.group(1).strip())
        price = price_match.group(1).strip()
        availability = availability_match.group(1).strip()
        rating = rating_match.group(1).strip()
        product_page_url = normalize_url(href_match.group(1))

        books.append(Book(title, price, availability, rating, product_page_url))

    logger.info("Parsed %d books from page", len(books))
    return books


def fetch_page(session: requests.Session, url: str, retries: int = RETRY_TOTAL) -> Optional[str]:
    attempt = 0
    while attempt <= retries:
        try:
            logger.debug("Fetching URL: %s (attempt=%d)", url, attempt + 1)
            response = session.get(url, timeout=TIMEOUT_SECONDS)
            if response.ok:
                return response.text
            logger.warning("Non-success status %d for %s", response.status_code, url)
        except requests.RequestException as exc:
            logger.warning("Request exception for %s: %s", url, exc)
        attempt += 1
        sleep_time = RETRY_BACKOFF_FACTOR * (2 ** (attempt - 1))
        logger.debug("Sleeping %.2f seconds before retry", sleep_time)
        time.sleep(sleep_time)
    logger.error("Failed to fetch page after %d attempts: %s", retries + 1, url)
    return None


class CsvBatchWriter:
    def __init__(self, path: str, batch_size: int = BATCH_SIZE) -> None:
        self.path = path
        self.batch_size = batch_size
        self.queue: Queue[List[Book]] = Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_writer, name="CsvWriter", daemon=True)
        self._thread.start()

    def submit(self, books: List[Book]) -> None:
        if books:
            self.queue.put(books)
            logger.debug("Submitted %d books to writer queue", len(books))

    def close(self) -> None:
        self._stop_event.set()
        self.queue.put([])
        self._thread.join()
        logger.info("CSV writer stopped")

    def _run_writer(self) -> None:
        with _write_lock, open(self.path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Title", "Price", "Availability", "Rating", "ProductPageUrl"])
            buffer: List[Book] = []
            logger.info("CSV writer started writing to %s", self.path)
            while not self._stop_event.is_set() or not self.queue.empty():
                try:
                    batch = self.queue.get(timeout=1)
                except Exception:
                    continue
                if not batch and self._stop_event.is_set():
                    break
                buffer.extend(batch)
                if len(buffer) >= self.batch_size:
                    self._flush_buffer(writer, buffer)
            if buffer:
                self._flush_buffer(writer, buffer)

    def _flush_buffer(self, writer: csv.writer, buffer: List[Book]) -> None:
        for book in buffer:
            writer.writerow(book.to_csv_row())
        logger.info("Wrote %d records to CSV", len(buffer))
        buffer.clear()


def build_page_urls(session: requests.Session) -> List[str]:
    landing_html = fetch_page(session, BASE_URL)
    if landing_html is None:
        raise RuntimeError("Unable to fetch the landing page")
    total_pages = parse_total_pages(landing_html)
    if total_pages < 1:
        total_pages = 1

    if total_pages == 1:
        return [BASE_URL]

    return [f"{BASE_URL}catalogue/page-{page_num}.html" for page_num in range(1, total_pages + 1)]


def scrape_page(session: requests.Session, url: str) -> List[Book]:
    html = fetch_page(session, url)
    if html is None:
        return []
    return parse_books_from_page(html)


def chunked(iterable: List[str], chunk_size: int) -> Iterator[List[str]]:
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i : i + chunk_size]


def main() -> None:
    logger.info("Starting robust scraper")
    session = create_session()
    page_urls = build_page_urls(session)
    writer = CsvBatchWriter(CSV_FILE, batch_size=BATCH_SIZE)

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(scrape_page, session, url): url for url in page_urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    books = future.result()
                    if books:
                        writer.submit(books)
                    else:
                        logger.warning("No books parsed from %s", url)
                except Exception as exc:
                    logger.exception("Error scraping %s: %s", url, exc)
    finally:
        writer.close()
    logger.info("Scraping completed")


if __name__ == "__main__":
    main()
