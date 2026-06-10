"""
Data extraction module for the ETL pipeline.

Handles extraction from CSV, JSON, and REST API sources.
"""

import csv
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

import requests

from src.utils import LoggerConfig, ExtractionException
from config.settings import (
    SALES_CSV_PATH,
    CUSTOMERS_JSON_PATH,
    PRODUCTS_API_ENDPOINT,
    API_TIMEOUT,
)


logger = LoggerConfig.get_logger(__name__)


class DataExtractor(ABC):
    """Abstract base class for data extractors."""

    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from source.

        Returns:
            List of dictionaries representing extracted data
        """
        pass


class CSVExtractor(DataExtractor):
    """Extracts data from CSV files."""

    def __init__(self, file_path: Path) -> None:
        """
        Initialize CSV extractor.

        Args:
            file_path: Path to CSV file
        """
        self.file_path = file_path

    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from CSV file.

        Returns:
            List of dictionaries with CSV data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            logger.info(f"Starting extraction from CSV: {self.file_path}")

            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")

            data: List[Dict[str, Any]] = []

            with open(self.file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                if reader.fieldnames is None:
                    raise ValueError("CSV file is empty or invalid")

                for row_num, row in enumerate(reader, start=2):
                    data.append(dict(row))

            logger.info(f"Successfully extracted {len(data)} records from CSV")
            return data

        except FileNotFoundError as e:
            logger.error(f"CSV file not found: {e}")
            raise ExtractionException(f"CSV file not found: {e}")
        except Exception as e:
            logger.error(f"Failed to extract from CSV: {e}")
            raise ExtractionException(f"CSV extraction failed: {e}")


class JSONExtractor(DataExtractor):
    """Extracts data from JSON files."""

    def __init__(self, file_path: Path) -> None:
        """
        Initialize JSON extractor.

        Args:
            file_path: Path to JSON file
        """
        self.file_path = file_path

    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from JSON file.

        Returns:
            List of dictionaries with JSON data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            logger.info(f"Starting extraction from JSON: {self.file_path}")

            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")

            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)

            # Handle both list and object responses
            if isinstance(raw_data, list):
                data = raw_data
            elif isinstance(raw_data, dict) and "data" in raw_data:
                data = raw_data["data"]
            else:
                data = [raw_data]

            if not isinstance(data, list):
                raise ValueError("JSON data is not a list")

            logger.info(f"Successfully extracted {len(data)} records from JSON")
            return data

        except FileNotFoundError as e:
            logger.error(f"JSON file not found: {e}")
            raise ExtractionException(f"JSON file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise ExtractionException(f"JSON parsing failed: {e}")
        except Exception as e:
            logger.error(f"Failed to extract from JSON: {e}")
            raise ExtractionException(f"JSON extraction failed: {e}")


class APIExtractor(DataExtractor):
    """Extracts data from REST APIs."""

    def __init__(
        self,
        endpoint: str,
        timeout: int = API_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize API extractor.

        Args:
            endpoint: API endpoint URL
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.headers = headers or {"Content-Type": "application/json"}

    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from REST API.

        Returns:
            List of dictionaries with API response data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            logger.info(f"Starting extraction from API: {self.endpoint}")

            response = requests.get(
                self.endpoint,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            json_data = response.json()

            # Handle both list and object responses
            if isinstance(json_data, list):
                data = json_data
            elif isinstance(json_data, dict) and "data" in json_data:
                data = json_data["data"]
            else:
                data = [json_data]

            if not isinstance(data, list):
                raise ValueError("API response is not a list")

            logger.info(f"Successfully extracted {len(data)} records from API")
            return data

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise ExtractionException(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise ExtractionException(f"API response parsing failed: {e}")
        except Exception as e:
            logger.error(f"Failed to extract from API: {e}")
            raise ExtractionException(f"API extraction failed: {e}")


class ExtractionOrchestrator:
    """Orchestrates data extraction from multiple sources."""

    def __init__(self) -> None:
        """Initialize extraction orchestrator."""
        self.sales_data: List[Dict[str, Any]] = []
        self.customers_data: List[Dict[str, Any]] = []
        self.products_data: List[Dict[str, Any]] = []

    def extract_sales(self) -> List[Dict[str, Any]]:
        """
        Extract sales data from CSV.

        Returns:
            List of sales records
        """
        try:
            extractor = CSVExtractor(SALES_CSV_PATH)
            self.sales_data = extractor.extract()
            return self.sales_data
        except ExtractionException:
            raise

    def extract_customers(self) -> List[Dict[str, Any]]:
        """
        Extract customer data from JSON.

        Returns:
            List of customer records
        """
        try:
            extractor = JSONExtractor(CUSTOMERS_JSON_PATH)
            self.customers_data = extractor.extract()
            return self.customers_data
        except ExtractionException:
            raise

    def extract_products(self) -> List[Dict[str, Any]]:
        """
        Extract product data from API.

        Returns:
            List of product records
        """
        try:
            extractor = APIExtractor(PRODUCTS_API_ENDPOINT)
            self.products_data = extractor.extract()
            return self.products_data
        except ExtractionException:
            raise

    def extract_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract data from all sources.

        Returns:
            Dictionary with extracted data from all sources
        """
        logger.info("Starting extraction from all sources")

        try:
            self.extract_sales()
        except ExtractionException as e:
            logger.warning(f"Sales extraction failed: {e}")

        try:
            self.extract_customers()
        except ExtractionException as e:
            logger.warning(f"Customers extraction failed: {e}")

        try:
            self.extract_products()
        except ExtractionException as e:
            logger.warning(f"Products extraction failed: {e}")

        logger.info("Extraction from all sources completed")

        return {
            "sales": self.sales_data,
            "customers": self.customers_data,
            "products": self.products_data,
        }
