"""Tab 3: Technology Notes — list panel + edit form panel."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from src.controllers.notes_controller import NotesController
from src.models import Note
from src.utils.constants import NOTE_CARD_VISIBLE_LINES, NOTE_TYPE_CHOICES
from src.utils.date_helpers import format_date
from src.utils.qt_date_helpers import datetime_to_qdate, qdate_to_datetime
from src.views.dialogs.confirm_dialog import confirm_action
from src.views.dialogs.message_dialogs import show_error, show_info
from src.views.widgets.search_bar import SearchBar
from src.views.widgets.table_models import ColumnSpec, GenericTableModel

_COLUMNS = [
    ColumnSpec("Fecha", "note_date", format_date),
    ColumnSpec("Tipo", "note_type"),
    ColumnSpec("Nota", "note_card", lambda v: (v or "")[:120]),
]
_FIELD_BY_COLUMN_INDEX = [spec.attribute for spec in _COLUMNS]


class TechnologyNotesTab(QWidget):
    """Master-detail view for notes attached to the selected technology.

    Args:
        controller: Controller mediating note CRUD/listing operations.
        parent: Optional Qt parent widget.
    """

    def __init__(self, controller: NotesController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._technology_id: Optional[str] = None
        self._current_note_id: Optional[str] = None
        self._sort_field = "note_date"
        self._sort_order = -1

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
        self._search_bar = SearchBar("Buscar en notas...", self)
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

        form_panel = QGroupBox("Detalle de Nota")
        form_outer = QVBoxLayout(form_panel)
        form_layout = QFormLayout()
        self._note_date = QDateEdit()
        self._note_date.setCalendarPopup(True)
        self._note_date.setDisplayFormat("yyyy-MM-dd")
        self._note_type = QComboBox()
        self._note_type.setEditable(True)
        self._note_type.addItems(NOTE_TYPE_CHOICES)
        self._note_card = QTextEdit()
        line_height = self._note_card.fontMetrics().lineSpacing()
        self._note_card.setFixedHeight(line_height * NOTE_CARD_VISIBLE_LINES + 12)
        form_layout.addRow("Fecha", self._note_date)
        form_layout.addRow("Tipo", self._note_type)
        form_layout.addRow("Contenido", self._note_card)
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

    def _current_note(self) -> Optional[Note]:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.row_object(indexes[0].row())

    def _on_selection_changed(self) -> None:
        note = self._current_note()
        if note is not None:
            self._load_form(note)

    def _on_header_clicked(self, section: int) -> None:
        field = _FIELD_BY_COLUMN_INDEX[section]
        if self._sort_field == field:
            self._sort_order *= -1
        else:
            self._sort_field = field
            self._sort_order = 1
        self.refresh()

    def refresh(self) -> None:
        """Reload notes for the current technology context."""
        if not self._technology_id:
            self._model.set_rows([])
            return
        notes = self._controller.list_notes(
            self._technology_id,
            search_text=self._search_bar.text(),
            sort_field=self._sort_field,
            sort_order=self._sort_order,
        )
        self._model.set_rows(notes or [])

    def _load_form(self, note: Note) -> None:
        self._current_note_id = note.id
        self._note_date.setDate(datetime_to_qdate(note.note_date))
        self._note_type.setCurrentText(note.note_type)
        self._note_card.setPlainText(note.note_card)

    def _start_new(self) -> None:
        self._current_note_id = None
        self._note_date.setDate(datetime_to_qdate(None))
        self._note_type.setCurrentText("")
        self._note_card.clear()

    def _save(self) -> None:
        if not self._technology_id:
            show_info(self, "Seleccione una tecnología antes de agregar notas.")
            return
        data = {
            "note_date": qdate_to_datetime(self._note_date.date()),
            "note_type": self._note_type.currentText(),
            "note_card": self._note_card.toPlainText(),
        }
        if self._current_note_id:
            note = self._controller.update_note(self._current_note_id, self._technology_id, data)
        else:
            note = self._controller.create_note(self._technology_id, data)
        if note is not None:
            self._load_form(note)

    def _delete(self) -> None:
        if not self._current_note_id:
            return
        if confirm_action(self, "Confirmar eliminación", "¿Eliminar esta nota?"):
            if self._controller.delete_note(self._current_note_id):
                self._start_new()
