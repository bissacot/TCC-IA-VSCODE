#!/usr/bin/env python3
"""Robust, concurrent scraper for books.toscrape.com."""
from __future__ import annotations

import argparse
import csv
import logging
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(frozen=True)
class BookRecord:
    title: str
    price: str
    availability: str
    rating: str
    product_page: str
    description: str


class CSVBatchWriter:
    def __init__(self, destination: Path, batch_size: int = 50) -> None:
        self.destination = destination
        self.batch_size = batch_size
        self.lock = threading.Lock()
        self.file = None
        self.writer = None

    def __enter__(self) -> "CSVBatchWriter":
        self.file = open(self.destination, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["title", "price", "availability", "rating", "product_page", "description"])
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.file is not None:
            self.file.flush()
            self.file.close()

    def write_batch(self, records: List[BookRecord]) -> None:
        if not records:
            return

        with self.lock:
            for record in records:
                self.writer.writerow([
                    record.title,
                    record.price,
                    record.availability,
                    record.rating,
                    record.product_page,
                    record.description,
                ])
            self.file.flush()
            logging.debug("Wrote %d records to %s", len(records), self.destination)


def initialize_logger(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_session(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"],
        backoff_factor=backoff_factor,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "robust-scraper/1.0"})
    return session


def fetch_html(session: requests.Session, url: str, timeout: int = 15, attempts: int = 5) -> str:
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            wait = 2 ** (attempt - 1)
            logging.warning("Request failed for %s (attempt %d/%d): %s", url, attempt, attempts, exc)
            if attempt == attempts:
                logging.error("Exceeded retry limit for %s", url)
                raise
            logging.debug("Sleeping %s seconds before retrying %s", wait, url)
            time.sleep(wait)
    raise RuntimeError(f"Unexpected fetch failure for {url}")


def extract_page_urls(html: str, page_url: str) -> List[str]:
    next_link = re.search(r'<li class="next">\s*<a href="([^\"]+)">', html)
    if not next_link:
        return []
    next_href = next_link.group(1)
    return [urljoin(page_url, next_href)]


def parse_listed_books(html: str, page_url: str) -> List[tuple[str, str]]:
    books = []
    for match in re.finditer(
        r'<article class="product_pod">.*?<h3>\s*<a href="([^"]+)" title="([^"]+)">',
        html,
        re.DOTALL,
    ):
        link = urljoin(page_url, match.group(1))
        title = html_unescape(match.group(2)).strip()
        books.append((link, title))
    return books


def parse_book_details(html: str, product_page: str) -> BookRecord:
    price = extract_first(html, r'<p class="price_color">([^<]+)</p>')
    availability = extract_first(html, r'<p class="instock availability">\s*<i class="icon-ok"></i>\s*([^<]+)</p>')
    rating = extract_first(html, r'<p class="star-rating ([A-Za-z]+)"')
    description = extract_description(html)
    title = extract_first(html, r'<div class="product_main">\s*<h1>([^<]+)</h1>')
    return BookRecord(
        title=html_unescape(title or ""),
        price=price or "",
        availability=html_unescape(availability or "").strip(),
        rating=rating or "",
        product_page=product_page,
        description=html_unescape(description or "").strip(),
    )


def extract_description(html: str) -> Optional[str]:
    description_block = re.search(r'<div id="product_description">.*?<p>(.*?)</p>', html, re.DOTALL)
    if description_block:
        return re.sub(r"\s+", " ", description_block.group(1)).strip()
    return None


def extract_first(html: str, pattern: str) -> Optional[str]:
    match = re.search(pattern, html, re.DOTALL)
    return match.group(1).strip() if match else None


def html_unescape(value: str) -> str:
    return (value
            .replace("&amp;", "&")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
            .replace("&lt;", "<")
            .replace("&gt;", ">"))


def collect_catalog_pages(session: requests.Session, start_url: str) -> List[str]:
    pages = [start_url]
    current_url = start_url
    while True:
        html = fetch_html(session, current_url)
        next_pages = extract_page_urls(html, current_url)
        if not next_pages:
            break
        next_url = next_pages[0]
        if next_url in pages:
            break
        pages.append(next_url)
        current_url = next_url
    logging.info("Discovered %d catalog pages", len(pages))
    return pages


def scrape_book(session: requests.Session, product_page: str, title: str) -> BookRecord:
    html = fetch_html(session, product_page)
    record = parse_book_details(html, product_page)
    if not record.title:
        record = dataclass_replace_title(record, title)
    logging.debug("Scraped book: %s", record.title)
    return record


def dataclass_replace_title(record: BookRecord, title: str) -> BookRecord:
    return BookRecord(
        title=title,
        price=record.price,
        availability=record.availability,
        rating=record.rating,
        product_page=record.product_page,
        description=record.description,
    )


def scrape_page(session: requests.Session, page_url: str, worker_count: int) -> List[BookRecord]:
    html = fetch_html(session, page_url)
    book_summaries = parse_listed_books(html, page_url)
    logging.info("Page %s contains %d books", page_url, len(book_summaries))

    records: List[BookRecord] = []
    with ThreadPoolExecutor(max_workers=min(worker_count, len(book_summaries) or 1)) as detail_executor:
        future_to_book = {
            detail_executor.submit(scrape_book, session, product_page, title): (product_page, title)
            for product_page, title in book_summaries
        }
        for future in as_completed(future_to_book):
            try:
                record = future.result()
                records.append(record)
            except Exception as exc:
                page_product_page, page_title = future_to_book[future]
                logging.error("Failed to scrape book %s (%s): %s", page_title, page_product_page, exc)
    return records


def run_scraper(start_url: str, output_path: Path, max_workers: int, batch_size: int) -> int:
    session = build_session()
    catalog_pages = collect_catalog_pages(session, start_url)

    total_books = 0
    with CSVBatchWriter(output_path, batch_size=batch_size) as writer:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(scrape_page, session, page_url, max_workers): page_url
                for page_url in catalog_pages
            }
            for future in as_completed(future_to_page):
                page_url = future_to_page[future]
                try:
                    records = future.result()
                    writer.write_batch(records)
                    total_books += len(records)
                    logging.info("Completed page %s with %d books", page_url, len(records))
                except Exception as exc:
                    logging.error("Page %s failed: %s", page_url, exc)

    return total_books


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Concurrent, resilient scraper for http://books.toscrape.com/")
    parser.add_argument("--output", default="books.csv", help="CSV file to write scraped books")
    parser.add_argument("--workers", type=int, default=8, help="Maximum worker threads for page and detail scraping")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of rows to flush to CSV per write")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--start-url", default="http://books.toscrape.com/", help="Start URL for the book catalog")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    initialize_logger(args.log_level)

    output_path = Path(args.output)
    logging.info("Starting scraper against %s", args.start_url)
    total = run_scraper(args.start_url, output_path, args.workers, args.batch_size)
    logging.info("Finished scraping %d books; saved to %s", total, output_path)


if __name__ == "__main__":
    main()
