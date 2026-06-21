"""robust_scraper.py

A production-ready, single-file web scraper for http://books.toscrape.com/

Features:
- Type hints throughout
- Native `logging`
- `requests.Session` with TCP reuse
- Exponential-backoff retry decorator for network/HTTP errors
- `concurrent.futures.ThreadPoolExecutor` for parallel fetching
- Thread-safe, batched CSV writer context manager

Usage: python robust_scraper.py --output books.csv --workers 10 --batch 50
"""
from __future__ import annotations

import argparse
import csv
import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests

try:
    from bs4 import BeautifulSoup
except Exception as exc:  # pragma: no cover - helpful runtime message
    raise ImportError(
        "BeautifulSoup is required. Install with: pip install beautifulsoup4 lxml"
    ) from exc

LOGGER = logging.getLogger("robust_scraper")


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    fmt = "%(asctime)s %(levelname)s [%(threadName)s] %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(level)


def retry(
    retries: int = 5,
    backoff_factor: float = 0.5,
    allowed_statuses: Optional[Iterable[int]] = None,
):
    """Decorator that retries a function on exceptions or on HTTP response codes.

    The wrapped function may return a requests.Response or raise requests exceptions.
    If the returned response has a status code in `allowed_statuses` or >=500 it will retry.
    """

    allowed_statuses = set(allowed_statuses or [429])

    def _decorator(func):
        def _wrapped(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    attempt += 1
                    resp = func(*args, **kwargs)
                    # If the function returns a Response, check status
                    if isinstance(resp, requests.Response):
                        status = resp.status_code
                        if status >= 500 or status in allowed_statuses:
                            raise requests.HTTPError(f"status={status}")
                    return resp
                except Exception as exc:
                    if attempt >= retries:
                        LOGGER.exception("Max retries reached")
                        raise
                    # exponential backoff with jitter
                    backoff = backoff_factor * (2 ** (attempt - 1))
                    jitter = backoff * 0.1
                    sleep_for = backoff + (jitter * (0.5 - time.time() % 1))
                    LOGGER.warning(
                        "Retry %d/%d after %0.2fs due to %s",
                        attempt,
                        retries,
                        sleep_for,
                        exc,
                    )
                    time.sleep(sleep_for)

        return _wrapped

    return _decorator


class HTTPClient:
    """Wraps requests.Session for connection reuse and provides get() with retries."""

    def __init__(self, base_headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "robust-scraper/1.0 (+https://example.com)",
                **(base_headers or {}),
            }
        )
        self.timeout = timeout

    @retry(retries=6, backoff_factor=0.8, allowed_statuses=[429])
    def get(self, url: str, **kwargs) -> requests.Response:
        LOGGER.debug("GET %s", url)
        resp = self.session.get(url, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp

    def close(self) -> None:
        try:
            self.session.close()
        except Exception:
            LOGGER.debug("Session close failed", exc_info=True)


@dataclass
class Book:
    title: str
    price: str
    availability: str
    rating: str
    category: str
    upc: Optional[str]
    product_page_url: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "rating": self.rating,
            "category": self.category,
            "upc": self.upc or "",
            "product_page_url": self.product_page_url,
        }


