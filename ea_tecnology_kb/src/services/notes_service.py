"""Business logic for technology notes (tech_notes)."""

from __future__ import annotations

from typing import Any, Optional

from src.exceptions import RecordNotFoundError
from src.infrastructure.logging import get_logger
from src.models import Note
from src.repositories import NotesRepository, TechnologyRepository
from src.utils.validators import (
    validate_object_id,
    validate_optional_date,
    validate_optional_string,
)

logger = get_logger(__name__)


class NotesService:
    """Encapsulates validation and business rules for technology notes.

    Args:
        repository: Data-access repository for the ``tech_notes`` collection.
        technology_repository: Used to validate the owning technology exists.
    """

    def __init__(self, repository: NotesRepository, technology_repository: TechnologyRepository) -> None:
        self._repository = repository
        self._technology_repository = technology_repository

    def _ensure_technology_exists(self, technology_id: str) -> None:
        """Raise if the referenced technology does not exist.

        Args:
            technology_id: Id of the technology to check.

        Raises:
            RecordNotFoundError: If the technology does not exist.
        """
        if self._technology_repository.find_by_id(technology_id) is None:
            raise RecordNotFoundError("La tecnología asociada no existe.")

    def create_note(self, technology_id: str, data: dict[str, Any]) -> Note:
        """Validate and persist a new note for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data.

        Returns:
            The persisted :class:`Note`, including its new id.

        Raises:
            ValidationError: If validation fails.
            RecordNotFoundError: If the owning technology does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        note = Note(
            technology_id=technology_id,
            note_date=validate_optional_date(data.get("note_date"), "note_date"),
            note_type=validate_optional_string(data.get("note_type")),
            note_card=validate_optional_string(data.get("note_card")),
        )
        record_id = self._repository.insert_one(note.to_dict())
        note.id = record_id
        logger.info("Note created for technology %s (%s)", technology_id, record_id)
        return note

    def update_note(self, note_id: str, technology_id: str, data: dict[str, Any]) -> Note:
        """Validate and update an existing note.

        Args:
            note_id: Id of the note to update.
            technology_id: Owning technology's id.
            data: Raw form data with the new values.

        Returns:
            The updated :class:`Note`.

        Raises:
            ValidationError: If validation fails.
            RecordNotFoundError: If the note or technology does not exist.
        """
        validate_object_id(note_id, "note_id")
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        note = Note(
            id=note_id,
            technology_id=technology_id,
            note_date=validate_optional_date(data.get("note_date"), "note_date"),
            note_type=validate_optional_string(data.get("note_type")),
            note_card=validate_optional_string(data.get("note_card")),
        )
        matched = self._repository.update_one(note_id, note.to_dict())
        if not matched:
            raise RecordNotFoundError("La nota solicitada no existe.")
        logger.info("Note updated: %s", note_id)
        return note

    def delete_note(self, note_id: str) -> None:
        """Delete a single note.

        Args:
            note_id: Id of the note to delete.

        Raises:
            RecordNotFoundError: If the note does not exist.
        """
        validate_object_id(note_id, "note_id")
        if not self._repository.delete_one(note_id):
            raise RecordNotFoundError("La nota solicitada no existe.")
        logger.info("Note deleted: %s", note_id)

    def get_note(self, note_id: str) -> Note:
        """Retrieve a single note by id.

        Args:
            note_id: Id of the note to fetch.

        Returns:
            The matching :class:`Note`.

        Raises:
            RecordNotFoundError: If the note does not exist.
        """
        validate_object_id(note_id, "note_id")
        document = self._repository.find_by_id(note_id)
        if document is None:
            raise RecordNotFoundError("La nota solicitada no existe.")
        return Note.from_dict(document)

    def list_notes(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "note_date",
        sort_order: int = -1,
    ) -> list[Note]:
        """List notes for a technology, with optional search and sorting.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Note` records.
        """
        validate_object_id(technology_id, "technology_id")
        documents = self._repository.find_by_technology_id(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )
        return [Note.from_dict(doc) for doc in documents]

    def list_all(self) -> list[Note]:
        """Return every note record, for reporting/export purposes.

        Returns:
            All note records.
        """
        return [Note.from_dict(doc) for doc in self._repository.find_all()]
