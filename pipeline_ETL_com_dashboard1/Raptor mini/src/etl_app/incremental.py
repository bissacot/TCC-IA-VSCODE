from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


def get_last_processed_timestamp(path: Path = settings.last_processed_file) -> datetime | None:
    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        logger.warning("Invalid last processed timestamp stored in %s", path)
        return None


def set_last_processed_timestamp(timestamp: datetime, path: Path = settings.last_processed_file) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(timestamp.isoformat(), encoding="utf-8")
    logger.info("Updated last processed timestamp to %s", timestamp.isoformat())


def filter_incremental_sales(df: "pandas.DataFrame", last_timestamp: datetime | None) -> "pandas.DataFrame":
    if last_timestamp is None:
        return df
    return df[df["sale_date"] > last_timestamp].copy()
