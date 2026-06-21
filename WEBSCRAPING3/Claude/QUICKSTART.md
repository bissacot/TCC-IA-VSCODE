# Quick Start Guide

Get your robust web scraper running in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requires:**
- Python 3.8 or higher
- pip (Python package manager)

## 2. Run the Scraper

### Option A: Simple One-Liner (Recommended)

```bash
python robust_scraper.py
```

This will:
- Scrape all books from http://books.toscrape.com/
- Save data to `books_data.csv`
- Log progress to `scraper.log`
- Take approximately 2-5 minutes (depends on your internet)

### Option B: Test First (Recommended for First Run)

Edit `robust_scraper.py` and change this line:

```python
max_pages=None  # Change to: max_pages=2  # to test with just 2 pages
```

Then run:

```bash
python robust_scraper.py
```

This will scrape only the first 2 pages (about 40 books) in ~30 seconds.

### Option C: Use Examples

Interactive example menu:

```bash
python examples.py
```

Choose from:
1. Basic usage
2. Quick test
3. High performance
4. Conservative settings
5. Error handling
6. Batch processing
7. Production deployment

## 3. Check the Output

### View the CSV file

```bash
# Windows
type books_data.csv

# macOS/Linux
cat books_data.csv

# Or open in Excel/Sheets
```

### View the Log file

```bash
type scraper.log
```

## 4. Customize (Optional)

### Edit configuration in `robust_scraper.py`:

```python
BASE_URL = "http://books.toscrape.com/"
OUTPUT_CSV = "books_data.csv"          # Change output filename
BATCH_SIZE = 50                        # More = faster, uses more memory
MAX_WORKERS = 5                        # More = parallel threads
REQUEST_TIMEOUT = 10                   # Seconds to wait per request
MAX_RETRIES = 3                        # How many times to retry
```

### Or use the separate `config.py` file:

```bash
# Edit config.py with your settings
python robust_scraper.py  # Will read from config.py
```

## 5. Example Results

```
Total Books: 1000
Total Pages: 50
Duration: 180 seconds (3 minutes)
Success: True
Output File: books_data.csv
```

CSV columns:
```
title,price,rating,availability,url
"A Light in the Attic","£51.77","Three","In stock","http://..."
"Tipping Point...","£48.23","Five","In stock","http://..."
...
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'requests'"

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

### Problem: No books scraped

**Solution:** Check your internet connection and logs

```bash
# View detailed logs
type scraper.log

# Try with more retries and longer timeout
# Edit robust_scraper.py:
MAX_RETRIES = 5
REQUEST_TIMEOUT = 20
```

### Problem: Very slow scraping

**Solution:** Increase workers and batch size

```python
# In robust_scraper.py or examples.py:
scraper = RobustBookScraper(
    max_workers=10,      # Was 5
    batch_size=200,      # Was 50
)
```

## Next Steps

1. ✅ Run the basic scraper
2. ✅ Check the CSV output
3. ✅ Review the logs
4. ✅ Read `README.md` for full documentation
5. ✅ Check `examples.py` for advanced usage
6. ✅ Modify `config.py` or `robust_scraper.py` for your needs

## Key Features at a Glance

✓ **Modular Design** - Clean, well-organized code with type hints
✓ **Robust Retry Logic** - Automatic retries with exponential backoff
✓ **Concurrent Processing** - Parallel scraping with thread pool
✓ **Thread-Safe CSV** - Batch writing with locks
✓ **Comprehensive Logging** - Detailed logs to file and console
✓ **Error Handling** - Graceful failures, never crashes
✓ **Production Ready** - Ready for real-world deployment

## Production Checklist

Before deploying to production:

- [ ] Test with `max_pages=2` first
- [ ] Monitor the `scraper.log` file
- [ ] Check output `books_data.csv` is valid
- [ ] Adjust `MAX_WORKERS` based on server load
- [ ] Consider adding request delays between pages
- [ ] Set up log rotation for long-running scrapes
- [ ] Test error handling with network interruptions

## Tips & Tricks

### Scrape only first N pages for testing:

```python
scraper = RobustBookScraper(max_pages=5)
```

### Process results programmatically:

```python
import csv

with open("books_data.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['title']} - {row['price']}")
```

### Resume scraping:

Change `APPEND_TO_CSV = True` in config, scraper will append to existing file.

### Run on a schedule:

```bash
# Windows Task Scheduler
# or
# Linux crontab: 0 2 * * * python /path/to/robust_scraper.py
```

## Need Help?

1. Check `README.md` for full documentation
2. View `scraper.log` for detailed error messages
3. Run `examples.py` to see different configurations
4. Check `robust_scraper.py` source code (heavily commented)

---

**You're all set! Happy scraping! 🚀**
