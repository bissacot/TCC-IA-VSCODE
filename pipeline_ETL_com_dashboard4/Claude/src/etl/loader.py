"""
Data loading module for the ETL pipeline.

Handles loading transformed data into PostgreSQL database.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.utils import LoggerConfig, LoadingException
from src.database import (
    DatabaseConnection,
    Customer,
    Product,
    Sale,
    DataQualityMetrics,
    Base,
)
from config.settings import DB_URL
from src.etl.transformer import DataQualityReport


logger = LoggerConfig.get_logger(__name__)


class DatabaseInitializer:
    """Initializes database schema and tables."""

    @staticmethod
    def create_all_tables() -> None:
        """
        Create all database tables.

        Raises:
            LoadingException: If table creation fails
        """
        try:
            logger.info("Creating database tables")

            engine = create_engine(DB_URL)
            Base.metadata.create_all(engine)

            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise LoadingException(f"Table creation failed: {e}")

    @staticmethod
    def drop_all_tables() -> None:
        """
        Drop all database tables.

        WARNING: This will delete all data!

        Raises:
            LoadingException: If table drop fails
        """
        try:
            logger.warning("Dropping all database tables")

            engine = create_engine(DB_URL)
            Base.metadata.drop_all(engine)

            logger.info("Database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise LoadingException(f"Table drop failed: {e}")


class DataLoader:
    """Loads transformed data into database."""

    def __init__(self) -> None:
        """Initialize data loader."""
        self.engine = create_engine(DB_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.etl_run_id = str(uuid.uuid4())
        self.records_loaded = 0
        self.records_failed = 0

    def load_customers(self, customers_data: List[Dict[str, Any]]) -> int:
        """
        Load customer data into database.

        Args:
            customers_data: List of customer records

        Returns:
            Number of records loaded

        Raises:
            LoadingException: If loading fails
        """
        logger.info(f"Loading {len(customers_data)} customer records")

        session = self.SessionLocal()
        records_loaded = 0

        try:
            for customer_data in customers_data:
                try:
                    customer = Customer(
                        name=customer_data["name"],
                        email=customer_data["email"],
                        phone=customer_data.get("phone"),
                        state=customer_data["state"],
                        city=customer_data.get("city"),
                        zipcode=customer_data.get("zipcode"),
                    )

                    session.add(customer)
                    records_loaded += 1

                except IntegrityError:
                    session.rollback()
                    logger.warning(f"Duplicate customer email: {customer_data['email']}")
                    self.records_failed += 1
                    continue
                except Exception as e:
                    session.rollback()
                    logger.warning(f"Error loading customer {customer_data}: {e}")
                    self.records_failed += 1
                    continue

            session.commit()
            self.records_loaded += records_loaded
            logger.info(f"Successfully loaded {records_loaded} customer records")
            return records_loaded

        except Exception as e:
            session.rollback()
            logger.error(f"Customer loading failed: {e}")
            raise LoadingException(f"Customer loading failed: {e}")
        finally:
            session.close()

    def load_products(self, products_data: List[Dict[str, Any]]) -> int:
        """
        Load product data into database.

        Args:
            products_data: List of product records

        Returns:
            Number of records loaded

        Raises:
            LoadingException: If loading fails
        """
        logger.info(f"Loading {len(products_data)} product records")

        session = self.SessionLocal()
        records_loaded = 0

        try:
            for product_data in products_data:
                try:
                    product = Product(
                        name=product_data["name"],
                        category=product_data["category"],
                        price=product_data["price"],
                        description=product_data.get("description"),
                    )

                    session.add(product)
                    records_loaded += 1

                except Exception as e:
                    session.rollback()
                    logger.warning(f"Error loading product {product_data}: {e}")
                    self.records_failed += 1
                    continue

            session.commit()
            self.records_loaded += records_loaded
            logger.info(f"Successfully loaded {records_loaded} product records")
            return records_loaded

        except Exception as e:
            session.rollback()
            logger.error(f"Product loading failed: {e}")
            raise LoadingException(f"Product loading failed: {e}")
        finally:
            session.close()

    def load_sales(self, sales_data: List[Dict[str, Any]]) -> int:
        """
        Load sales data into database.

        Args:
            sales_data: List of sales records

        Returns:
            Number of records loaded

        Raises:
            LoadingException: If loading fails
        """
        logger.info(f"Loading {len(sales_data)} sales records")

        session = self.SessionLocal()
        records_loaded = 0

        try:
            for sale_data in sales_data:
                try:
                    sale = Sale(
                        customer_id=sale_data["customer_id"],
                        product_id=sale_data["product_id"],
                        quantity=sale_data["quantity"],
                        unit_price=sale_data["unit_price"],
                        total_value=sale_data["total_value"],
                        sale_date=sale_data["sale_date"],
                        year=sale_data["year"],
                        month=sale_data["month"],
                        quarter=sale_data["quarter"],
                    )

                    session.add(sale)
                    records_loaded += 1

                except IntegrityError:
                    session.rollback()
                    logger.warning(f"Foreign key constraint error for sale: {sale_data}")
                    self.records_failed += 1
                    continue
                except Exception as e:
                    session.rollback()
                    logger.warning(f"Error loading sale {sale_data}: {e}")
                    self.records_failed += 1
                    continue

            session.commit()
            self.records_loaded += records_loaded
            logger.info(f"Successfully loaded {records_loaded} sales records")
            return records_loaded

        except Exception as e:
            session.rollback()
            logger.error(f"Sales loading failed: {e}")
            raise LoadingException(f"Sales loading failed: {e}")
        finally:
            session.close()

    def save_quality_metrics(
        self,
        quality_report: DataQualityReport,
        status: str = "success",
    ) -> None:
        """
        Save data quality metrics to database.

        Args:
            quality_report: Quality report from transformation
            status: ETL execution status
        """
        session = self.SessionLocal()

        try:
            metrics = DataQualityMetrics(
                etl_run_id=self.etl_run_id,
                processed_records=quality_report.processed_records,
                invalid_records=quality_report.invalid_records,
                duplicates_removed=quality_report.duplicates_removed,
                missing_values_percentage=quality_report.missing_values_percentage,
                processing_time_seconds=quality_report.processing_time,
                status=status,
            )

            session.add(metrics)
            session.commit()

            logger.info(f"Quality metrics saved for ETL run {self.etl_run_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save quality metrics: {e}")
        finally:
            session.close()

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of loading operation.

        Returns:
            Dictionary with loading statistics
        """
        return {
            "etl_run_id": self.etl_run_id,
            "records_loaded": self.records_loaded,
            "records_failed": self.records_failed,
            "timestamp": datetime.now().isoformat(),
        }
