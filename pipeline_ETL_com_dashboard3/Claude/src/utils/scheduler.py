"""ETL Job Scheduling."""

import schedule
import time
from typing import Callable
from datetime import datetime
from src.utils.logger import logger
from src.utils.config import load_config_from_env
from src.etl_pipeline import ETLPipeline


class ETLScheduler:
    """Schedules and manages ETL jobs."""
    
    def __init__(self):
        """Initialize ETL scheduler."""
        self.config = load_config_from_env()
        self.jobs = []
    
    def schedule_daily_job(self, job_time: str = "02:00") -> None:
        """
        Schedule daily ETL job.
        
        Args:
            job_time: Time to run job in HH:MM format (default: 02:00)
        """
        def run_etl():
            logger.info(f"Starting scheduled ETL job at {datetime.now()}")
            try:
                pipeline = ETLPipeline(self.config)
                pipeline.run()
                logger.info("Scheduled ETL job completed successfully")
            except Exception as e:
                logger.error(f"Scheduled ETL job failed: {str(e)}", exc_info=True)
        
        schedule.every().day.at(job_time).do(run_etl)
        self.jobs.append(run_etl)
        logger.info(f"Scheduled daily ETL job at {job_time}")
    
    def schedule_hourly_job(self) -> None:
        """Schedule hourly ETL job."""
        def run_etl():
            logger.info(f"Starting scheduled hourly ETL job at {datetime.now()}")
            try:
                pipeline = ETLPipeline(self.config)
                pipeline.run()
                logger.info("Scheduled hourly ETL job completed successfully")
            except Exception as e:
                logger.error(f"Scheduled hourly ETL job failed: {str(e)}", exc_info=True)
        
        schedule.every().hour.do(run_etl)
        self.jobs.append(run_etl)
        logger.info("Scheduled hourly ETL job")
    
    def schedule_weekly_job(self, day: str = "monday", job_time: str = "02:00") -> None:
        """
        Schedule weekly ETL job.
        
        Args:
            day: Day of week (monday, tuesday, etc.)
            job_time: Time to run job in HH:MM format
        """
        def run_etl():
            logger.info(f"Starting scheduled weekly ETL job at {datetime.now()}")
            try:
                pipeline = ETLPipeline(self.config)
                pipeline.run()
                logger.info("Scheduled weekly ETL job completed successfully")
            except Exception as e:
                logger.error(f"Scheduled weekly ETL job failed: {str(e)}", exc_info=True)
        
        schedule.every().week.at(job_time).do(run_etl).tag(day)
        self.jobs.append(run_etl)
        logger.info(f"Scheduled weekly ETL job on {day} at {job_time}")
    
    def run_scheduler(self) -> None:
        """Run the scheduler (blocking call)."""
        logger.info("Starting ETL scheduler...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("ETL scheduler stopped")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)
    
    def run_scheduler_background(self) -> None:
        """Run scheduler in background (requires APScheduler or similar)."""
        logger.info("Note: For background scheduling, use APScheduler instead")


def main():
    """Main scheduler entry point."""
    scheduler = ETLScheduler()
    
    # Schedule jobs
    scheduler.schedule_daily_job("02:00")  # Run at 2 AM daily
    scheduler.schedule_weekly_job("sunday", "03:00")  # Run on Sundays at 3 AM
    
    # Start scheduler
    scheduler.run_scheduler()


if __name__ == "__main__":
    main()
