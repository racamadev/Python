"""EA Technology KB — application entry point (composition root).

Wires together the infrastructure, data, business and presentation layers
and starts the Qt event loop. Run with::

    python main.py
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.controllers.alternatives_controller import AlternativesController
from src.controllers.links_controller import LinksController
from src.controllers.notes_controller import NotesController
from src.controllers.technology_controller import TechnologyController
from src.exceptions import DatabaseConnectionError
from src.infrastructure.config import get_config
from src.infrastructure.database.database_manager import DatabaseManager
from src.infrastructure.database.mongo_connection import MongoConnection
from src.infrastructure.logging import get_logger, setup_logging
from src.repositories.alternatives_repository import AlternativesRepository
from src.repositories.links_repository import LinksRepository
from src.repositories.notes_repository import NotesRepository
from src.repositories.technology_repository import TechnologyRepository
from src.services.alternatives_service import AlternativesService
from src.services.export_service import ExportService
from src.services.links_service import LinksService
from src.services.notes_service import NotesService
from src.services.technology_service import TechnologyService
from src.utils.constants import (
    COLLECTION_ALTERNATIVES,
    COLLECTION_LINKS,
    COLLECTION_NOTES,
    COLLECTION_TECHNOLOGIES,
)
from src.views.main_window import MainWindow


def _apply_theme(app: QApplication, theme_name: str) -> None:
    """Apply the Qt Material stylesheet to the application.

    Args:
        app: The running :class:`QApplication`.
        theme_name: ``dark`` or ``light``.
    """
    try:
        from qt_material import apply_stylesheet

        material_theme = "dark_teal.xml" if theme_name == "dark" else "light_teal.xml"
        apply_stylesheet(app, theme=material_theme)
    except ImportError:
        # qt-material is optional at runtime; fall back to the default Qt style.
        pass


def main() -> int:
    """Bootstrap and run the EA Technology KB desktop application.

    Returns:
        The process exit code.
    """
    setup_logging()
    logger = get_logger(__name__)
    config = get_config()

    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    _apply_theme(app, config.app_theme)

    try:
        connection = MongoConnection.instance(config)
        db_manager = DatabaseManager(connection)
        db_manager.ensure_indexes()
    except DatabaseConnectionError as exc:
        logger.critical("Failed to start application: %s", exc)
        QMessageBox.critical(
            None,
            "Error de conexión",
            f"No se pudo conectar a MongoDB.\n\n{exc}\n\n"
            "Verifique la configuración en el archivo .env y que el servicio esté disponible.",
        )
        return 1

    technology_repository = TechnologyRepository(db_manager.get_collection(COLLECTION_TECHNOLOGIES))
    notes_repository = NotesRepository(db_manager.get_collection(COLLECTION_NOTES))
    alternatives_repository = AlternativesRepository(
        db_manager.get_collection(COLLECTION_ALTERNATIVES)
    )
    links_repository = LinksRepository(db_manager.get_collection(COLLECTION_LINKS))

    technology_service = TechnologyService(
        technology_repository, notes_repository, alternatives_repository, links_repository
    )
    notes_service = NotesService(notes_repository, technology_repository)
    alternatives_service = AlternativesService(alternatives_repository, technology_repository)
    links_service = LinksService(links_repository, technology_repository)
    export_service = ExportService(
        technology_service, notes_service, alternatives_service, links_service
    )

    technology_controller = TechnologyController(technology_service)
    notes_controller = NotesController(notes_service)
    alternatives_controller = AlternativesController(alternatives_service)
    links_controller = LinksController(links_service)

    window = MainWindow(
        config=config,
        technology_controller=technology_controller,
        notes_controller=notes_controller,
        alternatives_controller=alternatives_controller,
        links_controller=links_controller,
        export_service=export_service,
    )
    window.show()

    logger.info("%s started successfully.", config.app_name)
    exit_code = app.exec()
    connection.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
