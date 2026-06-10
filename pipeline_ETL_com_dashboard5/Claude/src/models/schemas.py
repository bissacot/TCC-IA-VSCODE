"""
Data models and schemas for the ETL pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class RecordStatus(Enum):
    """Status of a processed record."""
    VALID = "valid"
    INVALID = "invalid"
    DUPLICATE = "duplicate"
    MISSING_VALUES = "missing_values"


@dataclass
class Customer:
    """Customer data model."""
    customer_id: str
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


@dataclass
class Product:
    """Product data model."""
    product_id: str
    name: str
    category: str
    subcategory: Optional[str]
    price: float
    description: Optional[str]
    manufacturer: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': self.price,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


@dataclass
class Sale:
    """Sale data model."""
    sale_id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_value: float
    sale_date: datetime
    year: int
    month: int
    quarter: int
    state: Optional[str]
    payment_method: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_value': self.total_value,
            'sale_date': self.sale_date,
            'year': self.year,
            'month': self.month,
            'quarter': self.quarter,
            'state': self.state,
            'payment_method': self.payment_method,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


@dataclass
class DataQualityReport:
    """Data quality report model."""
    report_timestamp: datetime
    total_records_processed: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    duplicates_removed: int = 0
    missing_values_count: int = 0
    missing_values_percentage: float = 0.0
    data_type_errors: int = 0
    date_conversion_errors: int = 0
    processing_time_seconds: float = 0.0
    source_summary: Dict[str, Any] = field(default_factory=dict)
    transformation_summary: Dict[str, Any] = field(default_factory=dict)
    error_details: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_timestamp': self.report_timestamp,
            'total_records_processed': self.total_records_processed,
            'valid_records': self.valid_records,
            'invalid_records': self.invalid_records,
            'duplicates_removed': self.duplicates_removed,
            'missing_values_count': self.missing_values_count,
            'missing_values_percentage': self.missing_values_percentage,
            'data_type_errors': self.data_type_errors,
            'date_conversion_errors': self.date_conversion_errors,
            'processing_time_seconds': self.processing_time_seconds,
            'source_summary': self.source_summary,
            'transformation_summary': self.transformation_summary,
            'error_details': self.error_details,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), default=str, indent=2)
