"""
ETL Scheduler for automated pipeline execution.
"""

from datetime import datetime, time
from typing import Optional, Callable
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class ETLScheduler:
    """Manage scheduled ETL execution."""

    def __init__(self) -> None:
        """Initialize scheduler."""
        self.scheduler = BackgroundScheduler()
        logger.info("Initialized ETL Scheduler")

    def schedule_daily(
        self,
        job_func: Callable,
        hour: int = 2,
        minute: int = 0,
        job_id: str = "daily_etl",
    ) -> None:
        """
        Schedule job to run daily at specific time.

        Args:
            job_func: Function to execute
            hour: Hour (0-23)
            minute: Minute (0-59)
            job_id: Job identifier
        """
        try:
            self.scheduler.add_job(
                job_func,
                CronTrigger(hour=hour, minute=minute),
                id=job_id,
                name=f"Daily ETL at {hour:02d}:{minute:02d}",
                replace_existing=True,
            )
            logger.info(f"Scheduled daily job: {job_id} at {hour:02d}:{minute:02d}")
        except Exception as e:
            logger.error(f"Failed to schedule daily job: {str(e)}")
            raise

    def schedule_interval(
        self,
        job_func: Callable,
        hours: int = 1,
        job_id: str = "interval_etl",
    ) -> None:
        """
        Schedule job to run at regular intervals.

        Args:
            job_func: Function to execute
            hours: Interval in hours
            job_id: Job identifier
        """
        try:
            self.scheduler.add_job(
                job_func,
                'interval',
                hours=hours,
                id=job_id,
                name=f"Interval ETL every {hours} hour(s)",
                replace_existing=True,
            )
            logger.info(f"Scheduled interval job: {job_id} every {hours} hour(s)")
        except Exception as e:
            logger.error(f"Failed to schedule interval job: {str(e)}")
            raise

    def schedule_cron(
        self,
        job_func: Callable,
        cron_expression: str,
        job_id: str = "cron_etl",
    ) -> None:
        """
        Schedule job using cron expression.

        Args:
            job_func: Function to execute
            cron_expression: Cron expression (e.g., '0 2 * * *' for 2 AM daily)
            job_id: Job identifier
        """
        try:
            # Parse cron expression
            parts = cron_expression.split()
            if len(parts) != 5:
                raise ValueError("Invalid cron expression")

            minute, hour, day, month, day_of_week = parts

            self.scheduler.add_job(
                job_func,
                CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                ),
                id=job_id,
                name=f"Cron ETL: {cron_expression}",
                replace_existing=True,
            )
            logger.info(f"Scheduled cron job: {job_id} with expression: {cron_expression}")
        except Exception as e:
            logger.error(f"Failed to schedule cron job: {str(e)}")
            raise

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("ETL Scheduler started")
        else:
            logger.warning("Scheduler is already running")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("ETL Scheduler stopped")
        else:
            logger.warning("Scheduler is not running")

    def get_jobs(self) -> list:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()

    def remove_job(self, job_id: str) -> None:
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")

    def pause_job(self, job_id: str) -> None:
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job paused: {job_id}")
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {str(e)}")

    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job resumed: {job_id}")
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {str(e)}")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.scheduler.running
