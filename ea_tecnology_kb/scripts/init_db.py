"""Standalone script to initialize the ea_tecnology_kb MongoDB database.

Creates the four required collections (if missing) and all indexes
mandated by the data model. Safe to run multiple times (idempotent).

Usage::

    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running this script directly (``python scripts/init_db.py``) by
# adding the project root to sys.path so ``src`` is importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.infrastructure.config import get_config  # noqa: E402
from src.infrastructure.database.database_manager import DatabaseManager  # noqa: E402
from src.infrastructure.database.mongo_connection import MongoConnection  # noqa: E402
from src.infrastructure.logging import get_logger, setup_logging  # noqa: E402
from src.utils.constants import (  # noqa: E402
    COLLECTION_ALTERNATIVES,
    COLLECTION_LINKS,
    COLLECTION_NOTES,
    COLLECTION_TECHNOLOGIES,
)

_REQUIRED_COLLECTIONS = [
    COLLECTION_TECHNOLOGIES,
    COLLECTION_NOTES,
    COLLECTION_ALTERNATIVES,
    COLLECTION_LINKS,
]


def main() -> int:
    """Create required collections and indexes for ea_tecnology_kb.

    Returns:
        Process exit code (``0`` on success, ``1`` on failure).
    """
    setup_logging()
    logger = get_logger(__name__)
    config = get_config()

    logger.info(
        "Initializing database '%s' at %s:%s", config.mongo_database, config.mongo_host, config.mongo_port
    )

    connection = MongoConnection.instance(config)
    manager = DatabaseManager(connection)

    existing_collections = set(manager.database.list_collection_names())
    for collection_name in _REQUIRED_COLLECTIONS:
        if collection_name not in existing_collections:
            manager.database.create_collection(collection_name)
            logger.info("Created collection '%s'.", collection_name)
        else:
            logger.info("Collection '%s' already exists.", collection_name)

    manager.ensure_indexes()
    logger.info("Database initialization complete.")
    connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
