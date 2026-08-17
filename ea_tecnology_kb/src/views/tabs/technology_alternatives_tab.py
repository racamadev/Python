"""Tab 4: Technology Alternatives — list panel + edit form panel."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.controllers.alternatives_controller import AlternativesController
from src.models import Alternative
from src.views.dialogs.confirm_dialog import confirm_action
from src.views.dialogs.message_dialogs import show_error, show_info
from src.views.widgets.search_bar import SearchBar
from src.views.widgets.table_models import ColumnSpec, GenericTableModel

_COLUMNS = [
    ColumnSpec("Código", "alternative_code"),
    ColumnSpec("Producto", "alternative_product"),
    ColumnSpec("Descripción", "alternative_card", lambda v: (v or "")[:120]),
]
_FIELD_BY_COLUMN_INDEX = [spec.attribute for spec in _COLUMNS]


class TechnologyAlternativesTab(QWidget):
    """Master-detail view for alternatives attached to the selected technology.

    Args:
        controller: Controller mediating alternative CRUD/listing operations.
        parent: Optional Qt parent widget.
    """

    def __init__(self, controller: AlternativesController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._technology_id: Optional[str] = None
        self._current_alternative_id: Optional[str] = None
        self._sort_field = "alternative_product"
        self._sort_order = 1

        self._controller.error_occurred.connect(lambda msg: show_error(self, msg))
        self._controller.data_changed.connect(self.refresh)

        self._build_ui()
        self.set_technology(None, "")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._context_label = QLabel()
        self._context_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._context_label)

        splitter = QSplitter(Qt.Orientation.Vertical, self)

        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        self._search_bar = SearchBar("Buscar en alternativas...", self)
        self._search_bar.search_changed.connect(lambda _: self.refresh())
        list_layout.addWidget(self._search_bar)

        self._model = GenericTableModel(_COLUMNS)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionsClickable(True)
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        list_layout.addWidget(self._table)
        splitter.addWidget(list_panel)

        form_panel = QGroupBox("Detalle de Alternativa")
        form_outer = QVBoxLayout(form_panel)
        form_layout = QFormLayout()
        self._alternative_code = QLineEdit()
        self._alternative_product = QLineEdit()
        self._alternative_card = QTextEdit()
        self._alternative_card.setFixedHeight(self._alternative_card.fontMetrics().lineSpacing() * 6 + 12)
        form_layout.addRow("Código", self._alternative_code)
        form_layout.addRow("Producto", self._alternative_product)
        form_layout.addRow("Descripción", self._alternative_card)
        form_outer.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        self._btn_new = QPushButton("➕ New")
        self._btn_save = QPushButton("💾 Save")
        self._btn_delete = QPushButton("🗑️ Delete")
        self._btn_cancel = QPushButton("✖ Cancel")
        self._btn_new.clicked.connect(self._start_new)
        self._btn_save.clicked.connect(self._save)
        self._btn_delete.clicked.connect(self._delete)
        self._btn_cancel.clicked.connect(self._start_new)
        for button in (self._btn_new, self._btn_save, self._btn_delete, self._btn_cancel):
            buttons_layout.addWidget(button)
        buttons_layout.addStretch(1)
        form_outer.addLayout(buttons_layout)
        splitter.addWidget(form_panel)

        layout.addWidget(splitter, 1)

    def set_technology(self, technology_id: Optional[str], tech_code: str) -> None:
        """Set the technology context this tab operates against.

        Args:
            technology_id: Id of the owning technology, or ``None``.
            tech_code: Display code of the owning technology, for the header.
        """
        self._technology_id = technology_id
        has_context = technology_id is not None
        self._context_label.setText(
            f"Tecnología: {tech_code}" if has_context else "Seleccione una tecnología (Tab 1 o 2)."
        )
        for widget in (self._table, self._btn_new, self._btn_save, self._btn_delete, self._btn_cancel):
            widget.setEnabled(has_context)
        self._start_new()
        self.refresh()

    def _current_alternative(self) -> Optional[Alternative]:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.row_object(indexes[0].row())

    def _on_selection_changed(self) -> None:
        alternative = self._current_alternative()
        if alternative is not None:
            self._load_form(alternative)

    def _on_header_clicked(self, section: int) -> None:
        field = _FIELD_BY_COLUMN_INDEX[section]
        if self._sort_field == field:
            self._sort_order *= -1
        else:
            self._sort_field = field
            self._sort_order = 1
        self.refresh()

    def refresh(self) -> None:
        """Reload alternatives for the current technology context."""
        if not self._technology_id:
            self._model.set_rows([])
            return
        alternatives = self._controller.list_alternatives(
            self._technology_id,
            search_text=self._search_bar.text(),
            sort_field=self._sort_field,
            sort_order=self._sort_order,
        )
        self._model.set_rows(alternatives or [])

    def _load_form(self, alternative: Alternative) -> None:
        self._current_alternative_id = alternative.id
        self._alternative_code.setText(alternative.alternative_code)
        self._alternative_product.setText(alternative.alternative_product)
        self._alternative_card.setPlainText(alternative.alternative_card)

    def _start_new(self) -> None:
        self._current_alternative_id = None
        self._alternative_code.clear()
        self._alternative_product.clear()
        self._alternative_card.clear()

    def _save(self) -> None:
        if not self._technology_id:
            show_info(self, "Seleccione una tecnología antes de agregar alternativas.")
            return
        data = {
            "alternative_code": self._alternative_code.text(),
            "alternative_product": self._alternative_product.text(),
            "alternative_card": self._alternative_card.toPlainText(),
        }
        if self._current_alternative_id:
            alternative = self._controller.update_alternative(
                self._current_alternative_id, self._technology_id, data
            )
        else:
            alternative = self._controller.create_alternative(self._technology_id, data)
        if alternative is not None:
            self._load_form(alternative)

    def _delete(self) -> None:
        if not self._current_alternative_id:
            return
        if confirm_action(self, "Confirmar eliminación", "¿Eliminar esta alternativa?"):
            if self._controller.delete_alternative(self._current_alternative_id):
                self._start_new()
