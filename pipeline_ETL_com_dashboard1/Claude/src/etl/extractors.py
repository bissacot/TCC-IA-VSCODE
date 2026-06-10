"""
Data Extraction Modules
Extract data from multiple sources: CSV, JSON, and REST API
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import csv

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.logger import get_logger
from src.config import config

logger = get_logger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for extractors"""
    
    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from source"""
        pass
    
    @abstractmethod
    def validate_source(self) -> bool:
        """Validate data source availability"""
        pass


class CSVExtractor(BaseExtractor):
    """Extract sales data from CSV file"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        logger.info(f"Initializing CSV Extractor for {file_path}")
    
    def validate_source(self) -> bool:
        """Check if CSV file exists"""
        if not self.file_path.exists():
            logger.error(f"CSV file not found: {self.file_path}")
            return False
        
        try:
            pd.read_csv(self.file_path, nrows=1)
            logger.info(f"CSV file validated: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return False
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from CSV"""
        try:
            if not self.validate_source():
                raise FileNotFoundError(f"CSV file not found: {self.file_path}")
            
            df = pd.read_csv(self.file_path)
            logger.info(f"Extracted {len(df)} records from CSV")
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict(orient="records")
            return records
        
        except Exception as e:
            logger.error(f"CSV extraction failed: {e}")
            raise
    
    def extract_incremental(self, last_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract only new records (if CSV has ID column)"""
        try:
            records = self.extract()
            
            if last_id and "sale_id" in records[0]:
                # Filter records after last_id
                records = [r for r in records if str(r.get("sale_id", "")) > last_id]
                logger.info(f"Extracted {len(records)} incremental records from CSV")
            
            return records
        except Exception as e:
            logger.error(f"Incremental CSV extraction failed: {e}")
            raise


class JSONExtractor(BaseExtractor):
    """Extract customer data from JSON file"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        logger.info(f"Initializing JSON Extractor for {file_path}")
    
    def validate_source(self) -> bool:
        """Check if JSON file exists and is valid"""
        if not self.file_path.exists():
            logger.error(f"JSON file not found: {self.file_path}")
            return False
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                json.load(f)
            logger.info(f"JSON file validated: {self.file_path}")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"JSON validation failed: {e}")
            return False
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from JSON"""
        try:
            if not self.validate_source():
                raise FileNotFoundError(f"JSON file not found: {self.file_path}")
            
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle both list and dict responses
            records = data if isinstance(data, list) else [data]
            logger.info(f"Extracted {len(records)} records from JSON")
            
            return records
        
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            raise


class APIExtractor(BaseExtractor):
    """Extract product data from REST API"""
    
    def __init__(
        self,
        api_url: str,
        timeout: int = config.API_TIMEOUT,
        retries: int = config.API_RETRIES
    ):
        self.api_url = api_url
        self.timeout = timeout
        self.retries = retries
        self.session = self._create_session()
        logger.info(f"Initializing API Extractor for {api_url}")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def validate_source(self) -> bool:
        """Check if API is accessible"""
        try:
            response = self.session.head(
                self.api_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            is_valid = response.status_code < 400
            
            if is_valid:
                logger.info(f"API validated: {self.api_url}")
            else:
                logger.error(f"API validation failed with status {response.status_code}")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"API validation failed: {e}")
            return False
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from API"""
        try:
            if not self.validate_source():
                raise ConnectionError(f"API not accessible: {self.api_url}")
            
            response = self.session.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle both list and dict responses
            records = data if isinstance(data, list) else [data]
            logger.info(f"Extracted {len(records)} records from API")
            
            return records
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API extraction failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API extraction: {e}")
            raise
    
    def close(self) -> None:
        """Close session"""
        self.session.close()


class ExtractorFactory:
    """Factory for creating extractors"""
    
    @staticmethod
    def create_csv_extractor(file_path: Path) -> CSVExtractor:
        """Create CSV extractor"""
        return CSVExtractor(file_path)
    
    @staticmethod
    def create_json_extractor(file_path: Path) -> JSONExtractor:
        """Create JSON extractor"""
        return JSONExtractor(file_path)
    
    @staticmethod
    def create_api_extractor(
        api_url: str,
        timeout: int = config.API_TIMEOUT,
        retries: int = config.API_RETRIES
    ) -> APIExtractor:
        """Create API extractor"""
        return APIExtractor(api_url, timeout, retries)
