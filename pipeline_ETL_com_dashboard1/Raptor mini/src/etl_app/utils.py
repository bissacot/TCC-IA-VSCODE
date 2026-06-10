from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def standardize_date(value: Any) -> datetime | None:
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value

    text = str(value).strip()

    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unrecognized date format: {value}")


def ensure_path_exists(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_unique_records(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset)
