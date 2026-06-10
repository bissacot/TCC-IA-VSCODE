"""
Data Loading Modules
Load transformed data into PostgreSQL database
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import Customer, Product, Sale, DataQualityReport, IncrementalLoadLog
from src.database.repository import (
    CustomerRepository, ProductRepository, SaleRepository,
    DataQualityRepository, IncrementalLoadRepository
)
from src.logger import get_logger

logger = get_logger(__name__)


class BaseLoader(ABC):
    """Abstract base class for loaders"""
    
    def __init__(self, session: Session):
        self.session = session
    
    @abstractmethod
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load data to database"""
        pass
    
    def close(self) -> None:
        """Close session"""
        self.session.close()


class CustomerLoader(BaseLoader):
    """Load customer data to database"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = CustomerRepository(session)
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load customers to database"""
        logger.info(f"Loading {len(data)} customers to database")
        
        loaded_count = 0
        error_count = 0
        
        for record in data:
            try:
                customer = Customer(
                    customer_id=record["customer_id"],
                    name=record["name"],
                    email=record.get("email"),
                    phone=record.get("phone"),
                    state=record["state"],
                    city=record.get("city"),
                )
                
                self.repository.create(customer)
                loaded_count += 1
            
            except IntegrityError:
                # Customer already exists, update instead
                try:
                    existing = self.session.query(Customer).filter_by(
                        customer_id=record["customer_id"]
                    ).first()
                    
                    if existing:
                        existing.name = record["name"]
                        existing.email = record.get("email")
                        existing.phone = record.get("phone")
                        existing.state = record["state"]
                        existing.city = record.get("city")
                        existing.updated_at = datetime.utcnow()
                        
                        self.repository.update(existing)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Error updating customer {record.get('customer_id')}: {e}")
                    error_count += 1
            
            except Exception as e:
                logger.error(f"Error loading customer {record.get('customer_id')}: {e}")
                error_count += 1
        
        logger.info(f"Customer loading completed: {loaded_count} loaded, {error_count} errors")
        return loaded_count


class ProductLoader(BaseLoader):
    """Load product data to database"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = ProductRepository(session)
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load products to database"""
        logger.info(f"Loading {len(data)} products to database")
        
        loaded_count = 0
        error_count = 0
        
        for record in data:
            try:
                product = Product(
                    product_id=record["product_id"],
                    name=record["name"],
                    category=record["category"],
                    price=record["price"],
                    description=record.get("description"),
                    active=record.get("active", True),
                )
                
                self.repository.create(product)
                loaded_count += 1
            
            except IntegrityError:
                # Product already exists, update instead
                try:
                    existing = self.session.query(Product).filter_by(
                        product_id=record["product_id"]
                    ).first()
                    
                    if existing:
                        existing.name = record["name"]
                        existing.category = record["category"]
                        existing.price = record["price"]
                        existing.description = record.get("description")
                        existing.active = record.get("active", True)
                        existing.updated_at = datetime.utcnow()
                        
                        self.repository.update(existing)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Error updating product {record.get('product_id')}: {e}")
                    error_count += 1
            
            except Exception as e:
                logger.error(f"Error loading product {record.get('product_id')}: {e}")
                error_count += 1
        
        logger.info(f"Product loading completed: {loaded_count} loaded, {error_count} errors")
        return loaded_count


class SaleLoader(BaseLoader):
    """Load sales data to database"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = SaleRepository(session)
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load sales to database"""
        logger.info(f"Loading {len(data)} sales to database")
        
        loaded_count = 0
        error_count = 0
        
        for record in data:
            try:
                sale = Sale(
                    sale_id=record["sale_id"],
                    customer_id=record["customer_id"],
                    product_id=record["product_id"],
                    quantity=record["quantity"],
                    unit_price=record["unit_price"],
                    total_value=record["total_value"],
                    sale_date=record["sale_date"],
                    year=record["year"],
                    month=record["month"],
                    quarter=record["quarter"],
                )
                
                self.repository.create(sale)
                loaded_count += 1
            
            except IntegrityError as e:
                # Sale already exists, skip
                logger.debug(f"Sale already exists: {record.get('sale_id')}")
            
            except Exception as e:
                logger.error(f"Error loading sale {record.get('sale_id')}: {e}")
                error_count += 1
        
        logger.info(f"Sale loading completed: {loaded_count} loaded, {error_count} errors")
        return loaded_count


class DataQualityReportLoader(BaseLoader):
    """Load data quality reports to database"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = DataQualityRepository(session)
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load quality report"""
        if not data:
            return 0
        
        try:
            report_data = data[0]  # Expected to be single report
            
            report = DataQualityReport(
                total_records_processed=report_data.get("total_records_processed", 0),
                invalid_records=report_data.get("invalid_records", 0),
                duplicate_records_removed=report_data.get("duplicate_records_removed", 0),
                missing_values_percentage=report_data.get("missing_values_percentage", 0.0),
                sales_records=report_data.get("sales_records", 0),
                customer_records=report_data.get("customer_records", 0),
                product_records=report_data.get("product_records", 0),
                status=report_data.get("status", "COMPLETED"),
                error_message=report_data.get("error_message"),
                execution_time_seconds=report_data.get("execution_time_seconds", 0.0),
            )
            
            self.repository.create(report)
            logger.info("Quality report loaded successfully")
            return 1
        
        except Exception as e:
            logger.error(f"Error loading quality report: {e}")
            return 0


class ETLLoader:
    """Orchestrator for loading all data types"""
    
    def __init__(self, session: Session):
        self.session = session
        self.customer_loader = CustomerLoader(session)
        self.product_loader = ProductLoader(session)
        self.sale_loader = SaleLoader(session)
        self.quality_loader = DataQualityReportLoader(session)
    
    def load_all(
        self,
        sales: List[Dict[str, Any]],
        customers: List[Dict[str, Any]],
        products: List[Dict[str, Any]],
        quality_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """Load all data types"""
        logger.info("Starting comprehensive data load")
        
        results = {
            "customers_loaded": 0,
            "products_loaded": 0,
            "sales_loaded": 0,
            "quality_report_loaded": 0,
        }
        
        try:
            # Load customers first (dimension)
            results["customers_loaded"] = self.customer_loader.load(customers)
            
            # Load products (dimension)
            results["products_loaded"] = self.product_loader.load(products)
            
            # Load sales (fact table)
            results["sales_loaded"] = self.sale_loader.load(sales)
            
            # Load quality report
            if quality_report:
                results["quality_report_loaded"] = self.quality_loader.load([quality_report])
            
            logger.info(f"Data load completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Error during data load: {e}")
            raise
    
    def close(self) -> None:
        """Close all loaders"""
        self.customer_loader.close()
        self.product_loader.close()
        self.sale_loader.close()
        self.quality_loader.close()
