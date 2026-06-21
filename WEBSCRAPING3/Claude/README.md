# Robust Web Scraper for books.toscrape.com

A production-ready, resilient, and concurrent web scraper built with Python. Designed to efficiently scrape book data from the practice website while maintaining robustness and performance.

## Features

### ✅ Modular Design with Type Hints
- Full type annotations for all functions and classes
- `@dataclass` for structured data representation
- Clean separation of concerns

### ✅ Native Logging
- Dual-handler logging (console + file)
- Configurable log levels
- Timestamps and structured log messages
- Logs saved to `scraper.log`

### ✅ TCP Connection Reuse
- Uses `requests.Session` to maintain persistent connections
- Reduces overhead and improves performance
- Single session instance across all requests

### ✅ Retry Mechanisms with Exponential Backoff
- Automatic retry on HTTP errors (429, 500-504)
- Configurable exponential backoff factor
- Handles timeouts and connection errors gracefully
- Integrated with `urllib3.Retry` strategy

### ✅ Concurrent Processing
- `concurrent.futures.ThreadPoolExecutor` for parallel page scraping
- Configurable number of worker threads (default: 5)
- Efficient thread management with context managers
- Non-blocking future processing

### ✅ Thread-Safe CSV Batch Writing
- Custom `ThreadSafeCSVWriter` with locks
- Batch processing to minimize I/O operations
- Configurable batch size (default: 50 records)
- Automatic header writing on file creation
- UTF-8 encoding support

### ✅ Production-Ready Resilience
- Comprehensive error handling at all levels
- Graceful degradation on failures
- Browser-like User-Agent headers
- Timeout protection on requests
- Resource cleanup with context managers

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- requests
- beautifulsoup4
- urllib3

## Usage

### Basic Usage

```bash
python robust_scraper.py
```

This will:
1. Scrape all books from books.toscrape.com
2. Save data to `books_data.csv` in batches
3. Log progress to console and `scraper.log`

### Custom Configuration

Edit the configuration section in `robust_scraper.py`:

```python
BASE_URL = "http://books.toscrape.com/"
OUTPUT_CSV = "books_data.csv"
BATCH_SIZE = 50                    # Records per batch
MAX_WORKERS = 5                    # Concurrent threads
REQUEST_TIMEOUT = 10               # Seconds
MAX_RETRIES = 3                    # Retry attempts
BACKOFF_FACTOR = 0.5              # Exponential backoff multiplier
```

### Programmatic Usage

```python
from robust_scraper import RobustBookScraper

# Create scraper with custom settings
scraper = RobustBookScraper(
    output_file="my_books.csv",
    batch_size=100,
    max_workers=8,
    max_pages=5  # Limit to first 5 pages for testing
)

# Execute scraping
results = scraper.scrape()

print(f"Scraped {results['total_books']} books from {results['total_pages']} pages")
print(f"Completed in {results['duration_seconds']:.2f} seconds")
```

## Output

### CSV File Format

The scraper generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `title` | Book title |
| `price` | Price (e.g., "£19.99") |
| `rating` | Star rating (One, Two, Three, Four, Five) |
| `availability` | In stock status |
| `url` | Full URL to the book page |

### Example Output

```csv
title,price,rating,availability,url
"A Light in the Attic","£51.77","Three","In stock","http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
"Tipping Point: How Little Things Can Make a Big Difference","£48.23","Five","In stock","http://books.toscrape.com/catalogue/tipping-point-how-little-things-can-make-a-big-difference_997/index.html"
```

### Log File

Detailed logging to `scraper.log`:

```
2024-01-15 14:23:45 - __main__ - INFO - Scraping started
2024-01-15 14:23:46 - __main__ - INFO - Found 50 pages to scrape
2024-01-15 14:23:47 - __main__ - INFO - Scraped 20 books from http://books.toscrape.com/catalogue/page-1.html
...
```

## Architecture

### Core Classes

#### `Book` (Dataclass)
Represents a single book with type-safe fields and dictionary conversion.

