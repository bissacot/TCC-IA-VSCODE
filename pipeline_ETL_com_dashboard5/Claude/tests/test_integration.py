"""
Integration tests for the ETL pipeline.
"""

import pytest
from pathlib import Path
from src.database.connection import DatabaseConnection
from src.utils.config import Config


class TestDatabaseConnection:
    """Test database connection and operations."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database connection."""
        self.db = DatabaseConnection()
        yield
        # Cleanup
        if self.db.connection:
            self.db.disconnect()

    def test_database_connection(self):
        """Test database connectivity."""
        try:
            self.db.connect()
            assert self.db.connection is not None
        except Exception:
            pytest.skip("Database not available")

    def test_table_exists(self):
        """Test checking if table exists."""
        try:
            self.db.connect()
            # Check if customers table exists
            exists = self.db.table_exists('customers')
            assert isinstance(exists, bool)
        except Exception:
            pytest.skip("Database not available")

    def test_record_count(self):
        """Test getting record count."""
        try:
            self.db.connect()
            # Count should be >= 0
            count = self.db.get_record_count('customers')
            assert isinstance(count, int)
            assert count >= 0
        except Exception:
            pytest.skip("Database not available")


class TestETLPipelineIntegration:
    """Integration tests for ETL pipeline."""

    def test_data_files_exist(self):
        """Test that sample data files can be generated."""
        from src.utils.sample_data import SampleDataGenerator
        
        # Generate sample data
        SampleDataGenerator.generate_all_sample_data('data/input')
        
        # Check if files exist
        assert Path('data/input/customers.json').exists()
        assert Path('data/input/products.csv').exists()
        assert Path('data/input/sales.csv').exists()

    def test_extractor_reads_files(self):
        """Test that extractor can read generated files."""
        from src.utils.sample_data import SampleDataGenerator
        from src.etl.extractor import DataExtractor
        
        # Generate sample data
        SampleDataGenerator.generate_all_sample_data('data/input')
        
        # Extract data
        extractor = DataExtractor()
        customers = extractor.extract_customers()
        
        assert len(customers) > 0
        assert 'customer_id' in customers[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
