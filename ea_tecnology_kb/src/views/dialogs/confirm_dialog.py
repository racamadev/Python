"""Confirmation dialog helper."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def confirm_action(parent: QWidget | None, title: str, message: str) -> bool:
    """Prompt the user with a Yes/No confirmation dialog.

    Args:
        parent: Parent widget for modal positioning.
        title: Dialog window title.
        message: Confirmation question shown to the user.

    Returns:
        ``True`` if the user confirmed (clicked *Yes*), ``False`` otherwise.
    """
    result = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return result == QMessageBox.StandardButton.Yes