#### `ThreadSafeCSVWriter`
Manages thread-safe CSV writing with locks:
- `__init__()`: Initialize with filepath and column names
- `write_batch()`: Write rows with automatic lock acquisition

#### `RobustBookScraper` (Main Orchestrator)
Coordinates the entire scraping process:
- `scrape()`: Execute full pipeline
- `scrape_pages_concurrent()`: Parallel page scraping
- `write_batch()`: Batch writing to CSV
- `flush_remaining_books()`: Final data flush

### Core Functions

#### Session Management
- `create_session_with_retries()`: Creates configured session with retry strategy

#### Scraping Functions
- `fetch_page()`: HTTP request with error handling
- `parse_book()`: BeautifulSoup element parsing
- `scrape_page_books()`: Full page scraping
- `get_page_urls()`: Discover all paginated URLs

#### Logging
- `setup_logging()`: Configure dual handlers (console + file)

## Performance Considerations

### Concurrency
- **Default Workers**: 5 threads for parallel page scraping
- **Batch Size**: 50 records per CSV write (minimize I/O)
- **Connection Reuse**: Single Session instance for all requests

### Optimization Tips

1. **Increase MAX_WORKERS** for faster scraping (with respect to server rate limits)
   ```python
   scraper = RobustBookScraper(max_workers=10)
   ```

2. **Increase BATCH_SIZE** for fewer disk writes (use more memory)
   ```python
   scraper = RobustBookScraper(batch_size=200)
   ```

3. **Reduce REQUEST_TIMEOUT** for faster failure detection
   ```python
   REQUEST_TIMEOUT = 5
   ```

4. **Test with max_pages** before full scrape
   ```python
   scraper = RobustBookScraper(max_pages=2)
   ```

## Error Handling

The scraper handles:
- **Timeout Errors**: Request timeouts with configurable duration
- **HTTP Errors**: Automatic retry with exponential backoff
- **Connection Errors**: Network failures with graceful degradation
- **Parsing Errors**: Malformed HTML with warning logs
- **File Errors**: CSV write failures with error logging
- **Thread Errors**: Execution errors in worker threads

## Logging Levels

- **DEBUG**: Detailed execution flow (file only)
- **INFO**: Major events and statistics (console + file)
- **WARNING**: Parsing issues and recoverable errors
- **ERROR**: Critical failures and exceptions

## Best Practices

1. **Respect Server Rate Limits**: Consider adding delays between requests
2. **Monitor Logs**: Check `scraper.log` for issues during execution
3. **Test First**: Use `max_pages=2` to test before full scrape
4. **Check Output**: Validate CSV before processing further
5. **Handle Cleanup**: Ensure proper session closure (automatic with context managers)

## Troubleshooting

### No books scraped
- Check internet connection
- Verify `BASE_URL` is accessible
- Check `scraper.log` for detailed errors
- Ensure BeautifulSoup selectors match current HTML structure

### Slow performance
- Increase `MAX_WORKERS` (default: 5)
- Decrease `REQUEST_TIMEOUT` (default: 10)
- Check system resources and network bandwidth

### CSV file issues
- Verify disk space available
- Check file permissions in output directory
- Ensure no other process locks the CSV file

### Memory usage high
- Reduce `BATCH_SIZE` to flush more frequently
- Reduce `MAX_WORKERS` to limit concurrent threads
- Process output CSV in chunks

## Extensions

### Add Proxy Support
```python
session.proxies = {"http": "http://proxy:8080"}
```

### Add Request Delays
```python
import time
time.sleep(0.1)  # Add in scrape_page_books()
```

### Add Authentication
```python
session.auth = ("username", "password")
```

### Custom Data Processing
```python
# Extend Book class or modify parse_book() function
```

## License

This scraper is provided for educational purposes on practice websites only.

## Author Notes

Built with production-grade Python patterns:
- Type safety with type hints
- Comprehensive logging
- Thread-safe operations
- Resource cleanup with context managers
- Modular, reusable code structure
- Robust error handling throughout
