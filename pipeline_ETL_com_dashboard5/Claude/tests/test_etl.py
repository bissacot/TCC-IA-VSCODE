"""
Unit tests for the ETL pipeline.
"""

import pytest
from datetime import datetime
from src.utils.validators import Validators
from src.models.schemas import Customer, Product, Sale, DataQualityReport
from src.etl.transformer import DataTransformer


class TestValidators:
    """Test data validators."""

    def test_validate_email(self):
        """Test email validation."""
        assert Validators.validate_email("user@example.com") is True
        assert Validators.validate_email("invalid.email@") is False
        assert Validators.validate_email("invalid") is False

    def test_validate_phone(self):
        """Test phone validation."""
        assert Validators.validate_phone("1234567890") is True
        assert Validators.validate_phone("(123) 456-7890") is True
        assert Validators.validate_phone("123") is False
        assert Validators.validate_phone("abc") is False

    def test_validate_numeric(self):
        """Test numeric validation."""
        assert Validators.validate_numeric("123.45") is True
        assert Validators.validate_numeric("-50") is True
        assert Validators.validate_numeric("-50", allow_negative=False) is False
        assert Validators.validate_numeric("abc") is False

    def test_validate_date_format(self):
        """Test date format validation."""
        is_valid, parsed_date = Validators.validate_date_format("2024-01-15")
        assert is_valid is True
        assert parsed_date.year == 2024
        
        is_valid, parsed_date = Validators.validate_date_format("invalid")
        assert is_valid is False

    def test_is_null_or_empty(self):
        """Test null/empty validation."""
        assert Validators.is_null_or_empty(None) is True
        assert Validators.is_null_or_empty("") is True
        assert Validators.is_null_or_empty("   ") is True
        assert Validators.is_null_or_empty([]) is True
        assert Validators.is_null_or_empty("value") is False

    def test_sanitize_string(self):
        """Test string sanitization."""
        assert Validators.sanitize_string("  hello  ") == "hello"
        assert Validators.sanitize_string("test") == "test"


class TestDataModels:
    """Test data models."""

    def test_customer_model(self):
        """Test Customer model."""
        now = datetime.now()
        customer = Customer(
            customer_id="C001",
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
            country="USA",
            created_at=now,
            updated_at=now,
        )
        
        assert customer.customer_id == "C001"
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        
        data_dict = customer.to_dict()
        assert data_dict['customer_id'] == "C001"

    def test_product_model(self):
        """Test Product model."""
        now = datetime.now()
        product = Product(
            product_id="P001",
            name="Widget",
            category="Electronics",
            subcategory="Gadgets",
            price=99.99,
            description="A useful widget",
            manufacturer="Widget Corp",
            created_at=now,
            updated_at=now,
        )
        
        assert product.product_id == "P001"
        assert product.category == "Electronics"
        assert product.price == 99.99

    def test_sale_model(self):
        """Test Sale model."""
        now = datetime.now()
        sale = Sale(
            sale_id="S001",
            customer_id="C001",
            product_id="P001",
            quantity=5,
            unit_price=99.99,
            total_value=499.95,
            sale_date=now,
            year=2024,
            month=1,
            quarter=1,
            state="IL",
            payment_method="Credit Card",
            created_at=now,
            updated_at=now,
        )
        
        assert sale.sale_id == "S001"
        assert sale.quantity == 5
        assert sale.total_value == 499.95

    def test_data_quality_report_model(self):
        """Test DataQualityReport model."""
        report = DataQualityReport(
            report_timestamp=datetime.now(),
            total_records_processed=1000,
            valid_records=950,
            invalid_records=50,
            duplicates_removed=5,
        )
        
        assert report.total_records_processed == 1000
        assert report.valid_records == 950


class TestDataTransformer:
    """Test data transformer."""

    def test_transform_customers(self):
        """Test customer transformation."""
        transformer = DataTransformer()
        
        raw_data = [
            {
                'customer_id': 'C001',
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '1234567890',
                'city': 'Springfield',
                'state': 'IL',
            },
            {
                'customer_id': 'C002',
                'name': 'Jane Smith',
                'email': 'invalid-email',  # Invalid email
                'phone': None,
            }
        ]
        
        valid_customers, errors = transformer.transform_customers(raw_data)
        
        assert len(valid_customers) == 1  # Only valid customer
        assert len(errors) == 1  # One error

    def test_transform_products(self):
        """Test product transformation."""
        transformer = DataTransformer()
        
        raw_data = [
            {
                'product_id': 'P001',
                'name': 'Widget',
                'category': 'Electronics',
                'price': '99.99',
            },
            {
                'product_id': 'P002',
                'name': 'Gadget',
                'category': 'Electronics',
                'price': 'invalid',  # Invalid price
            }
        ]
        
        valid_products, errors = transformer.transform_products(raw_data)
        
        assert len(valid_products) == 1  # Only valid product
        assert len(errors) == 1  # One error

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        transformer = DataTransformer()
        
        data = [
            {'id': '1', 'name': 'Item 1'},
            {'id': '2', 'name': 'Item 2'},
            {'id': '1', 'name': 'Item 1 Duplicate'},
        ]
        
        unique_data, duplicates = transformer.remove_duplicates(data, 'id')
        
        assert len(unique_data) == 2
        assert duplicates == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
