"""Application-wide logging configuration.

Configures the Python root logger once, at application start-up, with:

* A :class:`~logging.handlers.RotatingFileHandler` writing structured
  entries to ``src/logs/app.log``.
* A console (``StreamHandler``) handler for interactive feedback.

Every module in the codebase should retrieve its own logger via
:func:`get_logger` rather than instantiating handlers itself.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from src.infrastructure.config import get_config

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging() -> None:
    """Configure the root logger with rotating file and console handlers.

    Safe to call multiple times: subsequent calls are no-ops so handlers
    are never duplicated.
    """
    global _configured
    if _configured:
        return

    config = get_config()
    log_file = config.logs_dir / "app.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level.upper())

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=config.log_max_bytes,
        backupCount=config.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(config.log_level.upper())

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(config.log_level.upper())

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Silence overly-verbose third-party loggers.
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    _configured = True
    root_logger.info("Logging initialized. Writing to %s", log_file)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, ensuring logging is configured.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    if not _configured:
        setup_logging()
    return logging.getLogger(name)
