"""A one-call configured logger built on the stdlib `logging`.

`get_logger(__name__)` returns a logger with a sane console format, configured
once (idempotent) so repeated calls don't stack handlers. Level is taken from the
`LOG_LEVEL` environment variable (default `INFO`). No third-party dependencies.
"""

from __future__ import annotations

import logging
import os

_CONFIGURED = False
_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


def _configure() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_FORMAT))
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Safe to call many times."""
    _configure()
    return logging.getLogger(name)
