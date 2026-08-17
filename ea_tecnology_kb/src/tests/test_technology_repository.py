"""Unit tests for TechnologyRepository."""

from __future__ import annotations

import pytest

from src.exceptions import DuplicateRecordError


class TestTechnologyRepository:
    def test_insert_and_find_by_id(self, technology_repository, sample_technology_data):
        record_id = technology_repository.insert_one(sample_technology_data)
        document = technology_repository.find_by_id(record_id)
        assert document is not None
        assert document["tech_code"] == "TC-001"

    def test_find_by_code(self, technology_repository, sample_technology_data):
        technology_repository.insert_one(sample_technology_data)
        document = technology_repository.find_by_code("TC-001")
        assert document is not None
        assert document["tech_product"] == "PostgreSQL"

    def test_duplicate_code_raises(self, technology_repository, sample_technology_data):
        technology_repository.insert_one(sample_technology_data)
        with pytest.raises(DuplicateRecordError):
            technology_repository.insert_one(sample_technology_data)

    def test_code_exists(self, technology_repository, sample_technology_data):
        technology_repository.insert_one(sample_technology_data)
        assert technology_repository.code_exists("TC-001") is True
        assert technology_repository.code_exists("TC-999") is False

    def test_code_exists_excludes_given_id(self, technology_repository, sample_technology_data):
        record_id = technology_repository.insert_one(sample_technology_data)
        assert technology_repository.code_exists("TC-001", exclude_id=record_id) is False

    def test_update_one(self, technology_repository, sample_technology_data):
        record_id = technology_repository.insert_one(sample_technology_data)
        updated = technology_repository.update_one(record_id, {"tech_product": "MySQL"})
        assert updated is True
        document = technology_repository.find_by_id(record_id)
        assert document["tech_product"] == "MySQL"

    def test_delete_one(self, technology_repository, sample_technology_data):
        record_id = technology_repository.insert_one(sample_technology_data)
        assert technology_repository.delete_one(record_id) is True
        assert technology_repository.find_by_id(record_id) is None

    def test_search_paginated_by_text(self, technology_repository, sample_technology_data):
        second = dict(sample_technology_data, tech_code="TC-002", tech_product="Redis")
        technology_repository.insert_one(sample_technology_data)
        technology_repository.insert_one(second)

        documents, total = technology_repository.search_paginated(search_text="Redis")
        assert total == 1
        assert documents[0]["tech_code"] == "TC-002"

    def test_search_paginated_column_filter(self, technology_repository, sample_technology_data):
        second = dict(sample_technology_data, tech_code="TC-002", tech_type="Messaging")
        technology_repository.insert_one(sample_technology_data)
        technology_repository.insert_one(second)

        documents, total = technology_repository.search_paginated(
            column_filters={"tech_type": "Messaging"}
        )
        assert total == 1
        assert documents[0]["tech_code"] == "TC-002"

    def test_search_paginated_pagination(self, technology_repository, sample_technology_data):
        for i in range(5):
            technology_repository.insert_one(
                dict(sample_technology_data, tech_code=f"TC-{i:03d}")
            )
        documents, total = technology_repository.search_paginated(page=1, page_size=2)
        assert total == 5
        assert len(documents) == 2
