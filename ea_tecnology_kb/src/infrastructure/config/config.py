"""Centralized application configuration loaded from environment variables.

Uses ``python-dotenv`` to load a ``.env`` file (if present) into the process
environment, then exposes strongly-typed configuration values through the
:class:`Config` singleton. All other layers should read configuration from
this module instead of calling ``os.getenv`` directly, keeping configuration
concerns in a single place.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Resolve the project root as the parent of the `src` package, then load the
# `.env` located there (if present) before reading any variable.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH if _ENV_PATH.exists() else None)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    """Immutable, strongly-typed application configuration.

    Attributes:
        mongo_host: MongoDB server hostname.
        mongo_port: MongoDB server port.
        mongo_database: Target database name.
        mongo_username: Optional authentication username.
        mongo_password: Optional authentication password.
        mongo_auth_source: Authentication database, defaults to ``admin``.
        mongo_timeout_ms: Server selection timeout in milliseconds.
        mongo_max_pool_size: Maximum connection pool size.
        mongo_reconnect_attempts: Number of reconnection attempts on failure.
        mongo_reconnect_delay_seconds: Base delay between reconnection retries.
        app_theme: UI theme name (``dark`` or ``light``).
        app_name: Display name of the application.
        app_page_size: Default number of rows per page in list views.
        log_level: Root logging level (e.g. ``INFO``, ``DEBUG``).
        log_max_bytes: Max size in bytes before rotating the log file.
        log_backup_count: Number of rotated log files to retain.
        export_dir: Directory where Excel exports are written.
        project_root: Absolute path to the project root directory.
    """

    mongo_host: str = field(default_factory=lambda: os.getenv("MONGO_HOST", "localhost"))
    mongo_port: int = field(default_factory=lambda: _get_int("MONGO_PORT", 27017))
    mongo_database: str = field(
        default_factory=lambda: os.getenv("MONGO_DATABASE", "ea_tecnology_kb")
    )
    mongo_username: Optional[str] = field(default_factory=lambda: os.getenv("MONGO_USERNAME") or None)
    mongo_password: Optional[str] = field(default_factory=lambda: os.getenv("MONGO_PASSWORD") or None)
    mongo_auth_source: str = field(default_factory=lambda: os.getenv("MONGO_AUTH_SOURCE", "admin"))
    mongo_timeout_ms: int = field(default_factory=lambda: _get_int("MONGO_TIMEOUT_MS", 5000))
    mongo_max_pool_size: int = field(default_factory=lambda: _get_int("MONGO_MAX_POOL_SIZE", 50))
    mongo_reconnect_attempts: int = field(
        default_factory=lambda: _get_int("MONGO_RECONNECT_ATTEMPTS", 5)
    )
    mongo_reconnect_delay_seconds: int = field(
        default_factory=lambda: _get_int("MONGO_RECONNECT_DELAY_SECONDS", 2)
    )

    app_theme: str = field(default_factory=lambda: os.getenv("APP_THEME", "dark"))
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "EA Technology KB"))
    app_page_size: int = field(default_factory=lambda: _get_int("APP_PAGE_SIZE", 50))

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_max_bytes: int = field(default_factory=lambda: _get_int("LOG_MAX_BYTES", 5 * 1024 * 1024))
    log_backup_count: int = field(default_factory=lambda: _get_int("LOG_BACKUP_COUNT", 5))

    export_dir: str = field(default_factory=lambda: os.getenv("EXPORT_DIR", "src/exports"))
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)

    @property
    def mongo_uri(self) -> str:
        """Build the MongoDB connection URI from the discrete settings.

        Returns:
            A ``mongodb://`` connection string, including credentials when
            both a username and password are configured.
        """
        if self.mongo_username and self.mongo_password:
            return (
                f"mongodb://{self.mongo_username}:{self.mongo_password}"
                f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"
                f"?authSource={self.mongo_auth_source}"
            )
        return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_database}"

    @property
    def logs_dir(self) -> Path:
        """Absolute path to the ``logs`` directory, created if missing."""
        path = self.project_root / "src" / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def exports_dir(self) -> Path:
        """Absolute path to the exports directory, created if missing."""
        path = self.project_root / self.export_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Return the process-wide :class:`Config` singleton.

    Returns:
        The lazily-initialized, immutable configuration instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
