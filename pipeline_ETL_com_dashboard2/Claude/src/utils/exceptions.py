"""
Custom exceptions for the ETL and Dashboard application.
"""


class ETLException(Exception):
    """Base exception for ETL operations."""

    pass


class ExtractionException(ETLException):
    """Exception during data extraction."""

    pass


class TransformationException(ETLException):
    """Exception during data transformation."""

    pass


class LoadException(ETLException):
    """Exception during data loading."""

    pass


class ValidationException(ETLException):
    """Exception during data validation."""

    pass


class DatabaseException(ETLException):
    """Exception related to database operations."""

    pass


class APIException(ETLException):
    """Exception related to API calls."""

    pass


class ConfigurationException(ETLException):
    """Exception related to configuration."""

    pass
