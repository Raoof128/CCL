"""Structured logging helpers for the confidential computing lab."""

from __future__ import annotations

import logging
from typing import Optional


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure a reusable root logger.

    The function is idempotent: multiple calls will not attach duplicate handlers.
    """
    logger = logging.getLogger("confidential_computing_lab")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(level)
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger configured for the lab."""
    return logging.getLogger(name or "confidential_computing_lab")


configure_logging()
