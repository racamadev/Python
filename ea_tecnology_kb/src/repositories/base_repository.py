"""Generic MongoDB repository implementing the Repository Pattern.

Concrete repositories subclass :class:`BaseRepository` to inherit standard
CRUD operations while adding entity-specific queries. All PyMongo errors
are caught here and re-raised as :class:`~src.exceptions.RepositoryError`
so upper layers never depend on PyMongo directly (dependency inversion).
"""

from __future__ import annotations

from typing import Any, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.exceptions import DuplicateRecordError, RepositoryError
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base class providing generic CRUD operations for a MongoDB collection.

    Args:
        collection: The PyMongo collection this repository operates on.
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    @property
    def collection(self) -> Collection:
        """Expose the underlying collection for subclass-specific queries."""
        return self._collection

    def insert_one(self, document: dict[str, Any]) -> str:
        """Insert a single document.

        Args:
            document: The document to persist.

        Returns:
            The inserted document's id as a string.

        Raises:
            DuplicateRecordError: If a unique index constraint is violated.
            RepositoryError: On any other database error.
        """
        try:
            result = self._collection.insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError as exc:
            logger.warning("Duplicate key on insert into %s: %s", self._collection.name, exc)
            raise DuplicateRecordError(
                "Ya existe un registro con ese valor único.", details=str(exc)
            ) from exc
        except PyMongoError as exc:
            logger.error("Error inserting into %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al insertar el registro.", details=str(exc)) from exc

    def find_by_id(self, record_id: str) -> Optional[dict[str, Any]]:
        """Find a single document by its ``_id``.

        Args:
            record_id: The document id as a string.

        Returns:
            The matching document, or ``None`` if not found.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            return self._collection.find_one({"_id": ObjectId(record_id)})
        except PyMongoError as exc:
            logger.error("Error finding by id in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al consultar el registro.", details=str(exc)) from exc

    def find_one(self, filters: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Find the first document matching ``filters``.

        Args:
            filters: MongoDB query filter.

        Returns:
            The matching document, or ``None`` if not found.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            return self._collection.find_one(filters)
        except PyMongoError as exc:
            logger.error("Error finding one in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al consultar el registro.", details=str(exc)) from exc

    def find_all(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[list[tuple[str, int]]] = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list[dict[str, Any]]:
        """Find documents matching ``filters`` with optional sort/pagination.

        Args:
            filters: MongoDB query filter; matches all documents if ``None``.
            sort: List of ``(field, direction)`` tuples.
            skip: Number of documents to skip.
            limit: Maximum number of documents to return (``0`` = no limit).

        Returns:
            A list of matching documents.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            cursor = self._collection.find(filters or {})
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as exc:
            logger.error("Error listing documents in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al listar los registros.", details=str(exc)) from exc

    def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """Count documents matching ``filters``.

        Args:
            filters: MongoDB query filter; counts all documents if ``None``.

        Returns:
            The number of matching documents.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            return self._collection.count_documents(filters or {})
        except PyMongoError as exc:
            logger.error("Error counting documents in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al contar los registros.", details=str(exc)) from exc

    def exists(self, filters: dict[str, Any]) -> bool:
        """Check whether at least one document matches ``filters``.

        Args:
            filters: MongoDB query filter.

        Returns:
            ``True`` if a matching document exists.
        """
        return self.find_one(filters) is not None

    def update_one(self, record_id: str, update: dict[str, Any]) -> bool:
        """Update a single document by id using a ``$set`` update.

        Args:
            record_id: The document id as a string.
            update: Fields to set.

        Returns:
            ``True`` if a document was matched, ``False`` otherwise.

        Raises:
            DuplicateRecordError: If a unique index constraint is violated.
            RepositoryError: On any other database error.
        """
        try:
            result = self._collection.update_one(
                {"_id": ObjectId(record_id)}, {"$set": update}
            )
            return result.matched_count > 0
        except DuplicateKeyError as exc:
            logger.warning("Duplicate key on update in %s: %s", self._collection.name, exc)
            raise DuplicateRecordError(
                "Ya existe un registro con ese valor único.", details=str(exc)
            ) from exc
        except PyMongoError as exc:
            logger.error("Error updating in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al actualizar el registro.", details=str(exc)) from exc

    def delete_one(self, record_id: str) -> bool:
        """Delete a single document by id.

        Args:
            record_id: The document id as a string.

        Returns:
            ``True`` if a document was deleted, ``False`` otherwise.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            result = self._collection.delete_one({"_id": ObjectId(record_id)})
            return result.deleted_count > 0
        except PyMongoError as exc:
            logger.error("Error deleting in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al eliminar el registro.", details=str(exc)) from exc

    def delete_many(self, filters: dict[str, Any]) -> int:
        """Delete all documents matching ``filters``.

        Args:
            filters: MongoDB query filter.

        Returns:
            The number of documents deleted.

        Raises:
            RepositoryError: On a database error.
        """
        try:
            result = self._collection.delete_many(filters)
            return result.deleted_count
        except PyMongoError as exc:
            logger.error("Error bulk deleting in %s: %s", self._collection.name, exc)
            raise RepositoryError("Error al eliminar los registros.", details=str(exc)) from exc
