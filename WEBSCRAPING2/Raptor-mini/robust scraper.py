import concurrent.futures
import csv
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from requests import Response, Session
from requests.exceptions import RequestException

BASE_URL = "http://books.toscrape.com/"
OUTPUT_CSV = Path("books.csv")
BATCH_SIZE = 20
MAX_WORKERS = 8
RETRY_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 1.5
HTTP_STATUS_RETRY = {429, 500, 502, 503, 504}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s - %(message)s",
)
logger = logging.getLogger("robust_scraper")


@dataclass(frozen=True)
class BookRecord:
    title: str
    price: str
    availability: str
    rating: str
    url: str

    def to_row(self) -> List[str]:
        return [self.title, self.price, self.availability, self.rating, self.url]


class CsvWriter:
    def __init__(self, output_path: Path, batch_size: int = BATCH_SIZE) -> None:
        self._output_path = output_path
        self._batch_size = batch_size
        self._lock = threading.Lock()
        self._buffer: List[BookRecord] = []
        self._file = None
        self._writer = None

    def __enter__(self) -> "CsvWriter":
        self._file = self._output_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["title", "price", "availability", "rating", "url"])
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.flush()
        if self._file:
            self._file.close()

    def add(self, record: BookRecord) -> None:
        with self._lock:
            self._buffer.append(record)
            if len(self._buffer) >= self._batch_size:
                self._flush_locked()

    def flush(self) -> None:
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self._buffer or self._writer is None:
            return
        rows = [record.to_row() for record in self._buffer]
        self._writer.writerows(rows)
        self._file.flush()
        self._buffer.clear()
        logger.debug("Flushed %d records to CSV", len(rows))


def retry_with_backoff(max_attempts: int = RETRY_ATTEMPTS, factor: float = RETRY_BACKOFF_FACTOR):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    response = func(*args, **kwargs)
                    if response.status_code in HTTP_STATUS_RETRY:
                        raise RequestException(f"Retryable status code: {response.status_code}")
                    return response
                except RequestException as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error("Request failed after %d attempts: %s", attempt, exc)
                        raise
                    delay = factor * (2 ** (attempt - 1))
                    logger.warning(
                        "Retrying request (attempt %d/%d) after %.1f sec due to: %s",
                        attempt,
                        max_attempts,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
        return wrapper
    return decorator


class RobustScraper:
    def __init__(self, base_url: str = BASE_URL, max_workers: int = MAX_WORKERS) -> None:
        self.base_url = base_url
        self.session = self._create_session()
        self.max_workers = max_workers

    @staticmethod
    def _create_session() -> Session:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "robust-scraper/1.0 (+https://github.com/)"
            }
        )
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=MAX_WORKERS, max_retries=0)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @retry_with_backoff()
    def _get(self, url: str, **kwargs) -> Response:
        logger.debug("GET %s", url)
        return self.session.get(url, timeout=15, **kwargs)

    def _get_page(self, page_url: str) -> Optional[str]:
        response = self._get(page_url)
        response.raise_for_status()
        return response.text

    def _parse_book_row(self, row_html: str) -> Optional[BookRecord]:
        try:
            title = row_html.split("title=\"")[1].split("\"")[0]
            relative_url = row_html.split("href=\"")[1].split("\"")[0]
            price = row_html.split("price_color")[1].split("£")[1].split("<")[0].strip()
            availability = row_html.split("availability")[1].split("<")[1].split(">")[1].strip()
            rating = row_html.split("star-rating ")[1].split("\"")[0].strip()
            absolute_url = urljoin(self.base_url, relative_url)
            return BookRecord(title=title, price=f"£{price}", availability=availability, rating=rating, url=absolute_url)
        except (IndexError, ValueError) as exc:
            logger.debug("Failed to parse book row: %s", exc)
            return None

    def _extract_books_from_page(self, page_content: str) -> List[BookRecord]:
        books: List[BookRecord] = []
        for row in page_content.split("<article class=\"product_pod\""):
            if "<h3>" not in row:
                continue
            record = self._parse_book_row(row)
            if record:
                books.append(record)
        logger.info("Parsed %d books from page", len(books))
        return books

    def _find_next_page(self, page_content: str, current_url: str) -> Optional[str]:
        if "next" not in page_content:
            return None
        try:
            next_fragment = page_content.split("<li class=\"next\"")[1]
            next_href = next_fragment.split("href=\"")[1].split("\"")[0]
            return urljoin(current_url, next_href)
        except IndexError:
            return None

    def scrape(self) -> None:
        current_url = self.base_url
        pages: List[str] = [current_url]

        while current_url:
            logger.info("Scheduling page fetch for %s", current_url)
            page_content = self._get_page(current_url)
            if page_content is None:
                break
            next_page = self._find_next_page(page_content, current_url)
            if next_page and next_page not in pages:
                pages.append(next_page)
            current_url = next_page

        logger.info("Found %d pages to scrape", len(pages))

        with CsvWriter(OUTPUT_CSV) as writer:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_page = {executor.submit(self._get_page, page_url): page_url for page_url in pages}
                for future in concurrent.futures.as_completed(future_to_page):
                    page_url = future_to_page[future]
                    try:
                        page_content = future.result()
                        if not page_content:
                            continue
                        records = self._extract_books_from_page(page_content)
                        for record in records:
                            writer.add(record)
                    except Exception as exc:
                        logger.error("Failed to scrape page %s: %s", page_url, exc)
            writer.flush()
        logger.info("Scraping complete. Data saved to %s", OUTPUT_CSV)


def main() -> None:
    scraper = RobustScraper()
    try:
        scraper.scrape()
    except Exception as exc:
        logger.exception("Unhandled exception during scraping: %s", exc)


if __name__ == "__main__":
    main()
