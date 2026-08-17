"""Main application window: composes the five master-detail tabs."""

from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from src.controllers.alternatives_controller import AlternativesController
from src.controllers.links_controller import LinksController
from src.controllers.notes_controller import NotesController
from src.controllers.technology_controller import TechnologyController
from src.infrastructure.config import Config
from src.models import Technology
from src.services.export_service import ExportService
from src.views.tabs.technology_alternatives_tab import TechnologyAlternativesTab
from src.views.tabs.technology_links_tab import TechnologyLinksTab
from src.views.tabs.technology_list_tab import TechnologyListTab
from src.views.tabs.technology_master_tab import TechnologyMasterTab
from src.views.tabs.technology_notes_tab import TechnologyNotesTab

_TAB_LIST = 0
_TAB_MASTER = 1
_TAB_NOTES = 2
_TAB_ALTERNATIVES = 3
_TAB_LINKS = 4


class MainWindow(QMainWindow):
    """Top-level application window hosting the five master-detail tabs.

    Args:
        config: Application configuration (window title, theme, etc).
        technology_controller: Controller for technology master records.
        notes_controller: Controller for note records.
        alternatives_controller: Controller for alternative records.
        links_controller: Controller for link records.
        export_service: Service used to generate the consolidated Excel export.
    """

    def __init__(
        self,
        config: Config,
        technology_controller: TechnologyController,
        notes_controller: NotesController,
        alternatives_controller: AlternativesController,
        links_controller: LinksController,
        export_service: ExportService,
    ) -> None:
        super().__init__()
        self._config = config
        self._current_technology: Optional[Technology] = None

        self.setWindowTitle(config.app_name)
        self.resize(1280, 800)

        self._list_tab = TechnologyListTab(technology_controller, export_service, self)
        self._master_tab = TechnologyMasterTab(technology_controller, self)
        self._notes_tab = TechnologyNotesTab(notes_controller, self)
        self._alternatives_tab = TechnologyAlternativesTab(alternatives_controller, self)
        self._links_tab = TechnologyLinksTab(links_controller, self)

        self._tabs = QTabWidget(self)
        self._tabs.addTab(self._list_tab, "Technologies List")
        self._tabs.addTab(self._master_tab, "Technology Master")
        self._tabs.addTab(self._notes_tab, "Notes")
        self._tabs.addTab(self._alternatives_tab, "Alternatives")
        self._tabs.addTab(self._links_tab, "Links")
        self.setCentralWidget(self._tabs)

        self._build_menu()
        self.statusBar().showMessage(f"Conectado a MongoDB · {config.mongo_database}")

        self._list_tab.new_requested.connect(self._on_new_requested)
        self._list_tab.edit_requested.connect(self._on_edit_requested)
        self._list_tab.technology_selected.connect(self._on_technology_selected)
        self._master_tab.technology_ready.connect(self._on_technology_selected)

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About",
            f"{self._config.app_name}\n\n"
            "Gestión, seguimiento y análisis de tecnologías de arquitectura empresarial.",
        )

    def _on_new_requested(self) -> None:
        self._master_tab.start_new()
        self._tabs.setCurrentIndex(_TAB_MASTER)

    def _on_edit_requested(self, technology: Technology) -> None:
        self._master_tab.load_for_edit(technology)
        self._tabs.setCurrentIndex(_TAB_MASTER)

    def _on_technology_selected(self, technology: Optional[Technology]) -> None:
        self._current_technology = technology
        technology_id = technology.id if technology else None
        tech_code = technology.tech_code if technology else ""
        self._notes_tab.set_technology(technology_id, tech_code)
        self._alternatives_tab.set_technology(technology_id, tech_code)
        self._links_tab.set_technology(technology_id, tech_code)
