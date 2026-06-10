"""
Data extraction from multiple sources: CSV, JSON, and REST API.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.logging_config import setup_logging
from src.utils.exceptions import ExtractionException

logger = setup_logging(__name__)


class DataExtractor(ABC):
    """Abstract base class for data extractors."""

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data and return as DataFrame."""
        pass


class CSVExtractor(DataExtractor):
    """Extract sales data from CSV file."""

    def __init__(self, file_path: str, **kwargs: Any) -> None:
        """
        Initialize CSV extractor.

        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
        """
        self.file_path = Path(file_path)
        self.kwargs = kwargs
        logger.info(f"Initialized CSV extractor for {self.file_path}")

    def extract(self) -> pd.DataFrame:
        """
        Extract data from CSV file.

        Returns:
            DataFrame with extracted data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"CSV file not found: {self.file_path}")

            logger.info(f"Extracting data from CSV: {self.file_path}")
            df = pd.read_csv(self.file_path, **self.kwargs)

            logger.info(
                f"Successfully extracted {len(df)} rows from CSV. "
                f"Columns: {list(df.columns)}"
            )
            return df

        except Exception as e:
            logger.error(f"CSV extraction failed: {str(e)}")
            raise ExtractionException(f"CSV extraction failed: {str(e)}")


class JSONExtractor(DataExtractor):
    """Extract customer data from JSON file."""

    def __init__(self, file_path: str, json_path: str = None) -> None:
        """
        Initialize JSON extractor.

        Args:
            file_path: Path to JSON file
            json_path: JSONPath to extract nested data (e.g., 'data.customers')
        """
        self.file_path = Path(file_path)
        self.json_path = json_path
        logger.info(f"Initialized JSON extractor for {self.file_path}")

    def extract(self) -> pd.DataFrame:
        """
        Extract data from JSON file.

        Returns:
            DataFrame with extracted data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"JSON file not found: {self.file_path}")

            logger.info(f"Extracting data from JSON: {self.file_path}")

            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Navigate to specified path if provided
            if self.json_path:
                for key in self.json_path.split("."):
                    data = data.get(key, [])

            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("JSON data must be a list or dict")

            logger.info(f"Successfully extracted {len(df)} rows from JSON")
            return df

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}")
            raise ExtractionException(f"JSON extraction failed: {str(e)}")


class APIExtractor(DataExtractor):
    """Extract product data from REST API."""

    def __init__(
        self,
        base_url: str,
        endpoint: str,
        api_key: str = None,
        timeout: int = 30,
        headers: Dict[str, str] = None,
    ) -> None:
        """
        Initialize API extractor.

        Args:
            base_url: Base URL of API
            endpoint: API endpoint path
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            headers: Optional additional headers
        """
        self.base_url = base_url
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout
        self.headers = headers or {}
        
        # Setup retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"Initialized API extractor for {base_url}{endpoint}")

    def extract(self) -> pd.DataFrame:
        """
        Extract data from REST API.

        Returns:
            DataFrame with extracted data

        Raises:
            ExtractionException: If extraction fails
        """
        try:
            url = f"{self.base_url}{self.endpoint}"
            
            # Prepare headers
            headers = self.headers.copy()
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["X-API-Key"] = self.api_key

            logger.info(f"Fetching data from API: {url}")

            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            # Handle different response formats
            if isinstance(data, dict) and "data" in data:
                data = data["data"]
            elif isinstance(data, dict) and "results" in data:
                data = data["results"]

            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("API response must be a list or dict")

            logger.info(f"Successfully extracted {len(df)} rows from API")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ExtractionException(f"API extraction failed: {str(e)}")
        except Exception as e:
            logger.error(f"API extraction failed: {str(e)}")
            raise ExtractionException(f"API extraction failed: {str(e)}")

    def close(self) -> None:
        """Close session."""
        self.session.close()


class MultiSourceExtractor:
    """Orchestrate extraction from multiple sources."""

    def __init__(self) -> None:
        """Initialize multi-source extractor."""
        self.extractors: Dict[str, DataExtractor] = {}
        logger.info("Initialized multi-source extractor")

    def register_extractor(self, name: str, extractor: DataExtractor) -> None:
        """
        Register an extractor.

        Args:
            name: Name/identifier for the extractor
            extractor: DataExtractor instance
        """
        self.extractors[name] = extractor
        logger.info(f"Registered extractor: {name}")

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extract data from all registered sources.

        Returns:
            Dictionary with source names as keys and DataFrames as values
        """
        results = {}
        errors = {}

        logger.info(f"Starting extraction from {len(self.extractors)} sources")

        for name, extractor in self.extractors.items():
            try:
                logger.info(f"Extracting from source: {name}")
                results[name] = extractor.extract()
            except Exception as e:
                logger.error(f"Failed to extract from {name}: {str(e)}")
                errors[name] = str(e)

        if errors:
            logger.warning(f"Extraction errors from {len(errors)} sources: {errors}")

        logger.info(f"Extraction complete. Successfully extracted from {len(results)} sources")
        return results
