"""
Unit tests for data extraction module.

Tests CSV, JSON, and API extractors.
"""

import pytest
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.etl.extractor import CSVExtractor, JSONExtractor
from src.utils import ExtractionException


class TestCSVExtractor:
    """Tests for CSV extraction."""

    def test_extract_valid_csv(self) -> None:
        """Test extraction from valid CSV file."""
        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("id,name,value\n")
            f.write("1,John,100\n")
            f.write("2,Jane,200\n")
            temp_path = Path(f.name)

        try:
            extractor = CSVExtractor(temp_path)
            data = extractor.extract()

            assert len(data) == 2
            assert data[0]["id"] == "1"
            assert data[0]["name"] == "John"
        finally:
            temp_path.unlink()

    def test_extract_missing_file(self) -> None:
        """Test extraction from missing file."""
        extractor = CSVExtractor(Path("/nonexistent/file.csv"))

        with pytest.raises(ExtractionException):
            extractor.extract()


class TestJSONExtractor:
    """Tests for JSON extraction."""

    def test_extract_valid_json_list(self) -> None:
        """Test extraction from valid JSON file (list format)."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}], f)
            temp_path = Path(f.name)

        try:
            extractor = JSONExtractor(temp_path)
            data = extractor.extract()

            assert len(data) == 2
            assert data[0]["name"] == "John"
        finally:
            temp_path.unlink()

    def test_extract_valid_json_object(self) -> None:
        """Test extraction from valid JSON file (object with data key)."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {"data": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]}, f
            )
            temp_path = Path(f.name)

        try:
            extractor = JSONExtractor(temp_path)
            data = extractor.extract()

            assert len(data) == 2
            assert data[0]["name"] == "John"
        finally:
            temp_path.unlink()

    def test_extract_invalid_json(self) -> None:
        """Test extraction from invalid JSON file."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = Path(f.name)

        try:
            extractor = JSONExtractor(temp_path)

            with pytest.raises(ExtractionException):
                extractor.extract()
        finally:
            temp_path.unlink()
