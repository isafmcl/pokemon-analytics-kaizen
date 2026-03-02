from __future__ import annotations
import logging
from logging import Logger
from typing import Optional

from .settings import get_settings

_LOGGER_NAME_PREFIX = "pokemon_analytics"


def _create_logger(name: str, level: int) -> Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> Logger:
    settings = get_settings()
    log_level_name = settings.log_level
    level = getattr(logging, log_level_name, logging.INFO)

    if name is None:
        full_name = _LOGGER_NAME_PREFIX
    else:
        full_name = f"{_LOGGER_NAME_PREFIX}.{name}"

    return _create_logger(full_name, level)
