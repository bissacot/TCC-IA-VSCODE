"""
Quick Start Examples for Robust Book Scraper

This file demonstrates various ways to use the robust_scraper module.
"""

from robust_scraper import RobustBookScraper

# ============================================================================
# Example 1: Basic Usage - Scrape All Books (Default Settings)
# ============================================================================

def example_basic():
    """Scrape all books with default settings."""
    print("\n" + "="*70)
    print("Example 1: Basic Usage - Scrape All Books")
    print("="*70)
    
    scraper = RobustBookScraper()
    results = scraper.scrape()
    
    print(f"\nResults:")
    print(f"  Total Books: {results['total_books']}")
    print(f"  Total Pages: {results['total_pages']}")
    print(f"  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"  Output: books_data.csv")


# ============================================================================
# Example 2: Quick Test - Scrape Only First 2 Pages
# ============================================================================

def example_quick_test():
    """Quick test scraping only the first 2 pages."""
    print("\n" + "="*70)
    print("Example 2: Quick Test - First 2 Pages Only")
    print("="*70)
    
    scraper = RobustBookScraper(
        max_pages=2,
        output_file="test_output.csv"
    )
    results = scraper.scrape()
    
    print(f"\nResults:")
    print(f"  Total Books: {results['total_books']}")
    print(f"  Total Pages: {results['total_pages']}")
    print(f"  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"  Output: test_output.csv")


# ============================================================================
# Example 3: High Performance - More Workers and Larger Batches
# ============================================================================

def example_high_performance():
    """Scrape with optimized settings for high performance."""
    print("\n" + "="*70)
    print("Example 3: High Performance Configuration")
    print("="*70)
    
    scraper = RobustBookScraper(
        output_file="books_fast.csv",
        batch_size=200,        # Larger batches = fewer I/O operations
        max_workers=10,        # More workers = faster scraping
        max_pages=None         # Scrape all pages
    )
    results = scraper.scrape()
    
    print(f"\nResults:")
    print(f"  Total Books: {results['total_books']}")
    print(f"  Total Pages: {results['total_pages']}")
    print(f"  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"  Performance: {results['total_books'] / results['duration_seconds']:.1f} books/sec")


# ============================================================================
# Example 4: Conservative Settings - For Reliable Scraping
# ============================================================================

def example_conservative():
    """Scrape with conservative settings for maximum reliability."""
    print("\n" + "="*70)
    print("Example 4: Conservative Configuration (Maximum Reliability)")
    print("="*70)
    
    scraper = RobustBookScraper(
        output_file="books_reliable.csv",
        batch_size=25,         # Small batches for frequent saving
        max_workers=2,         # Few workers = less strain on target
        max_pages=None
    )
    results = scraper.scrape()
    
    print(f"\nResults:")
    print(f"  Total Books: {results['total_books']}")
    print(f"  Total Pages: {results['total_pages']}")
    print(f"  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"  Output File: books_reliable.csv")


# ============================================================================
# Example 5: Error Handling - Graceful Failure Demonstration
# ============================================================================

def example_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n" + "="*70)
    print("Example 5: Error Handling")
    print("="*70)
    
    try:
        scraper = RobustBookScraper(
            max_pages=3,
            output_file="error_test.csv"
        )
        results = scraper.scrape()
        
        if results['success']:
            print(f"\n✓ Scraping successful!")
            print(f"  Total Books: {results['total_books']}")
        else:
            print(f"\n✗ Scraping failed!")
            if 'error' in results:
                print(f"  Error: {results['error']}")
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# Example 6: Batch Processing - Custom Logic After Scraping
# ============================================================================

def example_batch_processing():
    """Scrape and then process the output."""
    print("\n" + "="*70)
    print("Example 6: Batch Processing")
    print("="*70)
    
    import csv
    
    # Scrape data
    scraper = RobustBookScraper(
        max_pages=2,
        output_file="batch_test.csv"
    )
    results = scraper.scrape()
    
    # Process the output
    if results['success']:
        print(f"\nScraping complete. Processing {results['total_books']} books...")
        
        # Read and analyze the CSV
        books_by_rating = {}
        with open("batch_test.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rating = row['rating']
                books_by_rating[rating] = books_by_rating.get(rating, 0) + 1
        
        print("\nBooks by Rating:")
        for rating in sorted(books_by_rating.keys(), reverse=True):
            count = books_by_rating[rating]
            print(f"  {rating}: {count} books")


# ============================================================================
# Example 7: Production Deployment - Full Configuration
# ============================================================================

def example_production():
    """Production-ready configuration with all optimizations."""
    print("\n" + "="*70)
    print("Example 7: Production Configuration")
    print("="*70)
    
    import datetime
    
    # Create timestamped output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"books_scrape_{timestamp}.csv"
    
    scraper = RobustBookScraper(
        output_file=output_file,
        batch_size=100,
        max_workers=5,
        max_pages=None  # Scrape all
    )
    
    print(f"Starting production scrape...")
    print(f"Output file: {output_file}")
    
    results = scraper.scrape()
    
    print(f"\n{'='*70}")
    print(f"Production Scrape Complete")
    print(f"{'='*70}")
    print(f"Total Books: {results['total_books']}")
    print(f"Total Pages: {results['total_pages']}")
    print(f"Duration: {results['duration_seconds']:.2f} seconds")
    print(f"Success: {results['success']}")
    print(f"Output File: {output_file}")
    print(f"Log File: scraper.log")
    print(f"{'='*70}")


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Run examples."""
    examples = {
        "1": ("Basic Usage - All Books", example_basic),
        "2": ("Quick Test - First 2 Pages", example_quick_test),
        "3": ("High Performance", example_high_performance),
        "4": ("Conservative Settings", example_conservative),
        "5": ("Error Handling", example_error_handling),
        "6": ("Batch Processing", example_batch_processing),
        "7": ("Production Deployment", example_production),
    }
    
    print("\n" + "="*70)
    print("Robust Book Scraper - Examples")
    print("="*70)
    print("\nAvailable Examples:")
    
    for key, (description, _) in examples.items():
        print(f"  {key}: {description}")
    
    print("\n  0: Run All Examples")
    print("  q: Quit")
    
    choice = input("\nSelect example (0-7, q to quit): ").strip().lower()
    
    if choice == "q":
        print("Goodbye!")
        return
    
    if choice == "0":
        for key in ["1", "2", "3", "4", "5", "6", "7"]:
            _, func = examples[key]
            try:
                func()
            except Exception as e:
                print(f"Error in example {key}: {e}")
    elif choice in examples:
        _, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
