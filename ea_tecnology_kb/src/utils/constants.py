"""Application-wide constants: collection names, field names and choice lists.

Centralizing these values avoids "magic strings" scattered across the
repository, service, and view layers (DRY) and gives a single place to
update naming if the schema evolves.
"""

from __future__ import annotations

# --- MongoDB collection names -----------------------------------------------
COLLECTION_TECHNOLOGIES = "technologies"
COLLECTION_NOTES = "tech_notes"
COLLECTION_ALTERNATIVES = "tech_alternatives"
COLLECTION_LINKS = "tech_links"

# --- Choice lists ------------------------------------------------------------
YES_NO_CHOICES = ["Yes", "No"]

TECH_LIFECYCLE_CHOICES = [
    "Planned",
    "Emerging",
    "Adopt",
    "Trial",
    "Contain",
    "Hold",
    "Retire",
    "Retired",
]

TECH_CLASSIF_CHOICES = [
    "Strategic",
    "Tactical",
    "Legacy",
    "Emerging",
    "Experimental",
]

LINK_QUALITY_CHOICES = ["High", "Medium", "Low"]

LINK_TYPE_CHOICES = [
    "Documentation",
    "Vendor",
    "Community",
    "Article",
    "Video",
    "Repository",
    "Other",
]

NOTE_TYPE_CHOICES = [
    "General",
    "Risk",
    "Decision",
    "Review",
    "Recommendation",
]

# --- Pagination ---------------------------------------------------------------
DEFAULT_PAGE_SIZE = 50

# --- Sort direction -------------------------------------------------------------
SORT_ASCENDING = 1
SORT_DESCENDING = -1

# --- Date formats --------------------------------------------------------------
DATE_DISPLAY_FORMAT = "yyyy-MM-dd"
DATE_STORAGE_FORMAT = "%Y-%m-%d"
DATETIME_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- UI ---------------------------------------------------------------------
APP_ORG_NAME = "EA Tecnology"
NOTE_CARD_VISIBLE_LINES = 6
