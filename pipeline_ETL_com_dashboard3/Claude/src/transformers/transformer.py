"""Data transformation and validation."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from src.utils.logger import logger
from src.utils.exceptions import TransformationException, ValidationException
from src.utils.models import DataQualityReport


class DataTransformer:
    """Handles data transformation and validation."""
    
    def __init__(self):
        """Initialize the data transformer."""
        self.quality_report = DataQualityReport()
    
    def transform_sales_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityReport]:
        """
        Transform sales data with all cleaning and validation steps.
        
        Args:
            df: Raw sales DataFrame
        
        Returns:
            Tuple of (transformed DataFrame, quality report)
        """
        try:
            logger.info(f"Starting sales data transformation ({len(df)} rows)")
            self.quality_report.records_by_source['raw_sales'] = len(df)
            
            # Step 1: Remove duplicates
            df = self._remove_duplicates(df)
            
            # Step 2: Handle missing values
            df = self._handle_missing_values(df)
            
            # Step 3: Validate data types
            df = self._validate_data_types(df)
            
            # Step 4: Standardize dates
            df = self._standardize_dates(df)
            
            # Step 5: Create derived metrics
            df = self._create_derived_metrics(df)
            
            # Step 6: Validate business rules
            df = self._validate_business_rules(df)
            
            self.quality_report.total_records_processed = len(df)
            logger.info(f"Sales transformation complete ({len(df)} rows)")
            
            return df, self.quality_report
        
        except Exception as e:
            logger.error(f"Sales transformation failed: {str(e)}")
            raise TransformationException(f"Sales transformation error: {str(e)}")
    
    def transform_customer_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityReport]:
        """
        Transform customer data.
        
        Args:
            df: Raw customer DataFrame
        
        Returns:
            Tuple of (transformed DataFrame, quality report)
        """
        try:
            logger.info(f"Starting customer data transformation ({len(df)} rows)")
            self.quality_report.records_by_source['raw_customers'] = len(df)
            
            # Step 1: Remove duplicates
            df = self._remove_duplicates(df)
            
            # Step 2: Handle missing values
            df = self._handle_missing_values(df)
            
            # Step 3: Validate data types
            df = self._validate_data_types(df)
            
            # Step 4: Standardize dates
            df = self._standardize_dates(df)
            
            self.quality_report.total_records_processed = len(df)
            logger.info(f"Customer transformation complete ({len(df)} rows)")
            
            return df, self.quality_report
        
        except Exception as e:
            logger.error(f"Customer transformation failed: {str(e)}")
            raise TransformationException(f"Customer transformation error: {str(e)}")
    
    def transform_product_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQualityReport]:
        """
        Transform product data.
        
        Args:
            df: Raw product DataFrame
        
        Returns:
            Tuple of (transformed DataFrame, quality report)
        """
        try:
            logger.info(f"Starting product data transformation ({len(df)} rows)")
            self.quality_report.records_by_source['raw_products'] = len(df)
            
            # Step 1: Remove duplicates
            df = self._remove_duplicates(df)
            
            # Step 2: Handle missing values
            df = self._handle_missing_values(df)
            
            # Step 3: Validate data types
            df = self._validate_data_types(df)
            
            self.quality_report.total_records_processed = len(df)
            logger.info(f"Product transformation complete ({len(df)} rows)")
            
            return df, self.quality_report
        
        except Exception as e:
            logger.error(f"Product transformation failed: {str(e)}")
            raise TransformationException(f"Product transformation error: {str(e)}")
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_len = len(df)
        
        # Identify duplicate rows (keep first occurrence)
        df = df.drop_duplicates(keep='first')
        
        duplicates_count = initial_len - len(df)
        self.quality_report.duplicates_removed += duplicates_count
        
        if duplicates_count > 0:
            logger.info(f"Removed {duplicates_count} duplicate rows")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values."""
        missing_report: Dict[str, float] = {}
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_percentage = (missing_count / len(df)) * 100 if len(df) > 0 else 0
            
            if missing_percentage > 0:
                missing_report[column] = round(missing_percentage, 2)
                logger.debug(f"Column '{column}': {missing_percentage:.2f}% missing values")
        
        self.quality_report.missing_values_percentage.update(missing_report)
        
        # Remove rows with critical missing values
        critical_columns = df.columns[df.isna().all()].tolist()
        if critical_columns:
            df = df.dropna(axis=0, how='all')
            logger.info(f"Removed rows with all missing values")
        
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().any():
                median_value = df[col].median()
                df[col].fillna(median_value, inplace=True)
                logger.debug(f"Filled {col} missing values with median")
        
        # Fill string columns with 'Unknown'
        string_cols = df.select_dtypes(include=['object']).columns
        for col in string_cols:
            if df[col].isna().any():
                df[col].fillna('Unknown', inplace=True)
                logger.debug(f"Filled {col} missing values with 'Unknown'")
        
        return df
    
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and correct data types."""
        for column in df.columns:
            # Try to convert to numeric if applicable
            if df[column].dtype == 'object':
                # Check if column contains numeric values
                numeric_cols = ['price', 'amount', 'value', 'quantity', 'total', 'cost']
                if any(col_name in column.lower() for col_name in numeric_cols):
                    try:
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                        logger.debug(f"Converted {column} to numeric")
                    except Exception as e:
                        logger.warning(f"Could not convert {column} to numeric: {str(e)}")
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to ISO format."""
        date_cols = ['date', 'created_at', 'updated_at', 'registration_date', 'sale_date']
        
        for col in df.columns:
            if any(date_col in col.lower() for date_col in date_cols):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.debug(f"Standardized {col} to datetime")
                except Exception as e:
                    logger.warning(f"Could not standardize {col}: {str(e)}")
        
        return df
    
    def _create_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived metrics."""
        try:
            # Create total_value if quantity and unit_price exist
            if 'quantity' in df.columns and 'unit_price' in df.columns:
                if 'total_value' not in df.columns:
                    df['total_value'] = df['quantity'] * df['unit_price']
                    logger.debug("Created total_value metric")
            
            # Extract date components if sale_date exists
            if 'sale_date' in df.columns:
                df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
                if not 'sale_year' in df.columns:
                    df['sale_year'] = df['sale_date'].dt.year
                if not 'sale_month' in df.columns:
                    df['sale_month'] = df['sale_date'].dt.month
                if not 'sale_quarter' in df.columns:
                    df['sale_quarter'] = df['sale_date'].dt.quarter
                logger.debug("Created date component metrics")
        
        except Exception as e:
            logger.warning(f"Error creating derived metrics: {str(e)}")
        
        return df
    
    def _validate_business_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate business rules."""
        invalid_count = 0
        
        # Check for negative quantities
        if 'quantity' in df.columns:
            invalid_quantity = df[df['quantity'] < 0]
            if len(invalid_quantity) > 0:
                logger.warning(f"Found {len(invalid_quantity)} negative quantities")
                invalid_count += len(invalid_quantity)
                df = df[df['quantity'] >= 0]
        
        # Check for negative prices
        numeric_cols = ['price', 'unit_price', 'total_value']
        for col in numeric_cols:
            if col in df.columns:
                invalid_prices = df[df[col] < 0]
                if len(invalid_prices) > 0:
                    logger.warning(f"Found {len(invalid_prices)} negative {col} values")
                    invalid_count += len(invalid_prices)
                    df = df[df[col] >= 0]
        
        self.quality_report.total_invalid_records = invalid_count
        
        return df
    
    def get_quality_report(self) -> DataQualityReport:
        """Get the current quality report."""
        return self.quality_report
