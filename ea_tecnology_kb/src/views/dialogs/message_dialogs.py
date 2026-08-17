"""Friendly, consistently-styled message box helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(parent: QWidget | None, message: str, title: str = "Error") -> None:
    """Display a modal error message box.

    Args:
        parent: Parent widget for modal positioning.
        message: The error message to display.
        title: Dialog window title.
    """
    QMessageBox.critical(parent, title, message)


def show_warning(parent: QWidget | None, message: str, title: str = "Atención") -> None:
    """Display a modal warning message box.

    Args:
        parent: Parent widget for modal positioning.
        message: The warning message to display.
        title: Dialog window title.
    """
    QMessageBox.warning(parent, title, message)


def show_info(parent: QWidget | None, message: str, title: str = "Información") -> None:
    """Display a modal informational message box.

    Args:
        parent: Parent widget for modal positioning.
        message: The message to display.
        title: Dialog window title.
    """
    QMessageBox.information(parent, title, message)
