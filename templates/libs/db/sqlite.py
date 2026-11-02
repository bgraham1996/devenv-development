"""Zero-config SQLite helper — a reach-for-it prototype database.

Thin convenience layer over the stdlib `sqlite3`: sensible defaults (row access
by name, foreign keys on, WAL), a context-managed connection, and one-line
query/execute helpers. No third-party dependencies.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    """Open a tuned SQLite connection (named-row access, FKs on, WAL)."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


class SQLite:
    """A small, ergonomic wrapper around a SQLite database file."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._conn = connect(self.path)

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Run a statement and commit."""
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Run a SELECT and return all rows."""
        return list(self._conn.execute(sql, params).fetchall())

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager: commit on success, roll back on error."""
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        self._conn.close()
