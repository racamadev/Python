"""Application-wide exception hierarchy.

All custom exceptions raised across the layers of EA Technology KB derive
from :class:`AppException`, which allows the presentation layer to catch a
single base type and still branch on more specific error semantics when
useful (e.g. showing a different dialog for a validation error than for a
database connection error).
"""

from __future__ import annotations


class AppException(Exception):
    """Base class for all application-specific exceptions.

    Args:
        message: Human-readable, user-facing description of the error.
        details: Optional technical details useful for logging/debugging.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.details:
            return f"{self.message} ({self.details})"
        return self.message


class ValidationError(AppException):
    """Raised when input data fails business or format validation."""


class DuplicateRecordError(AppException):
    """Raised when attempting to persist a record that violates uniqueness."""


class RecordNotFoundError(AppException):
    """Raised when a requested record does not exist in the data store."""


class DatabaseConnectionError(AppException):
    """Raised when the application cannot establish/maintain a MongoDB connection."""


class RepositoryError(AppException):
    """Raised for unexpected data-access failures within the repository layer."""


class ServiceError(AppException):
    """Raised for unexpected failures within the business/service layer."""
