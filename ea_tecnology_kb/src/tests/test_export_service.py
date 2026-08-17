"""Unit tests for ExportService."""

from __future__ import annotations

from pathlib import Path

import openpyxl

from src.services.export_service import ExportService


class TestExportService:
    def test_export_all_creates_workbook_with_expected_sheets(
        self,
        technology_service,
        notes_service,
        alternatives_service,
        links_service,
        sample_technology_data,
        tmp_path: Path,
    ):
        technology = technology_service.create_technology(sample_technology_data)
        notes_service.create_note(technology.id, {"note_type": "Risk", "note_card": "x"})
        alternatives_service.create_alternative(
            technology.id, {"alternative_code": "ALT-1", "alternative_product": "Alt"}
        )
        links_service.create_link(
            technology.id, {"link_type": "Documentation", "link_url": "https://example.com"}
        )

        export_service = ExportService(
            technology_service, notes_service, alternatives_service, links_service
        )
        output_path = tmp_path / "export.xlsx"
        written_path = export_service.export_all(str(output_path))

        assert Path(written_path).exists()
        workbook = openpyxl.load_workbook(written_path)
        assert set(workbook.sheetnames) == {"Technologies", "Notes", "Alternatives", "Links"}
        assert workbook["Technologies"]["A1"].value == "tech_code"
        assert workbook["Technologies"]["A2"].value == "TC-001"
