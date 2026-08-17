"""Excel export orchestration using pandas + openpyxl.

Produces a single ``.xlsx`` workbook with one sheet per entity
(Technologies, Notes, Alternatives, Links), each professionally formatted
via :mod:`src.utils.excel_helpers`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from src.exceptions import ServiceError
from src.infrastructure.logging import get_logger
from src.models import Alternative, Link, Note, Technology
from src.services.alternatives_service import AlternativesService
from src.services.links_service import LinksService
from src.services.notes_service import NotesService
from src.services.technology_service import TechnologyService
from src.utils.date_helpers import format_date
from src.utils.excel_helpers import format_worksheet

logger = get_logger(__name__)

_TECH_COLUMNS = [
    "tech_code",
    "tech_type",
    "tech_product",
    "tech_std",
    "tech_classif",
    "tech_lifecycle",
    "tech_date",
    "tech_start_date",
    "tech_divest_date",
    "tech_end_date",
    "tech_trend",
]
_NOTE_COLUMNS = ["tech_code", "note_date", "note_type", "note_card"]
_ALTERNATIVE_COLUMNS = ["tech_code", "alternative_code", "alternative_product", "alternative_card"]
_LINK_COLUMNS = ["tech_code", "link_type", "link_url", "link_source", "link_quality"]


class ExportService:
    """Builds a multi-sheet Excel workbook from the application's data.

    Args:
        technology_service: Source of technology master records.
        notes_service: Source of note records.
        alternatives_service: Source of alternative records.
        links_service: Source of link records.
    """

    def __init__(
        self,
        technology_service: TechnologyService,
        notes_service: NotesService,
        alternatives_service: AlternativesService,
        links_service: LinksService,
    ) -> None:
        self._technology_service = technology_service
        self._notes_service = notes_service
        self._alternatives_service = alternatives_service
        self._links_service = links_service

    def export_all(self, file_path: str) -> str:
        """Export all technologies and their details to a single workbook.

        Args:
            file_path: Destination ``.xlsx`` path.

        Returns:
            The absolute path of the written file.

        Raises:
            ServiceError: If the export fails for any reason.
        """
        technologies = self._technology_service.list_all()
        notes = self._notes_service.list_all()
        alternatives = self._alternatives_service.list_all()
        links = self._links_service.list_all()
        return self.export_to_excel(file_path, technologies, notes, alternatives, links)

    def export_to_excel(
        self,
        file_path: str,
        technologies: list[Technology],
        notes: list[Note],
        alternatives: list[Alternative],
        links: list[Link],
    ) -> str:
        """Write technologies and related details to a formatted workbook.

        Args:
            file_path: Destination ``.xlsx`` path.
            technologies: Master records to export.
            notes: Note records to export.
            alternatives: Alternative records to export.
            links: Link records to export.

        Returns:
            The absolute path of the written file.

        Raises:
            ServiceError: If writing the workbook fails.
        """
        try:
            code_by_id = {tech.id: tech.tech_code for tech in technologies}

            technologies_df = self._technologies_to_dataframe(technologies)
            notes_df = self._notes_to_dataframe(notes, code_by_id)
            alternatives_df = self._alternatives_to_dataframe(alternatives, code_by_id)
            links_df = self._links_to_dataframe(links, code_by_id)

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                technologies_df.to_excel(writer, sheet_name="Technologies", index=False)
                notes_df.to_excel(writer, sheet_name="Notes", index=False)
                alternatives_df.to_excel(writer, sheet_name="Alternatives", index=False)
                links_df.to_excel(writer, sheet_name="Links", index=False)

                format_worksheet(writer.sheets["Technologies"], _TECH_COLUMNS)
                format_worksheet(writer.sheets["Notes"], _NOTE_COLUMNS)
                format_worksheet(writer.sheets["Alternatives"], _ALTERNATIVE_COLUMNS)
                format_worksheet(writer.sheets["Links"], _LINK_COLUMNS)

            logger.info("Excel export written to %s", path.resolve())
            return str(path.resolve())
        except (OSError, ValueError) as exc:
            logger.error("Excel export failed: %s", exc)
            raise ServiceError("Error al generar el archivo Excel.", details=str(exc)) from exc

    @staticmethod
    def _technologies_to_dataframe(technologies: list[Technology]) -> pd.DataFrame:
        rows = [
            {
                "tech_code": tech.tech_code,
                "tech_type": tech.tech_type,
                "tech_product": tech.tech_product,
                "tech_std": tech.tech_std,
                "tech_classif": tech.tech_classif,
                "tech_lifecycle": tech.tech_lifecycle,
                "tech_date": format_date(tech.tech_date),
                "tech_start_date": format_date(tech.tech_start_date),
                "tech_divest_date": format_date(tech.tech_divest_date),
                "tech_end_date": format_date(tech.tech_end_date),
                "tech_trend": tech.tech_trend,
            }
            for tech in technologies
        ]
        return pd.DataFrame(rows, columns=_TECH_COLUMNS)

    @staticmethod
    def _notes_to_dataframe(notes: list[Note], code_by_id: dict[Optional[str], str]) -> pd.DataFrame:
        rows = [
            {
                "tech_code": code_by_id.get(note.technology_id, ""),
                "note_date": format_date(note.note_date),
                "note_type": note.note_type,
                "note_card": note.note_card,
            }
            for note in notes
        ]
        return pd.DataFrame(rows, columns=_NOTE_COLUMNS)

    @staticmethod
    def _alternatives_to_dataframe(
        alternatives: list[Alternative], code_by_id: dict[Optional[str], str]
    ) -> pd.DataFrame:
        rows = [
            {
                "tech_code": code_by_id.get(alt.technology_id, ""),
                "alternative_code": alt.alternative_code,
                "alternative_product": alt.alternative_product,
                "alternative_card": alt.alternative_card,
            }
            for alt in alternatives
        ]
        return pd.DataFrame(rows, columns=_ALTERNATIVE_COLUMNS)

    @staticmethod
    def _links_to_dataframe(links: list[Link], code_by_id: dict[Optional[str], str]) -> pd.DataFrame:
        rows = [
            {
                "tech_code": code_by_id.get(link.technology_id, ""),
                "link_type": link.link_type,
                "link_url": link.link_url,
                "link_source": link.link_source,
                "link_quality": link.link_quality,
            }
            for link in links
        ]
        return pd.DataFrame(rows, columns=_LINK_COLUMNS)
