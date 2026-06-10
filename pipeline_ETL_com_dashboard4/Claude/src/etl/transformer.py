"""
Data transformation module for the ETL pipeline.

Handles data cleaning, validation, and enrichment.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from collections import Counter

import pandas as pd

from src.utils import LoggerConfig, DataValidator, DataTypeValidator, TransformationException
from config.settings import ISO_DATE_FORMAT


logger = LoggerConfig.get_logger(__name__)


class DataQualityReport:
    """Tracks data quality metrics during transformation."""

    def __init__(self) -> None:
        """Initialize quality report."""
        self.processed_records: int = 0
        self.invalid_records: int = 0
        self.duplicates_removed: int = 0
        self.missing_values_count: Dict[str, int] = {}
        self.missing_values_percentage: float = 0.0
        self.processing_time: float = 0.0

    def add_invalid_record(self) -> None:
        """Increment invalid records counter."""
        self.invalid_records += 1

    def add_duplicate_removed(self) -> None:
        """Increment duplicates removed counter."""
        self.duplicates_removed += 1

    def set_processing_time(self, duration: float) -> None:
        """Set processing duration."""
        self.processing_time = duration

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary.

        Returns:
            Dictionary representation of quality report
        """
        return {
            "processed_records": self.processed_records,
            "invalid_records": self.invalid_records,
            "duplicates_removed": self.duplicates_removed,
            "missing_values_percentage": self.missing_values_percentage,
            "processing_time_seconds": self.processing_time,
        }

    def __repr__(self) -> str:
        return (
            f"DataQualityReport("
            f"processed={self.processed_records}, "
            f"invalid={self.invalid_records}, "
            f"duplicates_removed={self.duplicates_removed}, "
            f"missing_values_pct={self.missing_values_percentage:.2f}%)"
        )


class SalesTransformer:
    """Transforms sales data."""

    REQUIRED_FIELDS = ["customer_id", "product_id", "quantity", "unit_price", "sale_date"]

    def __init__(self) -> None:
        """Initialize sales transformer."""
        self.quality_report = DataQualityReport()

    def transform(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityReport]:
        """
        Transform and validate sales data.

        Args:
            raw_data: Raw sales data from source

        Returns:
            Tuple of transformed data and quality report
        """
        logger.info(f"Starting sales transformation for {len(raw_data)} records")

        start_time = datetime.now()
        transformed_data: List[Dict[str, Any]] = []
        seen_records: set = set()

        for record in raw_data:
            try:
                # Validate required fields
                if not DataValidator.validate_required_fields(record, self.REQUIRED_FIELDS):
                    logger.warning(f"Missing required fields in record: {record}")
                    self.quality_report.add_invalid_record()
                    continue

                # Clean and validate data
                cleaned_record = self._clean_record(record)

                # Check for duplicates
                record_hash = self._hash_record(cleaned_record)
                if record_hash in seen_records:
                    self.quality_report.add_duplicate_removed()
                    continue

                seen_records.add(record_hash)

                # Transform data
                transformed_record = self._transform_record(cleaned_record)
                transformed_data.append(transformed_record)

            except Exception as e:
                logger.warning(f"Error transforming record {record}: {e}")
                self.quality_report.add_invalid_record()
                continue

        self.quality_report.processed_records = len(transformed_data)

        # Calculate missing values percentage
        if transformed_data:
            self.quality_report.missing_values_percentage = self._calculate_missing_percentage(
                transformed_data
            )

        duration = (datetime.now() - start_time).total_seconds()
        self.quality_report.set_processing_time(duration)

        logger.info(
            f"Sales transformation completed: {len(transformed_data)} valid records, "
            f"{self.quality_report.invalid_records} invalid, "
            f"{self.quality_report.duplicates_removed} duplicates removed"
        )

        return transformed_data, self.quality_report

    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a sales record."""
        return {
            "customer_id": str(record.get("customer_id", "")).strip(),
            "product_id": str(record.get("product_id", "")).strip(),
            "quantity": str(record.get("quantity", "")).strip(),
            "unit_price": str(record.get("unit_price", "")).strip(),
            "sale_date": str(record.get("sale_date", "")).strip(),
        }

    @staticmethod
    def _transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a cleaned sales record."""
        quantity = DataTypeValidator.to_int(record["quantity"], 0)
        unit_price = DataTypeValidator.to_float(record["unit_price"], 0.0)
        total_value = quantity * unit_price

        # Parse date
        sale_date = datetime.strptime(record["sale_date"], "%Y-%m-%d")

        return {
            "customer_id": int(record["customer_id"]),
            "product_id": int(record["product_id"]),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_value": total_value,
            "sale_date": sale_date.date(),
            "year": sale_date.year,
            "month": sale_date.month,
            "quarter": (sale_date.month - 1) // 3 + 1,
        }

    @staticmethod
    def _hash_record(record: Dict[str, Any]) -> str:
        """Create hash for duplicate detection."""
        key_fields = [
            record.get("customer_id"),
            record.get("product_id"),
            record.get("sale_date"),
        ]
        return "|".join(str(f) for f in key_fields)

    @staticmethod
    def _calculate_missing_percentage(data: List[Dict[str, Any]]) -> float:
        """Calculate percentage of missing values."""
        if not data:
            return 0.0

        total_cells = len(data) * len(data[0])
        missing_cells = sum(
            1 for record in data for value in record.values() if value is None
        )

        return (missing_cells / total_cells * 100) if total_cells > 0 else 0.0


