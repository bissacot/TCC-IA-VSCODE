from __future__ import annotations

import logging

from .config import Config


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
