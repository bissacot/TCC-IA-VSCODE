from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.etl_app.config import settings
from src.etl_app.logger import get_logger

logger = get_logger(__name__)

EXPORT_PATH = Path("reports")
EXCEL_PATH = EXPORT_PATH / "sales_export.xlsx"


def export_excel(output_path: Path = EXCEL_PATH) -> Path:
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.db_url)

    queries = {
        "sales": text("SELECT * FROM sales ORDER BY sale_date"),
        "customers": text("SELECT * FROM customers ORDER BY customer_id"),
        "products": text("SELECT * FROM products ORDER BY product_id"),
    }

    with engine.connect() as connection:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, query in queries.items():
                df = pd.read_sql(query, connection)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info("Excel export written to %s", output_path)
    return output_path


def main() -> None:
    export_excel()


if __name__ == "__main__":
    main()