class CustomerTransformer:
    """Transforms customer data."""

    REQUIRED_FIELDS = ["name", "email", "state"]

    def __init__(self) -> None:
        """Initialize customer transformer."""
        self.quality_report = DataQualityReport()

    def transform(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityReport]:
        """
        Transform and validate customer data.

        Args:
            raw_data: Raw customer data from source

        Returns:
            Tuple of transformed data and quality report
        """
        logger.info(f"Starting customer transformation for {len(raw_data)} records")

        start_time = datetime.now()
        transformed_data: List[Dict[str, Any]] = []
        seen_emails: set = set()

        for record in raw_data:
            try:
                # Validate required fields
                if not DataValidator.validate_required_fields(record, self.REQUIRED_FIELDS):
                    logger.warning(f"Missing required fields in customer record: {record}")
                    self.quality_report.add_invalid_record()
                    continue

                # Clean and validate data
                cleaned_record = self._clean_record(record)

                # Validate email
                if not DataValidator.validate_email(cleaned_record["email"]):
                    logger.warning(f"Invalid email: {cleaned_record['email']}")
                    self.quality_report.add_invalid_record()
                    continue

                # Check for duplicate emails
                if cleaned_record["email"] in seen_emails:
                    self.quality_report.add_duplicate_removed()
                    continue

                seen_emails.add(cleaned_record["email"])

                # Transform data
                transformed_record = self._transform_record(cleaned_record)
                transformed_data.append(transformed_record)

            except Exception as e:
                logger.warning(f"Error transforming customer record {record}: {e}")
                self.quality_report.add_invalid_record()
                continue

        self.quality_report.processed_records = len(transformed_data)

        if transformed_data:
            self.quality_report.missing_values_percentage = self._calculate_missing_percentage(
                transformed_data
            )

        duration = (datetime.now() - start_time).total_seconds()
        self.quality_report.set_processing_time(duration)

        logger.info(
            f"Customer transformation completed: {len(transformed_data)} valid records, "
            f"{self.quality_report.invalid_records} invalid"
        )

        return transformed_data, self.quality_report

    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a customer record."""
        return {
            "name": DataValidator.sanitize_string(record.get("name", "")),
            "email": DataValidator.sanitize_string(record.get("email", "")),
            "phone": DataValidator.sanitize_string(record.get("phone")),
            "state": DataValidator.sanitize_string(record.get("state", "")),
            "city": DataValidator.sanitize_string(record.get("city")),
            "zipcode": DataValidator.sanitize_string(record.get("zipcode")),
        }

    @staticmethod
    def _transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a cleaned customer record."""
        return {
            "name": record["name"],
            "email": record["email"],
            "phone": record["phone"],
            "state": record["state"],
            "city": record["city"],
            "zipcode": record["zipcode"],
        }

    @staticmethod
    def _calculate_missing_percentage(data: List[Dict[str, Any]]) -> float:
        """Calculate percentage of missing values."""
        if not data:
            return 0.0

        total_cells = len(data) * len(data[0])
        missing_cells = sum(
            1 for record in data for value in record.values() if value is None
        )

        return (missing_cells / total_cells * 100) if total_cells > 0 else 0.0


