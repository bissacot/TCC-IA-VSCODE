"""Data models and schemas."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


@dataclass
class Customer:
    """Customer data model."""
    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    registration_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'registration_date': self.registration_date
        }


@dataclass
class Product:
    """Product data model."""
    product_id: str
    name: str
    category: str
    price: Decimal
    description: Optional[str] = None
    sku: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'price': float(self.price),
            'description': self.description,
            'sku': self.sku
        }


@dataclass
class Sale:
    """Sale data model."""
    sale_id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    total_value: Decimal
    sale_date: datetime
    sale_month: int = field(init=False)
    sale_year: int = field(init=False)
    sale_quarter: int = field(init=False)
    
    def __post_init__(self):
        """Calculate derived fields."""
        self.sale_month = self.sale_date.month
        self.sale_year = self.sale_date.year
        self.sale_quarter = (self.sale_date.month - 1) // 3 + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_value': float(self.total_value),
            'sale_date': self.sale_date,
            'sale_month': self.sale_month,
            'sale_year': self.sale_year,
            'sale_quarter': self.sale_quarter
        }


@dataclass
class DataQualityReport:
    """Data quality report."""
    total_records_processed: int = 0
    total_invalid_records: int = 0
    duplicates_removed: int = 0
    missing_values_percentage: Dict[str, float] = field(default_factory=dict)
    records_by_source: Dict[str, int] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    processing_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_records_processed': self.total_records_processed,
            'total_invalid_records': self.total_invalid_records,
            'duplicates_removed': self.duplicates_removed,
            'missing_values_percentage': self.missing_values_percentage,
            'records_by_source': self.records_by_source,
            'validation_errors': self.validation_errors,
            'processing_timestamp': self.processing_timestamp.isoformat()
        }
