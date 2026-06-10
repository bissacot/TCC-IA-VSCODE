"""ETL Pipeline Orchestrator."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
from src.extractors import CSVExtractor, JSONExtractor, APIExtractor
from src.transformers import DataTransformer
from src.loaders import DataLoader
from src.utils.logger import logger, setup_logger
from src.utils.config import ETLConfig, load_config_from_env
from src.utils.models import DataQualityReport
from src.utils.exceptions import ETLException


class ETLPipeline:
    """Main ETL Pipeline Orchestrator."""
    
    def __init__(self, config: ETLConfig):
        """
        Initialize ETL Pipeline.
        
        Args:
            config: ETL configuration
        """
        self.config = config
        self.logger = setup_logger(
            __name__,
            log_file="logs/etl_pipeline.log",
            level=getattr(__import__('logging'), config.log_level)
        )
        self.quality_report = DataQualityReport()
        self.execution_start = None
        self.execution_end = None
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline.
        
        Returns:
            Pipeline execution summary
        """
        try:
            self.execution_start = datetime.now()
            self.logger.info("="*80)
            self.logger.info("Starting ETL Pipeline Execution")
            self.logger.info("="*80)
            
            # Step 1: Extract data
            customers_df, products_df, sales_df = self._extract_data()
            
            # Step 2: Transform data
            customers_df, products_df, sales_df = self._transform_data(
                customers_df, products_df, sales_df
            )
            
            # Step 3: Load data
            self._load_data(customers_df, products_df, sales_df)
            
            # Step 4: Generate quality report
            self._generate_quality_report()
            
            self.execution_end = datetime.now()
            
            summary = self._generate_summary()
            self.logger.info("="*80)
            self.logger.info("ETL Pipeline Execution Completed Successfully")
            self.logger.info("="*80)
            
            return summary
        
        except Exception as e:
            self.logger.error(f"ETL Pipeline failed: {str(e)}", exc_info=True)
            raise ETLException(f"ETL pipeline error: {str(e)}")
    
    def _extract_data(self) -> tuple:
        """Extract data from all sources."""
        self.logger.info("Starting data extraction phase...")
        
        try:
            # Extract customers from JSON
            self.logger.info(f"Extracting customers from: {self.config.json_path}")
            customer_extractor = JSONExtractor(self.config.json_path)
            customers_df = customer_extractor.extract()
            
            # Extract sales from CSV
            self.logger.info(f"Extracting sales from: {self.config.csv_path}")
            sales_extractor = CSVExtractor(self.config.csv_path)
            sales_df = sales_extractor.extract()
            
            # Extract products from API
            self.logger.info(f"Extracting products from API: {self.config.api_config.base_url}")
            product_extractor = APIExtractor(
                self.config.api_config,
                endpoint="/api/products"
            )
            products_df = product_extractor.extract()
            product_extractor.close()
            
            self.logger.info("Data extraction phase completed")
            return customers_df, products_df, sales_df
        
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            raise
    
    def _transform_data(self, customers_df, products_df, sales_df):
        """Transform extracted data."""
        self.logger.info("Starting data transformation phase...")
        
        try:
            transformer = DataTransformer()
            
            # Transform customers
            self.logger.info("Transforming customer data...")
            customers_df, customer_quality = transformer.transform_customer_data(customers_df)
            
            # Transform products
            self.logger.info("Transforming product data...")
            transformer = DataTransformer()
            products_df, product_quality = transformer.transform_product_data(products_df)
            
            # Transform sales
            self.logger.info("Transforming sales data...")
            transformer = DataTransformer()
            sales_df, sales_quality = transformer.transform_sales_data(sales_df)
            
            # Merge quality reports
            self.quality_report.total_records_processed = (
                customer_quality.total_records_processed +
                product_quality.total_records_processed +
                sales_quality.total_records_processed
            )
            self.quality_report.duplicates_removed = (
                customer_quality.duplicates_removed +
                product_quality.duplicates_removed +
                sales_quality.duplicates_removed
            )
            self.quality_report.total_invalid_records = (
                customer_quality.total_invalid_records +
                product_quality.total_invalid_records +
                sales_quality.total_invalid_records
            )
            self.quality_report.missing_values_percentage.update(
                customer_quality.missing_values_percentage
            )
            self.quality_report.missing_values_percentage.update(
                product_quality.missing_values_percentage
            )
            self.quality_report.missing_values_percentage.update(
                sales_quality.missing_values_percentage
            )
            
            self.logger.info("Data transformation phase completed")
            return customers_df, products_df, sales_df
        
        except Exception as e:
            self.logger.error(f"Data transformation failed: {str(e)}")
            raise
    
    def _load_data(self, customers_df, products_df, sales_df):
        """Load transformed data into database."""
        self.logger.info("Starting data loading phase...")
        
        try:
            loader = DataLoader(self.config.db_config)
            
            # Load customers
            self.logger.info("Loading customer data...")
            customer_rows = loader.load_customers(customers_df, self.config.incremental)
            self.quality_report.records_by_source['loaded_customers'] = customer_rows
            
            # Load products
            self.logger.info("Loading product data...")
            product_rows = loader.load_products(products_df, self.config.incremental)
            self.quality_report.records_by_source['loaded_products'] = product_rows
            
            # Load sales
            self.logger.info("Loading sales data...")
            sales_rows = loader.load_sales(sales_df, self.config.incremental)
            self.quality_report.records_by_source['loaded_sales'] = sales_rows
            
            loader.close()
            
            self.logger.info("Data loading phase completed")
        
        except Exception as e:
            self.logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def _generate_quality_report(self):
        """Generate data quality report."""
        self.logger.info("Generating quality report...")
        
        # Save quality report
        report_path = Path("data/output/quality_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.quality_report.to_dict(), f, indent=2, default=str)
        
        self.logger.info(f"Quality report saved to: {report_path}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        duration = (self.execution_end - self.execution_start).total_seconds()
        
        summary = {
            'status': 'success',
            'start_time': self.execution_start.isoformat(),
            'end_time': self.execution_end.isoformat(),
            'duration_seconds': duration,
            'total_records_processed': self.quality_report.total_records_processed,
            'total_invalid_records': self.quality_report.total_invalid_records,
            'duplicates_removed': self.quality_report.duplicates_removed,
            'records_by_source': self.quality_report.records_by_source,
            'missing_values_percentage': self.quality_report.missing_values_percentage
        }
        
        self.logger.info(f"Pipeline Summary:\n{json.dumps(summary, indent=2)}")
        
        # Save summary
        summary_path = Path("data/output/execution_summary.json")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        return summary
