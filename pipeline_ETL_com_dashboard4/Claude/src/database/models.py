"""
SQLAlchemy ORM models for the database.

Defines the data models for customers, products, and sales.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customer(Base):
    """Customer data model."""

    __tablename__ = "customers"

    customer_id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    email: str = Column(String(255), unique=True, nullable=False)
    phone: Optional[str] = Column(String(20))
    state: str = Column(String(2), nullable=False)
    city: Optional[str] = Column(String(100))
    zipcode: Optional[str] = Column(String(10))
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales: List["Sale"] = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_customers_email", "email"),
        Index("ix_customers_state", "state"),
        UniqueConstraint("email", name="uq_customers_email"),
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.customer_id}, name={self.name}, email={self.email})>"


class Product(Base):
    """Product data model."""

    __tablename__ = "products"

    product_id: int = Column(Integer, primary_key=True)
    name: str = Column(String(255), nullable=False)
    category: str = Column(String(100), nullable=False)
    price: float = Column(Float, nullable=False)
    description: Optional[str] = Column(String(1000))
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales: List["Sale"] = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_category", "category"),
        Index("ix_products_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.product_id}, name={self.name}, category={self.category})>"


class Sale(Base):
    """Sale transaction data model."""

    __tablename__ = "sales"

    sale_id: int = Column(Integer, primary_key=True)
    customer_id: int = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    product_id: int = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity: int = Column(Integer, nullable=False)
    unit_price: float = Column(Float, nullable=False)
    total_value: float = Column(Float, nullable=False)
    sale_date: datetime = Column(Date, nullable=False)
    year: int = Column(Integer, nullable=False)
    month: int = Column(Integer, nullable=False)
    quarter: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer: Customer = relationship("Customer", back_populates="sales")
    product: Product = relationship("Product", back_populates="sales")

    __table_args__ = (
        Index("ix_sales_customer_id", "customer_id"),
        Index("ix_sales_product_id", "product_id"),
        Index("ix_sales_date", "sale_date"),
        Index("ix_sales_year_month", "year", "month"),
    )

    def __repr__(self) -> str:
        return f"<Sale(id={self.sale_id}, customer_id={self.customer_id}, total={self.total_value})>"


class DataQualityMetrics(Base):
    """Data quality metrics tracking."""

    __tablename__ = "data_quality_metrics"

    metrics_id: int = Column(Integer, primary_key=True)
    etl_run_id: str = Column(String(50), nullable=False)
    processed_records: int = Column(Integer, nullable=False)
    invalid_records: int = Column(Integer, nullable=False)
    duplicates_removed: int = Column(Integer, nullable=False)
    missing_values_percentage: float = Column(Float, nullable=False)
    processing_time_seconds: float = Column(Float)
    status: str = Column(String(20), nullable=False, default="success")
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_quality_metrics_etl_run_id", "etl_run_id"),
        Index("ix_quality_metrics_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<DataQualityMetrics(etl_run={self.etl_run_id}, processed={self.processed_records})>"
