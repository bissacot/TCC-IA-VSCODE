from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine

from src.etl.config import Config
from src.etl.load import get_engine, initialize_schema, load_dataframe


def test_sqlite_initialize_and_load(tmp_path) -> None:
    Config.DATABASE_URL = f"sqlite:///{tmp_path / 'test.db'}"
    engine = get_engine()
    initialize_schema(engine)
    sample = pd.DataFrame([{"customer_id": "C1", "customer_name": "Acme", "email": "test@example.com", "phone": "555-0100", "state": "NY", "created_at": "2024-01-01"}])
    load_dataframe(sample, "customers", engine)
    result = pd.read_sql("SELECT * FROM customers", engine)
    assert len(result) == 1
