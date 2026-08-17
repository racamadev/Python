"""Business logic for technology reference links (tech_links)."""

from __future__ import annotations

from typing import Any

from src.exceptions import RecordNotFoundError
from src.infrastructure.logging import get_logger
from src.models import Link
from src.repositories import LinksRepository, TechnologyRepository
from src.utils.validators import validate_object_id, validate_optional_string, validate_url

logger = get_logger(__name__)


class LinksService:
    """Encapsulates validation and business rules for reference links.

    Args:
        repository: Data-access repository for the ``tech_links`` collection.
        technology_repository: Used to validate the owning technology exists.
    """

    def __init__(self, repository: LinksRepository, technology_repository: TechnologyRepository) -> None:
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

    def create_link(self, technology_id: str, data: dict[str, Any]) -> Link:
        """Validate and persist a new reference link for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data.

        Returns:
            The persisted :class:`Link`, including its new id.

        Raises:
            ValidationError: If validation fails (including malformed URL).
            RecordNotFoundError: If the owning technology does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        link = Link(
            technology_id=technology_id,
            link_type=validate_optional_string(data.get("link_type")),
            link_url=validate_url(data.get("link_url"), "link_url"),
            link_source=validate_optional_string(data.get("link_source")),
            link_quality=validate_optional_string(data.get("link_quality")),
        )
        record_id = self._repository.insert_one(link.to_dict())
        link.id = record_id
        logger.info("Link created for technology %s (%s)", technology_id, record_id)
        return link

    def update_link(self, link_id: str, technology_id: str, data: dict[str, Any]) -> Link:
        """Validate and update an existing reference link.

        Args:
            link_id: Id of the link to update.
            technology_id: Owning technology's id.
            data: Raw form data with the new values.

        Returns:
            The updated :class:`Link`.

        Raises:
            ValidationError: If validation fails (including malformed URL).
            RecordNotFoundError: If the link or technology does not exist.
        """
        validate_object_id(link_id, "link_id")
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        link = Link(
            id=link_id,
            technology_id=technology_id,
            link_type=validate_optional_string(data.get("link_type")),
            link_url=validate_url(data.get("link_url"), "link_url"),
            link_source=validate_optional_string(data.get("link_source")),
            link_quality=validate_optional_string(data.get("link_quality")),
        )
        matched = self._repository.update_one(link_id, link.to_dict())
        if not matched:
            raise RecordNotFoundError("El enlace solicitado no existe.")
        logger.info("Link updated: %s", link_id)
        return link

    def delete_link(self, link_id: str) -> None:
        """Delete a single reference link.

        Args:
            link_id: Id of the link to delete.

        Raises:
            RecordNotFoundError: If the link does not exist.
        """
        validate_object_id(link_id, "link_id")
        if not self._repository.delete_one(link_id):
            raise RecordNotFoundError("El enlace solicitado no existe.")
        logger.info("Link deleted: %s", link_id)

    def get_link(self, link_id: str) -> Link:
        """Retrieve a single reference link by id.

        Args:
            link_id: Id of the link to fetch.

        Returns:
            The matching :class:`Link`.

        Raises:
            RecordNotFoundError: If the link does not exist.
        """
        validate_object_id(link_id, "link_id")
        document = self._repository.find_by_id(link_id)
        if document is None:
            raise RecordNotFoundError("El enlace solicitado no existe.")
        return Link.from_dict(document)

    def list_links(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "link_type",
        sort_order: int = 1,
    ) -> list[Link]:
        """List reference links for a technology, with optional search/sorting.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Link` records.
        """
        validate_object_id(technology_id, "technology_id")
        documents = self._repository.find_by_technology_id(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )
        return [Link.from_dict(doc) for doc in documents]

    def list_all(self) -> list[Link]:
        """Return every reference link record, for reporting/export purposes.

        Returns:
            All link records.
        """
        return [Link.from_dict(doc) for doc in self._repository.find_all()]
