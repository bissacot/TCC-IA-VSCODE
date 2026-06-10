"""Unit tests for transformers."""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from src.transformers import DataTransformer


class TestDataTransformer(unittest.TestCase):
    """Test cases for data transformer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            'id': [1, 1, 2, 3, 3],
            'value': [100, 100, 200, 300, 300]
        })
        
        result = self.transformer._remove_duplicates(df)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(self.transformer.quality_report.duplicates_removed, 2)
    
    def test_handle_missing_values_numeric(self):
        """Test handling of missing numeric values."""
        df = pd.DataFrame({
            'value': [100, 200, np.nan, 400, 500]
        })
        
        result = self.transformer._handle_missing_values(df)
        
        # Should fill with median
        self.assertFalse(result['value'].isna().any())
    
    def test_handle_missing_values_string(self):
        """Test handling of missing string values."""
        df = pd.DataFrame({
            'name': ['A', 'B', None, 'D']
        })
        
        result = self.transformer._handle_missing_values(df)
        
        self.assertFalse(result['name'].isna().any())
    
    def test_standardize_dates(self):
        """Test date standardization."""
        df = pd.DataFrame({
            'sale_date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        result = self.transformer._standardize_dates(df)
        
        self.assertEqual(result['sale_date'].dtype.name, 'datetime64[ns]')
    
    def test_create_derived_metrics(self):
        """Test derived metric creation."""
        df = pd.DataFrame({
            'quantity': [2, 3, 4],
            'unit_price': [10, 15, 20],
            'sale_date': ['2024-01-01', '2024-02-01', '2024-03-01']
        })
        
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        result = self.transformer._create_derived_metrics(df)
        
        self.assertIn('total_value', result.columns)
        self.assertIn('sale_year', result.columns)
        self.assertIn('sale_month', result.columns)
        self.assertIn('sale_quarter', result.columns)
    
    def test_validate_business_rules_negative_quantity(self):
        """Test validation of negative quantities."""
        df = pd.DataFrame({
            'quantity': [1, 2, -1, 4],
            'unit_price': [10, 20, 30, 40]
        })
        
        result = self.transformer._validate_business_rules(df)
        
        self.assertEqual(len(result), 3)
    
    def test_validate_business_rules_negative_price(self):
        """Test validation of negative prices."""
        df = pd.DataFrame({
            'quantity': [1, 2, 3, 4],
            'unit_price': [10, -20, 30, 40]
        })
        
        result = self.transformer._validate_business_rules(df)
        
        self.assertEqual(len(result), 3)


if __name__ == '__main__':
    unittest.main()
