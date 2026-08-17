"""Repository for the ``tech_notes`` detail collection."""

from __future__ import annotations

import re
from typing import Any, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING

from src.repositories.base_repository import BaseRepository

_SEARCHABLE_FIELDS = ["note_type", "note_card"]


class NotesRepository(BaseRepository):
    """Data access for notes attached to a technology.

    Args:
        collection: The ``tech_notes`` PyMongo collection.
    """

    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)

    def find_by_technology_id(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "note_date",
        sort_order: int = -1,
    ) -> list[dict[str, Any]]:
        """List notes for a technology, optionally filtered and sorted.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text filter across searchable fields.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching, sorted list of note documents.
        """
        query: dict[str, Any] = {"technology_id": ObjectId(technology_id)}
        if search_text:
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            query["$or"] = [{field: pattern} for field in _SEARCHABLE_FIELDS]
        direction = ASCENDING if sort_order >= 0 else DESCENDING
        return self.find_all(filters=query, sort=[(sort_field, direction)])

    def delete_by_technology_id(self, technology_id: str) -> int:
        """Delete all notes belonging to a technology (cascade delete).

        Args:
            technology_id: Owning technology's id.

        Returns:
            The number of documents deleted.
        """
        return self.delete_many({"technology_id": ObjectId(technology_id)})
