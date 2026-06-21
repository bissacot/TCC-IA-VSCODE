from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text

from .config import Config


def get_engine() -> Any:
    engine = create_engine(Config.DATABASE_URL, future=True)
    return engine


def initialize_schema(engine: Any) -> None:
    schema_path = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    schema_sql = schema_path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.exec_driver_sql(schema_sql)


def load_dataframe(df: pd.DataFrame, table_name: str, engine: Any) -> None:
    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
