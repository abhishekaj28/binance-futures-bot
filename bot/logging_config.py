"""
logging_config.py
-----------------
Sets up structured logging:
  - File handler  → logs/trading_bot.log  (DEBUG and above)
  - Console handler → stdout              (INFO and above)

Call setup_logging() once at app startup.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

def setup_logging(level: str = "DEBUG") -> logging.Logger:
    """
    Configure root logger with both file and console handlers.
    Returns the root logger.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if root.handlers:
        return root

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── File handler (rotating, max 5 MB × 3 backups) ──────────────────────
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # ── Console handler ─────────────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)

    return root
