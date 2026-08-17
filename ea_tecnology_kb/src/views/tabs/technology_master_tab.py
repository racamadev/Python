"""Tab 2: Technology Master — vertical, grouped Add/Update/Delete form."""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.controllers.technology_controller import TechnologyController
from src.models import Technology
from src.utils.constants import TECH_CLASSIF_CHOICES, TECH_LIFECYCLE_CHOICES, YES_NO_CHOICES
from src.utils.qt_date_helpers import datetime_to_qdate, qdate_to_datetime
from src.views.dialogs.confirm_dialog import confirm_action
from src.views.dialogs.message_dialogs import show_error, show_info


class TechnologyMasterTab(QWidget):
    """Vertical, grouped master form for creating/editing technologies.

    Args:
        controller: Controller mediating technology CRUD operations.
        parent: Optional Qt parent widget.

    Signals:
        technology_ready: Emitted with the loaded/saved :class:`Technology`
            whenever the form displays a persisted record, so other tabs
            can pick up the same technology context.
    """

    technology_ready = Signal(object)

    def __init__(self, controller: TechnologyController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._current_id: Optional[str] = None

        self._controller.error_occurred.connect(lambda msg: show_error(self, msg))
        self._controller.success_message.connect(lambda msg: show_info(self, msg))

        self._build_ui()
        self.start_new()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        identification_group = QGroupBox("Identificación")
        identification_form = QFormLayout(identification_group)
        self._tech_code = QLineEdit()
        self._tech_code.setToolTip("Código único obligatorio de la tecnología.")
        self._tech_code.textChanged.connect(self._validate_realtime)
        self._tech_product = QLineEdit()
        self._tech_product.setToolTip("Nombre del producto/tecnología (obligatorio).")
        self._tech_product.textChanged.connect(self._validate_realtime)
        self._tech_type = QLineEdit()
        self._tech_type.setToolTip("Tipo/categoría de la tecnología.")
        identification_form.addRow("Código *", self._tech_code)
        identification_form.addRow("Producto *", self._tech_product)
        identification_form.addRow("Tipo", self._tech_type)
        form_layout.addWidget(identification_group)

        classification_group = QGroupBox("Clasificación")
        classification_form = QFormLayout(classification_group)
        self._tech_std = QComboBox()
        self._tech_std.addItems(YES_NO_CHOICES)
        self._tech_std.setToolTip("¿Es un estándar corporativo?")
        self._tech_classif = QComboBox()
        self._tech_classif.setEditable(True)
        self._tech_classif.addItems(TECH_CLASSIF_CHOICES)
        self._tech_lifecycle = QComboBox()
        self._tech_lifecycle.setEditable(True)
        self._tech_lifecycle.addItems(TECH_LIFECYCLE_CHOICES)
        self._tech_trend = QComboBox()
        self._tech_trend.addItems(YES_NO_CHOICES)
        self._tech_trend.setToolTip("¿Es una tecnología en tendencia?")
        classification_form.addRow("Estándar *", self._tech_std)
        classification_form.addRow("Clasificación", self._tech_classif)
        classification_form.addRow("Ciclo de Vida", self._tech_lifecycle)
        classification_form.addRow("Tendencia *", self._tech_trend)
        form_layout.addWidget(classification_group)

        dates_group = QGroupBox("Fechas")
        dates_form = QFormLayout(dates_group)
        self._tech_date = self._build_date_edit()
        self._tech_start_date = self._build_date_edit()
        self._tech_divest_date = self._build_date_edit()
        self._tech_end_date = self._build_date_edit()
        dates_form.addRow("Fecha Registro", self._tech_date)
        dates_form.addRow("Fecha Inicio", self._tech_start_date)
        dates_form.addRow("Fecha Desinversión", self._tech_divest_date)
        dates_form.addRow("Fecha Fin", self._tech_end_date)
        form_layout.addWidget(dates_group)

        self._validation_label = QLabel()
        self._validation_label.setStyleSheet("color: #e57373;")
        form_layout.addWidget(self._validation_label)
        form_layout.addStretch(1)

        scroll.setWidget(form_container)
        outer_layout.addWidget(scroll)

        buttons_layout = QHBoxLayout()
        self._btn_new = QPushButton("➕ Add")
        self._btn_save = QPushButton("💾 Save")
        self._btn_delete = QPushButton("🗑️ Delete")
        self._btn_cancel = QPushButton("✖ Cancel")
        self._btn_new.clicked.connect(self.start_new)
        self._btn_save.clicked.connect(self._save)
        self._btn_delete.clicked.connect(self._delete)
        self._btn_cancel.clicked.connect(self.start_new)
        for button in (self._btn_new, self._btn_save, self._btn_delete, self._btn_cancel):
            buttons_layout.addWidget(button)
        buttons_layout.addStretch(1)
        outer_layout.addLayout(buttons_layout)

    @staticmethod
    def _build_date_edit() -> QDateEdit:
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setDate(datetime_to_qdate(None))
        return date_edit

    def _validate_realtime(self) -> None:
        problems = []
        if not self._tech_code.text().strip():
            problems.append("El código es obligatorio.")
        if not self._tech_product.text().strip():
            problems.append("El producto es obligatorio.")
        self._validation_label.setText(" ".join(problems))
        for field, valid in (
            (self._tech_code, bool(self._tech_code.text().strip())),
            (self._tech_product, bool(self._tech_product.text().strip())),
        ):
            field.setStyleSheet("" if valid else "border: 1px solid #e57373;")

    def start_new(self) -> None:
        """Reset the form for creating a brand-new technology record."""
        self._current_id = None
        self._tech_code.clear()
        self._tech_code.setEnabled(True)
        self._tech_product.clear()
        self._tech_type.clear()
        self._tech_std.setCurrentIndex(0)
        self._tech_classif.setCurrentText("")
        self._tech_lifecycle.setCurrentText("")
        self._tech_trend.setCurrentIndex(0)
        self._tech_date.setDate(datetime_to_qdate(None))
        self._tech_start_date.setDate(datetime_to_qdate(None))
        self._tech_divest_date.setDate(datetime_to_qdate(None))
        self._tech_end_date.setDate(datetime_to_qdate(None))
        self._validation_label.clear()
        self._btn_delete.setEnabled(False)

    def load_for_edit(self, technology: Technology) -> None:
        """Populate the form with an existing technology's data.

        Args:
            technology: The technology record to edit.
        """
        self._current_id = technology.id
        self._tech_code.setText(technology.tech_code)
        self._tech_product.setText(technology.tech_product)
        self._tech_type.setText(technology.tech_type)
        self._tech_std.setCurrentText(technology.tech_std or "No")
        self._tech_classif.setCurrentText(technology.tech_classif)
        self._tech_lifecycle.setCurrentText(technology.tech_lifecycle)
        self._tech_trend.setCurrentText(technology.tech_trend or "No")
        self._tech_date.setDate(datetime_to_qdate(technology.tech_date))
        self._tech_start_date.setDate(datetime_to_qdate(technology.tech_start_date))
        self._tech_divest_date.setDate(datetime_to_qdate(technology.tech_divest_date))
        self._tech_end_date.setDate(datetime_to_qdate(technology.tech_end_date))
        self._validation_label.clear()
        self._btn_delete.setEnabled(True)
        self.technology_ready.emit(technology)

    def _collect_form_data(self) -> dict[str, Any]:
        return {
            "tech_code": self._tech_code.text(),
            "tech_product": self._tech_product.text(),
            "tech_type": self._tech_type.text(),
            "tech_std": self._tech_std.currentText(),
            "tech_classif": self._tech_classif.currentText(),
            "tech_lifecycle": self._tech_lifecycle.currentText(),
            "tech_trend": self._tech_trend.currentText(),
            "tech_date": qdate_to_datetime(self._tech_date.date()),
            "tech_start_date": qdate_to_datetime(self._tech_start_date.date()),
            "tech_divest_date": qdate_to_datetime(self._tech_divest_date.date()),
            "tech_end_date": qdate_to_datetime(self._tech_end_date.date()),
        }

    def _save(self) -> None:
        data = self._collect_form_data()
        if self._current_id:
            technology = self._controller.update_technology(self._current_id, data)
        else:
            technology = self._controller.create_technology(data)
        if technology is not None:
            self.load_for_edit(technology)

    def _delete(self) -> None:
        if not self._current_id:
            return
        if confirm_action(
            self,
            "Confirmar eliminación",
            "¿Eliminar esta tecnología y todos sus datos relacionados?",
        ):
            if self._controller.delete_technology(self._current_id):
                self.start_new()
