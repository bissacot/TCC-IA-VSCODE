"""CSV extractor for sales data."""

import pandas as pd
from pathlib import Path
from typing import Optional
from src.extractors.base import BaseExtractor
from src.utils.logger import logger
from src.utils.exceptions import ExtractionException


class CSVExtractor(BaseExtractor):
    """Extracts data from CSV files."""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        Initialize CSV extractor.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8)
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
    
    def validate_source(self) -> bool:
        """
        Validate that CSV file exists and is readable.
        
        Returns:
            True if file is valid
        """
        if not self.file_path.exists():
            logger.error(f"CSV file not found: {self.file_path}")
            return False
        
        if not self.file_path.is_file():
            logger.error(f"Path is not a file: {self.file_path}")
            return False
        
        logger.info(f"CSV source validated: {self.file_path}")
        return True
    
    def extract(self) -> pd.DataFrame:
        """
        Extract data from CSV file.
        
        Returns:
            DataFrame with CSV data
        
        Raises:
            ExtractionException: If extraction fails
        """
        try:
            if not self.validate_source():
                raise ExtractionException(f"Invalid CSV source: {self.file_path}")
            
            df = pd.read_csv(
                self.file_path,
                encoding=self.encoding,
                dtype_backend='numpy_nullable'
            )
            
            logger.info(f"Successfully extracted {len(df)} rows from {self.file_path}")
            return df
        
        except Exception as e:
            logger.error(f"Error extracting CSV data: {str(e)}")
            raise ExtractionException(f"CSV extraction failed: {str(e)}")
