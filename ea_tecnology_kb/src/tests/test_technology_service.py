"""Unit tests for TechnologyService."""

from __future__ import annotations

import pytest

from src.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError


class TestCreateTechnology:
    def test_creates_valid_technology(self, technology_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        assert technology.id is not None
        assert technology.tech_code == "TC-001"
        assert technology.created_at is not None

    def test_missing_code_raises_validation_error(self, technology_service, sample_technology_data):
        data = dict(sample_technology_data, tech_code="")
        with pytest.raises(ValidationError):
            technology_service.create_technology(data)

    def test_missing_product_raises_validation_error(self, technology_service, sample_technology_data):
        data = dict(sample_technology_data, tech_product="")
        with pytest.raises(ValidationError):
            technology_service.create_technology(data)

    def test_invalid_std_choice_raises(self, technology_service, sample_technology_data):
        data = dict(sample_technology_data, tech_std="Maybe")
        with pytest.raises(ValidationError):
            technology_service.create_technology(data)

    def test_invalid_trend_choice_raises(self, technology_service, sample_technology_data):
        data = dict(sample_technology_data, tech_trend="Maybe")
        with pytest.raises(ValidationError):
            technology_service.create_technology(data)

    def test_duplicate_code_raises(self, technology_service, sample_technology_data):
        technology_service.create_technology(sample_technology_data)
        with pytest.raises(DuplicateRecordError):
            technology_service.create_technology(sample_technology_data)


class TestUpdateTechnology:
    def test_updates_existing_record(self, technology_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        updated_data = dict(sample_technology_data, tech_product="MySQL")
        updated = technology_service.update_technology(technology.id, updated_data)
        assert updated.tech_product == "MySQL"

    def test_update_nonexistent_raises(self, technology_service, sample_technology_data):
        with pytest.raises(RecordNotFoundError):
            technology_service.update_technology("507f1f77bcf86cd799439011", sample_technology_data)


class TestDeleteTechnology:
    def test_delete_cascades_related_records(
        self, technology_service, notes_service, alternatives_service, links_service, sample_technology_data
    ):
        technology = technology_service.create_technology(sample_technology_data)
        notes_service.create_note(technology.id, {"note_type": "General", "note_card": "Note"})
        alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt Product"}
        )
        links_service.create_link(
            technology.id, {"link_type": "Documentation", "link_url": "https://example.com"}
        )

        technology_service.delete_technology(technology.id)

        assert notes_service.list_notes(technology.id) == []
        with pytest.raises(RecordNotFoundError):
            technology_service.get_technology(technology.id)

    def test_delete_nonexistent_raises(self, technology_service):
        with pytest.raises(RecordNotFoundError):
            technology_service.delete_technology("507f1f77bcf86cd799439011")


class TestListTechnologies:
    def test_list_returns_created_technology(self, technology_service, sample_technology_data):
        technology_service.create_technology(sample_technology_data)
        technologies, total = technology_service.list_technologies()
        assert total == 1
        assert technologies[0].tech_code == "TC-001"
