"""Debounced global-search input widget."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

_DEBOUNCE_MS = 350


class SearchBar(QWidget):
    """A labeled search field that debounces text-change notifications.

    Signals:
        search_changed: Emitted with the trimmed search text after the
            user pauses typing for :data:`_DEBOUNCE_MS` milliseconds.
    """

    search_changed = Signal(str)

    def __init__(self, placeholder: str = "Buscar...", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(self._emit_search_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("🔍")
        label.setToolTip("Búsqueda global")
        self._input = QLineEdit(self)
        self._input.setPlaceholderText(placeholder)
        self._input.setClearButtonEnabled(True)
        self._input.textChanged.connect(lambda _: self._timer.start())

        layout.addWidget(label)
        layout.addWidget(self._input)

    def _emit_search_changed(self) -> None:
        self.search_changed.emit(self._input.text().strip())

    def text(self) -> str:
        """Return the current, unmodified search text."""
        return self._input.text().strip()

    def clear(self) -> None:
        """Clear the search field without waiting for the debounce timer."""
        self._input.blockSignals(True)
        self._input.clear()
        self._input.blockSignals(False)
