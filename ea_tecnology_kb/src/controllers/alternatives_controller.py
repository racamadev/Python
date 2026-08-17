"""Controller mediating between alternatives views and :class:`AlternativesService`."""

from __future__ import annotations

from typing import Any, Optional

from src.controllers.base_controller import BaseController, handle_errors
from src.models import Alternative
from src.services.alternatives_service import AlternativesService


class AlternativesController(BaseController):
    """Coordinates CRUD and listing operations for alternative products.

    Args:
        service: Business-layer service for alternative records.
    """

    def __init__(self, service: AlternativesService) -> None:
        super().__init__()
        self._service = service

    @handle_errors
    def create_alternative(self, technology_id: str, data: dict[str, Any]) -> Optional[Alternative]:
        """Create a new alternative for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The created :class:`Alternative`, or ``None`` on failure.
        """
        alternative = self._service.create_alternative(technology_id, data)
        self.success_message.emit("Alternativa creada correctamente.")
        self.data_changed.emit()
        return alternative

    @handle_errors
    def update_alternative(
        self, alternative_id: str, technology_id: str, data: dict[str, Any]
    ) -> Optional[Alternative]:
        """Update an existing alternative.

        Args:
            alternative_id: Id of the alternative to update.
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The updated :class:`Alternative`, or ``None`` on failure.
        """
        alternative = self._service.update_alternative(alternative_id, technology_id, data)
        self.success_message.emit("Alternativa actualizada correctamente.")
        self.data_changed.emit()
        return alternative

    @handle_errors
    def delete_alternative(self, alternative_id: str) -> bool:
        """Delete an alternative.

        Args:
            alternative_id: Id of the alternative to delete.

        Returns:
            ``True`` on success, ``None`` (falsy) on failure.
        """
        self._service.delete_alternative(alternative_id)
        self.success_message.emit("Alternativa eliminada correctamente.")
        self.data_changed.emit()
        return True

    @handle_errors
    def list_alternatives(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "alternative_product",
        sort_order: int = 1,
    ) -> Optional[list[Alternative]]:
        """List alternatives for a technology.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Alternative` records, or ``None``
            on failure.
        """
        return self._service.list_alternatives(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )
