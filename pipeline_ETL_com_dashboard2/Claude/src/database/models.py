"""
SQLAlchemy ORM models for database tables.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customer(Base):
    """Customer table model."""

    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    state = Column(String(2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_customers_email", "email"),
        Index("ix_customers_state", "state"),
        Index("ix_customers_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Customer(customer_id={self.customer_id}, name={self.name})>"


class Product(Base):
    """Product table model."""

    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_products_category", "category"),
        Index("ix_products_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Product(product_id={self.product_id}, name={self.name})>"


class Sale(Base):
    """Sale table model."""

    __tablename__ = "sales"

    sale_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    product = relationship("Product", back_populates="sales")

    # Indexes
    __table_args__ = (
        Index("ix_sales_customer_id", "customer_id"),
        Index("ix_sales_product_id", "product_id"),
        Index("ix_sales_sale_date", "sale_date"),
        Index("ix_sales_year_month", "year", "month"),
        Index("ix_sales_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Sale(sale_id={self.sale_id}, total_value={self.total_value})>"


class DataQualityMetric(Base):
    """Data quality metrics table model."""

    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extraction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_records_processed = Column(Integer, nullable=False)
    invalid_records = Column(Integer, nullable=False)
    missing_values_percentage = Column(Float, nullable=False)
    duplicates_removed = Column(Integer, nullable=False)
    transformation_time_seconds = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # success, partial, failed
    details = Column(String(2000))  # JSON string with detailed metrics
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_dqm_extraction_timestamp", "extraction_timestamp"),
        Index("ix_dqm_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<DataQualityMetric(id={self.id}, status={self.status})>"
