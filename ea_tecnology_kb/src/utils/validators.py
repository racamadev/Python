"""Input validation and sanitization helpers.

These functions are shared by the service layer (business rule
enforcement) and the presentation layer (real-time form feedback), so
validation logic is defined exactly once (DRY).
"""

from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urlparse

from bson import ObjectId
from bson.errors import InvalidId

from src.exceptions import ValidationError

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sanitize_string(value: Optional[str]) -> str:
    """Trim whitespace, strip control characters and HTML-escape a string.

    Args:
        value: Raw input string, possibly ``None``.

    Returns:
        A sanitized string safe to persist and render; empty string if
        ``value`` was ``None``.
    """
    if value is None:
        return ""
    cleaned = _CONTROL_CHARS_RE.sub("", value).strip()
    return html.escape(cleaned, quote=False)


def validate_required_string(value: Optional[str], field_name: str) -> str:
    """Ensure a string field is present and non-empty after sanitization.

    Args:
        value: Raw field value.
        field_name: Human-readable field name used in error messages.

    Returns:
        The sanitized, validated string.

    Raises:
        ValidationError: If the sanitized value is empty.
    """
    sanitized = sanitize_string(value)
    if not sanitized:
        raise ValidationError(f"'{field_name}' es obligatorio.")
    return sanitized


def validate_choice(value: Optional[str], field_name: str, choices: Iterable[str]) -> str:
    """Ensure a value is one of a fixed set of allowed choices.

    Args:
        value: Raw field value.
        field_name: Human-readable field name used in error messages.
        choices: Allowed values (case-sensitive).

    Returns:
        The sanitized, validated value.

    Raises:
        ValidationError: If the value is empty or not among ``choices``.
    """
    sanitized = validate_required_string(value, field_name)
    choices_list = list(choices)
    if sanitized not in choices_list:
        allowed = ", ".join(choices_list)
        raise ValidationError(f"'{field_name}' debe ser uno de: {allowed}.")
    return sanitized


def validate_optional_string(value: Optional[str]) -> str:
    """Sanitize an optional free-text field, allowing empty strings.

    Args:
        value: Raw field value.

    Returns:
        The sanitized string (possibly empty).
    """
    return sanitize_string(value)


def validate_url(value: Optional[str], field_name: str = "link_url") -> str:
    """Validate that a string is a well-formed HTTP(S) URL.

    Args:
        value: Raw URL string.
        field_name: Human-readable field name used in error messages.

    Returns:
        The sanitized URL string.

    Raises:
        ValidationError: If the value is empty or not a valid HTTP(S) URL.
    """
    sanitized = validate_required_string(value, field_name)
    parsed = urlparse(sanitized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(
            f"'{field_name}' debe ser una URL válida (http:// o https://)."
        )
    return sanitized


def is_valid_url(value: Optional[str]) -> bool:
    """Non-raising URL validity check, useful before opening a browser.

    Args:
        value: URL string to check.

    Returns:
        ``True`` if the string is a well-formed HTTP(S) URL.
    """
    if not value:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_object_id(value: Optional[str], field_name: str = "id") -> ObjectId:
    """Validate and convert a string into a MongoDB :class:`ObjectId`.

    Args:
        value: Raw id string.
        field_name: Human-readable field name used in error messages.

    Returns:
        The corresponding :class:`~bson.objectid.ObjectId`.

    Raises:
        ValidationError: If the value is missing or not a valid ObjectId.
    """
    if not value:
        raise ValidationError(f"'{field_name}' es obligatorio.")
    try:
        return ObjectId(value)
    except (InvalidId, TypeError) as exc:
        raise ValidationError(f"'{field_name}' no es un identificador válido.") from exc


def validate_optional_date(value: Optional[datetime], field_name: str) -> Optional[datetime]:
    """Validate an optional datetime field.

    Args:
        value: A ``datetime`` instance or ``None``.
        field_name: Human-readable field name used in error messages.

    Returns:
        The same ``datetime`` instance, or ``None``.

    Raises:
        ValidationError: If ``value`` is provided but not a ``datetime``.
    """
    if value is None:
        return None
    if not isinstance(value, datetime):
        raise ValidationError(f"'{field_name}' debe ser una fecha válida.")
    return value


def validate_required_date(value: Optional[datetime], field_name: str) -> datetime:
    """Validate a required datetime field.

    Args:
        value: A ``datetime`` instance.
        field_name: Human-readable field name used in error messages.

    Returns:
        The validated ``datetime`` instance.

    Raises:
        ValidationError: If ``value`` is ``None`` or not a ``datetime``.
    """
    if value is None or not isinstance(value, datetime):
        raise ValidationError(f"'{field_name}' es obligatorio y debe ser una fecha válida.")
    return value