class CSVBatchWriter:
    """Thread-safe, batched CSV writer context manager."""

    def __init__(self, path: str, fieldnames: List[str], batch_size: int = 100) -> None:
        self.path = path
        self.fieldnames = fieldnames
        self.batch_size = max(1, batch_size)
        self._buffer: List[Dict[str, str]] = []
        self._lock = threading.Lock()
        self._file = None
        self._writer = None

    def __enter__(self) -> "CSVBatchWriter":
        # open file in append mode; write header if empty
        self._file = open(self.path, "a", newline='', encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        if self._file.tell() == 0:
            self._writer.writeheader()
            self._file.flush()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.flush()
        finally:
            try:
                if self._file:
                    self._file.close()
            except Exception:
                LOGGER.debug("Error closing CSV file", exc_info=True)

    def add(self, row: Dict[str, str]) -> None:
        with self._lock:
            self._buffer.append(row)
            if len(self._buffer) >= self.batch_size:
                self._flush_locked()

    def flush(self) -> None:
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self._buffer:
            return
        if not self._writer:
            raise RuntimeError("Writer not initialized")
        LOGGER.info("Flushing %d rows to %s", len(self._buffer), self.path)
        try:
            for row in self._buffer:
                self._writer.writerow(row)
            self._file.flush()
            self._buffer.clear()
        except Exception:
            LOGGER.exception("Failed to flush CSV buffer")


def parse_listing_page(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    urls: List[str] = []
    for article in soup.select("article.product_pod"):
        a = article.select_one("h3 > a")
        if a and a.get("href"):
            href = a["href"]
            full = urljoin(base_url, href)
            urls.append(full)
    return urls


def parse_book_page(html: str, page_url: str) -> Book:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("div.product_main > h1").get_text(strip=True)
    price = soup.select_one("p.price_color").get_text(strip=True) if soup.select_one("p.price_color") else ""
    availability = soup.select_one("p.availability").get_text(strip=True) if soup.select_one("p.availability") else ""
    # rating as text in class star-rating
    rating_tag = soup.select_one("p.star-rating")
    rating = ""
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating = next((c for c in classes if c != "star-rating"), "")
    # category from breadcrumb
    category = ""
    crumbs = soup.select("ul.breadcrumb li a")
    if len(crumbs) >= 3:
        category = crumbs[2].get_text(strip=True)
    # UPC from table
    upc = None
    table = soup.select_one("table.table.table-striped")
    if table:
        for row in table.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td and th.get_text(strip=True) == "UPC":
                upc = td.get_text(strip=True)
                break

    return Book(
        title=title,
        price=price,
        availability=availability,
        rating=rating,
        category=category,
        upc=upc,
        product_page_url=page_url,
    )


def crawl_listing_urls(client: HTTPClient, start_url: str) -> Iterable[str]:
    """Yield book detail URLs by following pagination from start_url."""
    next_url = start_url
    seen_pages = set()
    while next_url:
        if next_url in seen_pages:
            LOGGER.debug("Already visited page %s, stopping", next_url)
            break
        seen_pages.add(next_url)
        LOGGER.info("Fetching listing page: %s", next_url)
        resp = client.get(next_url)
        page_book_urls = parse_listing_page(resp.text, next_url)
        for u in page_book_urls:
            yield u
        # find next page link
        soup = BeautifulSoup(resp.text, "lxml")
        next_link = soup.select_one("li.next > a")
        if next_link and next_link.get("href"):
            next_url = urljoin(next_url, next_link["href"])
        else:
            break


def fetch_and_parse_book(client: HTTPClient, url: str) -> Optional[Book]:
    try:
        resp = client.get(url)
        book = parse_book_page(resp.text, url)
        LOGGER.debug("Parsed book: %s", book.title)
        return book
    except Exception:
        LOGGER.exception("Failed to fetch/parse %s", url)
        return None


def run_scraper(
    start_url: str,
    output: str,
    workers: int = 8,
    batch_size: int = 100,
    timeout: int = 10,
) -> None:
    client = HTTPClient(timeout=timeout)
    fieldnames = ["title", "price", "availability", "rating", "category", "upc", "product_page_url"]
    with CSVBatchWriter(output, fieldnames=fieldnames, batch_size=batch_size) as writer:
        try:
            # Prepare a list of book URLs by crawling listing pages (serial)
            book_urls: List[str] = list(crawl_listing_urls(client, start_url))
            LOGGER.info("Discovered %d book URLs", len(book_urls))

            # Fetch book pages concurrently and write in batches
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=workers) as exe:
                futures = {exe.submit(fetch_and_parse_book, client, u): u for u in book_urls}
                for fut in as_completed(futures):
                    url = futures[fut]
                    try:
                        book = fut.result()
                        if book:
                            writer.add(book.to_dict())
                    except Exception:
                        LOGGER.exception("Unhandled error processing %s", url)
        finally:
            client.close()


def build_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Robust concurrent scraper for books.toscrape.com")
    p.add_argument("--start", default="http://books.toscrape.com/", help="Start listing URL")
    p.add_argument("--output", default="books.csv", help="Output CSV file")
    p.add_argument("--workers", type=int, default=8, help="Number of worker threads")
    p.add_argument("--batch", type=int, default=50, help="CSV batch size")
    p.add_argument("--timeout", type=int, default=10, help="HTTP request timeout seconds")
    p.add_argument("--log-level", default="INFO", help="Log level, e.g. DEBUG or INFO")
    return p.parse_args()


def main() -> None:
    args = build_args()
    level = getattr(logging, args.log_level.upper(), logging.INFO)
    setup_logging(level=level)
    LOGGER.info("Starting scraper")
    run_scraper(start_url=args.start, output=args.output, workers=args.workers, batch_size=args.batch, timeout=args.timeout)
    LOGGER.info("Scraping finished")


if __name__ == "__main__":
    main()
