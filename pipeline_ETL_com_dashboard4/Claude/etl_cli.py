"""
Command-line interface for running ETL operations.

Provides commands for extracting, transforming, loading, and scheduling data.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import LoggerConfig
from src.etl import ETLPipeline
from src.etl.loader import DatabaseInitializer


logger = LoggerConfig.get_logger(__name__)


def setup_database(args: argparse.Namespace) -> None:
    """Initialize database schema."""
    logger.info("Setting up database schema")

    if args.drop:
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            DatabaseInitializer.drop_all_tables()

    DatabaseInitializer.create_all_tables()
    logger.info("Database setup completed")


def run_etl(args: argparse.Namespace) -> None:
    """Run the complete ETL pipeline."""
    logger.info("Starting ETL pipeline")

    try:
        pipeline = ETLPipeline()
        results = pipeline.run()

        logger.info("ETL Pipeline Results:")
        logger.info(f"  Status: {results['status']}")
        logger.info(f"  Records Processed: {results['records_processed']}")
        logger.info(f"  Records Invalid: {results['records_invalid']}")
        logger.info(f"  Duplicates Removed: {results['duplicates_removed']}")
        logger.info(f"  Records Loaded: {results['records_loaded']}")
        logger.info(f"  Duration: {results['duration_seconds']:.2f} seconds")

        print("\n" + "=" * 80)
        print("ETL EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Status: {results['status']}")
        print(f"ETL Run ID: {results['etl_run_id']}")
        print(f"Records Processed: {results['records_processed']}")
        print(f"Records Invalid: {results['records_invalid']}")
        print(f"Duplicates Removed: {results['duplicates_removed']}")
        print(f"Records Loaded: {results['records_loaded']}")
        print(f"Records Failed: {results['records_failed']}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


def main() -> None:
    """Parse arguments and execute requested operation."""
    parser = argparse.ArgumentParser(
        description="Sales ETL Pipeline - Extract, Transform, Load data"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Initialize database")
    setup_parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating new ones",
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run ETL pipeline")

    # Parse arguments
    args = parser.parse_args()

    if args.command == "setup":
        setup_database(args)
    elif args.command == "run":
        run_etl(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
