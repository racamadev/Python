"""Centralized exception hierarchy for EA Technology KB."""

from src.exceptions.app_exceptions import (
    AppException,
    ValidationError,
    DuplicateRecordError,
    RecordNotFoundError,
    DatabaseConnectionError,
    RepositoryError,
    ServiceError,
)

__all__ = [
    "AppException",
    "ValidationError",
    "DuplicateRecordError",
    "RecordNotFoundError",
    "DatabaseConnectionError",
    "RepositoryError",
    "ServiceError",
]
