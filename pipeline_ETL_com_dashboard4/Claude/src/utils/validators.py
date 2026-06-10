"""
Data validation utilities for the ETL pipeline.

Provides validators for data types, formats, and business rules.
"""

from typing import Any, List, Dict, Optional
from datetime import datetime
import re


class DataValidator:
    """Validates data according to specified rules."""

    @staticmethod
    def validate_email(email: Any) -> bool:
        """
        Validate email address format.

        Args:
            email: Email string to validate

        Returns:
            True if valid email format, False otherwise
        """
        if not isinstance(email, str):
            return False

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_date(date_str: Any, date_format: str = "%Y-%m-%d") -> bool:
        """
        Validate date string against specified format.

        Args:
            date_str: Date string to validate
            date_format: Expected date format

        Returns:
            True if valid date, False otherwise
        """
        if not isinstance(date_str, str):
            return False

        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_numeric(value: Any) -> bool:
        """
        Validate numeric value.

        Args:
            value: Value to validate

        Returns:
            True if valid numeric value, False otherwise
        """
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def validate_positive_numeric(value: Any) -> bool:
        """
        Validate positive numeric value.

        Args:
            value: Value to validate

        Returns:
            True if valid positive numeric value, False otherwise
        """
        try:
            num_value = float(value)
            return num_value > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def validate_currency(value: Any) -> bool:
        """
        Validate currency value (positive numeric).

        Args:
            value: Value to validate

        Returns:
            True if valid currency value, False otherwise
        """
        return DataValidator.validate_positive_numeric(value)

    @staticmethod
    def validate_phone(phone: Any) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone string to validate

        Returns:
            True if valid phone format, False otherwise
        """
        if not isinstance(phone, str):
            return False

        # Remove common separators
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)

        # Check if only digits and + sign
        return bool(re.match(r"^\+?[\d]{8,15}$", cleaned))

    @staticmethod
    def validate_required_fields(
        record: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """
        Validate that required fields are present and not None.

        Args:
            record: Dictionary to validate
            required_fields: List of required field names

        Returns:
            True if all required fields are present and not None
        """
        return all(
            field in record and record[field] is not None
            for field in required_fields
        )

    @staticmethod
    def sanitize_string(value: Any) -> Optional[str]:
        """
        Sanitize string value by stripping whitespace and handling None.

        Args:
            value: Value to sanitize

        Returns:
            Sanitized string or None if input is None/empty
        """
        if value is None:
            return None

        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None

        return str(value).strip()


class DataTypeValidator:
    """Validates and converts data types."""

    @staticmethod
    def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
        """
        Convert value to float.

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Float value or default
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
        """
        Convert value to integer.

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Integer value or default
        """
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def to_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
        """
        Convert value to boolean.

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Boolean value or default
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")

        if isinstance(value, (int, float)):
            return value != 0

        return default
