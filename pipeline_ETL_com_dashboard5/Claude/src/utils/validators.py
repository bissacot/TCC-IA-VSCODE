"""
Data validation utilities.
"""

from typing import Any, Tuple
from datetime import datetime
import re


class Validators:
    """Data validation utilities."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone format."""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)]+', '', phone)
        return len(cleaned) >= 10 and cleaned.isdigit()

    @staticmethod
    def validate_numeric(value: Any, allow_negative: bool = True) -> bool:
        """Validate numeric value."""
        try:
            float(value)
            if not allow_negative and float(value) < 0:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_date_format(date_str: str, format: str = '%Y-%m-%d') -> Tuple[bool, Any]:
        """
        Validate date format.
        Returns: (is_valid, parsed_date)
        """
        try:
            parsed_date = datetime.strptime(str(date_str), format)
            return True, parsed_date
        except (ValueError, TypeError):
            return False, None

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return re.match(uuid_pattern, str(uuid_str).lower()) is not None

    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> bool:
        """Validate integer value."""
        try:
            int_val = int(value)
            if min_value is not None and int_val < min_value:
                return False
            if max_value is not None and int_val > max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_null_or_empty(value: Any) -> bool:
        """Check if value is null or empty."""
        if value is None:
            return True
        if isinstance(value, str):
            return len(value.strip()) == 0
        if isinstance(value, (list, dict)):
            return len(value) == 0
        return False

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            return str(value)
        return value.strip()
