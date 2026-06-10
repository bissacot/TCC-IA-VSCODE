"""
Database Models Definition
SQLAlchemy ORM models for sales, customers, products, and quality metrics
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime,
    Date, Boolean, ForeignKey, Numeric, Text, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config import config
from src.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class Customer(Base):
    """Customer dimension table"""
    
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    state = Column(String(50), nullable=False)
    city = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = relationship("Sale", back_populates="customer")
    
    __table_args__ = (
        Index("idx_customer_email", "email"),
        Index("idx_customer_state", "state"),
    )


class Product(Base):
    """Product dimension table"""
    
    __tablename__ = "products"
    
    product_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = relationship("Sale", back_populates="product")
    
    __table_args__ = (
        Index("idx_product_category", "category"),
        Index("idx_product_active", "active"),
    )


class Sale(Base):
    """Sales fact table"""
    
    __tablename__ = "sales"
    
    sale_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_value = Column(Numeric(12, 2), nullable=False)
    sale_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="sales")
    product = relationship("Product", back_populates="sales")
    
    __table_args__ = (
        Index("idx_sale_customer_id", "customer_id"),
        Index("idx_sale_product_id", "product_id"),
        Index("idx_sale_date", "sale_date"),
        Index("idx_sale_year_month", "year", "month"),
        UniqueConstraint("sale_id", name="uq_sale_id"),
    )


class DataQualityReport(Base):
    """Data Quality Report tracking"""
    
    __tablename__ = "data_quality_report"
    
    id = Column(Integer, primary_key=True)
    execution_date = Column(DateTime, default=datetime.utcnow)
    total_records_processed = Column(Integer, nullable=False)
    invalid_records = Column(Integer, nullable=False)
    duplicate_records_removed = Column(Integer, nullable=False)
    missing_values_percentage = Column(Float, nullable=False)
    sales_records = Column(Integer, nullable=False)
    customer_records = Column(Integer, nullable=False)
    product_records = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # SUCCESS, PARTIAL, FAILED
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=False)
    
    __table_args__ = (
        Index("idx_quality_execution_date", "execution_date"),
        Index("idx_quality_status", "status"),
    )


class IncrementalLoadLog(Base):
    """Track incremental loads for delta processing"""
    
    __tablename__ = "incremental_load_log"
    
    id = Column(Integer, primary_key=True)
    source_name = Column(String(50), nullable=False)  # sales, customers, products
    last_loaded_id = Column(String(255), nullable=True)
    last_loaded_timestamp = Column(DateTime, nullable=True)
    last_modified_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    records_loaded = Column(Integer, nullable=False)
    load_timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("source_name", name="uq_incremental_source"),
        Index("idx_incremental_source", "source_name"),
    )


class DatabaseConnection:
    """Database connection management"""
    
    _engine = None
    _session_factory = None
    
    @classmethod
    def get_engine(cls):
        """Get or create database engine"""
        if cls._engine is None:
            try:
                cls._engine = create_engine(
                    config.get_database_url(),
                    poolclass=NullPool,
                    echo=config.DEBUG,
                    connect_args={"connect_timeout": 10}
                )
                logger.info(f"Database engine created: {config.DB_HOST}:{config.DB_PORT}")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise
        
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """Get or create session factory"""
        if cls._session_factory is None:
            engine = cls.get_engine()
            cls._session_factory = sessionmaker(bind=engine)
        
        return cls._session_factory
    
    @classmethod
    def get_session(cls) -> Session:
        """Get new database session"""
        factory = cls.get_session_factory()
        return factory()
    
    @classmethod
    def create_tables(cls) -> None:
        """Create all tables"""
        engine = cls.get_engine()
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    
    @classmethod
    def drop_tables(cls) -> None:
        """Drop all tables (use with caution)"""
        engine = cls.get_engine()
        Base.metadata.drop_all(engine)
        logger.warning("Database tables dropped")
    
    @classmethod
    def close(cls) -> None:
        """Close all connections"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            logger.info("Database connections closed")
