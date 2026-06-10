"""
ETL Pipeline orchestration.
"""

import time
from typing import Dict, Any, List
from datetime import datetime
from src.etl.extractor import DataExtractor
from src.etl.transformer import DataTransformer
from src.database.loader import DataLoader
from src.database.connection import DatabaseConnection
from src.utils.logger import get_logger
from src.utils.config import Config


logger = get_logger()


class ETLPipeline:
    """Main ETL pipeline orchestration."""

    def __init__(self):
        self.logger = get_logger()
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.db = DatabaseConnection()
        self.start_time = None
        self.end_time = None

    def initialize_database(self) -> None:
        """Initialize database schema."""
        self.logger.info("Initializing database schema...")
        
        # Read SQL schema file
        try:
            from pathlib import Path
            sql_file = Path(__file__).parent.parent.parent / 'sql' / 'schema.sql'
            if sql_file.exists():
                with open(sql_file, 'r') as f:
                    schema_sql = f.read()
                self.db.connect()
                self.db.create_schema(schema_sql)
            else:
                self.logger.warning(f"SQL schema file not found: {sql_file}")
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
        finally:
            self.db.disconnect()

    def run(self) -> Dict[str, Any]:
        """Execute complete ETL pipeline."""
        self.start_time = datetime.now()
        start_timestamp = time.time()

        self.logger.info("=" * 80)
        self.logger.info("Starting ETL Pipeline Execution")
        self.logger.info("=" * 80)

        try:
            # Step 1: Extract
            self.logger.info("\n--- EXTRACTION PHASE ---")
            extracted_data = self.extractor.extract_all()

            # Step 2: Transform
            self.logger.info("\n--- TRANSFORMATION PHASE ---")
            
            # Transform customers
            customers, customer_errors = self.transformer.transform_customers(
                extracted_data['customers']
            )
            customers_dict = {c.customer_id: c for c in customers}

            # Transform products
            products, product_errors = self.transformer.transform_products(
                extracted_data['products']
            )
            products_dict = {p.product_id: p for p in products}

            # Transform sales
            sales, sales_errors = self.transformer.transform_sales(
                extracted_data['sales'],
                customers_dict,
                products_dict
            )

            # Step 3: Load
            self.logger.info("\n--- LOADING PHASE ---")
            
            # Initialize database
            self.initialize_database()
            
            # Load data
            customers_loaded = self.loader.load_customers(customers)
            products_loaded = self.loader.load_products(products)
            sales_loaded = self.loader.load_sales(sales)

            # Step 4: Report
            self.logger.info("\n--- DATA QUALITY REPORT ---")
            
            end_timestamp = time.time()
            processing_time = end_timestamp - start_timestamp
            
            quality_report = self.transformer.quality_report.to_dict()
            quality_report['processing_time_seconds'] = processing_time
            quality_report['total_records_processed'] = (
                len(extracted_data['customers']) +
                len(extracted_data['products']) +
                len(extracted_data['sales'])
            )

            self.loader.load_quality_report(quality_report)

            result = {
                'status': 'SUCCESS',
                'start_time': self.start_time,
                'end_time': datetime.now(),
                'processing_time_seconds': processing_time,
                'extraction': {
                    'customers': len(extracted_data['customers']),
                    'products': len(extracted_data['products']),
                    'sales': len(extracted_data['sales']),
                    'errors': len(extracted_data['errors']),
                },
                'transformation': {
                    'customers_valid': len(customers),
                    'customers_invalid': len(customer_errors),
                    'products_valid': len(products),
                    'products_invalid': len(product_errors),
                    'sales_valid': len(sales),
                    'sales_invalid': len(sales_errors),
                },
                'loading': {
                    'customers_loaded': customers_loaded,
                    'products_loaded': products_loaded,
                    'sales_loaded': sales_loaded,
                },
                'quality_report': quality_report,
            }

            self._print_summary(result)
            return result

        except Exception as e:
            self.logger.error(f"ETL Pipeline failed: {str(e)}")
            result = {
                'status': 'FAILED',
                'error': str(e),
                'start_time': self.start_time,
                'end_time': datetime.now(),
            }
            self._print_summary(result)
            raise

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Print ETL execution summary."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("ETL EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Status: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            self.logger.info(f"\nProcessing Time: {result['processing_time_seconds']:.2f}s")
            
            self.logger.info("\nExtraction:")
            for key, value in result['extraction'].items():
                self.logger.info(f"  {key}: {value}")
            
            self.logger.info("\nTransformation:")
            for key, value in result['transformation'].items():
                self.logger.info(f"  {key}: {value}")
            
            self.logger.info("\nLoading:")
            for key, value in result['loading'].items():
                self.logger.info(f"  {key}: {value}")
            
            report = result.get('quality_report', {})
            self.logger.info("\nData Quality:")
            self.logger.info(f"  Total Records Processed: {report.get('total_records_processed', 0)}")
            self.logger.info(f"  Valid Records: {report.get('valid_records', 0)}")
            self.logger.info(f"  Invalid Records: {report.get('invalid_records', 0)}")
            self.logger.info(f"  Duplicates Removed: {report.get('duplicates_removed', 0)}")
            self.logger.info(f"  Missing Values: {report.get('missing_values_count', 0)}")
        else:
            self.logger.error(f"Error: {result.get('error')}")
        
        self.logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    Config.ensure_directories()
    pipeline = ETLPipeline()
    result = pipeline.run()
