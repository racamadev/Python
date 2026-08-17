"""Unit tests for BaseRepository generic CRUD operations."""

from __future__ import annotations

from src.repositories.base_repository import BaseRepository


class TestBaseRepository:
    def test_find_all_with_sort_skip_limit(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        for i in range(5):
            repo.insert_one({"n": i})

        results = repo.find_all(sort=[("n", -1)], skip=1, limit=2)
        assert [doc["n"] for doc in results] == [3, 2]

    def test_count(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        repo.insert_one({"n": 1})
        repo.insert_one({"n": 2})
        assert repo.count() == 2
        assert repo.count({"n": 1}) == 1

    def test_exists(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        repo.insert_one({"n": 1})
        assert repo.exists({"n": 1}) is True
        assert repo.exists({"n": 999}) is False

    def test_delete_many(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        repo.insert_one({"group": "a"})
        repo.insert_one({"group": "a"})
        repo.insert_one({"group": "b"})
        deleted = repo.delete_many({"group": "a"})
        assert deleted == 2
        assert repo.count() == 1

    def test_update_one_no_match_returns_false(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        from bson import ObjectId

        assert repo.update_one(str(ObjectId()), {"n": 1}) is False

    def test_delete_one_no_match_returns_false(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        from bson import ObjectId

        assert repo.delete_one(str(ObjectId())) is False

    def test_find_one_no_match_returns_none(self, mongo_database):
        repo = BaseRepository(mongo_database["scratch"])
        assert repo.find_one({"missing": True}) is None
