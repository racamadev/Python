"""Business logic for the technology master catalog."""

from __future__ import annotations

from typing import Any, Optional

from src.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from src.infrastructure.logging import get_logger
from src.models import Technology
from src.repositories import (
    AlternativesRepository,
    LinksRepository,
    NotesRepository,
    TechnologyRepository,
)
from src.utils.constants import YES_NO_CHOICES
from src.utils.date_helpers import now_utc
from src.utils.validators import (
    validate_choice,
    validate_object_id,
    validate_optional_date,
    validate_optional_string,
    validate_required_string,
)

logger = get_logger(__name__)


class TechnologyService:
    """Encapsulates validation, business rules and orchestration for
    technology master records, including cascading deletes of related
    notes, alternatives and links.

    Args:
        repository: Data-access repository for the technology collection.
        notes_repository: Used to cascade-delete related notes.
        alternatives_repository: Used to cascade-delete related alternatives.
        links_repository: Used to cascade-delete related links.
    """

    def __init__(
        self,
        repository: TechnologyRepository,
        notes_repository: NotesRepository,
        alternatives_repository: AlternativesRepository,
        links_repository: LinksRepository,
    ) -> None:
        self._repository = repository
        self._notes_repository = notes_repository
        self._alternatives_repository = alternatives_repository
        self._links_repository = links_repository

    def _validate_payload(
        self, data: dict[str, Any], exclude_id: Optional[str] = None
    ) -> Technology:
        """Validate and sanitize raw form data into a :class:`Technology`.

        Args:
            data: Raw input dictionary from the presentation layer.
            exclude_id: Existing record id to exclude from the uniqueness
                check (used when updating).

        Returns:
            A validated, sanitized :class:`Technology` instance.

        Raises:
            ValidationError: If any field fails validation.
            DuplicateRecordError: If ``tech_code`` is already in use.
        """
        tech_code = validate_required_string(data.get("tech_code"), "tech_code")
        tech_product = validate_required_string(data.get("tech_product"), "tech_product")
        tech_std = validate_choice(data.get("tech_std", "No"), "tech_std", YES_NO_CHOICES)
        tech_trend = validate_choice(data.get("tech_trend", "No"), "tech_trend", YES_NO_CHOICES)

        if self._repository.code_exists(tech_code, exclude_id=exclude_id):
            raise DuplicateRecordError(f"Ya existe una tecnología con el código '{tech_code}'.")

        return Technology(
            tech_code=tech_code,
            tech_product=tech_product,
            tech_std=tech_std,
            tech_trend=tech_trend,
            tech_type=validate_optional_string(data.get("tech_type")),
            tech_classif=validate_optional_string(data.get("tech_classif")),
            tech_lifecycle=validate_optional_string(data.get("tech_lifecycle")),
            tech_date=validate_optional_date(data.get("tech_date"), "tech_date"),
            tech_start_date=validate_optional_date(data.get("tech_start_date"), "tech_start_date"),
            tech_divest_date=validate_optional_date(
                data.get("tech_divest_date"), "tech_divest_date"
            ),
            tech_end_date=validate_optional_date(data.get("tech_end_date"), "tech_end_date"),
        )

    def create_technology(self, data: dict[str, Any]) -> Technology:
        """Validate and persist a new technology record.

        Args:
            data: Raw form data.

        Returns:
            The persisted :class:`Technology`, including its new id.

        Raises:
            ValidationError: If validation fails.
            DuplicateRecordError: If ``tech_code`` is already in use.
        """
        technology = self._validate_payload(data)
        now = now_utc()
        technology.created_at = now
        technology.updated_at = now
        record_id = self._repository.insert_one(technology.to_dict())
        technology.id = record_id
        logger.info("Technology created: %s (%s)", technology.tech_code, record_id)
        return technology

    def update_technology(self, technology_id: str, data: dict[str, Any]) -> Technology:
        """Validate and update an existing technology record.

        Args:
            technology_id: Id of the record to update.
            data: Raw form data with the new values.

        Returns:
            The updated :class:`Technology`.

        Raises:
            ValidationError: If validation fails.
            DuplicateRecordError: If ``tech_code`` is already in use by
                another record.
            RecordNotFoundError: If the record does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        technology = self._validate_payload(data, exclude_id=technology_id)
        technology.id = technology_id
        technology.updated_at = now_utc()

        update_payload = technology.to_dict()
        update_payload.pop("created_at", None)

        matched = self._repository.update_one(technology_id, update_payload)
        if not matched:
            raise RecordNotFoundError("La tecnología solicitada no existe.")
        logger.info("Technology updated: %s (%s)", technology.tech_code, technology_id)
        return technology

    def delete_technology(self, technology_id: str) -> None:
        """Delete a technology and cascade-delete its related detail records.

        Args:
            technology_id: Id of the record to delete.

        Raises:
            RecordNotFoundError: If the record does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        deleted = self._repository.delete_one(technology_id)
        if not deleted:
            raise RecordNotFoundError("La tecnología solicitada no existe.")

        notes_removed = self._notes_repository.delete_by_technology_id(technology_id)
        alternatives_removed = self._alternatives_repository.delete_by_technology_id(
            technology_id
        )
        links_removed = self._links_repository.delete_by_technology_id(technology_id)

        logger.info(
            "Technology deleted: %s (notes=%d, alternatives=%d, links=%d)",
            technology_id,
            notes_removed,
            alternatives_removed,
            links_removed,
        )

    def get_technology(self, technology_id: str) -> Technology:
        """Retrieve a single technology by id.

        Args:
            technology_id: Id of the record to fetch.

        Returns:
            The matching :class:`Technology`.

        Raises:
            RecordNotFoundError: If the record does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        document = self._repository.find_by_id(technology_id)
        if document is None:
            raise RecordNotFoundError("La tecnología solicitada no existe.")
        return Technology.from_dict(document)

    def list_technologies(
        self,
        search_text: str = "",
        column_filters: Optional[dict[str, str]] = None,
        sort_field: str = "tech_code",
        sort_order: int = 1,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Technology], int]:
        """List technologies with search, per-column filters, sort and paging.

        Args:
            search_text: Free-text search term.
            column_filters: Per-column filter values.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.
            page: 1-based page number.
            page_size: Number of records per page.

        Returns:
            A tuple of ``(technologies, total_count)``.
        """
        documents, total = self._repository.search_paginated(
            search_text=search_text,
            column_filters=column_filters,
            sort_field=sort_field,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
        return [Technology.from_dict(doc) for doc in documents], total

    def list_all(self) -> list[Technology]:
        """Return every technology record, for reporting/export purposes.

        Returns:
            All technology records, sorted by ``tech_code``.
        """
        documents = self._repository.find_all(sort=[("tech_code", 1)])
        return [Technology.from_dict(doc) for doc in documents]
