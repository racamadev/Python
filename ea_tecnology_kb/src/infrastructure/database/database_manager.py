"""Database-level operations: collection access and index management."""

from __future__ import annotations

from typing import Optional

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from src.exceptions import DatabaseConnectionError
from src.infrastructure.database.mongo_connection import MongoConnection
from src.infrastructure.logging import get_logger
from src.utils.constants import (
    COLLECTION_ALTERNATIVES,
    COLLECTION_LINKS,
    COLLECTION_NOTES,
    COLLECTION_TECHNOLOGIES,
)

logger = get_logger(__name__)


class DatabaseManager:
    """Facade over :class:`MongoConnection` for collection/index access.

    Centralizes the set of collections used by the application and the
    indexes that must exist for correct, performant querying, per the
    data-model specification.
    """

    def __init__(self, connection: Optional[MongoConnection] = None) -> None:
        self._connection = connection or MongoConnection.instance()

    @property
    def database(self) -> Database:
        """Return the active application database."""
        return self._connection.database

    def get_collection(self, name: str) -> Collection:
        """Return a handle to the named collection.

        Args:
            name: Collection name (see ``src.utils.constants``).

        Returns:
            The requested :class:`~pymongo.collection.Collection`.
        """
        return self.database[name]

    def ensure_indexes(self) -> None:
        """Create all required indexes if they do not already exist.

        Raises:
            DatabaseConnectionError: If index creation fails due to a
                connectivity or server-side error.
        """
        try:
            technologies = self.get_collection(COLLECTION_TECHNOLOGIES)
            technologies.create_index(
                [("tech_code", ASCENDING)], unique=True, name="ux_tech_code"
            )
            technologies.create_index([("tech_product", ASCENDING)], name="ix_tech_product")
            technologies.create_index([("tech_type", ASCENDING)], name="ix_tech_type")

            notes = self.get_collection(COLLECTION_NOTES)
            notes.create_index([("technology_id", ASCENDING)], name="ix_notes_technology_id")

            alternatives = self.get_collection(COLLECTION_ALTERNATIVES)
            alternatives.create_index(
                [("technology_id", ASCENDING)], name="ix_alternatives_technology_id"
            )

            links = self.get_collection(COLLECTION_LINKS)
            links.create_index([("technology_id", ASCENDING)], name="ix_links_technology_id")

            logger.info("MongoDB indexes verified/created successfully.")
        except PyMongoError as exc:
            logger.error("Failed to create indexes: %s", exc)
            raise DatabaseConnectionError(
                "Failed to create required MongoDB indexes.", details=str(exc)
            ) from exc
