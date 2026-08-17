"""Unit tests for AlternativesService."""

from __future__ import annotations

import pytest

from src.exceptions import RecordNotFoundError


class TestAlternativesService:
    def test_create_alternative_for_existing_technology(
        self, technology_service, alternatives_service, sample_technology_data
    ):
        technology = technology_service.create_technology(sample_technology_data)
        alternative = alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt Product"}
        )
        assert alternative.id is not None
        assert alternative.technology_id == technology.id

    def test_create_alternative_for_missing_technology_raises(self, alternatives_service):
        with pytest.raises(RecordNotFoundError):
            alternatives_service.create_alternative(
                "507f1f77bcf86cd799439011",
                {"alternative_code": "ALT-1", "alternative_product": "Alt Product"},
            )

    def test_get_alternative(self, technology_service, alternatives_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        alternative = alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt Product"}
        )
        fetched = alternatives_service.get_alternative(alternative.id)
        assert fetched.alternative_code == "ALT-1"

    def test_get_missing_alternative_raises(self, alternatives_service):
        with pytest.raises(RecordNotFoundError):
            alternatives_service.get_alternative("507f1f77bcf86cd799439011")

    def test_update_alternative(self, technology_service, alternatives_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        alternative = alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt Product"}
        )
        updated = alternatives_service.update_alternative(
            alternative.id, technology.id, {"alternative_code": "ALT-2", "alternative_product": "New"}
        )
        assert updated.alternative_code == "ALT-2"

    def test_delete_nonexistent_alternative_raises(self, alternatives_service):
        with pytest.raises(RecordNotFoundError):
            alternatives_service.delete_alternative("507f1f77bcf86cd799439011")

    def test_list_all(self, technology_service, alternatives_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt Product"}
        )
        assert len(alternatives_service.list_all()) == 1
