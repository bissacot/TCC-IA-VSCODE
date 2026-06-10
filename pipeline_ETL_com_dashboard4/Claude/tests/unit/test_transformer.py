"""
Unit tests for data transformation module.

Tests sales, customer, and product transformers.
"""

import pytest
from datetime import datetime

from src.etl.transformer import (
    SalesTransformer,
    CustomerTransformer,
    ProductTransformer,
)


class TestSalesTransformer:
    """Tests for sales data transformation."""

    def test_transform_valid_sales(self) -> None:
        """Test transformation of valid sales data."""
        transformer = SalesTransformer()

        raw_data = [
            {
                "customer_id": "1",
                "product_id": "2",
                "quantity": "5",
                "unit_price": "100.00",
                "sale_date": "2024-01-15",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 1
        assert transformed[0]["customer_id"] == 1
        assert transformed[0]["product_id"] == 2
        assert transformed[0]["quantity"] == 5
        assert transformed[0]["total_value"] == 500.0
        assert report.processed_records == 1
        assert report.invalid_records == 0

    def test_transform_missing_required_field(self) -> None:
        """Test transformation with missing required field."""
        transformer = SalesTransformer()

        raw_data = [
            {
                "customer_id": "1",
                "product_id": "2",
                # Missing quantity
                "unit_price": "100.00",
                "sale_date": "2024-01-15",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 0
        assert report.invalid_records == 1

    def test_transform_duplicate_detection(self) -> None:
        """Test duplicate record detection."""
        transformer = SalesTransformer()

        raw_data = [
            {
                "customer_id": "1",
                "product_id": "2",
                "quantity": "5",
                "unit_price": "100.00",
                "sale_date": "2024-01-15",
            },
            {
                "customer_id": "1",
                "product_id": "2",
                "quantity": "3",
                "unit_price": "100.00",
                "sale_date": "2024-01-15",
            },
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 1
        assert report.duplicates_removed == 1


class TestCustomerTransformer:
    """Tests for customer data transformation."""

    def test_transform_valid_customer(self) -> None:
        """Test transformation of valid customer data."""
        transformer = CustomerTransformer()

        raw_data = [
            {
                "name": "John Smith",
                "email": "john@example.com",
                "state": "CA",
                "city": "San Francisco",
                "phone": "(555) 123-4567",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 1
        assert transformed[0]["name"] == "John Smith"
        assert transformed[0]["email"] == "john@example.com"
        assert report.processed_records == 1
        assert report.invalid_records == 0

    def test_transform_invalid_email(self) -> None:
        """Test transformation with invalid email."""
        transformer = CustomerTransformer()

        raw_data = [
            {
                "name": "John Smith",
                "email": "invalid-email",
                "state": "CA",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 0
        assert report.invalid_records == 1

    def test_transform_duplicate_email(self) -> None:
        """Test duplicate email detection."""
        transformer = CustomerTransformer()

        raw_data = [
            {
                "name": "John Smith",
                "email": "john@example.com",
                "state": "CA",
            },
            {
                "name": "Jane Smith",
                "email": "john@example.com",
                "state": "CA",
            },
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 1
        assert report.duplicates_removed == 1


class TestProductTransformer:
    """Tests for product data transformation."""

    def test_transform_valid_product(self) -> None:
        """Test transformation of valid product data."""
        transformer = ProductTransformer()

        raw_data = [
            {
                "name": "Laptop",
                "category": "Electronics",
                "price": "899.99",
                "description": "High-performance laptop",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 1
        assert transformed[0]["name"] == "Laptop"
        assert transformed[0]["price"] == 899.99
        assert report.processed_records == 1
        assert report.invalid_records == 0

    def test_transform_invalid_price(self) -> None:
        """Test transformation with invalid price."""
        transformer = ProductTransformer()

        raw_data = [
            {
                "name": "Laptop",
                "category": "Electronics",
                "price": "-100",
                "description": "High-performance laptop",
            }
        ]

        transformed, report = transformer.transform(raw_data)

        assert len(transformed) == 0
        assert report.invalid_records == 1
