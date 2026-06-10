from __future__ import annotations


class ETLException(Exception):
    """Base exception for ETL processing."""


class DataValidationException(ETLException):
    """Raised when source data fails validation."""


class ExtractionException(ETLException):
    """Raised during extraction failures."""


class LoadException(ETLException):
    """Raised during load failures."""
