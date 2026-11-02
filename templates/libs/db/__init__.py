"""db — database building blocks.

Seed implementation: a zero-config SQLite helper (`sqlite.py`). Add a Postgres
helper here when a project needs one.
"""

from .sqlite import SQLite, connect

__all__ = ["SQLite", "connect"]
