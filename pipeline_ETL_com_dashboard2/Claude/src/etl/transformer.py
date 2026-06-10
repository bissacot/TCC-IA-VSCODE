"""
Data transformation and cleaning operations.
"""

from datetime import datetime
from typing import Dict, Tuple, List, Any, Optional
import json

import pandas as pd
import numpy as np

from src.utils.logging_config import setup_logging
from src.utils.exceptions import TransformationException
from src.utils.models import DataQualityReport

logger = setup_logging(__name__)


class DataTransformer:
    """Transform and clean extracted data."""

    def __init__(self) -> None:
        """Initialize data transformer."""
        self.quality_metrics = {}
        self.transformation_start_time = None
        logger.info("Initialized data transformer")

    def transform_sales_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Transform sales data.

        Args:
            df: Raw sales DataFrame

        Returns:
            Tuple of transformed DataFrame and quality metrics
        """
        try:
            logger.info(f"Transforming sales data: {len(df)} rows")
            start_time = datetime.utcnow()

            # Store original row count
            original_count = len(df)

            # Remove duplicates
            duplicates_before = len(df)
            df = df.drop_duplicates(subset=["sale_id"], keep="first")
            duplicates_removed = duplicates_before - len(df)

            # Handle missing values
            df = self._handle_missing_values(df)

            # Validate and convert data types
            df = self._validate_and_convert_sales_types(df)

            # Standardize dates
            if "sale_date" in df.columns:
                df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")

            # Create derived metrics
            df = self._create_sales_metrics(df)

            # Calculate metrics
            invalid_records = df[df.isna().any(axis=1)].shape[0]
            missing_percentage = (df.isna().sum().sum() / (len(df) * len(df.columns))) * 100

            metrics = {
                "source": "csv_sales",
                "original_count": original_count,
                "final_count": len(df),
                "invalid_records": invalid_records,
                "duplicates_removed": duplicates_removed,
                "missing_percentage": missing_percentage,
                "transformation_time": (datetime.utcnow() - start_time).total_seconds(),
            }

            logger.info(f"Sales transformation complete: {metrics}")
            return df, metrics

        except Exception as e:
            logger.error(f"Sales transformation failed: {str(e)}")
            raise TransformationException(f"Sales transformation failed: {str(e)}")

    def transform_customer_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Transform customer data.

        Args:
            df: Raw customer DataFrame

        Returns:
            Tuple of transformed DataFrame and quality metrics
        """
        try:
            logger.info(f"Transforming customer data: {len(df)} rows")
            start_time = datetime.utcnow()

            original_count = len(df)

            # Remove duplicates
            duplicates_before = len(df)
            df = df.drop_duplicates(subset=["customer_id"], keep="first")
            duplicates_removed = duplicates_before - len(df)

            # Handle missing values
            df = self._handle_missing_values(df)

            # Validate types
            df = self._validate_and_convert_customer_types(df)

            invalid_records = df[df.isna().any(axis=1)].shape[0]
            missing_percentage = (df.isna().sum().sum() / (len(df) * len(df.columns))) * 100

            metrics = {
                "source": "json_customers",
                "original_count": original_count,
                "final_count": len(df),
                "invalid_records": invalid_records,
                "duplicates_removed": duplicates_removed,
                "missing_percentage": missing_percentage,
                "transformation_time": (datetime.utcnow() - start_time).total_seconds(),
            }

            logger.info(f"Customer transformation complete: {metrics}")
            return df, metrics

        except Exception as e:
            logger.error(f"Customer transformation failed: {str(e)}")
            raise TransformationException(f"Customer transformation failed: {str(e)}")

    def transform_product_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Transform product data.

        Args:
            df: Raw product DataFrame

        Returns:
            Tuple of transformed DataFrame and quality metrics
        """
        try:
            logger.info(f"Transforming product data: {len(df)} rows")
            start_time = datetime.utcnow()

            original_count = len(df)

            # Remove duplicates
            duplicates_before = len(df)
            df = df.drop_duplicates(subset=["product_id"], keep="first")
            duplicates_removed = duplicates_before - len(df)

            # Handle missing values
            df = self._handle_missing_values(df)

            # Validate types
            df = self._validate_and_convert_product_types(df)

            invalid_records = df[df.isna().any(axis=1)].shape[0]
            missing_percentage = (df.isna().sum().sum() / (len(df) * len(df.columns))) * 100

            metrics = {
                "source": "api_products",
                "original_count": original_count,
                "final_count": len(df),
                "invalid_records": invalid_records,
                "duplicates_removed": duplicates_removed,
                "missing_percentage": missing_percentage,
                "transformation_time": (datetime.utcnow() - start_time).total_seconds(),
            }

            logger.info(f"Product transformation complete: {metrics}")
            return df, metrics

        except Exception as e:
            logger.error(f"Product transformation failed: {str(e)}")
            raise TransformationException(f"Product transformation failed: {str(e)}")

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in DataFrame."""
        # Drop rows where critical fields are missing
        critical_columns = df.columns[0:1]  # ID column is critical
        df = df.dropna(subset=critical_columns)

        # Fill numeric columns with 0
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)

        # Fill string columns with empty string
        string_columns = df.select_dtypes(include=[object]).columns
        df[string_columns] = df[string_columns].fillna("")

        return df

    def _validate_and_convert_sales_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types for sales."""
        type_mapping = {
            "sale_id": str,
            "customer_id": str,
            "product_id": str,
            "quantity": int,
            "unit_price": float,
            "total_value": float,
        }

        for col, dtype in type_mapping.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {col} to {dtype.__name__}")
                    df[col] = pd.NA

        return df

    def _validate_and_convert_customer_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types for customers."""
        type_mapping = {
            "customer_id": str,
            "name": str,
            "email": str,
            "phone": str,
            "state": str,
        }

        for col, dtype in type_mapping.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {col} to {dtype.__name__}")
                    df[col] = pd.NA

        return df

    def _validate_and_convert_product_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types for products."""
        type_mapping = {
            "product_id": str,
            "name": str,
            "category": str,
            "price": float,
            "description": str,
        }

        for col, dtype in type_mapping.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {col} to {dtype.__name__}")
                    df[col] = pd.NA

        return df

    def _create_sales_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived metrics for sales."""
        if "sale_date" in df.columns:
            df["year"] = df["sale_date"].dt.year
            df["month"] = df["sale_date"].dt.month
            df["quarter"] = df["sale_date"].dt.quarter
            df["sale_date"] = df["sale_date"].dt.strftime("%Y-%m-%d")

        return df

    def generate_quality_report(
        self,
        metrics: Dict[str, dict],
        transformation_time: float,
    ) -> DataQualityReport:
        """
        Generate data quality report.

        Args:
            metrics: Metrics from all data sources
            transformation_time: Total transformation time in seconds

        Returns:
            DataQualityReport instance
        """
        total_processed = sum(m.get("final_count", 0) for m in metrics.values())
        total_invalid = sum(m.get("invalid_records", 0) for m in metrics.values())
        total_duplicates = sum(m.get("duplicates_removed", 0) for m in metrics.values())
        avg_missing = sum(
            m.get("missing_percentage", 0) for m in metrics.values()
        ) / len(metrics) if metrics else 0

        sources_processed = {
            m.get("source", "unknown"): m.get("final_count", 0)
            for m in metrics.values()
        }

        status = "success" if total_invalid == 0 else "partial"

        report = DataQualityReport(
            total_records_processed=total_processed,
            invalid_records=total_invalid,
            missing_values_percentage=avg_missing,
            duplicates_removed=total_duplicates,
            sources_processed=sources_processed,
            transformation_time_seconds=transformation_time,
            status=status,
        )

        logger.info(f"Quality report generated: {report}")
        return report