class ProductTransformer:
    """Transforms product data."""

    REQUIRED_FIELDS = ["name", "category", "price"]

    def __init__(self) -> None:
        """Initialize product transformer."""
        self.quality_report = DataQualityReport()

    def transform(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], DataQualityReport]:
        """
        Transform and validate product data.

        Args:
            raw_data: Raw product data from source

        Returns:
            Tuple of transformed data and quality report
        """
        logger.info(f"Starting product transformation for {len(raw_data)} records")

        start_time = datetime.now()
        transformed_data: List[Dict[str, Any]] = []
        seen_products: set = set()

        for record in raw_data:
            try:
                # Validate required fields
                if not DataValidator.validate_required_fields(record, self.REQUIRED_FIELDS):
                    logger.warning(f"Missing required fields in product record: {record}")
                    self.quality_report.add_invalid_record()
                    continue

                # Clean and validate data
                cleaned_record = self._clean_record(record)

                # Validate price
                if not DataValidator.validate_currency(cleaned_record["price"]):
                    logger.warning(f"Invalid price: {cleaned_record['price']}")
                    self.quality_report.add_invalid_record()
                    continue

                # Check for duplicates
                product_hash = (cleaned_record["name"], cleaned_record["category"])
                if product_hash in seen_products:
                    self.quality_report.add_duplicate_removed()
                    continue

                seen_products.add(product_hash)

                # Transform data
                transformed_record = self._transform_record(cleaned_record)
                transformed_data.append(transformed_record)

            except Exception as e:
                logger.warning(f"Error transforming product record {record}: {e}")
                self.quality_report.add_invalid_record()
                continue

        self.quality_report.processed_records = len(transformed_data)

        if transformed_data:
            self.quality_report.missing_values_percentage = self._calculate_missing_percentage(
                transformed_data
            )

        duration = (datetime.now() - start_time).total_seconds()
        self.quality_report.set_processing_time(duration)

        logger.info(
            f"Product transformation completed: {len(transformed_data)} valid records, "
            f"{self.quality_report.invalid_records} invalid"
        )

        return transformed_data, self.quality_report

    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a product record."""
        return {
            "name": DataValidator.sanitize_string(record.get("name", "")),
            "category": DataValidator.sanitize_string(record.get("category", "")),
            "price": str(record.get("price", "")).strip(),
            "description": DataValidator.sanitize_string(record.get("description")),
        }

    @staticmethod
    def _transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a cleaned product record."""
        return {
            "name": record["name"],
            "category": record["category"],
            "price": DataTypeValidator.to_float(record["price"], 0.0),
            "description": record["description"],
        }

    @staticmethod
    def _calculate_missing_percentage(data: List[Dict[str, Any]]) -> float:
        """Calculate percentage of missing values."""
        if not data:
            return 0.0

        total_cells = len(data) * len(data[0])
        missing_cells = sum(
            1 for record in data for value in record.values() if value is None
        )

        return (missing_cells / total_cells * 100) if total_cells > 0 else 0.0
