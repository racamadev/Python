"""Business logic for technology alternatives (tech_alternatives)."""

from __future__ import annotations

from typing import Any

from src.exceptions import RecordNotFoundError
from src.infrastructure.logging import get_logger
from src.models import Alternative
from src.repositories import AlternativesRepository, TechnologyRepository
from src.utils.validators import validate_object_id, validate_optional_string

logger = get_logger(__name__)


class AlternativesService:
    """Encapsulates validation and business rules for alternative products.

    Args:
        repository: Data-access repository for the ``tech_alternatives`` collection.
        technology_repository: Used to validate the owning technology exists.
    """

    def __init__(
        self, repository: AlternativesRepository, technology_repository: TechnologyRepository
    ) -> None:
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

    def create_alternative(self, technology_id: str, data: dict[str, Any]) -> Alternative:
        """Validate and persist a new alternative for a technology.

        Args:
            technology_id: Owning technology's id.
            data: Raw form data.

        Returns:
            The persisted :class:`Alternative`, including its new id.

        Raises:
            ValidationError: If validation fails.
            RecordNotFoundError: If the owning technology does not exist.
        """
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        alternative = Alternative(
            technology_id=technology_id,
            alternative_code=validate_optional_string(data.get("alternative_code")),
            alternative_product=validate_optional_string(data.get("alternative_product")),
            alternative_card=validate_optional_string(data.get("alternative_card")),
        )
        record_id = self._repository.insert_one(alternative.to_dict())
        alternative.id = record_id
        logger.info("Alternative created for technology %s (%s)", technology_id, record_id)
        return alternative

    def update_alternative(
        self, alternative_id: str, technology_id: str, data: dict[str, Any]
    ) -> Alternative:
        """Validate and update an existing alternative.

        Args:
            alternative_id: Id of the alternative to update.
            technology_id: Owning technology's id.
            data: Raw form data with the new values.

        Returns:
            The updated :class:`Alternative`.

        Raises:
            ValidationError: If validation fails.
            RecordNotFoundError: If the alternative or technology does not exist.
        """
        validate_object_id(alternative_id, "alternative_id")
        validate_object_id(technology_id, "technology_id")
        self._ensure_technology_exists(technology_id)

        alternative = Alternative(
            id=alternative_id,
            technology_id=technology_id,
            alternative_code=validate_optional_string(data.get("alternative_code")),
            alternative_product=validate_optional_string(data.get("alternative_product")),
            alternative_card=validate_optional_string(data.get("alternative_card")),
        )
        matched = self._repository.update_one(alternative_id, alternative.to_dict())
        if not matched:
            raise RecordNotFoundError("La alternativa solicitada no existe.")
        logger.info("Alternative updated: %s", alternative_id)
        return alternative

    def delete_alternative(self, alternative_id: str) -> None:
        """Delete a single alternative.

        Args:
            alternative_id: Id of the alternative to delete.

        Raises:
            RecordNotFoundError: If the alternative does not exist.
        """
        validate_object_id(alternative_id, "alternative_id")
        if not self._repository.delete_one(alternative_id):
            raise RecordNotFoundError("La alternativa solicitada no existe.")
        logger.info("Alternative deleted: %s", alternative_id)

    def get_alternative(self, alternative_id: str) -> Alternative:
        """Retrieve a single alternative by id.

        Args:
            alternative_id: Id of the alternative to fetch.

        Returns:
            The matching :class:`Alternative`.

        Raises:
            RecordNotFoundError: If the alternative does not exist.
        """
        validate_object_id(alternative_id, "alternative_id")
        document = self._repository.find_by_id(alternative_id)
        if document is None:
            raise RecordNotFoundError("La alternativa solicitada no existe.")
        return Alternative.from_dict(document)

    def list_alternatives(
        self,
        technology_id: str,
        search_text: str = "",
        sort_field: str = "alternative_product",
        sort_order: int = 1,
    ) -> list[Alternative]:
        """List alternatives for a technology, with optional search and sorting.

        Args:
            technology_id: Owning technology's id.
            search_text: Optional free-text search term.
            sort_field: Field to sort by.
            sort_order: ``1`` ascending, ``-1`` descending.

        Returns:
            The matching list of :class:`Alternative` records.
        """
        validate_object_id(technology_id, "technology_id")
        documents = self._repository.find_by_technology_id(
            technology_id, search_text=search_text, sort_field=sort_field, sort_order=sort_order
        )
        return [Alternative.from_dict(doc) for doc in documents]

    def list_all(self) -> list[Alternative]:
        """Return every alternative record, for reporting/export purposes.

        Returns:
            All alternative records.
        """
        return [Alternative.from_dict(doc) for doc in self._repository.find_all()]
