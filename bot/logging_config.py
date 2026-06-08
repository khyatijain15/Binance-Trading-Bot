"""
Centralized logging configuration for the trading bot.

Creates a rotating file handler that writes to ``logs/trading.log`` and an
optional console handler.  Call :func:`setup_logging` once at application
start-up.

Log format::

    2026-06-08 12:30:45,123 | INFO | bot.orders | Order placed successfully
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LOG_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE: str = os.path.join(LOG_DIR, "trading.log")
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
MAX_LOG_BYTES: int = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT: int = 3


def setup_logging(level: int = logging.DEBUG, console: bool = True) -> None:
    """Configure the root logger for the trading bot.

    Args:
        level: Minimum logging level (default ``DEBUG``).
        console: If *True*, also log to *stderr* at ``INFO`` level.
    """
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on repeated calls
    if root_logger.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- File handler (rotating) ---
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # --- Console handler ---
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
