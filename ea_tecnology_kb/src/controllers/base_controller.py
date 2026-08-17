"""Shared controller infrastructure: centralized exception handling.

Views should never catch :class:`~src.exceptions.AppException` themselves;
controllers translate every business/data-access failure into the
``error_occurred`` Qt signal so a single dialog/status-bar handler in the
view layer can present it to the user.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar

from PySide6.QtCore import QObject, Signal

from src.exceptions import AppException
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

_F = TypeVar("_F", bound=Callable[..., Any])


def handle_errors(func: _F) -> _F:
    """Decorator that routes exceptions from a controller method to
    the ``error_occurred`` signal instead of propagating them to the UI.

    Args:
        func: The bound controller method to wrap.

    Returns:
        A wrapped function returning ``None`` (and emitting
        ``error_occurred``) whenever the wrapped call raises.
    """

    @functools.wraps(func)
    def wrapper(self: "BaseController", *args: Any, **kwargs: Any) -> Optional[Any]:
        try:
            return func(self, *args, **kwargs)
        except AppException as exc:
            logger.warning("%s: %s", func.__name__, exc)
            self.error_occurred.emit(exc.message)
            return None
        except Exception as exc:  # noqa: BLE001 - last-resort safety net
            logger.exception("Unexpected error in %s", func.__name__)
            self.error_occurred.emit(f"Ocurrió un error inesperado: {exc}")
            return None

    return wrapper  # type: ignore[return-value]


class BaseController(QObject):
    """Base class for all presentation-layer controllers.

    Signals:
        error_occurred: Emitted with a user-friendly message when an
            operation fails.
        success_message: Emitted with a user-friendly message when an
            operation completes successfully.
        data_changed: Emitted after any create/update/delete so views can
            refresh their data.
    """

    error_occurred = Signal(str)
    success_message = Signal(str)
    data_changed = Signal()
