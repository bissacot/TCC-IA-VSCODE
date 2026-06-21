#!/usr/bin/env python3
"""robust scraper.py

A resilient, concurrent scraper for http://books.toscrape.com/

Features:
- Type hints and modular design
- Native logging
- requests.Session with HTTPAdapter for connection reuse
- Exponential backoff retries for transient failures
- concurrent.futures.ThreadPoolExecutor for parallel processing
- Thread-safe batch CSV saving

Usage:
    python "robust scraper.py" --output books.csv --workers 8 --batch 50

"""
from __future__ import annotations

import csv
import logging
import math
import random
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Dict, Generator, Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from bs4 import BeautifulSoup
except Exception as e:  # pragma: no cover - helpful error message
    raise ImportError(
        "BeautifulSoup4 is required: pip install beautifulsoup4"
    ) from e

LOGGER = logging.getLogger("robust_scraper")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s %(message)s",
)


def retry_backoff(
    *,
    tries: int = 4,
    backoff_factor: float = 0.5,
    max_backoff: float = 30.0,
    allowed_exceptions: Iterable[type] = (requests.RequestException,),
):
    """Decorator implementing exponential backoff with jitter.

    Retries the wrapped function on specified exceptions.
    """

    def _decorator(func):
        def _wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    is_allowed = any(isinstance(exc, ex) for ex in allowed_exceptions)
                    attempt += 1
                    if not is_allowed or attempt > tries:
                        LOGGER.debug("No more retries: %s", exc)
                        raise
                    backoff = min(max_backoff, backoff_factor * (2 ** (attempt - 1)))
                    jitter = random.uniform(0, backoff * 0.1)
                    sleep_time = backoff + jitter
                    LOGGER.warning(
                        "Retry %d/%d after %0.2fs due to: %s",
                        attempt,
                        tries,
                        sleep_time,
                        exc,
                    )
                    time.sleep(sleep_time)

        return _wrapper

    return _decorator


@dataclass
class BookItem:
    title: str
    price: str
    availability: str
    rating: str
    product_page: str


class CSVBatchWriter:
    """Thread-safe CSV batch writer used as a context manager.

    Opens the file in append mode and writes rows using a lock to ensure thread-safety.
    """

    def __init__(self, filepath: str, fieldnames: List[str]):
        self.filepath = filepath
        self.fieldnames = fieldnames
        self.lock = threading.Lock()
        self._file = None
        self._writer = None

    def __enter__(self):
        # Open once; callers should keep the context open for the lifetime of the run
        self._file = open(self.filepath, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        # If file is empty, write header
        if self._file.tell() == 0:
            self._writer.writeheader()
            self._file.flush()
        return self

    def write_batch(self, items: Iterable[BookItem]):
        rows = [asdict(item) for item in items]
        if not rows:
            return
        with self.lock:
            for row in rows:
                self._writer.writerow(row)
            self._file.flush()

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._file:
                self._file.close()
        finally:
            self._file = None
            self._writer = None


class Scraper:
    BASE_URL = "http://books.toscrape.com/"

    def __init__(self, *, max_workers: int = 8, session: Optional[requests.Session] = None):
        self.max_workers = max_workers
        self.session = session or self._create_session()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._write_lock = threading.Lock()

    def _create_session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=100, pool_maxsize=100)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        return s

    @retry_backoff(tries=5, backoff_factor=0.5)
    def fetch(self, url: str, timeout: float = 10.0) -> requests.Response:
        LOGGER.debug("Fetching URL: %s", url)
        resp = self.session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp

    def iter_listing_pages(self, start_url: Optional[str] = None) -> Generator[str, None, None]:
        url = start_url or self.BASE_URL
        while True:
            LOGGER.info("Listing page: %s", url)
            resp = self.fetch(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            yield resp.text
            # find next page link
            next_btn = soup.select_one("li.next > a")
            if not next_btn:
                break
            next_href = next_btn.get("href")
            # build absolute url
            if "catalogue/" in url and "catalogue/" in next_href:
                url = requests.compat.urljoin(url, next_href)
            else:
                url = requests.compat.urljoin(url, next_href)

    def parse_listing(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for article in soup.select("article.product_pod"):
            a = article.select_one("h3 > a")
            href = a.get("href")
            full = requests.compat.urljoin(self.BASE_URL, href)
            links.append(full)
        LOGGER.debug("Found %d book links", len(links))
        return links

    @retry_backoff(tries=4, backoff_factor=0.4)
    def parse_book(self, url: str) -> BookItem:
        resp = self.fetch(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one("div.product_main > h1").text.strip()
        price = soup.select_one("p.price_color").text.strip()
        availability = soup.select_one("p.availability").text.strip()
        # rating is stored in class attribute like 'star-rating Three'
        rating_cls = soup.select_one("p.star-rating").get("class", [])
        rating = "".join([c for c in rating_cls if c != "star-rating"]) or "Unknown"
        return BookItem(title=title, price=price, availability=availability, rating=rating, product_page=url)

    def scrape(self, *, output: str = "books.csv", batch_size: int = 100, start_url: Optional[str] = None):
        fieldnames = ["title", "price", "availability", "rating", "product_page"]
        pending: List[BookItem] = []

        with CSVBatchWriter(output, fieldnames) as writer:
            futures: List[Future] = []
            for listing_html in self.iter_listing_pages(start_url=start_url):
                links = self.parse_listing(listing_html)
                for link in links:
                    fut = self.executor.submit(self.parse_book, link)
                    futures.append(fut)

                    # check completed futures to collect results incrementally
                    if len(futures) >= self.max_workers * 4:
                        for done in as_completed(futures):
                            try:
                                item = done.result()
                                pending.append(item)
                            except Exception as e:
                                LOGGER.exception("Failed to parse book: %s", e)
                            if len(pending) >= batch_size:
                                writer.write_batch(pending)
                                pending.clear()
                        futures = []

            # drain remaining futures
            for done in as_completed(futures):
                try:
                    item = done.result()
                    pending.append(item)
                except Exception:
                    LOGGER.exception("Error finishing a future")
                if len(pending) >= batch_size:
                    writer.write_batch(pending)
                    pending.clear()

            # final flush
            if pending:
                writer.write_batch(pending)

        self.executor.shutdown(wait=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Robust concurrent scraper for books.toscrape.com")
    parser.add_argument("--output", "-o", default="books.csv", help="CSV output file")
    parser.add_argument("--workers", "-w", default=8, type=int, help="Number of worker threads")
    parser.add_argument("--batch", "-b", default=100, type=int, help="Batch size for CSV writes")
    parser.add_argument("--start", default=None, help="Start URL (optional)")
    args = parser.parse_args()

    LOGGER.info("Starting scraper with %d workers", args.workers)
    scraper = Scraper(max_workers=args.workers)
    try:
        scraper.scrape(output=args.output, batch_size=args.batch, start_url=args.start)
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user; shutting down")
    except Exception:
        LOGGER.exception("Scraper terminated with an error")


if __name__ == "__main__":
    main()
