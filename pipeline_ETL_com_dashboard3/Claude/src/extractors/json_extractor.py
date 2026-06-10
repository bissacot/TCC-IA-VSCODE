"""JSON extractor for customer data."""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from src.extractors.base import BaseExtractor
from src.utils.logger import logger
from src.utils.exceptions import ExtractionException


class JSONExtractor(BaseExtractor):
    """Extracts data from JSON files."""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        Initialize JSON extractor.
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding (default: utf-8)
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
    
    def validate_source(self) -> bool:
        """
        Validate that JSON file exists and is readable.
        
        Returns:
            True if file is valid
        """
        if not self.file_path.exists():
            logger.error(f"JSON file not found: {self.file_path}")
            return False
        
        if not self.file_path.is_file():
            logger.error(f"Path is not a file: {self.file_path}")
            return False
        
        logger.info(f"JSON source validated: {self.file_path}")
        return True
    
    def extract(self) -> pd.DataFrame:
        """
        Extract data from JSON file.
        
        Returns:
            DataFrame with JSON data
        
        Raises:
            ExtractionException: If extraction fails
        """
        try:
            if not self.validate_source():
                raise ExtractionException(f"Invalid JSON source: {self.file_path}")
            
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            # Handle both list and dict structures
            if isinstance(data, dict):
                if 'data' in data:
                    data = data['data']
                else:
                    data = [data]
            
            if not isinstance(data, list):
                raise ExtractionException("JSON data must be a list or contain a 'data' key with list")
            
            df = pd.DataFrame(data)
            logger.info(f"Successfully extracted {len(df)} rows from {self.file_path}")
            return df
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            raise ExtractionException(f"JSON parsing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting JSON data: {str(e)}")
            raise ExtractionException(f"JSON extraction failed: {str(e)}")
