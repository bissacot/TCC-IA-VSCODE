"""
Main entry point for ETL pipeline execution.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from src.config import DatabaseConfig, ETLConfig
from src.database.connection import DatabaseManager
from src.database.initialization import create_all_tables
from src.etl.pipeline import ETLPipeline
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def run_etl(
    csv_path: str,
    json_path: str,
    api_base_url: str,
    api_endpoint: str,
    api_key: str = None,
) -> bool:
    """
    Run ETL pipeline.

    Args:
        csv_path: Path to sales CSV file
        json_path: Path to customer JSON file
        api_base_url: API base URL for products
        api_endpoint: API endpoint path
        api_key: Optional API key

    Returns:
        True if successful
    """
    try:
        # Initialize pipeline
        pipeline = ETLPipeline()

        # Setup database
        if not pipeline.setup_database():
            logger.error("Database setup failed")
            return False

        # Register data sources
        api_config = {
            "base_url": api_base_url,
            "endpoint": api_endpoint,
            "api_key": api_key or "",
            "timeout": 30,
        }

        pipeline.register_data_sources(
            csv_path=csv_path,
            json_path=json_path,
            api_config=api_config,
        )

        # Run pipeline
        success, quality_report, error_msg = pipeline.run()

        if success:
            logger.info("ETL pipeline completed successfully")
            if quality_report:
                logger.info(f"Quality Report: {quality_report}")
            return True
        else:
            logger.error(f"ETL pipeline failed: {error_msg}")
            return False

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return False


def run_dashboard() -> None:
    """Run Streamlit dashboard."""
    import subprocess

    try:
        logger.info("Starting Streamlit dashboard...")
        subprocess.run(
            ["streamlit", "run", "src/dashboard/app.py"],
            check=True,
        )
    except Exception as e:
        logger.error(f"Failed to start dashboard: {str(e)}")
        raise


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ETL and Dashboard Solution for Sales Analysis"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ETL command
    etl_parser = subparsers.add_parser("etl", help="Run ETL pipeline")
    etl_parser.add_argument("--csv", required=True, help="Path to sales CSV file")
    etl_parser.add_argument("--json", required=True, help="Path to customer JSON file")
    etl_parser.add_argument("--api-url", required=True, help="API base URL")
    etl_parser.add_argument("--api-endpoint", required=True, help="API endpoint path")
    etl_parser.add_argument("--api-key", help="API key (optional)")

    # Dashboard command
    subparsers.add_parser("dashboard", help="Run Streamlit dashboard")

    # Init command
    subparsers.add_parser("init", help="Initialize database")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "etl":
            success = run_etl(
                csv_path=args.csv,
                json_path=args.json,
                api_base_url=args.api_url,
                api_endpoint=args.api_endpoint,
                api_key=args.api_key,
            )
            return 0 if success else 1

        elif args.command == "dashboard":
            run_dashboard()
            return 0

        elif args.command == "init":
            logger.info("Initializing database...")
            DatabaseManager.initialize(DatabaseConfig)
            create_all_tables()
            logger.info("Database initialized successfully")
            return 0

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    finally:
        DatabaseManager.close()


if __name__ == "__main__":
    sys.exit(main())
