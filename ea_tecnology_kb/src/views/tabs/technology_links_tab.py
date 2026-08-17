"""Tab 5: Technology Links — list panel + edit form panel + Open Link."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.controllers.links_controller import LinksController
from src.models import Link
from src.utils.constants import LINK_QUALITY_CHOICES, LINK_TYPE_CHOICES
from src.views.dialogs.confirm_dialog import confirm_action
from src.views.dialogs.message_dialogs import show_error, show_info
from src.views.widgets.search_bar import SearchBar
from src.views.widgets.table_models import ColumnSpec, GenericTableModel

_COLUMNS = [
    ColumnSpec("Tipo", "link_type"),
    ColumnSpec("URL", "link_url"),
    ColumnSpec("Fuente", "link_source"),
    ColumnSpec("Calidad", "link_quality"),
]
_FIELD_BY_COLUMN_INDEX = [spec.attribute for spec in _COLUMNS]


class TechnologyLinksTab(QWidget):
    """Master-detail view for reference links attached to the selected technology.

    Args:
        controller: Controller mediating link CRUD/listing operations and
            browser opening.
        parent: Optional Qt parent widget.
    """

    def __init__(self, controller: LinksController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._technology_id: Optional[str] = None
        self._current_link_id: Optional[str] = None
        self._sort_field = "link_type"
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
        top_layout = QHBoxLayout()
        self._search_bar = SearchBar("Buscar en enlaces...", self)
        self._search_bar.search_changed.connect(lambda _: self.refresh())
        top_layout.addWidget(self._search_bar)
        self._btn_open = QPushButton("🌐 Open Link")
        self._btn_open.clicked.connect(self._open_selected_link)
        top_layout.addWidget(self._btn_open)
        list_layout.addLayout(top_layout)

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
        self._table.doubleClicked.connect(lambda _: self._open_selected_link())
        list_layout.addWidget(self._table)
        splitter.addWidget(list_panel)

        form_panel = QGroupBox("Detalle de Enlace")
        form_outer = QVBoxLayout(form_panel)
        form_layout = QFormLayout()
        self._link_type = QComboBox()
        self._link_type.setEditable(True)
        self._link_type.addItems(LINK_TYPE_CHOICES)
        self._link_url = QLineEdit()
        self._link_url.setPlaceholderText("https://...")
        self._link_source = QLineEdit()
        self._link_quality = QComboBox()
        self._link_quality.setEditable(True)
        self._link_quality.addItems(LINK_QUALITY_CHOICES)
        form_layout.addRow("Tipo", self._link_type)
        form_layout.addRow("URL *", self._link_url)
        form_layout.addRow("Fuente", self._link_source)
        form_layout.addRow("Calidad", self._link_quality)
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
        for widget in (
            self._table,
            self._btn_new,
            self._btn_save,
            self._btn_delete,
            self._btn_cancel,
            self._btn_open,
        ):
            widget.setEnabled(has_context)
        self._context_label.setText(
            f"Tecnología: {tech_code}" if has_context else "Seleccione una tecnología (Tab 1 o 2)."
        )
        self._start_new()
        self.refresh()

    def _current_link(self) -> Optional[Link]:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.row_object(indexes[0].row())

    def _on_selection_changed(self) -> None:
        link = self._current_link()
        if link is not None:
            self._load_form(link)

    def _on_header_clicked(self, section: int) -> None:
        field = _FIELD_BY_COLUMN_INDEX[section]
        if self._sort_field == field:
            self._sort_order *= -1
        else:
            self._sort_field = field
            self._sort_order = 1
        self.refresh()

    def refresh(self) -> None:
        """Reload reference links for the current technology context."""
        if not self._technology_id:
            self._model.set_rows([])
            return
        links = self._controller.list_links(
            self._technology_id,
            search_text=self._search_bar.text(),
            sort_field=self._sort_field,
            sort_order=self._sort_order,
        )
        self._model.set_rows(links or [])

    def _load_form(self, link: Link) -> None:
        self._current_link_id = link.id
        self._link_type.setCurrentText(link.link_type)
        self._link_url.setText(link.link_url)
        self._link_source.setText(link.link_source)
        self._link_quality.setCurrentText(link.link_quality)

    def _start_new(self) -> None:
        self._current_link_id = None
        self._link_type.setCurrentText("")
        self._link_url.clear()
        self._link_source.clear()
        self._link_quality.setCurrentText("")

    def _save(self) -> None:
        if not self._technology_id:
            show_info(self, "Seleccione una tecnología antes de agregar enlaces.")
            return
        data = {
            "link_type": self._link_type.currentText(),
            "link_url": self._link_url.text(),
            "link_source": self._link_source.text(),
            "link_quality": self._link_quality.currentText(),
        }
        if self._current_link_id:
            link = self._controller.update_link(self._current_link_id, self._technology_id, data)
        else:
            link = self._controller.create_link(self._technology_id, data)
        if link is not None:
            self._load_form(link)

    def _delete(self) -> None:
        if not self._current_link_id:
            return
        if confirm_action(self, "Confirmar eliminación", "¿Eliminar este enlace?"):
            if self._controller.delete_link(self._current_link_id):
                self._start_new()

    def _open_selected_link(self) -> None:
        link = self._current_link()
        if link is None:
            show_info(self, "Seleccione un enlace de la lista.")
            return
        self._controller.open_link(link.link_url)
