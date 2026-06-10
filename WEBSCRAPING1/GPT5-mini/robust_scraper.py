# Installation:
# pip install requests beautifulsoup4 tenacity
#
# Usage:
# python robust_scraper.py --start-url http://books.toscrape.com/ --workers 10 --output products.csv --batch 50

import argparse
import csv
import logging
import os
import random
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_random_exponential)
from concurrent.futures import ThreadPoolExecutor, wait, Future
from queue import Queue

# Configuration / constants
DEFAULT_TIMEOUT: int = 10
DEFAULT_WORKERS: int = 10
DEFAULT_BATCH_SIZE: int = 50
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
FIELDNAMES = [
    "title",
    "price",
    "availability",
    "rating",
    "image_url",
    "product_page_url",
]

USER_AGENTS = [
    # Modern browser user-agents (truncated to common modern browsers)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Edg/116.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"
    " (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/115.0.0.0 Safari/537.36",
]

# Logging setup
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
)


@dataclass
class Product:
    """Data model for a product record."""
    title: str
    price: str
    availability: str
    rating: int
    image_url: str
    product_page_url: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a CSV-serializable dict of the product."""
        return {
            "title": self.title,
            "price": self.price,
            "availability": self.availability,
            "rating": self.rating,
            "image_url": self.image_url,
            "product_page_url": self.product_page_url,
        }


class SessionManager:
    """Thread-local session manager that provides connection pooling and graceful close.

    Each worker thread receives its own requests.Session instance which is reused
    across calls in that thread to reuse TCP connections.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self._local = threading.local()
        self._sessions: List[requests.Session] = []
        self._lock = threading.Lock()

    def __enter__(self) -> "SessionManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close_all()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"Accept-Language": "en-US,en;q=0.9"})
        return session

    def get_session(self) -> requests.Session:
        """Return a thread-local session, creating one if necessary."""
        if not hasattr(self._local, "session") or self._local.session is None:
            s = self._create_session()
            self._local.session = s
            with self._lock:
                self._sessions.append(s)
        return self._local.session

    def close_all(self) -> None:
        """Close all tracked sessions."""
        with self._lock:
            for s in self._sessions:
                try:
                    s.close()
                except Exception:
                    pass
            self._sessions.clear()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Perform an HTTP request using a thread-local session with randomized User-Agent.

        This function delegates to a retry-protected function that implements exponential
        backoff + jitter and retries on connection errors, timeouts and selected HTTP codes.
        """
        session = self.get_session()
        headers = kwargs.pop("headers", {})
        # Rotate user-agent per request
        headers["User-Agent"] = random.choice(USER_AGENTS)
        kwargs["headers"] = headers
        kwargs.setdefault("timeout", self.timeout)
        return _do_request_with_retry(session, method, url, **kwargs)


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _do_request_with_retry(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    """Low-level request with retry behavior.

    Raises requests.exceptions.RequestException on repeated failures so callers can handle it.
    """
    try:
        response = session.request(method, url, **kwargs)
    except requests.exceptions.RequestException:
        logging.warning("Request exception for %s %s; will retry.", method, url)
        raise
    # Retry on certain server-side statuses by raising an exception so tenacity retries.
    if response.status_code in RETRY_STATUS_CODES:
        logging.warning("Received status %s for %s; triggering retry.", response.status_code, url)
        # Raise an HTTPError to be caught by tenacity's retry logic
        raise requests.exceptions.HTTPError(f"HTTP {response.status_code} for {url}", response=response)
    return response


def discover_pages(session_mgr: SessionManager, start_url: str) -> List[str]:
    """Discover pagination pages by following the 'Next' link.

    Args:
        session_mgr: SessionManager for HTTP requests.
        start_url: The starting URL of the catalogue.

    Returns:
        A list of absolute page URLs in discovery order.
    """
    pages: List[str] = []
    seen = set()
    next_url: Optional[str] = start_url
    while next_url and next_url not in seen:
        try:
            resp = session_mgr.request("GET", next_url)
            text = resp.text
        except Exception as exc:
            logging.exception("Failed to fetch page %s: %s", next_url, exc)
            break
        pages.append(next_url)
        seen.add(next_url)
        soup = BeautifulSoup(text, "html.parser")
        next_link = soup.select_one("li.next a")
        if next_link and next_link.get("href"):
            href = next_link["href"]
            next_url = urljoin(next_url, href)
        else:
            next_url = None
    logging.info("Discovered %d pages", len(pages))
    return pages


def parse_listing_links(html: str, base_url: str) -> List[str]:
    """Extract product detail URLs from a listing page.

    Args:
        html: Listing page HTML.
        base_url: Base URL used for resolving relative links.

    Returns:
        A list of absolute product page URLs.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("article.product_pod h3 a"):
        href = a.get("href")
        if href:
            links.append(urljoin(base_url, href))
    return links


