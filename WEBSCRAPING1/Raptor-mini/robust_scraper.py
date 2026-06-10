# Installation:
# pip install requests beautifulsoup4 tenacity

import csv
import logging
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import Response
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

BASE_URL = "http://books.toscrape.com/"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]
FIELDNAMES = ["title", "price", "availability", "star_rating", "image_url"]
DEFAULT_WORKERS = 8
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_RETRY_ATTEMPTS = 5

logger = logging.getLogger(__name__)


class RetryableRequestError(requests.RequestException):
    """Custom exception used to signal retryable HTTP errors."""


class HttpClient:
    """HTTP client that reuses session connections and retries failed requests."""

    def __init__(self, timeout: float = DEFAULT_TIMEOUT_SECONDS, max_retries: int = DEFAULT_RETRY_ATTEMPTS) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._local = threading.local()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        session = getattr(self._local, "session", None)
        if session is not None:
            session.close()

    def _session(self) -> requests.Session:
        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            self._local.session = session
        return session

    def _build_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    @retry(
        retry=retry_if_exception_type((requests.exceptions.RequestException, RetryableRequestError)),
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        reraise=True,
    )
    def get(self, url: str) -> str:
        session = self._session()
        headers = self._build_headers()
        logger.debug("Fetching URL %s with headers %s", url, headers)
        try:
            response: Response = session.get(url, headers=headers, timeout=self._timeout)
        except requests.exceptions.Timeout as exc:
            logger.warning("Timeout fetching %s: %s", url, exc)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.warning("Connection error fetching %s: %s", url, exc)
            raise

        if response.status_code in RETRYABLE_STATUS_CODES:
            logger.warning("Retryable HTTP error %s while fetching %s", response.status_code, url)
            raise RetryableRequestError(f"Status {response.status_code} for {url}")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            logger.error("Non-retryable HTTP error %s while fetching %s", response.status_code, url)
            raise

        logger.info("Fetched %s [%s]", url, response.status_code)
        return response.text


class PageParser:
    """Page parser that extracts product data and pagination links."""

    @staticmethod
    def _parse_star_rating(classes: Iterable[str]) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        for token in classes:
            if token in rating_map:
                return rating_map[token]
        return 0

    def parse_products(self, html: str, page_url: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for article in soup.select("article.product_pod"):
            title_tag = article.select_one("h3 a")
            price_tag = article.select_one("p.price_color")
            availability_tag = article.select_one("p.instock.availability")
            image_tag = article.select_one("img")
            if not title_tag or not price_tag or not availability_tag or not image_tag:
                logger.debug("Skipping incomplete product card on %s", page_url)
                continue

            title = title_tag.get("title", title_tag.text).strip()
            price = price_tag.text.strip()
            availability = availability_tag.text.strip()
            star_rating = self._parse_star_rating(article.get("class", []))
            image_src = image_tag.get("src", "")
            image_url = urljoin(page_url, image_src)

            items.append(
                {
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "star_rating": str(star_rating),
                    "image_url": image_url,
                }
            )

        logger.info("Parsed %s products from %s", len(items), page_url)
        return items

    def find_next_page(self, html: str, page_url: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one("li.next a")
        if not next_link:
            return None
        href = next_link.get("href")
        if not href:
            return None
        next_url = urljoin(page_url, href)
        logger.debug("Discovered next page %s from %s", next_url, page_url)
        return next_url


class CsvWriter:
    """Thread-safe CSV writer for continuous persistence."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._file = None
        self._writer = None

    def __enter__(self) -> "CsvWriter":
        self._file = open(self._path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDNAMES)
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._file is not None:
            self._file.close()

    def write_rows(self, rows: List[Dict[str, str]]) -> None:
        if not rows:
            return
        with self._lock:
            assert self._writer is not None
            for row in rows:
                self._writer.writerow(row)
            self._file.flush()
        logger.debug("Wrote %s rows to CSV", len(rows))


class RobustScraper:
    """Main scraper implementation for paginated product discovery and persistence."""

    def __init__(self, base_url: str = BASE_URL, output_path: str = "products.csv", workers: int = DEFAULT_WORKERS) -> None:
        self.base_url = base_url
        self.output_path = output_path
        self.workers = workers
        self.client = HttpClient()
        self.parser = PageParser()

    def discover_page_urls(self) -> List[str]:
        urls: List[str] = []
        next_page_url: Optional[str] = self.base_url
        while next_page_url:
            html = self.client.get(next_page_url)
            urls.append(next_page_url)
            next_page_url = self.parser.find_next_page(html, next_page_url)
        logger.info("Discovered %s pages", len(urls))
        return urls

    def _process_page(self, page_url: str, writer: CsvWriter) -> None:
        html = self.client.get(page_url)
        products = self.parser.parse_products(html, page_url)
        writer.write_rows(products)

    def run(self) -> None:
        logger.info("Starting scraper with %s workers", self.workers)
        with self.client, CsvWriter(self.output_path) as writer:
            page_urls = self.discover_page_urls()
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                future_to_url = {
                    executor.submit(self._process_page, url, writer): url for url in page_urls
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                        logger.info("Completed processing %s", url)
                    except Exception as exc:
                        logger.exception("Failed to process %s: %s", url, exc)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    configure_logging()
    scraper = RobustScraper()
    scraper.run()


if __name__ == "__main__":
    main()
