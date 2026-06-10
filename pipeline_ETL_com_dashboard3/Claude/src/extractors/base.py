"""Base extractor interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class BaseExtractor(ABC):
    """Base class for data extractors."""
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Extract data and return as DataFrame.
        
        Returns:
            DataFrame with extracted data
        """
        pass
    
    @abstractmethod
    def validate_source(self) -> bool:
        """
        Validate that the data source is accessible.
        
        Returns:
            True if source is valid, False otherwise
        """
        pass
