"""
ETL scheduler for automated pipeline execution.

Supports scheduling ETL runs at specified intervals.
"""

import sys
from pathlib import Path
import time
from datetime import datetime

import schedule

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import LoggerConfig
from src.etl import ETLPipeline
from config.settings import SCHEDULE_INTERVAL


logger = LoggerConfig.get_logger(__name__)


def job() -> None:
    """Execute ETL job."""
    logger.info("=" * 80)
    logger.info(f"Scheduled ETL job started at {datetime.now()}")
    logger.info("=" * 80)

    try:
        pipeline = ETLPipeline()
        results = pipeline.run()

        logger.info("Scheduled ETL completed successfully")
        logger.info(f"Results: {results}")

    except Exception as e:
        logger.error(f"Scheduled ETL failed: {e}", exc_info=True)


def main() -> None:
    """Start the scheduler."""
    logger.info("Starting ETL Scheduler")
    logger.info(f"Schedule: {SCHEDULE_INTERVAL}")

    # Schedule job
    # Simple daily schedule at 2 AM
    schedule.every().day.at("02:00").do(job)

    logger.info("Scheduler initialized. Waiting for scheduled jobs...")

    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
