"""
Custom exceptions for the ETL application.

Provides domain-specific exception classes for better error handling.
"""


class ETLException(Exception):
    """Base exception for all ETL-related errors."""

    pass


class ExtractionException(ETLException):
    """Exception raised during data extraction phase."""

    pass


class TransformationException(ETLException):
    """Exception raised during data transformation phase."""

    pass


class LoadingException(ETLException):
    """Exception raised during data loading phase."""

    pass


class ValidationException(ETLException):
    """Exception raised during data validation."""

    pass


class DatabaseException(ETLException):
    """Exception raised during database operations."""

    pass


class APIException(ETLException):
    """Exception raised during API calls."""

    pass


class ConfigurationException(ETLException):
    """Exception raised due to configuration errors."""

    pass


class FileException(ETLException):
    """Exception raised during file operations."""

    pass
