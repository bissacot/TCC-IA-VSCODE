"""
Main ETL pipeline orchestration.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional
import time

import pandas as pd

from src.config import ETLConfig
from src.database.connection import DatabaseManager
from src.database.initialization import create_all_tables
from src.etl.extractor import MultiSourceExtractor, CSVExtractor, JSONExtractor, APIExtractor
from src.etl.transformer import DataTransformer
from src.etl.loader import DataLoader
from src.utils.logging_config import setup_logging
from src.utils.models import DataQualityReport

logger = setup_logging(__name__)


class ETLPipeline:
    """Main ETL pipeline orchestrator."""

    def __init__(self) -> None:
        """Initialize ETL pipeline."""
        self.extractor = MultiSourceExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.start_time = None
        logger.info("Initialized ETL pipeline")

    def setup_database(self) -> bool:
        """
        Setup database connection and create tables.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Setting up database...")
            DatabaseManager.initialize()

            # Check health
            if not DatabaseManager.health_check():
                logger.error("Database health check failed")
                return False

            # Create tables
            create_all_tables()
            logger.info("Database setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            return False

    def register_data_sources(
        self,
        csv_path: Optional[str] = None,
        json_path: Optional[str] = None,
        api_config: Optional[Dict] = None,
    ) -> None:
        """
        Register data sources.

        Args:
            csv_path: Path to CSV file with sales data
            json_path: Path to JSON file with customer data
            api_config: Dictionary with API configuration
        """
        if csv_path:
            self.extractor.register_extractor(
                "csv_sales",
                CSVExtractor(csv_path),
            )
            logger.info(f"Registered CSV extractor: {csv_path}")

        if json_path:
            self.extractor.register_extractor(
                "json_customers",
                JSONExtractor(json_path),
            )
            logger.info(f"Registered JSON extractor: {json_path}")

        if api_config:
            self.extractor.register_extractor(
                "api_products",
                APIExtractor(**api_config),
            )
            logger.info(f"Registered API extractor: {api_config.get('base_url')}")

    def run(self) -> Tuple[bool, DataQualityReport, Optional[str]]:
        """
        Run complete ETL pipeline.

        Returns:
            Tuple of (success, quality_report, error_message)
        """
        self.start_time = datetime.utcnow()
        error_message = None

        try:
            logger.info("=" * 80)
            logger.info("Starting ETL Pipeline Execution")
            logger.info("=" * 80)

            # 1. EXTRACT
            logger.info("\n[STEP 1] EXTRACTION PHASE")
            logger.info("-" * 80)
            extracted_data = self.extractor.extract_all()

            if not extracted_data:
                error_message = "No data extracted from any source"
                logger.error(error_message)
                return False, None, error_message

            # 2. TRANSFORM
            logger.info("\n[STEP 2] TRANSFORMATION PHASE")
            logger.info("-" * 80)
            transform_start = datetime.utcnow()
            transform_metrics = {}

            # Transform each data source
            if "csv_sales" in extracted_data:
                sales_df, metrics = self.transformer.transform_sales_data(
                    extracted_data["csv_sales"]
                )
                transform_metrics["sales"] = metrics
            else:
                sales_df = pd.DataFrame()

            if "json_customers" in extracted_data:
                customers_df, metrics = self.transformer.transform_customer_data(
                    extracted_data["json_customers"]
                )
                transform_metrics["customers"] = metrics
            else:
                customers_df = pd.DataFrame()

            if "api_products" in extracted_data:
                products_df, metrics = self.transformer.transform_product_data(
                    extracted_data["api_products"]
                )
                transform_metrics["products"] = metrics
            else:
                products_df = pd.DataFrame()

            transform_time = (datetime.utcnow() - transform_start).total_seconds()

            # 3. LOAD
            logger.info("\n[STEP 3] LOADING PHASE")
            logger.info("-" * 80)
            load_start = datetime.utcnow()

            customers_loaded = 0
            products_loaded = 0
            sales_loaded = 0

            if not customers_df.empty:
                customers_loaded = self.loader.load_customers(
                    customers_df,
                    incremental=ETLConfig.INCREMENTAL_MODE,
                )

            if not products_df.empty:
                products_loaded = self.loader.load_products(
                    products_df,
                    incremental=ETLConfig.INCREMENTAL_MODE,
                )

            if not sales_df.empty:
                sales_loaded = self.loader.load_sales(sales_df)

            load_time = (datetime.utcnow() - load_start).total_seconds()

            # 4. GENERATE QUALITY REPORT
            logger.info("\n[STEP 4] DATA QUALITY REPORTING")
            logger.info("-" * 80)
            
            metrics_list = [
                transform_metrics.get(key, {}) 
                for key in ["customers", "products", "sales"]
            ]
            metrics_list = [m for m in metrics_list if m]

            quality_report = self.transformer.generate_quality_report(
                metrics_list,
                transform_time,
            )

            # Store quality report
            self.loader.store_quality_report(quality_report)

            # 5. SAVE LAST RUN TIME
            logger.info("\n[STEP 5] FINALIZING")
            logger.info("-" * 80)
            self._save_last_run_time()

            # Summary
            total_time = (datetime.utcnow() - self.start_time).total_seconds()
            logger.info("\n" + "=" * 80)
            logger.info("ETL Pipeline Execution Summary")
            logger.info("=" * 80)
            logger.info(f"Total Execution Time: {total_time:.2f} seconds")
            logger.info(f"Customers Loaded: {customers_loaded}")
            logger.info(f"Products Loaded: {products_loaded}")
            logger.info(f"Sales Loaded: {sales_loaded}")
            logger.info(f"Quality Report Status: {quality_report.status}")
            logger.info("=" * 80 + "\n")

            return True, quality_report, None

        except Exception as e:
            error_message = f"ETL pipeline failed: {str(e)}"
            logger.error(error_message)
            return False, None, error_message

    def _save_last_run_time(self) -> None:
        """Save last run timestamp to file."""
        try:
            ETLConfig.LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ETLConfig.LAST_RUN_FILE, "w") as f:
                f.write(datetime.utcnow().isoformat())
            logger.info(f"Last run time saved to {ETLConfig.LAST_RUN_FILE}")
        except Exception as e:
            logger.warning(f"Failed to save last run time: {str(e)}")

    def get_last_run_time(self) -> Optional[datetime]:
        """Get last run timestamp."""
        try:
            if ETLConfig.LAST_RUN_FILE.exists():
                with open(ETLConfig.LAST_RUN_FILE, "r") as f:
                    return datetime.fromisoformat(f.read().strip())
        except Exception as e:
            logger.warning(f"Failed to read last run time: {str(e)}")
        return None
