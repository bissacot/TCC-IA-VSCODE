#!/usr/bin/env python3
"""robust scraper.py

A resilient, concurrent scraper for http://books.toscrape.com/

Features:
- Type hints and dataclasses
- requests.Session with connection pooling
- Exponential backoff retry decorator for HTTP operations
- concurrent.futures.ThreadPoolExecutor for parallel processing
- Thread-safe batch CSV writer using a context manager
- Native logging
"""
from __future__ import annotations

import csv
import logging
import math
import random
import threading
import time
from dataclasses import dataclass, asdict
from typing import Callable, Dict, Generator, Iterable, List, Optional

import requests

try:
    from bs4 import BeautifulSoup
except Exception as exc:  # pragma: no cover - runtime dependency message
    raise RuntimeError(
        "BeautifulSoup (bs4) is required. Install with: pip install beautifulsoup4"
    ) from exc

from concurrent.futures import ThreadPoolExecutor, as_completed

LOGGER = logging.getLogger("robust_scraper")


@dataclass
class Book:
    title: str
    price: str
    availability: str
    rating: str
    product_page_url: str


def setup_logging(level: int = logging.INFO, logfile: Optional[str] = None) -> None:
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def exponential_backoff(
    max_retries: int = 5,
    base_delay: float = 0.5,
    factor: float = 2.0,
    jitter: float = 0.1,
    allowed_statuses: Iterable[int] = (500, 502, 503, 504),
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    response = func(*args, **kwargs)
                except requests.RequestException as e:
                    attempt += 1
                    if attempt > max_retries:
                        LOGGER.exception("Max retries exceeded for request")
                        raise
                    delay = base_delay * (factor ** (attempt - 1))
                    delay = delay * (1 + random.uniform(-jitter, jitter))
                    LOGGER.warning(
                        "Request failed (%s). Retry %d/%d after %.2fs",
                        e,
                        attempt,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                # If we got a response, check status
                if isinstance(response, requests.Response) and response.status_code in allowed_statuses:
                    attempt += 1
                    if attempt > max_retries:
                        LOGGER.error(
                            "Status %d persists after %d attempts", response.status_code, attempt
                        )
                        response.raise_for_status()
                    delay = base_delay * (factor ** (attempt - 1))
                    delay = delay * (1 + random.uniform(-jitter, jitter))
                    LOGGER.warning(
                        "Received status %d. Retry %d/%d after %.2fs",
                        response.status_code,
                        attempt,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                return response

        return wrapper

    return decorator


class CSVBatchWriter:
    """Thread-safe CSV batch writer.

    Usage:
        with CSVBatchWriter(path, fieldnames, batch_size=50) as writer:
            writer.add_rows(iterable_of_dicts)
    """

    def __init__(self, path: str, fieldnames: List[str], batch_size: int = 50, encoding: str = "utf-8"):
        self.path = path
        self.fieldnames = fieldnames
        self.batch_size = batch_size
        self.encoding = encoding
        self._lock = threading.Lock()
        self._buffer: List[Dict[str, str]] = []
        self._file = None
        self._writer: Optional[csv.DictWriter] = None

    def __enter__(self) -> "CSVBatchWriter":
        self._file = open(self.path, "w", newline="", encoding=self.encoding)
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            self.flush()
        finally:
            if self._file:
                self._file.close()

    def add_row(self, row: Dict[str, str]) -> None:
        with self._lock:
            self._buffer.append(row)
            if len(self._buffer) >= self.batch_size:
                self._flush_no_lock()

    def add_rows(self, rows: Iterable[Dict[str, str]]) -> None:
        with self._lock:
            for r in rows:
                self._buffer.append(r)
                if len(self._buffer) >= self.batch_size:
                    self._flush_no_lock()

    def flush(self) -> None:
        with self._lock:
            self._flush_no_lock()

    def _flush_no_lock(self) -> None:
        if not self._buffer:
            return
        if not self._writer:
            raise RuntimeError("Writer not initialized")
        for row in self._buffer:
            self._writer.writerow(row)
        self._file.flush()
        self._buffer.clear()


class Scraper:
    BASE_URL = "http://books.toscrape.com/"

    def __init__(self, session: Optional[requests.Session] = None, max_workers: int = 8, timeout: int = 10):
        self.session = session or self._create_session()
        self.max_workers = max_workers
        self.timeout = timeout

    @staticmethod
    def _create_session() -> requests.Session:
        s = requests.Session()
        # Keep a reasonable pool size
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        return s

    @exponential_backoff()
    def _get(self, url: str, **kwargs) -> requests.Response:
        LOGGER.debug("GET %s", url)
        resp = self.session.get(url, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp

    def crawl_index_pages(self, start: str = "") -> List[str]:
        """Crawl paginated index pages and return product page URLs (absolute)."""
        urls: List[str] = []
        next_url = self.BASE_URL + start
        while next_url:
            LOGGER.info("Fetching index page: %s", next_url)
            resp = self._get(next_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            # find all product links on page
            for article in soup.select("article.product_pod"):
                a = article.find("a")
                href = a.get("href")
                if href:
                    # href can be relative like '../../../catalogue/...'
                    full = requests.compat.urljoin(next_url, href)
                    urls.append(full)

            # find next page
            next_li = soup.select_one("li.next > a")
            if next_li and next_li.get("href"):
                next_href = next_li.get("href")
                next_url = requests.compat.urljoin(next_url, next_href)
            else:
                next_url = ""

        LOGGER.info("Discovered %d product pages", len(urls))
        return urls

    def parse_product_page(self, url: str) -> Optional[Book]:
        try:
            resp = self._get(url)
        except Exception:
            LOGGER.exception("Failed to fetch product page %s", url)
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.select_one("div.product_main > h1")
        title = title_tag.text.strip() if title_tag else ""

        price_tag = soup.select_one("p.price_color")
        price = price_tag.text.strip() if price_tag else ""

        avail_tag = soup.select_one("p.instock.availability")
        availability = avail_tag.text.strip() if avail_tag else ""

        # rating is in class like 'star-rating Three'
        rating_tag = soup.select_one("p.star-rating")
        rating = ""
        if rating_tag:
            classes = rating_tag.get("class", [])
            rating = " ".join(classes).replace("star-rating", "").strip()

        return Book(title=title, price=price, availability=availability, rating=rating, product_page_url=url)

    def run(self, output_csv: str, batch_size: int = 50) -> None:
        product_urls = self.crawl_index_pages("")

        fieldnames = ["title", "price", "availability", "rating", "product_page_url"]
        with CSVBatchWriter(output_csv, fieldnames, batch_size=batch_size) as writer:
            with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
                futures = {ex.submit(self.parse_product_page, u): u for u in product_urls}
                for fut in as_completed(futures):
                    url = futures[fut]
                    try:
                        book = fut.result()
                        if book:
                            writer.add_row(asdict(book))
                            LOGGER.debug("Wrote book from %s", url)
                    except Exception:
                        LOGGER.exception("Error processing %s", url)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Robust scraper for books.toscrape.com")
    parser.add_argument("--output", "-o", default="books.csv", help="Output CSV file")
    parser.add_argument("--workers", "-w", type=int, default=8, help="Number of worker threads")
    parser.add_argument("--batch", "-b", type=int, default=50, help="CSV batch size")
    parser.add_argument("--log", default=None, help="Log file path")
    args = parser.parse_args()

    setup_logging(logfile=args.log)
    LOGGER.info("Starting scraper")
    session = requests.Session()
    scraper = Scraper(session=session, max_workers=args.workers)
    scraper.run(args.output, batch_size=args.batch)
    LOGGER.info("Scraping finished. Output: %s", args.output)


if __name__ == "__main__":
    main()
