"""Unit tests for LinksService."""

from __future__ import annotations

import pytest

from src.exceptions import RecordNotFoundError, ValidationError


class TestLinksService:
    def test_create_link_with_valid_url(self, technology_service, links_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        link = links_service.create_link(
            technology.id,
            {"link_type": "Documentation", "link_url": "https://example.com", "link_source": "Vendor"},
        )
        assert link.id is not None
        assert link.link_url == "https://example.com"

    def test_create_link_with_invalid_url_raises(
        self, technology_service, links_service, sample_technology_data
    ):
        technology = technology_service.create_technology(sample_technology_data)
        with pytest.raises(ValidationError):
            links_service.create_link(technology.id, {"link_type": "Documentation", "link_url": "not-a-url"})

    def test_create_link_for_missing_technology_raises(self, links_service):
        with pytest.raises(RecordNotFoundError):
            links_service.create_link(
                "507f1f77bcf86cd799439011", {"link_type": "Documentation", "link_url": "https://example.com"}
            )

    def test_delete_link(self, technology_service, links_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        link = links_service.create_link(
            technology.id, {"link_type": "Documentation", "link_url": "https://example.com"}
        )
        links_service.delete_link(link.id)
        assert links_service.list_links(technology.id) == []
