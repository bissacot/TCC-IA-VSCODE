"""Custom exceptions for the ETL pipeline."""


class ETLException(Exception):
    """Base exception for ETL pipeline."""
    pass


class ExtractionException(ETLException):
    """Raised when data extraction fails."""
    pass


class TransformationException(ETLException):
    """Raised when data transformation fails."""
    pass


class LoadingException(ETLException):
    """Raised when data loading fails."""
    pass


class ValidationException(ETLException):
    """Raised when data validation fails."""
    pass


class DatabaseException(ETLException):
    """Raised when database operations fail."""
    pass


class APIException(ETLException):
    """Raised when API calls fail."""
    pass


class ConfigException(ETLException):
    """Raised when configuration is invalid."""
    pass
