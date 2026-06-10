"""
Data models using Pydantic for type validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class Customer(BaseModel):
    """Customer data model."""

    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "customer_id": "CUST001",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+55 11 98765-4321",
                "state": "SP",
                "created_at": "2024-01-01T10:00:00",
            }
        }


class Product(BaseModel):
    """Product data model."""

    product_id: str
    name: str
    category: str
    price: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("price")
    def validate_price(cls, v: float) -> float:
        """Validate price is positive."""
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "product_id": "PROD001",
                "name": "Laptop",
                "category": "Electronics",
                "price": 1999.99,
                "description": "High-performance laptop",
                "created_at": "2024-01-01T10:00:00",
            }
        }


class Sale(BaseModel):
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("quantity")
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is positive."""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @validator("total_value")
    def validate_total_value(cls, v: float) -> float:
        """Validate total_value is positive."""
        if v < 0:
            raise ValueError("Total value cannot be negative")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "sale_id": "SALE001",
                "customer_id": "CUST001",
                "product_id": "PROD001",
                "quantity": 2,
                "unit_price": 1999.99,
                "total_value": 3999.98,
                "sale_date": "2024-01-15T10:00:00",
                "year": 2024,
                "month": 1,
                "quarter": 1,
                "created_at": "2024-01-15T10:00:00",
            }
        }


class DataQualityReport(BaseModel):
    """Data quality report model."""

    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_records_processed: int
    invalid_records: int
    missing_values_percentage: float
    duplicates_removed: int
    sources_processed: dict
    transformation_time_seconds: float
    status: str  # success, partial, failed

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "extraction_timestamp": "2024-01-15T10:00:00",
                "total_records_processed": 10000,
                "invalid_records": 50,
                "missing_values_percentage": 2.5,
                "duplicates_removed": 100,
                "sources_processed": {
                    "csv_sales": 5000,
                    "json_customers": 3000,
                    "api_products": 2000,
                },
                "transformation_time_seconds": 125.5,
                "status": "success",
            }
        }
