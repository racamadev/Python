"""Pure date/time helpers used across the infrastructure, service and
export layers. Deliberately free of any Qt dependency so business logic
never depends on the presentation toolkit (see ``qt_date_helpers`` for
``QDate``/``QDateTime`` conversions used by the views).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.utils.constants import DATE_STORAGE_FORMAT


def now_utc() -> datetime:
    """Return the current UTC timestamp (naive, for MongoDB storage).

    Returns:
        The current UTC ``datetime``.
    """
    return datetime.utcnow()


def format_date(value: Optional[datetime]) -> str:
    """Format a ``datetime`` for display purposes (``YYYY-MM-DD``).

    Args:
        value: A ``datetime`` instance, or ``None``.

    Returns:
        The formatted date string, or an empty string if ``value`` is
        ``None``.
    """
    if value is None:
        return ""
    return value.strftime(DATE_STORAGE_FORMAT)


def format_datetime(value: Optional[datetime]) -> str:
    """Format a ``datetime`` including time for display purposes.

    Args:
        value: A ``datetime`` instance, or ``None``.

    Returns:
        The formatted date-time string, or an empty string if ``value`` is
        ``None``.
    """
    if value is None:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def parse_date(value: Optional[str]) -> Optional[datetime]:
    """Parse a ``YYYY-MM-DD`` string into a ``datetime``.

    Args:
        value: Date string, or ``None``/empty.

    Returns:
        The parsed ``datetime``, or ``None`` if ``value`` is falsy.

    Raises:
        ValueError: If ``value`` is present but not a valid date string.
    """
    if not value:
        return None
    return datetime.strptime(value, DATE_STORAGE_FORMAT)
