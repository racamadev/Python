"""Technology domain model (master record)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId


@dataclass
class Technology:
    """Represents a single technology/product tracked in the master catalog.

    Attributes:
        id: MongoDB ObjectId as a string, ``None`` for unsaved records.
        tech_code: Unique business code identifying the technology.
        tech_date: Date the record was catalogued.
        tech_type: Free-text category/type of the technology.
        tech_product: Product/technology display name.
        tech_std: Whether the technology is a corporate standard (``Yes``/``No``).
        tech_classif: Classification (e.g. Strategic, Tactical, Legacy).
        tech_lifecycle: Current lifecycle stage.
        tech_start_date: Date the technology entered active use.
        tech_divest_date: Planned/actual divestment date.
        tech_end_date: End-of-life date.
        tech_trend: Whether the technology is trending (``Yes``/``No``).
        created_at: Record creation timestamp (server-managed).
        updated_at: Last update timestamp (server-managed).
    """

    tech_code: str
    tech_product: str
    tech_date: Optional[datetime] = None
    tech_type: str = ""
    tech_std: str = "No"
    tech_classif: str = ""
    tech_lifecycle: str = ""
    tech_start_date: Optional[datetime] = None
    tech_divest_date: Optional[datetime] = None
    tech_end_date: Optional[datetime] = None
    tech_trend: str = "No"
    id: Optional[str] = None
    created_at: Optional[datetime] = field(default=None)
    updated_at: Optional[datetime] = field(default=None)

    def to_dict(self, include_id: bool = False) -> dict[str, Any]:
        """Serialize the model into a MongoDB-ready dictionary.

        Args:
            include_id: When ``True`` and :attr:`id` is set, includes
                ``_id`` as an :class:`~bson.objectid.ObjectId` in the output.

        Returns:
            A dictionary suitable for ``insert_one``/``update_one``.
        """
        data: dict[str, Any] = {
            "tech_code": self.tech_code,
            "tech_date": self.tech_date,
            "tech_type": self.tech_type,
            "tech_product": self.tech_product,
            "tech_std": self.tech_std,
            "tech_classif": self.tech_classif,
            "tech_lifecycle": self.tech_lifecycle,
            "tech_start_date": self.tech_start_date,
            "tech_divest_date": self.tech_divest_date,
            "tech_end_date": self.tech_end_date,
            "tech_trend": self.tech_trend,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if include_id and self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Technology":
        """Build a :class:`Technology` from a MongoDB document.

        Args:
            data: Raw document as returned by PyMongo.

        Returns:
            The corresponding :class:`Technology` instance.
        """
        return cls(
            id=str(data["_id"]) if data.get("_id") is not None else None,
            tech_code=data.get("tech_code", ""),
            tech_date=data.get("tech_date"),
            tech_type=data.get("tech_type", ""),
            tech_product=data.get("tech_product", ""),
            tech_std=data.get("tech_std", "No"),
            tech_classif=data.get("tech_classif", ""),
            tech_lifecycle=data.get("tech_lifecycle", ""),
            tech_start_date=data.get("tech_start_date"),
            tech_divest_date=data.get("tech_divest_date"),
            tech_end_date=data.get("tech_end_date"),
            tech_trend=data.get("tech_trend", "No"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
