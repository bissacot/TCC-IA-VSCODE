"""
Main ETL orchestrator that coordinates the entire pipeline.

Manages the flow from extraction through transformation to loading.
"""

from typing import Dict, Any, List
from datetime import datetime
import json

from src.utils import LoggerConfig
from src.etl.extractor import ExtractionOrchestrator
from src.etl.transformer import (
    SalesTransformer,
    CustomerTransformer,
    ProductTransformer,
    DataQualityReport,
)
from src.etl.loader import DataLoader, DatabaseInitializer
from config.settings import REPORTS_PATH


logger = LoggerConfig.get_logger(__name__)


class ETLPipeline:
    """Orchestrates the complete ETL pipeline."""

    def __init__(self) -> None:
        """Initialize ETL pipeline."""
        self.extractor = ExtractionOrchestrator()
        self.data_loader = DataLoader()
        self.quality_reports: Dict[str, DataQualityReport] = {}
        self.pipeline_start_time = None
        self.pipeline_end_time = None

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline.

        Returns:
            Dictionary with execution results and metrics
        """
        logger.info("=" * 80)
        logger.info("Starting ETL Pipeline Execution")
        logger.info("=" * 80)

        self.pipeline_start_time = datetime.now()

        try:
            # Step 1: Initialize Database
            logger.info("Step 1: Initializing database")
            DatabaseInitializer.create_all_tables()

            # Step 2: Extract Data
            logger.info("Step 2: Extracting data from sources")
            extracted_data = self.extractor.extract_all()

            # Step 3: Transform Data
            logger.info("Step 3: Transforming data")
            transformed_data = self._transform_data(extracted_data)

            # Step 4: Load Data
            logger.info("Step 4: Loading data into database")
            self._load_data(transformed_data)

            # Step 5: Generate Reports
            logger.info("Step 5: Generating reports")
            self._generate_reports()

            self.pipeline_end_time = datetime.now()

            results = self._generate_execution_summary()

            logger.info("=" * 80)
            logger.info("ETL Pipeline Execution Completed Successfully")
            logger.info("=" * 80)

            return results

        except Exception as e:
            logger.error(f"ETL Pipeline execution failed: {e}", exc_info=True)
            self.pipeline_end_time = datetime.now()
            raise

    def _transform_data(
        self, extracted_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Transform extracted data.

        Args:
            extracted_data: Raw data from extraction phase

        Returns:
            Dictionary with transformed data
        """
        transformed_data = {}

        # Transform sales data
        if extracted_data.get("sales"):
            sales_transformer = SalesTransformer()
            transformed_sales, quality_report = sales_transformer.transform(
                extracted_data["sales"]
            )
            transformed_data["sales"] = transformed_sales
            self.quality_reports["sales"] = quality_report
            logger.info(f"Sales transformation: {quality_report}")

        # Transform customer data
        if extracted_data.get("customers"):
            customer_transformer = CustomerTransformer()
            transformed_customers, quality_report = customer_transformer.transform(
                extracted_data["customers"]
            )
            transformed_data["customers"] = transformed_customers
            self.quality_reports["customers"] = quality_report
            logger.info(f"Customers transformation: {quality_report}")

        # Transform product data
        if extracted_data.get("products"):
            product_transformer = ProductTransformer()
            transformed_products, quality_report = product_transformer.transform(
                extracted_data["products"]
            )
            transformed_data["products"] = transformed_products
            self.quality_reports["products"] = quality_report
            logger.info(f"Products transformation: {quality_report}")

        return transformed_data

    def _load_data(self, transformed_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Load transformed data into database.

        Args:
            transformed_data: Transformed data from transformation phase
        """
        if transformed_data.get("customers"):
            self.data_loader.load_customers(transformed_data["customers"])

        if transformed_data.get("products"):
            self.data_loader.load_products(transformed_data["products"])

        if transformed_data.get("sales"):
            self.data_loader.load_sales(transformed_data["sales"])

        # Save quality metrics
        for data_type, report in self.quality_reports.items():
            self.data_loader.save_quality_metrics(report, status="success")

    def _generate_reports(self) -> None:
        """Generate execution reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_PATH / f"etl_report_{timestamp}.json"

        report_data = {
            "execution_time": {
                "start": self.pipeline_start_time.isoformat(),
                "end": self.pipeline_end_time.isoformat(),
                "duration_seconds": (
                    self.pipeline_end_time - self.pipeline_start_time
                ).total_seconds(),
            },
            "quality_metrics": {
                data_type: report.to_dict()
                for data_type, report in self.quality_reports.items()
            },
            "loader_status": self.data_loader.get_status_summary(),
        }

        try:
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

            logger.info(f"ETL report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save ETL report: {e}")

    def _generate_execution_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        duration = (self.pipeline_end_time - self.pipeline_start_time).total_seconds()

        return {
            "status": "success",
            "etl_run_id": self.data_loader.etl_run_id,
            "duration_seconds": duration,
            "records_processed": sum(
                r.processed_records for r in self.quality_reports.values()
            ),
            "records_invalid": sum(
                r.invalid_records for r in self.quality_reports.values()
            ),
            "duplicates_removed": sum(
                r.duplicates_removed for r in self.quality_reports.values()
            ),
            "records_loaded": self.data_loader.records_loaded,
            "records_failed": self.data_loader.records_failed,
            "quality_reports": {
                data_type: report.to_dict()
                for data_type, report in self.quality_reports.items()
            },
        }
