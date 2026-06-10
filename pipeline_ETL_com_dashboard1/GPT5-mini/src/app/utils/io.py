from __future__ import annotations

import pandas as pd
from pathlib import Path


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def read_json(path: str) -> list[dict]:
    import json

    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
