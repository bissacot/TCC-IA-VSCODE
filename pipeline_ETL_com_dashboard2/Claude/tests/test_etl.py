"""
Unit tests for ETL pipeline.
"""

import pytest
import pandas as pd
import tempfile
import json
from pathlib import Path
from datetime import datetime

from src.etl.extractor import CSVExtractor, JSONExtractor
from src.etl.transformer import DataTransformer
from src.utils.exceptions import ExtractionException


class TestCSVExtractor:
    """Test CSV extractor."""

    def test_extract_valid_csv(self):
        """Test extracting valid CSV file."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sale_id,customer_id,product_id,quantity,unit_price,total_value,sale_date\n")
            f.write("SALE001,CUST001,PROD001,2,100.00,200.00,2024-01-15\n")
            f.write("SALE002,CUST002,PROD002,1,150.00,150.00,2024-01-16\n")
            temp_path = f.name

        try:
            extractor = CSVExtractor(temp_path)
            df = extractor.extract()

            assert len(df) == 2
            assert list(df.columns) == [
                "sale_id", "customer_id", "product_id", "quantity",
                "unit_price", "total_value", "sale_date"
            ]
        finally:
            Path(temp_path).unlink()

    def test_extract_nonexistent_csv(self):
        """Test extracting non-existent CSV file."""
        extractor = CSVExtractor("/nonexistent/path.csv")

        with pytest.raises(ExtractionException):
            extractor.extract()


class TestJSONExtractor:
    """Test JSON extractor."""

    def test_extract_valid_json(self):
        """Test extracting valid JSON file."""
        # Create temporary JSON file
        data = [
            {
                "customer_id": "CUST001",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+55 11 98765-4321",
                "state": "SP"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            extractor = JSONExtractor(temp_path)
            df = extractor.extract()

            assert len(df) == 1
            assert df.iloc[0]["customer_id"] == "CUST001"
        finally:
            Path(temp_path).unlink()

    def test_extract_nested_json(self):
        """Test extracting nested JSON."""
        data = {
            "data": {
                "customers": [
                    {"customer_id": "CUST001", "name": "John"}
                ]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            extractor = JSONExtractor(temp_path, json_path="data.customers")
            df = extractor.extract()

            assert len(df) == 1
            assert df.iloc[0]["customer_id"] == "CUST001"
        finally:
            Path(temp_path).unlink()


class TestDataTransformer:
    """Test data transformer."""

    def test_transform_sales_data(self):
        """Test sales data transformation."""
        transformer = DataTransformer()

        df = pd.DataFrame({
            "sale_id": ["SALE001", "SALE002", "SALE001"],  # Duplicate
            "customer_id": ["CUST001", "CUST002", "CUST001"],
            "product_id": ["PROD001", "PROD002", "PROD001"],
            "quantity": [2, 1, 2],
            "unit_price": [100.0, 150.0, 100.0],
            "total_value": [200.0, 150.0, 200.0],
            "sale_date": ["2024-01-15", "2024-01-16", "2024-01-15"],
        })

        result_df, metrics = transformer.transform_sales_data(df)

        # Should have removed duplicate
        assert len(result_df) == 2
        assert metrics["duplicates_removed"] == 1
        assert "year" in result_df.columns
        assert "month" in result_df.columns
        assert "quarter" in result_df.columns

    def test_handle_missing_values(self):
        """Test handling missing values."""
        transformer = DataTransformer()

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["John", None, "Jane"],
            "value": [100.0, 200.0, None],
        })

        result = transformer._handle_missing_values(df)

        # Critical column not dropped
        assert len(result) == 3
        # String missing values filled
        assert result.iloc[1]["name"] == ""
        # Numeric missing values filled
        assert result.iloc[2]["value"] == 0


@pytest.fixture
def sample_sales_df():
    """Create sample sales DataFrame."""
    return pd.DataFrame({
        "sale_id": ["S001", "S002", "S003"],
        "customer_id": ["C001", "C002", "C001"],
        "product_id": ["P001", "P002", "P001"],
        "quantity": [2, 1, 3],
        "unit_price": [100.0, 200.0, 100.0],
        "total_value": [200.0, 200.0, 300.0],
        "sale_date": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "year": [2024, 2024, 2024],
        "month": [1, 1, 1],
        "quarter": [1, 1, 1],
    })


def test_data_transformer_initialization():
    """Test transformer initialization."""
    transformer = DataTransformer()
    assert transformer is not None
    assert transformer.quality_metrics == {}


def test_generate_quality_report(sample_sales_df):
    """Test quality report generation."""
    transformer = DataTransformer()

    metrics = [
        {
            "source": "csv_sales",
            "original_count": 100,
            "final_count": 95,
            "invalid_records": 5,
            "duplicates_removed": 0,
            "missing_percentage": 2.5,
        }
    ]

    report = transformer.generate_quality_report(metrics, 10.5)

    assert report.total_records_processed == 95
    assert report.duplicates_removed == 0
    assert report.transformation_time_seconds == 10.5
    assert report.status == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
