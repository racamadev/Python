"""Low-level MongoDB connection management with automatic reconnection.

Implements :class:`MongoConnection` as a thread-safe singleton wrapping a
``pymongo.MongoClient``. Connection failures are retried with an exponential
backoff, and every public accessor validates the connection is alive before
handing the client back to callers (self-healing on transient network
issues, dropped replica-set elections, etc.).
"""

from __future__ import annotations

import threading
import time
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from src.exceptions import DatabaseConnectionError
from src.infrastructure.config import Config, get_config
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class MongoConnection:
    """Thread-safe singleton managing the MongoDB client lifecycle.

    Use :meth:`instance` to obtain the shared connection. Direct
    instantiation is discouraged outside of tests, where an explicit
    :class:`Config` can be injected.
    """

    _instance: Optional["MongoConnection"] = None
    _lock = threading.Lock()

    def __init__(self, config: Optional[Config] = None) -> None:
        self._config = config or get_config()
        self._client: Optional[MongoClient] = None
        self._connect_lock = threading.Lock()
        self._connect()

    @classmethod
    def instance(cls, config: Optional[Config] = None) -> "MongoConnection":
        """Return the process-wide singleton, creating it on first use.

        Args:
            config: Optional configuration override, only honored the first
                time the singleton is created.

        Returns:
            The shared :class:`MongoConnection` instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Dispose of the singleton. Intended for use in tests only."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
            cls._instance = None

    def _connect(self) -> None:
        """Establish the MongoDB client with retry/backoff on failure.

        Raises:
            DatabaseConnectionError: If all reconnection attempts are
                exhausted without establishing a connection.
        """
        attempts = max(1, self._config.mongo_reconnect_attempts)
        delay = self._config.mongo_reconnect_delay_seconds

        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                client: MongoClient = MongoClient(
                    self._config.mongo_uri,
                    serverSelectionTimeoutMS=self._config.mongo_timeout_ms,
                    maxPoolSize=self._config.mongo_max_pool_size,
                )
                # Force a round-trip so connection issues surface immediately.
                client.admin.command("ping")
                self._client = client
                logger.info(
                    "Connected to MongoDB at %s:%s (database=%s)",
                    self._config.mongo_host,
                    self._config.mongo_port,
                    self._config.mongo_database,
                )
                return
            except PyMongoError as exc:
                last_error = exc
                logger.warning(
                    "MongoDB connection attempt %d/%d failed: %s",
                    attempt,
                    attempts,
                    exc,
                )
                if attempt < attempts:
                    time.sleep(delay * attempt)

        message = "Could not establish a connection to MongoDB after retries."
        logger.error(message)
        raise DatabaseConnectionError(message, details=str(last_error))

    def _ensure_connected(self) -> None:
        """Verify the client is alive, reconnecting automatically if not."""
        if self._client is None:
            self._connect()
            return
        try:
            self._client.admin.command("ping")
        except PyMongoError:
            logger.warning("Lost MongoDB connection. Attempting to reconnect...")
            with self._connect_lock:
                self._connect()

    @property
    def client(self) -> MongoClient:
        """Return a live ``MongoClient``, reconnecting if necessary."""
        self._ensure_connected()
        assert self._client is not None  # noqa: S101 - guaranteed by _connect
        return self._client

    @property
    def database(self) -> Database:
        """Return the configured application database."""
        return self.client[self._config.mongo_database]

    def close(self) -> None:
        """Close the underlying client connection, if open."""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed.")

    def health_check(self) -> bool:
        """Check connectivity without raising.

        Returns:
            ``True`` if the server responds to a ping, ``False`` otherwise.
        """
        try:
            self._ensure_connected()
            return True
        except DatabaseConnectionError:
            return False
