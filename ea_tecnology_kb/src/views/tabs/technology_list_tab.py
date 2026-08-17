"""Tab 1: Technologies List — searchable, filterable, sortable, paginated."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.controllers.technology_controller import TechnologyController
from src.models import Technology
from src.services.export_service import ExportService
from src.utils.constants import DEFAULT_PAGE_SIZE
from src.utils.date_helpers import format_date
from src.views.dialogs.confirm_dialog import confirm_action
from src.views.dialogs.message_dialogs import show_error, show_info
from src.views.widgets.filter_header import ColumnFilterBar
from src.views.widgets.search_bar import SearchBar
from src.views.widgets.table_models import ColumnSpec, GenericTableModel

_COLUMNS = [
    ColumnSpec("Código", "tech_code"),
    ColumnSpec("Tipo", "tech_type"),
    ColumnSpec("Producto", "tech_product"),
    ColumnSpec("Estándar", "tech_std"),
    ColumnSpec("Clasificación", "tech_classif"),
    ColumnSpec("Fecha Desinversión", "tech_divest_date", format_date),
    ColumnSpec("Fecha Fin", "tech_end_date", format_date),
]
_FILTERABLE_COLUMNS = [
    ("tech_code", "Código"),
    ("tech_type", "Tipo"),
    ("tech_product", "Producto"),
    ("tech_std", "Estándar"),
    ("tech_classif", "Clasificación"),
]
_FIELD_BY_COLUMN_INDEX = [spec.attribute for spec in _COLUMNS]


class TechnologyListTab(QWidget):
    """Master list view for browsing, searching and managing technologies.

    Args:
        controller: Controller mediating technology CRUD/listing operations.
        export_service: Service used to generate the consolidated Excel export.
        parent: Optional Qt parent widget.

    Signals:
        new_requested: Emitted when the user wants to create a technology.
        edit_requested: Emitted with the selected :class:`Technology` when
            the user wants to edit it.
        technology_selected: Emitted with the selected :class:`Technology`
            (or ``None``) whenever the table selection changes.
    """

    new_requested = Signal()
    edit_requested = Signal(object)
    technology_selected = Signal(object)

    def __init__(
        self,
        controller: TechnologyController,
        export_service: ExportService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._export_service = export_service

        self._page = 1
        self._page_size = DEFAULT_PAGE_SIZE
        self._total = 0
        self._sort_field = "tech_code"
        self._sort_order = 1

        self._controller.error_occurred.connect(lambda msg: show_error(self, msg))
        self._controller.data_changed.connect(self.refresh)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        toolbar_layout = QHBoxLayout()
        self._btn_new = QPushButton("➕ New (Ctrl+N)")
        self._btn_edit = QPushButton("✏️ Edit (Ctrl+E)")
        self._btn_delete = QPushButton("🗑️ Delete (Del)")
        self._btn_refresh = QPushButton("🔄 Refresh (F5)")
        self._btn_export = QPushButton("📊 Export Excel (Ctrl+Shift+E)")
        for button in (
            self._btn_new,
            self._btn_edit,
            self._btn_delete,
            self._btn_refresh,
            self._btn_export,
        ):
            toolbar_layout.addWidget(button)
        toolbar_layout.addStretch(1)
        layout.addLayout(toolbar_layout)

        self._btn_new.clicked.connect(self.new_requested.emit)
        self._btn_edit.clicked.connect(self._emit_edit_requested)
        self._btn_delete.clicked.connect(self._delete_selected)
        self._btn_refresh.clicked.connect(self.refresh)
        self._btn_export.clicked.connect(self._export_to_excel)

        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_requested.emit)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._emit_edit_requested)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, activated=self._delete_selected)
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, activated=self._export_to_excel)

        self._search_bar = SearchBar("Buscar en todas las columnas...", self)
        self._search_bar.search_changed.connect(self._on_search_changed)
        layout.addWidget(self._search_bar)

        self._filter_bar = ColumnFilterBar(_FILTERABLE_COLUMNS, self)
        self._filter_bar.filters_changed.connect(self._on_filters_changed)
        layout.addWidget(self._filter_bar)

        self._model = GenericTableModel(_COLUMNS)
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSortingEnabled(False)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionsClickable(True)
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self._table.doubleClicked.connect(lambda _: self._emit_edit_requested())
        self._table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table)

        pagination_layout = QHBoxLayout()
        self._btn_prev = QPushButton("◀ Anterior")
        self._btn_next = QPushButton("Siguiente ▶")
        self._page_label = QLabel()
        self._btn_prev.clicked.connect(self._go_previous_page)
        self._btn_next.clicked.connect(self._go_next_page)
        pagination_layout.addWidget(self._btn_prev)
        pagination_layout.addWidget(self._page_label)
        pagination_layout.addWidget(self._btn_next)
        pagination_layout.addStretch(1)
        layout.addLayout(pagination_layout)

    def _current_technology(self) -> Optional[Technology]:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.row_object(indexes[0].row())

    def _on_selection_changed(self) -> None:
        self.technology_selected.emit(self._current_technology())

    def _emit_edit_requested(self) -> None:
        technology = self._current_technology()
        if technology is None:
            show_info(self, "Seleccione una tecnología de la lista.")
            return
        self.edit_requested.emit(technology)

    def _delete_selected(self) -> None:
        technology = self._current_technology()
        if technology is None:
            show_info(self, "Seleccione una tecnología de la lista.")
            return
        if confirm_action(
            self,
            "Confirmar eliminación",
            f"¿Eliminar la tecnología '{technology.tech_code}' y todos sus datos relacionados "
            "(notas, alternativas, enlaces)?",
        ):
            self._controller.delete_technology(technology.id)

    def _on_search_changed(self, _: str) -> None:
        self._page = 1
        self.refresh()

    def _on_filters_changed(self, _: dict) -> None:
        self._page = 1
        self.refresh()

    def _on_header_clicked(self, section: int) -> None:
        field = _FIELD_BY_COLUMN_INDEX[section]
        if self._sort_field == field:
            self._sort_order *= -1
        else:
            self._sort_field = field
            self._sort_order = 1
        self.refresh()

    def _go_previous_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            self.refresh()

    def _go_next_page(self) -> None:
        max_page = max(1, -(-self._total // self._page_size))
        if self._page < max_page:
            self._page += 1
            self.refresh()

    def refresh(self) -> None:
        """Reload the current page from the backend using the active
        search text, column filters, sort field/order and page number.
        """
        result = self._controller.list_technologies(
            search_text=self._search_bar.text(),
            column_filters=self._filter_bar.current_filters(),
            sort_field=self._sort_field,
            sort_order=self._sort_order,
            page=self._page,
            page_size=self._page_size,
        )
        if result is None:
            return
        technologies, total = result
        self._total = total
        self._model.set_rows(technologies)

        max_page = max(1, -(-total // self._page_size))
        self._page_label.setText(f"Página {self._page} de {max_page} — {total} registros")
        self._btn_prev.setEnabled(self._page > 1)
        self._btn_next.setEnabled(self._page < max_page)

    def _export_to_excel(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar a Excel", "ea_tecnology_kb_export.xlsx", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        try:
            written_path = self._export_service.export_all(file_path)
            show_info(self, f"Exportación completada:\n{written_path}", title="Exportación exitosa")
        except Exception as exc:  # noqa: BLE001
            show_error(self, f"No se pudo exportar el archivo: {exc}")
