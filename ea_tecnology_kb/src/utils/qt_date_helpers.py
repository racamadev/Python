"""Qt-specific date conversion helpers, used only by the presentation layer.

Kept separate from :mod:`src.utils.date_helpers` so the service and
repository layers never import PySide6.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import QDate, QDateTime


def qdate_to_datetime(qdate: QDate) -> Optional[datetime]:
    """Convert a ``QDate`` to a Python ``datetime`` at midnight.

    Args:
        qdate: A Qt date value; ``None``/invalid dates map to ``None``.

    Returns:
        The equivalent ``datetime``, or ``None`` if ``qdate`` is invalid.
    """
    if qdate is None or not qdate.isValid():
        return None
    return datetime(qdate.year(), qdate.month(), qdate.day())


def datetime_to_qdate(value: Optional[datetime]) -> QDate:
    """Convert a Python ``datetime`` to a ``QDate``.

    Args:
        value: A ``datetime`` instance, or ``None``.

    Returns:
        The equivalent ``QDate``; today's date if ``value`` is ``None``.
    """
    if value is None:
        return QDate.currentDate()
    return QDate(value.year, value.month, value.day)


def qdatetime_to_datetime(value: QDateTime) -> Optional[datetime]:
    """Convert a ``QDateTime`` to a Python ``datetime``.

    Args:
        value: A Qt date-time value.

    Returns:
        The equivalent ``datetime``, or ``None`` if invalid.
    """
    if value is None or not value.isValid():
        return None
    return value.toPython()
