"""Generic Qt table model backing the master and detail list views.

A single, column-spec-driven :class:`QAbstractTableModel` implementation is
reused across all list views (technologies, notes, alternatives, links) to
avoid duplicating boilerplate model code per entity (DRY).
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ColumnSpec:
    """Declarative description of a single table column.

    Args:
        header: Column header label shown to the user.
        attribute: Attribute name read off each row object via ``getattr``.
        formatter: Optional callable transforming the raw attribute value
            into a display string.
    """

    def __init__(
        self,
        header: str,
        attribute: str,
        formatter: Optional[Callable[[Any], str]] = None,
    ) -> None:
        self.header = header
        self.attribute = attribute
        self.formatter = formatter

    def value_of(self, row_object: Any) -> str:
        """Return the formatted display value for ``row_object``.

        Args:
            row_object: The domain object backing a table row.

        Returns:
            The formatted string to display in the cell.
        """
        raw_value = getattr(row_object, self.attribute, "")
        if self.formatter is not None:
            return self.formatter(raw_value)
        return "" if raw_value is None else str(raw_value)


class GenericTableModel(QAbstractTableModel):
    """A read-only table model driven by a list of :class:`ColumnSpec`.

    Args:
        columns: Ordered column definitions.
        rows: Initial list of domain objects to display.
        parent: Optional Qt parent object.
    """

    def __init__(
        self,
        columns: Sequence[ColumnSpec],
        rows: Optional[list[Any]] = None,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self._columns = list(columns)
        self._rows: list[Any] = rows or []

    def set_rows(self, rows: list[Any]) -> None:
        """Replace the model's data and refresh all attached views.

        Args:
            rows: New list of domain objects to display.
        """
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def row_object(self, row_index: int) -> Any:
        """Return the domain object backing a given row.

        Args:
            row_index: 0-based row index.

        Returns:
            The domain object at ``row_index``.
        """
        return self._rows[row_index]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:  # noqa: N802
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            column = self._columns[index.column()]
            return column.value_of(self._rows[index.row()])
        return None

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._columns[section].header
        return str(section + 1)
