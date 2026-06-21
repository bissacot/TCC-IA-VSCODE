"""
Configuration file for robust_scraper.py

Modify these settings to customize scraper behavior without editing the main script.
"""

# ============================================================================
# Target Configuration
# ============================================================================

BASE_URL = "http://books.toscrape.com/"
OUTPUT_CSV = "books_data.csv"


# ============================================================================
# Performance Configuration
# ============================================================================

# Number of concurrent worker threads
# - Higher = faster but more strain on server and system
# - Lower = slower but more reliable and server-friendly
# Recommended: 3-10 for production use
MAX_WORKERS = 5

# Number of books to accumulate before writing to CSV
# - Higher = faster (fewer I/O operations) but uses more memory
# - Lower = slower but uses less memory and safer for failures
# Recommended: 25-200 for production use
BATCH_SIZE = 50


# ============================================================================
# Request Configuration
# ============================================================================

# Timeout for HTTP requests in seconds
# - If request takes longer than this, it will timeout and retry
# - Lower values fail faster but may timeout on slow connections
# Recommended: 5-30 seconds
REQUEST_TIMEOUT = 10

# Maximum number of retry attempts for failed requests
# - Higher = more resilient but slower on failures
# - Lower = faster but less resilient
# Recommended: 2-5 retries
MAX_RETRIES = 3

# Exponential backoff multiplier for retries
# - Wait time = backoff_factor * (2 ** (retry_count - 1))
# - For first retry: 0.5 * 2^0 = 0.5 seconds
# - For second retry: 0.5 * 2^1 = 1 second
# - For third retry: 0.5 * 2^2 = 2 seconds
# Recommended: 0.3-1.0
BACKOFF_FACTOR = 0.5


# ============================================================================
# Scraping Limits
# ============================================================================

# Maximum number of pages to scrape
# - Set to None to scrape all pages
# - Set to a number (e.g., 5) to limit scraping for testing
# Recommended: None for production, or a small number for testing
MAX_PAGES = None  # Change to 2 or 5 for quick testing


# ============================================================================
# Logging Configuration
# ============================================================================

# Log file name
LOG_FILE = "scraper.log"

# Log level for console output
# - "DEBUG": Very detailed, all messages
# - "INFO": Major events and statistics
# - "WARNING": Only warnings and errors
# - "ERROR": Only errors
CONSOLE_LOG_LEVEL = "INFO"

# Log level for file output
# - "DEBUG": Very detailed (recommended for troubleshooting)
# - "INFO": Major events
# - "WARNING": Only warnings and errors
# - "ERROR": Only errors
FILE_LOG_LEVEL = "DEBUG"


# ============================================================================
# User Agent Configuration
# ============================================================================

# Custom User-Agent header (optional)
# Leave empty to use default browser-like User-Agent
# CUSTOM_USER_AGENT = ""

# Or specify a custom one:
# CUSTOM_USER_AGENT = "MyBot/1.0 (+http://mysite.com/bot)"


# ============================================================================
# Proxy Configuration
# ============================================================================

# Set to None to disable proxies
# Set to dict to enable proxies
# Example:
# PROXY_CONFIG = {
#     "http": "http://proxy.example.com:8080",
#     "https": "https://proxy.example.com:8080",
# }
PROXY_CONFIG = None


# ============================================================================
# Output Configuration
# ============================================================================

# Whether to append to existing CSV or overwrite
# - True: Append to existing file (good for resuming)
# - False: Overwrite existing file (good for fresh scrapes)
APPEND_TO_CSV = False

# CSV encoding (recommended: utf-8)
CSV_ENCODING = "utf-8"

# CSV line terminator
CSV_LINE_TERMINATOR = "\r\n"


# ============================================================================
# Advanced Configuration
# ============================================================================

# Request headers (customize as needed)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# HTTP status codes to retry on
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# HTTP methods to retry
RETRY_METHODS = ["GET", "HEAD"]


# ============================================================================
# Feature Flags
# ============================================================================

# Enable/disable concurrent processing
# - True: Use ThreadPoolExecutor for parallel scraping
# - False: Scrape pages sequentially (slower but simpler)
ENABLE_CONCURRENT = True

# Enable/disable batch writing
# - True: Write in batches (recommended for large scrapes)
# - False: Write after each page (slower but safer)
ENABLE_BATCH_WRITING = True

# Enable/disable logging
# - True: Write detailed logs (recommended)
# - False: No logging (not recommended)
ENABLE_LOGGING = True


# ============================================================================
# Preset Configurations
# ============================================================================

PRESETS = {
    "quick_test": {
        "MAX_WORKERS": 2,
        "BATCH_SIZE": 25,
        "MAX_RETRIES": 2,
        "MAX_PAGES": 2,
    },
    "balanced": {
        "MAX_WORKERS": 5,
        "BATCH_SIZE": 50,
        "MAX_RETRIES": 3,
        "MAX_PAGES": None,
    },
    "high_performance": {
        "MAX_WORKERS": 10,
        "BATCH_SIZE": 200,
        "MAX_RETRIES": 2,
        "MAX_PAGES": None,
    },
    "conservative": {
        "MAX_WORKERS": 2,
        "BATCH_SIZE": 25,
        "MAX_RETRIES": 5,
        "MAX_PAGES": None,
    },
}


# ============================================================================
# Usage Examples
# ============================================================================

"""
# To use a preset configuration:

from config import PRESETS
preset = PRESETS["quick_test"]

# Then use in your scraper:
from robust_scraper import RobustBookScraper

scraper = RobustBookScraper(
    max_workers=preset["MAX_WORKERS"],
    batch_size=preset["BATCH_SIZE"],
    max_pages=preset["MAX_PAGES"],
)

results = scraper.scrape()


# To manually configure:

from robust_scraper import RobustBookScraper

scraper = RobustBookScraper(
    output_file="my_books.csv",
    batch_size=100,
    max_workers=8,
    max_pages=None,
)

results = scraper.scrape()
"""
