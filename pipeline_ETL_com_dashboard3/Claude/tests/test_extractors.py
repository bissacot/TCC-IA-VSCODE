"""Unit tests for extractors."""

import unittest
from pathlib import Path
import pandas as pd
import json
import tempfile
from src.extractors import CSVExtractor, JSONExtractor
from src.utils.exceptions import ExtractionException


class TestCSVExtractor(unittest.TestCase):
    """Test cases for CSV extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "test.csv"
        
        # Create test CSV
        test_data = {
            'id': [1, 2, 3],
            'value': [100, 200, 300],
            'name': ['A', 'B', 'C']
        }
        pd.DataFrame(test_data).to_csv(self.csv_path, index=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_extract_valid_csv(self):
        """Test extracting valid CSV file."""
        extractor = CSVExtractor(str(self.csv_path))
        df = extractor.extract()
        
        self.assertEqual(len(df), 3)
        self.assertIn('id', df.columns)
        self.assertEqual(df['id'].tolist(), [1, 2, 3])
    
    def test_validate_source_valid_file(self):
        """Test validation with valid file."""
        extractor = CSVExtractor(str(self.csv_path))
        self.assertTrue(extractor.validate_source())
    
    def test_validate_source_missing_file(self):
        """Test validation with missing file."""
        extractor = CSVExtractor("/nonexistent/path/file.csv")
        self.assertFalse(extractor.validate_source())
    
    def test_extract_missing_file_raises_exception(self):
        """Test extraction with missing file raises exception."""
        extractor = CSVExtractor("/nonexistent/path/file.csv")
        with self.assertRaises(ExtractionException):
            extractor.extract()


class TestJSONExtractor(unittest.TestCase):
    """Test cases for JSON extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.json_path = Path(self.temp_dir.name) / "test.json"
        
        # Create test JSON
        test_data = [
            {'id': 1, 'name': 'A'},
            {'id': 2, 'name': 'B'}
        ]
        with open(self.json_path, 'w') as f:
            json.dump(test_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_extract_valid_json_list(self):
        """Test extracting valid JSON list."""
        extractor = JSONExtractor(str(self.json_path))
        df = extractor.extract()
        
        self.assertEqual(len(df), 2)
        self.assertIn('id', df.columns)
    
    def test_validate_source_valid_file(self):
        """Test validation with valid file."""
        extractor = JSONExtractor(str(self.json_path))
        self.assertTrue(extractor.validate_source())


if __name__ == '__main__':
    unittest.main()
