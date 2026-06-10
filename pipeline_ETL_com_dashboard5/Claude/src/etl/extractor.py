"""
Data extraction from various sources.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config import Config


logger = get_logger()


class CSVExtractor:
    """Extract data from CSV files."""

    @staticmethod
    def extract(file_path: str, encoding: str = 'utf-8', **kwargs) -> List[Dict[str, Any]]:
        """
        Extract data from CSV file.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            **kwargs: Additional arguments for csv.DictReader
            
        Returns:
            List of dictionaries representing CSV rows
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"CSV file not found: {file_path}")
                return []

            data = []
            with open(path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, **kwargs)
                data = list(reader)

            logger.info(f"Successfully extracted {len(data)} records from CSV: {file_path}")
            return data

        except Exception as e:
            logger.error(f"Error extracting CSV from {file_path}: {str(e)}")
            raise


class JSONExtractor:
    """Extract data from JSON files."""

    @staticmethod
    def extract(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Extract data from JSON file.
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding
            
        Returns:
            List of dictionaries from JSON
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"JSON file not found: {file_path}")
                return []

            with open(path, 'r', encoding=encoding) as f:
                data = json.load(f)

            # Ensure data is a list
            if isinstance(data, dict):
                # Try to find a list in the dictionary
                for value in data.values():
                    if isinstance(value, list):
                        data = value
                        break
            
            if not isinstance(data, list):
                data = [data] if data else []

            logger.info(f"Successfully extracted {len(data)} records from JSON: {file_path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error extracting JSON from {file_path}: {str(e)}")
            raise


class APIExtractor:
    """Extract data from REST API."""

    @staticmethod
    def extract(
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[tuple] = None,
        pagination_key: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract data from REST API.
        
        Args:
            endpoint: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            headers: Request headers
            auth: Authentication tuple (username, password)
            pagination_key: Key for paginated data
            
        Returns:
            List of dictionaries from API response
        """
        try:
            all_data = []
            url = endpoint if endpoint.startswith('http') else f"{Config.API_BASE_URL}{endpoint}"
            
            headers = headers or {}
            headers.setdefault('Content-Type', 'application/json')
            
            retry_count = 0
            max_retries = Config.API_RETRY_ATTEMPTS
            page = 1
            
            while retry_count < max_retries:
                try:
                    # Add pagination if needed
                    request_params = (params or {}).copy()
                    if pagination_key:
                        request_params['page'] = page
                    
                    response = requests.request(
                        method=method,
                        url=url,
                        params=request_params,
                        headers=headers,
                        auth=auth,
                        timeout=Config.API_TIMEOUT
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Handle paginated responses
                    if pagination_key and isinstance(data, dict):
                        page_data = data.get(pagination_key, [])
                        if not page_data:
                            break
                        all_data.extend(page_data)
                        page += 1
                    else:
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                        break
                    
                    retry_count = 0  # Reset retry counter on success

                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"API request failed (attempt {retry_count}/{max_retries}): {str(e)}")
                    else:
                        logger.error(f"API request failed after {max_retries} attempts: {str(e)}")
                        raise

            logger.info(f"Successfully extracted {len(all_data)} records from API: {endpoint}")
            return all_data

        except Exception as e:
            logger.error(f"Error extracting data from API {endpoint}: {str(e)}")
            raise


class DataExtractor:
    """Main data extraction orchestrator."""

    def __init__(self):
        self.logger = get_logger()

    def extract_sales(self) -> List[Dict[str, Any]]:
        """Extract sales data from CSV."""
        return CSVExtractor.extract(Config.CSV_SALES_PATH)

    def extract_customers(self) -> List[Dict[str, Any]]:
        """Extract customers data from JSON."""
        return JSONExtractor.extract(Config.JSON_CUSTOMERS_PATH)

    def extract_products(self) -> List[Dict[str, Any]]:
        """Extract products data from API."""
        return APIExtractor.extract(
            endpoint=Config.API_PRODUCTS_ENDPOINT,
            pagination_key='results'
        )

    def extract_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data from all sources."""
        self.logger.info("Starting data extraction from all sources...")
        
        results = {
            'sales': [],
            'customers': [],
            'products': [],
            'errors': []
        }

        # Extract sales
        try:
            results['sales'] = self.extract_sales()
        except Exception as e:
            self.logger.error(f"Failed to extract sales: {str(e)}")
            results['errors'].append({'source': 'sales', 'error': str(e)})

        # Extract customers
        try:
            results['customers'] = self.extract_customers()
        except Exception as e:
            self.logger.error(f"Failed to extract customers: {str(e)}")
            results['errors'].append({'source': 'customers', 'error': str(e)})

        # Extract products
        try:
            results['products'] = self.extract_products()
        except Exception as e:
            self.logger.error(f"Failed to extract products: {str(e)}")
            results['errors'].append({'source': 'products', 'error': str(e)})

        self.logger.info(
            f"Data extraction completed - "
            f"Sales: {len(results['sales'])}, "
            f"Customers: {len(results['customers'])}, "
            f"Products: {len(results['products'])}"
        )

        return results
