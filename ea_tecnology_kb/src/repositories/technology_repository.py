"""Repository for the ``technologies`` master collection."""

from __future__ import annotations

import re
from typing import Any, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from src.exceptions import RepositoryError
from src.infrastructure.logging import get_logger
from src.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_SEARCHABLE_FIELDS = [
    "tech_code",
    "tech_type",
    "tech_product",
    "tech_std",
    "tech_classif",
    "tech_lifecycle",
    "tech_trend",
]


class TechnologyRepository(BaseRepository):
    """Data access for the technology master catalog.

    Args:
        collection: The ``technologies`` PyMongo collection.
    """

    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)

    def find_by_code(self, tech_code: str) -> Optional[dict[str, Any]]:
        """Find a technology by its unique business code.

        Args:
            tech_code: The technology code to look up.

        Returns:
            The matching document, or ``None`` if not found.
        """
        return self.find_one({"tech_code": tech_code})

    def code_exists(self, tech_code: str, exclude_id: Optional[str] = None) -> bool:
        """Check whether a technology code is already in use.

        Args:
            tech_code: The technology code to check.
            exclude_id: Optional id to exclude from the check (used on update).

        Returns:
            ``True`` if another record already uses ``tech_code``.
        """
        query: dict[str, Any] = {"tech_code": tech_code}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.exists(query)

    def search_paginated(
        self,
        search_text: str = "",
        column_filters: Optional[dict[str, str]] = None,
        sort_field: str = "tech_code",
        sort_order: int = 1,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search, filter, sort and paginate the technology catalog.

        Args:
            search_text: Free-text term matched (case-insensitive, partial)
                against all searchable fields.
            column_filters: Per-column filter values, keyed by field name.
            sort_field: Field to sort by.
            sort_order: ``1`` for ascending, ``-1`` for descending.
            page: 1-based page number.
            page_size: Number of records per page.

        Returns:
            A tuple of ``(page_of_documents, total_matching_count)``.

        Raises:
            RepositoryError: On a database error.
        """
        query: dict[str, Any] = {}

        if search_text:
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            query["$or"] = [{field: pattern} for field in _SEARCHABLE_FIELDS]

        if column_filters:
            for field, value in column_filters.items():
                if value:
                    query[field] = re.compile(re.escape(value), re.IGNORECASE)

        try:
            total = self.count(query)
            skip = max(0, (page - 1) * page_size)
            documents = self.find_all(
                filters=query,
                sort=[(sort_field, sort_order)],
                skip=skip,
                limit=page_size,
            )
            return documents, total
        except PyMongoError as exc:
            logger.error("Error searching technologies: %s", exc)
            raise RepositoryError("Error al buscar tecnologías.", details=str(exc)) from exc
