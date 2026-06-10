"""
Data loading into PostgreSQL database.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import Customer, Product, Sale, DataQualityMetric
from src.utils.logging_config import setup_logging
from src.utils.exceptions import LoadException
from src.utils.models import DataQualityReport

logger = setup_logging(__name__)


class DataLoader:
    """Load transformed data into PostgreSQL."""

    def __init__(self, session: Optional[Session] = None) -> None:
        """
        Initialize data loader.

        Args:
            session: Optional SQLAlchemy session
        """
        self.session = session
        logger.info("Initialized data loader")

    def _get_session(self) -> Session:
        """Get database session."""
        if self.session is None:
            return DatabaseManager.get_session()
        return self.session

    def load_customers(self, df: pd.DataFrame, incremental: bool = False) -> int:
        """
        Load customer data.

        Args:
            df: Customer DataFrame
            incremental: If True, update existing records

        Returns:
            Number of records loaded

        Raises:
            LoadException: If loading fails
        """
        try:
            session = self._get_session()
            logger.info(f"Loading {len(df)} customer records")

            loaded_count = 0

            for _, row in df.iterrows():
                try:
                    # Check if customer exists
                    existing = session.query(Customer).filter(
                        Customer.customer_id == row.get("customer_id")
                    ).first()

                    if existing and not incremental:
                        continue

                    customer_data = {
                        "customer_id": str(row.get("customer_id", "")),
                        "name": str(row.get("name", "")),
                        "email": str(row.get("email", "")),
                        "phone": str(row.get("phone", "")) if row.get("phone") else None,
                        "state": str(row.get("state", "")),
                    }

                    if existing and incremental:
                        for key, value in customer_data.items():
                            setattr(existing, key, value)
                    else:
                        customer = Customer(**customer_data)
                        session.add(customer)

                    loaded_count += 1

                except Exception as e:
                    logger.warning(f"Error loading customer {row.get('customer_id')}: {str(e)}")
                    continue

            session.commit()
            logger.info(f"Successfully loaded {loaded_count} customer records")
            return loaded_count

        except Exception as e:
            logger.error(f"Customer loading failed: {str(e)}")
            raise LoadException(f"Customer loading failed: {str(e)}")
        finally:
            if self.session is None:
                session.close()

    def load_products(self, df: pd.DataFrame, incremental: bool = False) -> int:
        """
        Load product data.

        Args:
            df: Product DataFrame
            incremental: If True, update existing records

        Returns:
            Number of records loaded

        Raises:
            LoadException: If loading fails
        """
        try:
            session = self._get_session()
            logger.info(f"Loading {len(df)} product records")

            loaded_count = 0

            for _, row in df.iterrows():
                try:
                    # Check if product exists
                    existing = session.query(Product).filter(
                        Product.product_id == row.get("product_id")
                    ).first()

                    if existing and not incremental:
                        continue

                    product_data = {
                        "product_id": str(row.get("product_id", "")),
                        "name": str(row.get("name", "")),
                        "category": str(row.get("category", "")),
                        "price": float(row.get("price", 0)),
                        "description": str(row.get("description", "")) if row.get("description") else None,
                    }

                    if existing and incremental:
                        for key, value in product_data.items():
                            setattr(existing, key, value)
                    else:
                        product = Product(**product_data)
                        session.add(product)

                    loaded_count += 1

                except Exception as e:
                    logger.warning(f"Error loading product {row.get('product_id')}: {str(e)}")
                    continue

            session.commit()
            logger.info(f"Successfully loaded {loaded_count} product records")
            return loaded_count

        except Exception as e:
            logger.error(f"Product loading failed: {str(e)}")
            raise LoadException(f"Product loading failed: {str(e)}")
        finally:
            if self.session is None:
                session.close()

    def load_sales(self, df: pd.DataFrame) -> int:
        """
        Load sales data.

        Args:
            df: Sales DataFrame

        Returns:
            Number of records loaded

        Raises:
            LoadException: If loading fails
        """
        try:
            session = self._get_session()
            logger.info(f"Loading {len(df)} sales records")

            loaded_count = 0

            for _, row in df.iterrows():
                try:
                    # Check if sale exists
                    existing = session.query(Sale).filter(
                        Sale.sale_id == row.get("sale_id")
                    ).first()

                    if existing:
                        continue

                    sale_data = {
                        "sale_id": str(row.get("sale_id", "")),
                        "customer_id": str(row.get("customer_id", "")),
                        "product_id": str(row.get("product_id", "")),
                        "quantity": int(row.get("quantity", 0)),
                        "unit_price": float(row.get("unit_price", 0)),
                        "total_value": float(row.get("total_value", 0)),
                        "sale_date": pd.to_datetime(row.get("sale_date")),
                        "year": int(row.get("year", 0)),
                        "month": int(row.get("month", 0)),
                        "quarter": int(row.get("quarter", 0)),
                    }

                    sale = Sale(**sale_data)
                    session.add(sale)
                    loaded_count += 1

                except Exception as e:
                    logger.warning(f"Error loading sale {row.get('sale_id')}: {str(e)}")
                    continue

            session.commit()
            logger.info(f"Successfully loaded {loaded_count} sales records")
            return loaded_count

        except Exception as e:
            logger.error(f"Sales loading failed: {str(e)}")
            raise LoadException(f"Sales loading failed: {str(e)}")
        finally:
            if self.session is None:
                session.close()

    def store_quality_report(self, report: DataQualityReport) -> None:
        """
        Store data quality report in database.

        Args:
            report: DataQualityReport instance
        """
        try:
            session = self._get_session()

            metric = DataQualityMetric(
                extraction_timestamp=report.extraction_timestamp,
                total_records_processed=report.total_records_processed,
                invalid_records=report.invalid_records,
                missing_values_percentage=report.missing_values_percentage,
                duplicates_removed=report.duplicates_removed,
                transformation_time_seconds=report.transformation_time_seconds,
                status=report.status,
                details=str(report.sources_processed),
            )

            session.add(metric)
            session.commit()
            logger.info("Quality report stored successfully")

        except Exception as e:
            logger.error(f"Failed to store quality report: {str(e)}")
            raise LoadException(f"Failed to store quality report: {str(e)}")
        finally:
            if self.session is None:
                session.close()

    def delete_old_data(self, days: int = 365) -> None:
        """
        Delete old data older than specified days.

        Args:
            days: Number of days to retain
        """
        try:
            session = self._get_session()
            cutoff_date = datetime.utcnow() - pd.Timedelta(days=days)

            deleted_sales = session.query(Sale).filter(
                Sale.sale_date < cutoff_date
            ).delete()

            session.commit()
            logger.info(f"Deleted {deleted_sales} old sales records")

        except Exception as e:
            logger.error(f"Failed to delete old data: {str(e)}")
        finally:
            if self.session is None:
                session.close()
