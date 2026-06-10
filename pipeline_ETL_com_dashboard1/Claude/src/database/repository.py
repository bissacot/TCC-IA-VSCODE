"""
Database Utilities and Repository Pattern
Data access layer with repository pattern for clean code principles
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.database.models import (
    Customer, Product, Sale, DataQualityReport,
    IncrementalLoadLog, DatabaseConnection
)
from src.logger import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model
    
    def create(self, obj: Any) -> Any:
        """Create and save object"""
        try:
            self.session.add(obj)
            self.session.commit()
            return obj
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def create_many(self, objects: List[Any]) -> List[Any]:
        """Create and save multiple objects"""
        try:
            self.session.add_all(objects)
            self.session.commit()
            return objects
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating multiple {self.model.__name__}: {e}")
            raise
    
    def get_by_id(self, obj_id: Any) -> Optional[Any]:
        """Get object by ID"""
        return self.session.query(self.model).filter_by(id=obj_id).first()
    
    def get_all(self) -> List[Any]:
        """Get all objects"""
        return self.session.query(self.model).all()
    
    def update(self, obj: Any) -> Any:
        """Update object"""
        try:
            self.session.merge(obj)
            self.session.commit()
            return obj
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    def delete(self, obj: Any) -> None:
        """Delete object"""
        try:
            self.session.delete(obj)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise
    
    def close(self) -> None:
        """Close session"""
        self.session.close()


class CustomerRepository(BaseRepository):
    """Customer data access layer"""
    
    def __init__(self, session: Session):
        super().__init__(session, Customer)
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return self.session.query(Customer).filter_by(email=email).first()
    
    def get_by_state(self, state: str) -> List[Customer]:
        """Get customers by state"""
        return self.session.query(Customer).filter_by(state=state).all()
    
    def count_unique(self) -> int:
        """Count unique customers"""
        return self.session.query(func.count(func.distinct(Customer.customer_id))).scalar()


class ProductRepository(BaseRepository):
    """Product data access layer"""
    
    def __init__(self, session: Session):
        super().__init__(session, Product)
    
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return self.session.query(Product).filter_by(category=category).all()
    
    def get_active_products(self) -> List[Product]:
        """Get active products"""
        return self.session.query(Product).filter_by(active=True).all()
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        result = self.session.query(func.distinct(Product.category)).all()
        return [row[0] for row in result]


class SaleRepository(BaseRepository):
    """Sales data access layer"""
    
    def __init__(self, session: Session):
        super().__init__(session, Sale)
    
    def get_by_customer(self, customer_id: str) -> List[Sale]:
        """Get sales by customer"""
        return self.session.query(Sale).filter_by(customer_id=customer_id).all()
    
    def get_by_product(self, product_id: str) -> List[Sale]:
        """Get sales by product"""
        return self.session.query(Sale).filter_by(product_id=product_id).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Sale]:
        """Get sales within date range"""
        return self.session.query(Sale).filter(
            and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
        ).all()
    
    def get_by_state(self, state: str) -> List[Sale]:
        """Get sales by customer state"""
        return self.session.query(Sale).join(Customer).filter(
            Customer.state == state
        ).all()
    
    def get_by_year_month(self, year: int, month: int) -> List[Sale]:
        """Get sales by year and month"""
        return self.session.query(Sale).filter(
            and_(Sale.year == year, Sale.month == month)
        ).all()
    
    def get_total_revenue(self) -> float:
        """Get total revenue"""
        result = self.session.query(func.sum(Sale.total_value)).scalar()
        return float(result) if result else 0.0
    
    def get_total_count(self) -> int:
        """Get total number of sales"""
        return self.session.query(func.count(Sale.sale_id)).scalar()
    
    def get_average_ticket(self) -> float:
        """Get average ticket value"""
        result = self.session.query(func.avg(Sale.total_value)).scalar()
        return float(result) if result else 0.0
    
    def get_revenue_by_month(self) -> List[Dict[str, Any]]:
        """Get revenue grouped by year and month"""
        result = self.session.query(
            Sale.year,
            Sale.month,
            func.sum(Sale.total_value).label("revenue"),
            func.count(Sale.sale_id).label("count")
        ).group_by(Sale.year, Sale.month).all()
        
        return [
            {
                "year": row[0],
                "month": row[1],
                "revenue": float(row[2]),
                "count": row[3]
            }
            for row in result
        ]
    
    def get_revenue_by_category(self) -> List[Dict[str, Any]]:
        """Get revenue by product category"""
        result = self.session.query(
            Product.category,
            func.sum(Sale.total_value).label("revenue"),
            func.count(Sale.sale_id).label("count")
        ).join(Product).group_by(Product.category).all()
        
        return [
            {
                "category": row[0],
                "revenue": float(row[1]),
                "count": row[2]
            }
            for row in result
        ]
    
    def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top products by sales quantity"""
        result = self.session.query(
            Product.product_id,
            Product.name,
            Product.category,
            func.sum(Sale.quantity).label("quantity"),
            func.sum(Sale.total_value).label("revenue")
        ).join(Product).group_by(
            Product.product_id, Product.name, Product.category
        ).order_by(
            func.sum(Sale.quantity).desc()
        ).limit(limit).all()
        
        return [
            {
                "product_id": row[0],
                "name": row[1],
                "category": row[2],
                "quantity": row[3],
                "revenue": float(row[4])
            }
            for row in result
        ]
    
    def get_revenue_by_state(self) -> List[Dict[str, Any]]:
        """Get revenue by state"""
        result = self.session.query(
            Customer.state,
            func.sum(Sale.total_value).label("revenue"),
            func.count(Sale.sale_id).label("count")
        ).join(Customer).group_by(Customer.state).all()
        
        return [
            {
                "state": row[0],
                "revenue": float(row[1]),
                "count": row[2]
            }
            for row in result
        ]


class DataQualityRepository(BaseRepository):
    """Data Quality Report repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, DataQualityReport)
    
    def get_latest(self) -> Optional[DataQualityReport]:
        """Get latest quality report"""
        return self.session.query(DataQualityReport).order_by(
            DataQualityReport.execution_date.desc()
        ).first()
    
    def get_by_status(self, status: str) -> List[DataQualityReport]:
        """Get reports by status"""
        return self.session.query(DataQualityReport).filter_by(status=status).all()


class IncrementalLoadRepository(BaseRepository):
    """Incremental Load tracking repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, IncrementalLoadLog)
    
    def get_by_source(self, source_name: str) -> Optional[IncrementalLoadLog]:
        """Get incremental load log for source"""
        return self.session.query(IncrementalLoadLog).filter_by(
            source_name=source_name
        ).first()
    
    def update_load_log(
        self,
        source_name: str,
        last_loaded_id: Optional[str],
        last_loaded_timestamp: Optional[datetime],
        records_loaded: int
    ) -> IncrementalLoadLog:
        """Update or create incremental load log"""
        log = self.get_by_source(source_name)
        
        if log:
            log.last_loaded_id = last_loaded_id
            log.last_loaded_timestamp = last_loaded_timestamp
            log.records_loaded = records_loaded
            log.last_modified_timestamp = datetime.utcnow()
        else:
            log = IncrementalLoadLog(
                source_name=source_name,
                last_loaded_id=last_loaded_id,
                last_loaded_timestamp=last_loaded_timestamp,
                records_loaded=records_loaded
            )
        
        return self.create(log) if not self.get_by_source(source_name) else self.update(log)


def get_session() -> Session:
    """Get database session"""
    return DatabaseConnection.get_session()
