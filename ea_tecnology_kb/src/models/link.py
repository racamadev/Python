"""Link domain model (technology detail: tech_links)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bson import ObjectId


@dataclass
class Link:
    """A reference link (documentation, article, vendor page...) for a technology.

    Attributes:
        id: MongoDB ObjectId as a string, ``None`` for unsaved records.
        technology_id: Foreign key referencing the owning technology.
        link_type: Category of the link (e.g. Documentation, Vendor).
        link_url: Target URL, must be a valid HTTP(S) address.
        link_source: Source/publisher name.
        link_quality: Subjective quality rating (High/Medium/Low).
    """

    technology_id: str
    link_type: str = ""
    link_url: str = ""
    link_source: str = ""
    link_quality: str = ""
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
            "link_type": self.link_type,
            "link_url": self.link_url,
            "link_source": self.link_source,
            "link_quality": self.link_quality,
        }
        if include_id and self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Link":
        """Build a :class:`Link` from a MongoDB document.

        Args:
            data: Raw document as returned by PyMongo.

        Returns:
            The corresponding :class:`Link` instance.
        """
        return cls(
            id=str(data["_id"]) if data.get("_id") is not None else None,
            technology_id=str(data.get("technology_id", "")),
            link_type=data.get("link_type", ""),
            link_url=data.get("link_url", ""),
            link_source=data.get("link_source", ""),
            link_quality=data.get("link_quality", ""),
        )
