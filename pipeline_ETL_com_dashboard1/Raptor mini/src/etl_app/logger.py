from __future__ import annotations

import logging
from logging import Logger

from .config import settings


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(settings.log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
