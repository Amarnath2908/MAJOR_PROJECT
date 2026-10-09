"""
utils/logger.py — Centralised Logging Factory
===============================================
Provides a single get_logger() factory function used by every module
in the project.  All loggers share the same format and handler so that
log output is consistent across the entire application.

Usage
-----
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Something happened.")
    logger.error("Something went wrong: %s", str(exc))
"""

import logging
import sys
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Format
# ─────────────────────────────────────────────────────────────────────────────

LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
"""
Log line format example:
    2026-07-30 09:45:12,345 | INFO     | api.upload:42 | File uploaded successfully.
"""

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


# ─────────────────────────────────────────────────────────────────────────────
# Logger Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Return a named logger pre-configured with a StreamHandler.

    If a logger with this name already exists (Python's logging module
    caches loggers by name), it is returned as-is to avoid adding
    duplicate handlers on repeated calls.

    Parameters
    ----------
    name : str
        Logger name — typically pass ``__name__`` so the logger is
        identified by its module path (e.g. ``api.upload``).
    level : int, optional
        Minimum log level (default: ``logging.DEBUG``).

    Returns
    -------
    logging.Logger
        A configured logger instance ready for use.

    Examples
    --------
    >>> logger = get_logger(__name__)
    >>> logger.info("Server started.")
    2026-07-30 09:45:12,345 | INFO     | main:55 | Server started.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger is already configured.
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # ── Console Handler ───────────────────────────────────────────────────────
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Prevent log records from propagating to the root logger
    # (avoids duplicate output when the root logger also has handlers).
    logger.propagate = False

    return logger


# ─────────────────────────────────────────────────────────────────────────────
# Application-Level Root Logger
# ─────────────────────────────────────────────────────────────────────────────

# One shared logger for use in files that don't have a meaningful __name__
app_logger: logging.Logger = get_logger("designverse")
