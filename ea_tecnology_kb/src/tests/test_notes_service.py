"""Unit tests for NotesService."""

from __future__ import annotations

import pytest

from src.exceptions import RecordNotFoundError


class TestNotesService:
    def test_create_note_for_existing_technology(
        self, technology_service, notes_service, sample_technology_data
    ):
        technology = technology_service.create_technology(sample_technology_data)
        note = notes_service.create_note(
            technology.id, {"note_type": "Risk", "note_card": "Some risk description."}
        )
        assert note.id is not None
        assert note.technology_id == technology.id

    def test_create_note_for_missing_technology_raises(self, notes_service):
        with pytest.raises(RecordNotFoundError):
            notes_service.create_note(
                "507f1f77bcf86cd799439011", {"note_type": "Risk", "note_card": "x"}
            )

    def test_list_notes_returns_created_note(
        self, technology_service, notes_service, sample_technology_data
    ):
        technology = technology_service.create_technology(sample_technology_data)
        notes_service.create_note(technology.id, {"note_type": "Risk", "note_card": "x"})
        notes = notes_service.list_notes(technology.id)
        assert len(notes) == 1

    def test_update_note(self, technology_service, notes_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        note = notes_service.create_note(technology.id, {"note_type": "Risk", "note_card": "x"})
        updated = notes_service.update_note(
            note.id, technology.id, {"note_type": "Decision", "note_card": "y"}
        )
        assert updated.note_type == "Decision"

    def test_delete_note(self, technology_service, notes_service, sample_technology_data):
        technology = technology_service.create_technology(sample_technology_data)
        note = notes_service.create_note(technology.id, {"note_type": "Risk", "note_card": "x"})
        notes_service.delete_note(note.id)
        assert notes_service.list_notes(technology.id) == []

    def test_delete_nonexistent_note_raises(self, notes_service):
        with pytest.raises(RecordNotFoundError):
            notes_service.delete_note("507f1f77bcf86cd799439011")
