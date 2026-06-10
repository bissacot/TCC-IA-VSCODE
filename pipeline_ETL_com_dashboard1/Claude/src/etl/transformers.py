"""
Data Transformation Modules
Transform, validate, and enrich extracted data
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from datetime import datetime, date
import re

import pandas as pd
import numpy as np

from src.logger import get_logger
from src.config import config

logger = get_logger(__name__)


class DataQualityMetrics:
    """Track data quality metrics"""
    
    def __init__(self):
        self.total_records = 0
        self.invalid_records = 0
        self.duplicates_removed = 0
        self.missing_values_count = 0
        self.total_values = 0
    
    @property
    def missing_value_percentage(self) -> float:
        """Calculate missing value percentage"""
        if self.total_values == 0:
            return 0.0
        return (self.missing_values_count / self.total_values) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_records": self.total_records,
            "invalid_records": self.invalid_records,
            "duplicates_removed": self.duplicates_removed,
            "missing_value_percentage": self.missing_value_percentage,
        }


class BaseTransformer(ABC):
    """Abstract base class for transformers"""
    
    def __init__(self):
        self.metrics = DataQualityMetrics()
    
    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityMetrics]:
        """Transform data"""
        pass


class SalesTransformer(BaseTransformer):
    """Transform sales data"""
    
    def __init__(self):
        super().__init__()
        self.required_fields = ["sale_id", "customer_id", "product_id", "quantity", "unit_price", "sale_date"]
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate individual sales record"""
        # Check required fields
        for field in self.required_fields:
            if field not in record or record[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate numeric fields
        try:
            quantity = int(record["quantity"])
            unit_price = float(record["unit_price"])
            
            if quantity <= 0:
                return False, "Quantity must be positive"
            if unit_price <= 0:
                return False, "Unit price must be positive"
        
        except (ValueError, TypeError) as e:
            return False, f"Invalid numeric field: {e}"
        
        return True, None
    
    def standardize_date(self, date_str: str) -> date:
        """Convert date string to ISO format"""
        if isinstance(date_str, date):
            return date_str
        
        # Try common date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def calculate_derived_metrics(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics"""
        quantity = int(record["quantity"])
        unit_price = float(record["unit_price"])
        total_value = quantity * unit_price
        
        sale_date = self.standardize_date(record["sale_date"])
        
        return {
            "total_value": total_value,
            "sale_date": sale_date,
            "year": sale_date.year,
            "month": sale_date.month,
            "quarter": (sale_date.month - 1) // 3 + 1,
        }
    
    def transform(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityMetrics]:
        """Transform sales data"""
        logger.info(f"Starting sales data transformation for {len(data)} records")
        
        transformed_data = []
        seen_ids = set()
        
        self.metrics.total_records = len(data)
        
        for record in data:
            # Validate record
            is_valid, error_msg = self.validate_record(record)
            if not is_valid:
                logger.warning(f"Invalid sales record: {error_msg}")
                self.metrics.invalid_records += 1
                continue
            
            # Check for duplicates
            sale_id = str(record["sale_id"])
            if sale_id in seen_ids:
                logger.debug(f"Duplicate sales record found: {sale_id}")
                self.metrics.duplicates_removed += 1
                continue
            
            seen_ids.add(sale_id)
            
            # Calculate derived metrics
            derived = self.calculate_derived_metrics(record)
            
            # Build transformed record
            transformed_record = {
                "sale_id": sale_id,
                "customer_id": str(record["customer_id"]),
                "product_id": str(record["product_id"]),
                "quantity": int(record["quantity"]),
                "unit_price": float(record["unit_price"]),
                **derived
            }
            
            transformed_data.append(transformed_record)
            
            # Track missing values
            self.metrics.total_values += len(transformed_record)
        
        logger.info(
            f"Sales transformation completed: "
            f"{len(transformed_data)} valid records, "
            f"{self.metrics.invalid_records} invalid, "
            f"{self.metrics.duplicates_removed} duplicates"
        )
        
        return transformed_data, self.metrics


class CustomerTransformer(BaseTransformer):
    """Transform customer data"""
    
    def __init__(self):
        super().__init__()
        self.required_fields = ["customer_id", "name", "state"]
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate individual customer record"""
        for field in self.required_fields:
            if field not in record or record[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate email format if present
        if "email" in record and record["email"]:
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, str(record["email"])):
                return False, f"Invalid email format: {record['email']}"
        
        return True, None
    
    def clean_name(self, name: str) -> str:
        """Clean and standardize name"""
        return name.strip().title() if name else ""
    
    def clean_state(self, state: str) -> str:
        """Clean and standardize state code"""
        return state.strip().upper() if state else ""
    
    def transform(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityMetrics]:
        """Transform customer data"""
        logger.info(f"Starting customer data transformation for {len(data)} records")
        
        transformed_data = []
        seen_ids = set()
        
        self.metrics.total_records = len(data)
        
        for record in data:
            # Validate record
            is_valid, error_msg = self.validate_record(record)
            if not is_valid:
                logger.warning(f"Invalid customer record: {error_msg}")
                self.metrics.invalid_records += 1
                continue
            
            # Check for duplicates
            customer_id = str(record["customer_id"])
            if customer_id in seen_ids:
                logger.debug(f"Duplicate customer record found: {customer_id}")
                self.metrics.duplicates_removed += 1
                continue
            
            seen_ids.add(customer_id)
            
            # Build transformed record
            transformed_record = {
                "customer_id": customer_id,
                "name": self.clean_name(record.get("name", "")),
                "email": record.get("email", "").lower() if record.get("email") else None,
                "phone": record.get("phone", ""),
                "state": self.clean_state(record.get("state", "")),
                "city": record.get("city", ""),
            }
            
            transformed_data.append(transformed_record)
            self.metrics.total_values += len(transformed_record)
        
        logger.info(
            f"Customer transformation completed: "
            f"{len(transformed_data)} valid records, "
            f"{self.metrics.invalid_records} invalid, "
            f"{self.metrics.duplicates_removed} duplicates"
        )
        
        return transformed_data, self.metrics


class ProductTransformer(BaseTransformer):
    """Transform product data"""
    
    def __init__(self):
        super().__init__()
        self.required_fields = ["id", "name", "price"]
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate individual product record"""
        for field in self.required_fields:
            if field not in record or record[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate price
        try:
            price = float(record["price"])
            if price <= 0:
                return False, "Price must be positive"
        except (ValueError, TypeError):
            return False, "Invalid price format"
        
        return True, None
    
    def transform(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityMetrics]:
        """Transform product data"""
        logger.info(f"Starting product data transformation for {len(data)} records")
        
        transformed_data = []
        seen_ids = set()
        
        self.metrics.total_records = len(data)
        
        for record in data:
            # Validate record
            is_valid, error_msg = self.validate_record(record)
            if not is_valid:
                logger.warning(f"Invalid product record: {error_msg}")
                self.metrics.invalid_records += 1
                continue
            
            # Check for duplicates
            product_id = str(record.get("id", ""))
            if product_id in seen_ids:
                logger.debug(f"Duplicate product record found: {product_id}")
                self.metrics.duplicates_removed += 1
                continue
            
            seen_ids.add(product_id)
            
            # Build transformed record
            transformed_record = {
                "product_id": product_id,
                "name": record.get("name", "").strip(),
                "category": record.get("category", "Uncategorized").strip(),
                "price": float(record["price"]),
                "description": record.get("description", ""),
                "active": record.get("active", True),
            }
            
            transformed_data.append(transformed_record)
            self.metrics.total_values += len(transformed_record)
        
        logger.info(
            f"Product transformation completed: "
            f"{len(transformed_data)} valid records, "
            f"{self.metrics.invalid_records} invalid, "
            f"{self.metrics.duplicates_removed} duplicates"
        )
        
        return transformed_data, self.metrics