def parse_product_page(html: str, base_url: str) -> Optional[Product]:
    """Parse a product page and extract required fields.

    Args:
        html: Product detail page HTML.
        base_url: URL of the product page (used to resolve images).

    Returns:
        Product dataclass or None if parsing failed.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Title
    title_el = soup.select_one("div.product_main h1") or soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    # Price
    price_el = soup.select_one("p.price_color")
    price = price_el.get_text(strip=True) if price_el else ""

    # Availability
    avail_el = soup.select_one("p.availability")
    availability = avail_el.get_text(strip=True) if avail_el else ""

    # Star rating: classes like "star-rating Three"
    rating = 0
    rating_el = soup.select_one("p.star-rating")
    if rating_el:
        for cls in rating_el.get("class", []):
            if cls.lower() in {"one", "two", "three", "four", "five"}:
                mapping = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
                rating = mapping.get(cls.lower(), 0)
                break

    # Image URL
    img_el = soup.select_one("div.carousel-inner img") or soup.select_one("div.item img") or soup.select_one("img")
    image_url = urljoin(base_url, img_el["src"]) if (img_el and img_el.get("src")) else ""

    if not title:
        logging.debug("Parsed product missing title at %s", base_url)
        return None

    return Product(
        title=title,
        price=price,
        availability=availability,
        rating=rating,
        image_url=image_url,
        product_page_url=base_url,
    )


def fetch_listing_and_submit_products(
    page_url: str,
    session_mgr: SessionManager,
    detail_executor: ThreadPoolExecutor,
    product_queue: Queue,
) -> None:
    """Fetch a listing page, parse product links, and submit detail tasks."""
    try:
        resp = session_mgr.request("GET", page_url)
        product_links = parse_listing_links(resp.text, page_url)
        logging.info("Page %s -> %d product links", page_url, len(product_links))
        for purl in product_links:
            # Submit detail fetch tasks to the detail executor
            detail_executor.submit(fetch_product_and_enqueue, purl, session_mgr, product_queue)
    except Exception as exc:
        logging.exception("Failed to process listing %s: %s", page_url, exc)


def fetch_product_and_enqueue(product_url: str, session_mgr: SessionManager, product_queue: Queue) -> None:
    """Fetch a product page, parse, and put the product into the queue for CSV writing."""
    try:
        resp = session_mgr.request("GET", product_url)
        product = parse_product_page(resp.text, product_url)
        if product:
            # Put raw dict into queue for writer
            product_queue.put(product.to_dict())
            logging.debug("Enqueued product: %s", product.title)
    except Exception as exc:
        logging.exception("Failed to fetch/parse product %s: %s", product_url, exc)


class CSVWriter(threading.Thread):
    """Background CSV writer thread that consumes product records from a queue."""

    def __init__(self, file_path: str, fieldnames: List[str], product_queue: Queue, batch_size: int = DEFAULT_BATCH_SIZE) -> None:
        super().__init__(daemon=True)
        self.file_path = file_path
        self.fieldnames = fieldnames
        self.queue = product_queue
        self.batch_size = max(1, batch_size)

    def run(self) -> None:
        """Run the writer loop. Expects `None` sentinel to stop."""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)) or ".", exist_ok=True)
        with open(self.file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            csvfile.flush()
            buffer: List[Dict[str, Any]] = []
            while True:
                item = self.queue.get()
                try:
                    if item is None:
                        # Sentinel received; flush buffer and exit
                        if buffer:
                            writer.writerows(buffer)
                            csvfile.flush()
                            buffer.clear()
                        self.queue.task_done()
                        break
                    buffer.append(item)
                    self.queue.task_done()
                    if len(buffer) >= self.batch_size:
                        writer.writerows(buffer)
                        csvfile.flush()
                        buffer.clear()
                except Exception:
                    logging.exception("Error while writing CSV row")
                    self.queue.task_done()
            logging.info("CSV writer finished and closed %s", self.file_path)


def robust_scrape(
    start_url: str = "http://books.toscrape.com/",
    workers: int = DEFAULT_WORKERS,
    output: str = "products.csv",
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Main scraping pipeline orchestrator.

    1. Discover all listing pages by following "Next".
    2. Fetch listing pages concurrently to collect product links.
    3. Fetch product detail pages concurrently and parse required fields.
    4. Stream product records to a background CSV writer with batching.

    Args:
        start_url: Root URL to start scraping from.
        workers: Number of worker threads for concurrent fetching.
        output: Output CSV file path.
        batch_size: Number of rows to write per batch to the CSV.
    """
    logging.info("Starting robust scraper for %s with %d workers", start_url, workers)
    product_queue: Queue = Queue(maxsize=10000)

    with SessionManager(timeout=DEFAULT_TIMEOUT) as session_mgr:
        writer = CSVWriter(output, FIELDNAMES, product_queue, batch_size=batch_size)
        writer.start()

        # Discover pages (sequential but quick)
        pages = discover_pages(session_mgr, start_url)
        if not pages:
            logging.error("No pages found; exiting.")
            product_queue.put(None)
            writer.join()
            return

        # Use two executors: one for listing pages, one for product detail pages.
        # Listing tasks will submit detail tasks to the detail executor.
        try:
            with ThreadPoolExecutor(max_workers=workers) as listing_executor:
                with ThreadPoolExecutor(max_workers=workers) as detail_executor:
                    listing_futures: List[Future] = []
                    for p in pages:
                        f = listing_executor.submit(fetch_listing_and_submit_products, p, session_mgr, detail_executor, product_queue)
                        listing_futures.append(f)
                    # Wait for all listing pages to be submitted/processed
                    wait(listing_futures)
                    logging.info("All listing pages processed; waiting for product detail tasks...")
                    # Shutdown detail executor and wait for all product tasks to finish
                    detail_executor.shutdown(wait=True)
        except KeyboardInterrupt:
            logging.warning("Interrupted by user; shutting down.")
        except Exception:
            logging.exception("Unhandled exception in executors.")
        finally:
            # Signal writer to finish and close
            product_queue.put(None)
            writer.join()
            logging.info("Scraping complete; output at %s", output)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robust concurrent scraper for books.toscrape.com")
    parser.add_argument("--start-url", type=str, default="http://books.toscrape.com/", help="Start URL")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of worker threads")
    parser.add_argument("--output", type=str, default="products.csv", help="Output CSV path")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH_SIZE, help="CSV write batch size")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    robust_scrape(start_url=args.start_url, workers=args.workers, output=args.output, batch_size=args.batch)