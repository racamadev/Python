"""Note domain model (technology detail: tech_notes)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId


@dataclass
class Note:
    """A note attached to a technology.

    Attributes:
        id: MongoDB ObjectId as a string, ``None`` for unsaved records.
        technology_id: Foreign key referencing the owning technology.
        note_date: Date the note was authored.
        note_type: Category of the note (e.g. Risk, Decision).
        note_card: Free-text, multi-line note content.
    """

    technology_id: str
    note_date: Optional[datetime] = None
    note_type: str = ""
    note_card: str = ""
    id: Optional[str] = None

    def to_dict(self, include_id: bool = False) -> dict[str, Any]:
        """Serialize the model into a MongoDB-ready dictionary.

        Args:
            include_id: When ``True`` and :attr:`id` is set, includes
                ``_id`` in the output.

        Returns:
            A dictionary suitable for ``insert_one``/``update_one``.
        """
        data: dict[str, Any] = {
            "technology_id": ObjectId(self.technology_id),
            "note_date": self.note_date,
            "note_type": self.note_type,
            "note_card": self.note_card,
        }
        if include_id and self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        """Build a :class:`Note` from a MongoDB document.

        Args:
            data: Raw document as returned by PyMongo.

        Returns:
            The corresponding :class:`Note` instance.
        """
        return cls(
            id=str(data["_id"]) if data.get("_id") is not None else None,
            technology_id=str(data.get("technology_id", "")),
            note_date=data.get("note_date"),
            note_type=data.get("note_type", ""),
            note_card=data.get("note_card", ""),
        )
