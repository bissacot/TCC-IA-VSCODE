"""
Unit Tests for ETL Pipeline
Test extraction, transformation, and loading components
"""

import pytest
from pathlib import Path
from datetime import date
from typing import Dict, Any, List

from src.etl.extractors import CSVExtractor, JSONExtractor, APIExtractor
from src.etl.transformers import (
    SalesTransformer, CustomerTransformer, ProductTransformer,
    DataQualityMetrics
)
from src.config import config


class TestDataQualityMetrics:
    """Test DataQualityMetrics class"""
    
    def test_initialization(self):
        """Test metrics initialization"""
        metrics = DataQualityMetrics()
        assert metrics.total_records == 0
        assert metrics.invalid_records == 0
        assert metrics.duplicates_removed == 0
        assert metrics.missing_value_percentage == 0.0
    
    def test_missing_value_percentage(self):
        """Test missing value percentage calculation"""
        metrics = DataQualityMetrics()
        metrics.total_values = 100
        metrics.missing_values_count = 10
        
        assert metrics.missing_value_percentage == 10.0
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = DataQualityMetrics()
        metrics.total_records = 100
        metrics.invalid_records = 5
        metrics.duplicates_removed = 2
        
        data = metrics.to_dict()
        
        assert data["total_records"] == 100
        assert data["invalid_records"] == 5
        assert data["duplicates_removed"] == 2


class TestSalesTransformer:
    """Test SalesTransformer class"""
    
    def test_initialization(self):
        """Test transformer initialization"""
        transformer = SalesTransformer()
        assert transformer.required_fields == [
            "sale_id", "customer_id", "product_id", "quantity", "unit_price", "sale_date"
        ]
    
    def test_validate_record_valid(self):
        """Test validation of valid record"""
        transformer = SalesTransformer()
        record = {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is True
        assert error is None
    
    def test_validate_record_missing_field(self):
        """Test validation with missing field"""
        transformer = SalesTransformer()
        record = {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            # missing unit_price
            "sale_date": "2024-01-15"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is False
        assert "Missing required field" in error
    
    def test_validate_record_negative_quantity(self):
        """Test validation with negative quantity"""
        transformer = SalesTransformer()
        record = {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": -1,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is False
        assert "positive" in error.lower()
    
    def test_standardize_date_iso_format(self):
        """Test date standardization with ISO format"""
        transformer = SalesTransformer()
        result = transformer.standardize_date("2024-01-15")
        
        assert result == date(2024, 1, 15)
    
    def test_standardize_date_br_format(self):
        """Test date standardization with BR format"""
        transformer = SalesTransformer()
        result = transformer.standardize_date("15/01/2024")
        
        assert result == date(2024, 1, 15)
    
    def test_calculate_derived_metrics(self):
        """Test derived metrics calculation"""
        transformer = SalesTransformer()
        record = {
            "quantity": 2,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        }
        
        derived = transformer.calculate_derived_metrics(record)
        
        assert derived["total_value"] == 100.0
        assert derived["year"] == 2024
        assert derived["month"] == 1
        assert derived["quarter"] == 1
    
    def test_transform_valid_records(self):
        """Test transformation of valid records"""
        transformer = SalesTransformer()
        data = [
            {
                "sale_id": "S001",
                "customer_id": "C001",
                "product_id": "P001",
                "quantity": 2,
                "unit_price": 50.00,
                "sale_date": "2024-01-15"
            },
            {
                "sale_id": "S002",
                "customer_id": "C002",
                "product_id": "P002",
                "quantity": 1,
                "unit_price": 100.00,
                "sale_date": "2024-02-20"
            }
        ]
        
        transformed, metrics = transformer.transform(data)
        
        assert len(transformed) == 2
        assert metrics.total_records == 2
        assert metrics.invalid_records == 0
        assert metrics.duplicates_removed == 0


class TestCustomerTransformer:
    """Test CustomerTransformer class"""
    
    def test_validate_record_valid(self):
        """Test validation of valid customer record"""
        transformer = CustomerTransformer()
        record = {
            "customer_id": "C001",
            "name": "João Silva",
            "state": "SP",
            "email": "joao@example.com"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is True
    
    def test_validate_record_invalid_email(self):
        """Test validation with invalid email"""
        transformer = CustomerTransformer()
        record = {
            "customer_id": "C001",
            "name": "João Silva",
            "state": "SP",
            "email": "invalid-email"
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is False
        assert "email" in error.lower()
    
    def test_clean_name(self):
        """Test name cleaning"""
        transformer = CustomerTransformer()
        
        result = transformer.clean_name("  joão silva  ")
        assert result == "João Silva"
    
    def test_clean_state(self):
        """Test state cleaning"""
        transformer = CustomerTransformer()
        
        result = transformer.clean_state("  sp  ")
        assert result == "SP"


class TestProductTransformer:
    """Test ProductTransformer class"""
    
    def test_validate_record_valid(self):
        """Test validation of valid product record"""
        transformer = ProductTransformer()
        record = {
            "id": "P001",
            "name": "Product 1",
            "price": 50.00
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is True
    
    def test_validate_record_negative_price(self):
        """Test validation with negative price"""
        transformer = ProductTransformer()
        record = {
            "id": "P001",
            "name": "Product 1",
            "price": -50.00
        }
        
        is_valid, error = transformer.validate_record(record)
        assert is_valid is False


class TestCSVExtractor:
    """Test CSV Extractor"""
    
    def test_validate_source_exists(self):
        """Test CSV source validation"""
        extractor = CSVExtractor(config.CSV_SALES_PATH)
        # Note: This will return True if file exists
        result = extractor.validate_source()
        assert isinstance(result, bool)
    
    def test_validate_source_not_exists(self):
        """Test CSV source validation with non-existent file"""
        extractor = CSVExtractor(Path("non_existent.csv"))
        result = extractor.validate_source()
        assert result is False


@pytest.fixture
def sample_sales_data() -> List[Dict[str, Any]]:
    """Sample sales data for testing"""
    return [
        {
            "sale_id": "S001",
            "customer_id": "C001",
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 50.00,
            "sale_date": "2024-01-15"
        },
        {
            "sale_id": "S002",
            "customer_id": "C002",
            "product_id": "P002",
            "quantity": 1,
            "unit_price": 100.00,
            "sale_date": "2024-01-20"
        }
    ]


@pytest.fixture
def sample_customer_data() -> List[Dict[str, Any]]:
    """Sample customer data for testing"""
    return [
        {
            "customer_id": "C001",
            "name": "João Silva",
            "email": "joao@example.com",
            "state": "SP"
        },
        {
            "customer_id": "C002",
            "name": "Maria Santos",
            "email": "maria@example.com",
            "state": "RJ"
        }
    ]


def test_sales_transformation_integration(sample_sales_data):
    """Integration test for sales transformation"""
    transformer = SalesTransformer()
    transformed, metrics = transformer.transform(sample_sales_data)
    
    assert len(transformed) == 2
    assert all("sale_id" in record for record in transformed)
    assert all("total_value" in record for record in transformed)


def test_customer_transformation_integration(sample_customer_data):
    """Integration test for customer transformation"""
    transformer = CustomerTransformer()
    transformed, metrics = transformer.transform(sample_customer_data)
    
    assert len(transformed) == 2
    assert all("customer_id" in record for record in transformed)
    assert all("state" in record for record in transformed)
