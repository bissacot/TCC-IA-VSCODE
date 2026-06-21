#!/usr/bin/env python3
"""
robust scraper.py

A resilient, concurrent web scraper for http://books.toscrape.com/

Features:
- Single-file implementation with type hints
- Native `logging` configuration
- Uses `requests.Session` for connection reuse
- Retry with exponential backoff and jitter for HTTP/network errors
- Concurrency via `concurrent.futures.ThreadPoolExecutor`
- Thread-safe batch CSV saving

Dependencies:
- requests
- beautifulsoup4

Install: pip install requests beautifulsoup4

Usage:
    python "robust scraper.py" --output books.csv --workers 8 --batch 50
"""
from __future__ import annotations

import argparse
import csv
import contextlib
import dataclasses
import logging
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class BookData:
    title: str
    price: str
    availability: str
    rating: str
    product_page_url: str


class RobustScraper:
    def __init__(
        self,
        start_url: str = "http://books.toscrape.com/",
        output_file: str = "books.csv",
        max_workers: int = 8,
        batch_size: int = 100,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.start_url = start_url
        self.output_file = output_file
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.session = requests.Session()
        self.csv_lock = threading.Lock()

        self.logger = logger or logging.getLogger(__name__)
        # ensure directory exists
        out_dir = os.path.dirname(os.path.abspath(self.output_file))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

    # HTTP GET with retries and exponential backoff
    def _get(self, url: str, **kwargs) -> requests.Response:
        attempt = 0
        while True:
            try:
                self.logger.debug("GET %s (attempt %d)", url, attempt + 1)
                resp = self.session.get(url, timeout=10, **kwargs)
                resp.raise_for_status()
                return resp
            except Exception as exc:  # requests.RequestException covers many cases
                if attempt >= self.max_retries:
                    self.logger.error("Max retries reached for %s: %s", url, exc)
                    raise
                backoff = self.backoff_factor * (2 ** attempt)
                jitter = random.uniform(0, backoff * 0.1)
                sleep_time = backoff + jitter
                self.logger.warning(
                    "Request failed (%s). Backing off %.2fs and retrying...",
                    exc,
                    sleep_time,
                )
                time.sleep(sleep_time)
                attempt += 1

    # Parse a book list page and return product page URLs
    def parse_list_page(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []
        for article in soup.select("article.product_pod"):
            a = article.find("a")
            if not a:
                continue
            href = a.get("href")
            if not href:
                continue
            full = urljoin(base_url, href)
            # links on this site sometimes use relative paths with ../
            links.append(full)
        self.logger.debug("Found %d book links on page", len(links))
        return links

    def parse_book_page(self, html: str, url: str) -> BookData:
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.select_one("div.product_main > h1")
        title = title_tag.text.strip() if title_tag else ""
        price_tag = soup.select_one("p.price_color")
        price = price_tag.text.strip() if price_tag else ""
        avail_tag = soup.select_one("p.availability")
        availability = (
            " ".join(avail_tag.text.split()) if avail_tag else ""
        )
        rating_tag = soup.select_one("p.star-rating")
        rating = ""
        if rating_tag:
            classes = rating_tag.get("class", [])
            # rating classes: e.g., ['star-rating', 'Three']
            for cls in classes:
                if cls.lower() in {
                    "one",
                    "two",
                    "three",
                    "four",
                    "five",
                    "zero",
                }:
                    rating = cls
                    break

        return BookData(
            title=title,
            price=price,
            availability=availability,
            rating=rating,
            product_page_url=url,
        )

    def fetch_book(self, url: str) -> Optional[BookData]:
        try:
            resp = self._get(url)
            return self.parse_book_page(resp.text, url)
        except Exception:
            self.logger.exception("Failed to fetch or parse book %s", url)
            return None

    # Thread-safe batch save
    def save_batch(self, batch: Iterable[BookData]) -> None:
        if not batch:
            return
        with self.csv_lock:
            file_exists = os.path.exists(self.output_file)
            write_header = not file_exists or os.path.getsize(self.output_file) == 0
            with open(self.output_file, "a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(
                    fh,
                    fieldnames=["title", "price", "availability", "rating", "product_page_url"],
                )
                if write_header:
                    writer.writeheader()
                for item in batch:
                    writer.writerow(dataclasses.asdict(item))
        self.logger.info("Saved %d records to %s", len(list(batch)), self.output_file)

    # Crawl paginated listing pages starting from start_url and yield product URLs
    def iter_list_pages(self, start_url: str, max_pages: Optional[int] = None) -> Iterable[str]:
        url = start_url
        page_count = 0
        while url:
            self.logger.info("Fetching list page: %s", url)
            try:
                resp = self._get(url)
            except Exception:
                self.logger.exception("Stopping pagination due to fetch error: %s", url)
                break
            links = self.parse_list_page(resp.text, url)
            for link in links:
                yield link
            page_count += 1
            if max_pages and page_count >= max_pages:
                self.logger.debug("Reached max_pages=%d, stopping", max_pages)
                break
            # find next page link
            soup = BeautifulSoup(resp.text, "html.parser")
            next_a = soup.select_one("li.next > a")
            if next_a and next_a.get("href"):
                url = urljoin(url, next_a.get("href"))
            else:
                break

    def run(self, start_url: Optional[str] = None, max_pages: Optional[int] = None) -> None:
        start_url = start_url or self.start_url
        product_urls = []
        # We'll stream product URLs and submit them to the executor
        batch: List[BookData] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url: Dict = {}
            # Submit tasks as we discover URLs
            for url in self.iter_list_pages(start_url, max_pages=max_pages):
                # normalize product page to absolute url and sometimes remove query parts
                fut = executor.submit(self.fetch_book, url)
                future_to_url[fut] = url

            # As futures complete, collect results and write in batches
            completed_count = 0
            for fut in as_completed(list(future_to_url.keys())):
                url = future_to_url.get(fut)
                try:
                    result = fut.result()
                    if result:
                        batch.append(result)
                except Exception:
                    self.logger.exception("Exception while processing %s", url)

                completed_count += 1
                if len(batch) >= self.batch_size:
                    # drain and save
                    self.save_batch(batch)
                    batch = []

            # final flush
            if batch:
                self.save_batch(batch)

        self.logger.info("Scrape complete. Processed %d items.", completed_count)


def configure_logging(level: int = logging.INFO) -> None:
    fmt = "%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Robust concurrent scraper for books.toscrape.com")
    p.add_argument("--start-url", default="http://books.toscrape.com/", help="Start URL")
    p.add_argument("--output", default="books.csv", help="Output CSV file")
    p.add_argument("--workers", type=int, default=8, help="Number of worker threads")
    p.add_argument("--batch", type=int, default=100, help="Batch size for CSV writes")
    p.add_argument("--max-pages", type=int, default=None, help="Max listing pages to crawl (optional)")
    p.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger("robust_scraper")

    scraper = RobustScraper(
        start_url=args.start_url,
        output_file=args.output,
        max_workers=args.workers,
        batch_size=args.batch,
        max_retries=3,
        backoff_factor=0.5,
        logger=logger,
    )
    scraper.run(start_url=args.start_url, max_pages=args.max_pages)


if __name__ == "__main__":
    main()
