"""Alternative domain model (technology detail: tech_alternatives)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bson import ObjectId


@dataclass
class Alternative:
    """A competing/alternative product recorded against a technology.

    Attributes:
        id: MongoDB ObjectId as a string, ``None`` for unsaved records.
        technology_id: Foreign key referencing the owning technology.
        alternative_code: Business code of the alternative product.
        alternative_product: Display name of the alternative product.
        alternative_card: Free-text, multi-line description/rationale.
    """

    technology_id: str
    alternative_code: str = ""
    alternative_product: str = ""
    alternative_card: str = ""
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
            "alternative_code": self.alternative_code,
            "alternative_product": self.alternative_product,
            "alternative_card": self.alternative_card,
        }
        if include_id and self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Alternative":
        """Build an :class:`Alternative` from a MongoDB document.

        Args:
            data: Raw document as returned by PyMongo.

        Returns:
            The corresponding :class:`Alternative` instance.
        """
        return cls(
            id=str(data["_id"]) if data.get("_id") is not None else None,
            technology_id=str(data.get("technology_id", "")),
            alternative_code=data.get("alternative_code", ""),
            alternative_product=data.get("alternative_product", ""),
            alternative_card=data.get("alternative_card", ""),
        )
