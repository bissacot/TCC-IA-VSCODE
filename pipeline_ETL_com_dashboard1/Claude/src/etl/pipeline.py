"""
Main ETL Pipeline Orchestrator
Complete ETL workflow: Extract, Transform, Load
"""

from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import traceback

from src.config import config
from src.logger import get_logger
from src.database.models import DatabaseConnection
from src.database.repository import IncrementalLoadRepository

from src.etl.extractors import ExtractorFactory
from src.etl.transformers import (
    SalesTransformer, CustomerTransformer, ProductTransformer,
    DataQualityMetrics
)
from src.etl.loaders import ETLLoader

logger = get_logger(__name__)


class ETLPipeline:
    """Complete ETL Pipeline"""
    
    def __init__(self, use_incremental: bool = config.INCREMENTAL_LOAD):
        self.use_incremental = use_incremental
        self.start_time = None
        self.end_time = None
        self.quality_metrics = {
            "sales": DataQualityMetrics(),
            "customers": DataQualityMetrics(),
            "products": DataQualityMetrics(),
        }
    
    def extract_sales(self) -> Tuple[list, DataQualityMetrics]:
        """Extract sales data from CSV"""
        logger.info("Extracting sales data from CSV")
        
        try:
            extractor = ExtractorFactory.create_csv_extractor(config.CSV_SALES_PATH)
            
            if self.use_incremental:
                session = DatabaseConnection.get_session()
                repo = IncrementalLoadRepository(session)
                log = repo.get_by_source("sales")
                
                if log:
                    logger.info(f"Loading sales incremental from ID: {log.last_loaded_id}")
                    data = extractor.extract_incremental(log.last_loaded_id)
                else:
                    data = extractor.extract()
                
                session.close()
            else:
                data = extractor.extract()
            
            logger.info(f"Extracted {len(data)} sales records")
            
            transformer = SalesTransformer()
            transformed, metrics = transformer.transform(data)
            
            return transformed, metrics
        
        except Exception as e:
            logger.error(f"Error extracting sales data: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def extract_customers(self) -> Tuple[list, DataQualityMetrics]:
        """Extract customer data from JSON"""
        logger.info("Extracting customer data from JSON")
        
        try:
            extractor = ExtractorFactory.create_json_extractor(config.JSON_CUSTOMERS_PATH)
            data = extractor.extract()
            
            logger.info(f"Extracted {len(data)} customer records")
            
            transformer = CustomerTransformer()
            transformed, metrics = transformer.transform(data)
            
            return transformed, metrics
        
        except Exception as e:
            logger.error(f"Error extracting customer data: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def extract_products(self) -> Tuple[list, DataQualityMetrics]:
        """Extract product data from API"""
        logger.info("Extracting product data from API")
        
        try:
            extractor = ExtractorFactory.create_api_extractor(config.PRODUCT_API_URL)
            data = extractor.extract()
            extractor.close()
            
            logger.info(f"Extracted {len(data)} product records")
            
            transformer = ProductTransformer()
            transformed, metrics = transformer.transform(data)
            
            return transformed, metrics
        
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def generate_quality_report(
        self,
        sales_count: int,
        customers_count: int,
        products_count: int,
        execution_time: float
    ) -> Dict[str, Any]:
        """Generate data quality report"""
        logger.info("Generating data quality report")
        
        total_records = (
            self.quality_metrics["sales"].total_records +
            self.quality_metrics["customers"].total_records +
            self.quality_metrics["products"].total_records
        )
        
        invalid_records = (
            self.quality_metrics["sales"].invalid_records +
            self.quality_metrics["customers"].invalid_records +
            self.quality_metrics["products"].invalid_records
        )
        
        duplicates_removed = (
            self.quality_metrics["sales"].duplicates_removed +
            self.quality_metrics["customers"].duplicates_removed +
            self.quality_metrics["products"].duplicates_removed
        )
        
        avg_missing_percentage = (
            (self.quality_metrics["sales"].missing_value_percentage +
             self.quality_metrics["customers"].missing_value_percentage +
             self.quality_metrics["products"].missing_value_percentage) / 3
        )
        
        report = {
            "total_records_processed": total_records,
            "invalid_records": invalid_records,
            "duplicate_records_removed": duplicates_removed,
            "missing_values_percentage": avg_missing_percentage,
            "sales_records": sales_count,
            "customer_records": customers_count,
            "product_records": products_count,
            "status": "SUCCESS" if invalid_records == 0 else "PARTIAL",
            "execution_time_seconds": execution_time,
        }
        
        logger.info(f"Quality Report:\n{report}")
        return report
    
    def run(self) -> Dict[str, Any]:
        """Execute complete ETL pipeline"""
        logger.info("=" * 80)
        logger.info("Starting ETL Pipeline Execution")
        logger.info(f"Incremental Mode: {self.use_incremental}")
        logger.info("=" * 80)
        
        self.start_time = datetime.utcnow()
        
        try:
            # Step 1: Extract
            logger.info("\n[STEP 1] Data Extraction")
            logger.info("-" * 80)
            
            sales_data, self.quality_metrics["sales"] = self.extract_sales()
            customers_data, self.quality_metrics["customers"] = self.extract_customers()
            products_data, self.quality_metrics["products"] = self.extract_products()
            
            logger.info(f"Extracted - Sales: {len(sales_data)}, Customers: {len(customers_data)}, Products: {len(products_data)}")
            
            # Step 2: Load
            logger.info("\n[STEP 2] Data Loading")
            logger.info("-" * 80)
            
            session = DatabaseConnection.get_session()
            loader = ETLLoader(session)
            
            # Generate quality report
            self.end_time = datetime.utcnow()
            execution_time = (self.end_time - self.start_time).total_seconds()
            
            quality_report = self.generate_quality_report(
                len(sales_data),
                len(customers_data),
                len(products_data),
                execution_time
            )
            
            # Load all data
            load_results = loader.load_all(
                sales_data,
                customers_data,
                products_data,
                quality_report
            )
            
            loader.close()
            session.close()
            
            # Final Report
            logger.info("\n[FINAL REPORT]")
            logger.info("=" * 80)
            logger.info(f"Execution Time: {execution_time:.2f} seconds")
            logger.info(f"Load Results: {load_results}")
            logger.info(f"Quality Report: {quality_report}")
            logger.info("=" * 80)
            logger.info("ETL Pipeline Completed Successfully!")
            logger.info("=" * 80)
            
            return {
                "success": True,
                "execution_time_seconds": execution_time,
                "load_results": load_results,
                "quality_report": quality_report,
            }
        
        except Exception as e:
            logger.error("=" * 80)
            logger.error("ETL Pipeline Failed!")
            logger.error(f"Error: {e}")
            logger.error(traceback.format_exc())
            logger.error("=" * 80)
            
            self.end_time = datetime.utcnow()
            execution_time = (self.end_time - self.start_time).total_seconds()
            
            return {
                "success": False,
                "error": str(e),
                "execution_time_seconds": execution_time,
                "traceback": traceback.format_exc(),
            }


def run_etl_pipeline(use_incremental: bool = config.INCREMENTAL_LOAD) -> Dict[str, Any]:
    """Run ETL pipeline and return results"""
    
    # Ensure database tables exist
    try:
        DatabaseConnection.create_tables()
    except Exception as e:
        logger.info(f"Tables may already exist: {e}")
    
    pipeline = ETLPipeline(use_incremental)
    return pipeline.run()


if __name__ == "__main__":
    result = run_etl_pipeline()
