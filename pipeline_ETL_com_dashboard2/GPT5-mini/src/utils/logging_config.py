import logging
from logging import Logger
from src.config import settings


def configure_logging() -> Logger:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        level=level,
    )
    return logging.getLogger("sales_etl")
