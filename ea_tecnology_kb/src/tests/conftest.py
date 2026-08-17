"""Shared pytest fixtures backed by an in-memory MongoDB (mongomock)."""

from __future__ import annotations

import mongomock
import pytest

from src.repositories.alternatives_repository import AlternativesRepository
from src.repositories.links_repository import LinksRepository
from src.repositories.notes_repository import NotesRepository
from src.repositories.technology_repository import TechnologyRepository
from src.services.alternatives_service import AlternativesService
from src.services.links_service import LinksService
from src.services.notes_service import NotesService
from src.services.technology_service import TechnologyService
from src.utils.constants import (
    COLLECTION_ALTERNATIVES,
    COLLECTION_LINKS,
    COLLECTION_NOTES,
    COLLECTION_TECHNOLOGIES,
)


@pytest.fixture
def mongo_database():
    """Provide an isolated, in-memory MongoDB database for each test."""
    client = mongomock.MongoClient()
    database = client["ea_tecnology_kb_test"]
    database[COLLECTION_TECHNOLOGIES].create_index("tech_code", unique=True)
    return database


@pytest.fixture
def technology_repository(mongo_database) -> TechnologyRepository:
    return TechnologyRepository(mongo_database[COLLECTION_TECHNOLOGIES])


@pytest.fixture
def notes_repository(mongo_database) -> NotesRepository:
    return NotesRepository(mongo_database[COLLECTION_NOTES])


@pytest.fixture
def alternatives_repository(mongo_database) -> AlternativesRepository:
    return AlternativesRepository(mongo_database[COLLECTION_ALTERNATIVES])


@pytest.fixture
def links_repository(mongo_database) -> LinksRepository:
    return LinksRepository(mongo_database[COLLECTION_LINKS])


@pytest.fixture
def technology_service(
    technology_repository, notes_repository, alternatives_repository, links_repository
) -> TechnologyService:
    return TechnologyService(
        technology_repository, notes_repository, alternatives_repository, links_repository
    )


@pytest.fixture
def notes_service(notes_repository, technology_repository) -> NotesService:
    return NotesService(notes_repository, technology_repository)


@pytest.fixture
def alternatives_service(alternatives_repository, technology_repository) -> AlternativesService:
    return AlternativesService(alternatives_repository, technology_repository)


@pytest.fixture
def links_service(links_repository, technology_repository) -> LinksService:
    return LinksService(links_repository, technology_repository)


@pytest.fixture
def sample_technology_data() -> dict:
    return {
        "tech_code": "TC-001",
        "tech_product": "PostgreSQL",
        "tech_type": "Database",
        "tech_std": "Yes",
        "tech_classif": "Strategic",
        "tech_lifecycle": "Adopt",
        "tech_trend": "Yes",
    }
