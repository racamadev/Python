"""Per-column filter bar used above master/detail tables."""

from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

_DEBOUNCE_MS = 350


class ColumnFilterBar(QWidget):
    """Renders one labeled text field per filterable column.

    Args:
        columns: Ordered ``(field_name, label)`` pairs to build filters for.
        parent: Optional Qt parent widget.

    Signals:
        filters_changed: Emitted with a ``{field_name: value}`` dict of the
            non-empty filters, after the user pauses typing.
    """

    filters_changed = Signal(dict)

    def __init__(self, columns: Sequence[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fields: dict[str, QLineEdit] = {}

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(self._emit_filters_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        for field_name, label in columns:
            column_box = QWidget(self)
            column_layout = QHBoxLayout(column_box)
            column_layout.setContentsMargins(0, 0, 4, 0)
            column_layout.addWidget(QLabel(label))
            line_edit = QLineEdit(column_box)
            line_edit.setPlaceholderText(f"Filtrar {label}...")
            line_edit.setClearButtonEnabled(True)
            line_edit.textChanged.connect(lambda _: self._timer.start())
            column_layout.addWidget(line_edit)
            layout.addWidget(column_box)
            self._fields[field_name] = line_edit

        layout.addStretch(1)

    def _emit_filters_changed(self) -> None:
        self.filters_changed.emit(self.current_filters())

    def current_filters(self) -> dict[str, str]:
        """Return the currently entered, non-empty column filters.

        Returns:
            A dict mapping field name to filter text.
        """
        return {name: field.text().strip() for name, field in self._fields.items() if field.text().strip()}

    def clear(self) -> None:
        """Clear all filter fields without waiting for the debounce timer."""
        for field in self._fields.values():
            field.blockSignals(True)
            field.clear()
            field.blockSignals(False)
