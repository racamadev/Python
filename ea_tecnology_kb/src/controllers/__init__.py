"""Presentation-layer controllers bridging views and services."""

from src.controllers.technology_controller import TechnologyController
from src.controllers.notes_controller import NotesController
from src.controllers.alternatives_controller import AlternativesController
from src.controllers.links_controller import LinksController

__all__ = [
    "TechnologyController",
    "NotesController",
    "AlternativesController",
    "LinksController",
]
