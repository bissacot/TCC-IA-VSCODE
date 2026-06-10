"""REST API extractor for product data."""

import pandas as pd
from typing import Dict, Any, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.extractors.base import BaseExtractor
from src.utils.logger import logger
from src.utils.exceptions import ExtractionException, APIException
from src.utils.config import APIConfig


class APIExtractor(BaseExtractor):
    """Extracts data from REST APIs."""
    
    def __init__(
        self,
        api_config: APIConfig,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize API extractor.
        
        Args:
            api_config: API configuration
            endpoint: API endpoint path
            params: Query parameters
            headers: Custom headers
        """
        self.api_config = api_config
        self.endpoint = endpoint
        self.params = params or {}
        self.headers = headers or {'Content-Type': 'application/json'}
        self.url = f"{api_config.base_url}/{endpoint.lstrip('/')}"
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.api_config.retry_attempts,
            backoff_factor=self.api_config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=['GET', 'POST']
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def validate_source(self) -> bool:
        """
        Validate API connectivity.
        
        Returns:
            True if API is accessible
        """
        try:
            response = self.session.get(
                self.url,
                params=self.params,
                headers=self.headers,
                timeout=self.api_config.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"API source validated: {self.url}")
                return True
            else:
                logger.error(f"API returned status {response.status_code}: {self.url}")
                return False
        
        except requests.RequestException as e:
            logger.error(f"API validation failed: {str(e)}")
            return False
    
    def extract(self) -> pd.DataFrame:
        """
        Extract data from REST API.
        
        Returns:
            DataFrame with API data
        
        Raises:
            ExtractionException: If extraction fails
        """
        try:
            if not self.validate_source():
                raise APIException(f"Invalid API source: {self.url}")
            
            response = self.session.get(
                self.url,
                params=self.params,
                headers=self.headers,
                timeout=self.api_config.timeout
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Handle common API response structures
            if isinstance(data, dict):
                if 'data' in data:
                    data = data['data']
                elif 'results' in data:
                    data = data['results']
                else:
                    data = [data]
            
            if not isinstance(data, list):
                raise APIException("API response must be a list or contain 'data'/'results' key")
            
            df = pd.DataFrame(data)
            logger.info(f"Successfully extracted {len(df)} rows from {self.url}")
            return df
        
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ExtractionException(f"API extraction failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting API data: {str(e)}")
            raise ExtractionException(f"API extraction failed: {str(e)}")
    
    def close(self) -> None:
        """Close the requests session."""
        self.session.close()
