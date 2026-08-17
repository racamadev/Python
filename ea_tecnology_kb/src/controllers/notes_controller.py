"""Controller mediating between notes views and :class:`NotesService`."""

from __future__ import annotations

from typing import Any, Optional

from src.controllers.base_controller import BaseController, handle_errors
from src.models import Note
from src.services.notes_service import NotesService


class NotesController(BaseController):
    """Coordinates CRUD and listing operations for technology notes.

    Args:
        service: Business-layer service for note records.
    """

    def __init__(self, service: NotesService) -> None:
        super().__init__()
        self._service = service

    @handle_errors
    def create_note(self, technology_id: str, data: dict[str, Any]) -> Optional[Note]:
        """Create a new note for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The created :class:`Note`, or ``None`` on failure.
        """
        note = self._service.create_note(technology_id, data)
        self.success_message.emit("Nota creada correctamente.")
        self.data_changed.emit()
        return note

    @handle_errors
    def update_note(self, note_id: str, technology_id: str, data: dict[str, Any]) -> Optional[Note]:
        """Update an existing note.

        Args:
            note_id: Id of the note to update.
            technology_id: Owning technology's id.
            data: Raw form data collected from the view.

        Returns:
            The updated :class:`Note`, or ``None`` on failure.
        """
        note = self._service.update_note(note_id, technology_id, data)
        self.success_message.emit("Nota actualizada correctamente.")
        self.data_changed.emit()
        return note

    @handle_errors
    def delete_note(self, note_id: str) -> bool:
        """Delete a note.

        Args:
            note_id: Id of the note to delete.

        Returns:
            ``True`` on success, ``None`` (falsy) on failure.
        """
        self._service.delete_note(note_id)
        self.success_message.emit("Nota eliminada correctamente.")
        self.data_changed.emit()
        return True

    @handle_errors
    def list_notes(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "note_date",
        sort_order: int = -1,
    ) -> Optional[list[Note]]:
        """List notes for a technology.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Note` records, or ``None`` on failure.
        """
        return self._service.list_notes(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )
