"""Controller mediating between links views and :class:`LinksService`."""

from __future__ import annotations

import webbrowser
from typing import Any, Optional

from src.controllers.base_controller import BaseController, handle_errors
from src.models import Link
from src.services.links_service import LinksService
from src.utils.validators import is_valid_url


class LinksController(BaseController):
    """Coordinates CRUD, listing and browser-opening for reference links.

    Args:
        service: Business-layer service for link records.
    """

    def __init__(self, service: LinksService) -> None:
        super().__init__()
        self._service = service

    @handle_errors
    def create_link(self, technology_id: str, data: dict[str, Any]) -> Optional[Link]:
        """Create a new reference link for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The created :class:`Link`, or ``None`` on failure.
        """
        link = self._service.create_link(technology_id, data)
        self.success_message.emit("Enlace creado correctamente.")
        self.data_changed.emit()
        return link

    @handle_errors
    def update_link(self, link_id: str, technology_id: str, data: dict[str, Any]) -> Optional[Link]:
        """Update an existing reference link.

        Args:
            link_id: Id of the link to update.
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The updated :class:`Link`, or ``None`` on failure.
        """
        link = self._service.update_link(link_id, technology_id, data)
        self.success_message.emit("Enlace actualizado correctamente.")
        self.data_changed.emit()
        return link

    @handle_errors
    def delete_link(self, link_id: str) -> bool:
        """Delete a reference link.

        Args:
            link_id: Id of the link to delete.

        Returns:
            ``True`` on success, ``None`` (falsy) on failure.
        """
        self._service.delete_link(link_id)
        self.success_message.emit("Enlace eliminado correctamente.")
        self.data_changed.emit()
        return True

    @handle_errors
    def list_links(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "link_type",
        sort_order: int = 1,
    ) -> Optional[list[Link]]:
        """List reference links for a technology.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Link` records, or ``None`` on failure.
        """
        return self._service.list_links(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )

    @handle_errors
    def open_link(self, url: str) -> bool:
        """Validate a URL and open it in the system's default browser.

        Args:
            url: The URL to open.

        Returns:
            ``True`` if the URL was valid and the browser was launched;
            ``None`` (falsy) if validation failed.
        """
        if not is_valid_url(url):
            self.error_occurred.emit(f"La URL '{url}' no es válida.")
            return False
        webbrowser.open(url)
        return True
