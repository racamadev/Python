"""Controller mediating between technology views and :class:`TechnologyService`."""

from __future__ import annotations

from typing import Any, Optional

from src.controllers.base_controller import BaseController, handle_errors
from src.models import Technology
from src.services.technology_service import TechnologyService


class TechnologyController(BaseController):
    """Coordinates CRUD and listing operations for the technology master.

    Args:
        service: Business-layer service for technology records.
    """

    def __init__(self, service: TechnologyService) -> None:
        super().__init__()
        self._service = service

    @handle_errors
    def create_technology(self, data: dict[str, Any]) -> Optional[Technology]:
        """Create a new technology record.

        Args:
            data: Raw form data collected from the view.

        Returns:
            The created :class:`Technology`, or ``None`` on failure (an
            ``error_occurred`` signal will have been emitted in that case).
        """
        technology = self._service.create_technology(data)
        self.success_message.emit(f"Tecnología '{technology.tech_code}' creada correctamente.")
        self.data_changed.emit()
        return technology

    @handle_errors
    def update_technology(self, technology_id: str, data: dict[str, Any]) -> Optional[Technology]:
        """Update an existing technology record.

        Args:
            technology_id: Id of the record to update.
            data: Raw form data collected from the view.

        Returns:
            The updated :class:`Technology`, or ``None`` on failure.
        """
        technology = self._service.update_technology(technology_id, data)
        self.success_message.emit(f"Tecnología '{technology.tech_code}' actualizada correctamente.")
        self.data_changed.emit()
        return technology

    @handle_errors
    def delete_technology(self, technology_id: str) -> bool:
        """Delete a technology record and its related details.

        Args:
            technology_id: Id of the record to delete.

        Returns:
            ``True`` on success, ``None`` (falsy) on failure.
        """
        self._service.delete_technology(technology_id)
        self.success_message.emit("Tecnología eliminada correctamente.")
        self.data_changed.emit()
        return True

    @handle_errors
    def get_technology(self, technology_id: str) -> Optional[Technology]:
        """Fetch a single technology record.

        Args:
            technology_id: Id of the record to fetch.

        Returns:
            The matching :class:`Technology`, or ``None`` on failure.
        """
        return self._service.get_technology(technology_id)

    @handle_errors
    def list_technologies(
        self,
        search_text: str = "",
        column_filters: Optional[dict[str, str]] = None,
        sort_field: str = "tech_code",
        sort_order: int = 1,
        page: int = 1,
        page_size: int = 50,
    ) -> Optional[tuple[list[Technology], int]]:
        """List technologies with search, filters, sorting and paging.

        Args:
            search_text: Free-text search term.
            column_filters: Per-column filter values.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.
            page: 1-based page number.
            page_size: Number of records per page.

        Returns:
            A tuple of ``(technologies, total_count)``, or ``None`` on failure.
        """
        return self._service.list_technologies(
            search_text=search_text,
            column_filters=column_filters,
            sort_field=sort_field,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
