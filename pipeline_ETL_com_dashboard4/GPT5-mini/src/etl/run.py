from ..extract import extract_sales, extract_customers, extract_products
from ..transform import transform_sales
from ..quality import generate_quality_report
from ..load import get_engine, ensure_schema, upsert_customers, upsert_products, upsert_sales
from ..logger import logger
from pathlib import Path
import os


def run_etl():
    logger.info("Starting ETL")
    sales = extract_sales()
    customers = extract_customers()
    products = extract_products()

    sales_clean, report = transform_sales(sales)
    q = generate_quality_report(report)
    logger.info(f"Data quality: {q}")

    engine = get_engine()
    # Ensure schema
    root = Path(__file__).resolve().parents[3]
    schema_path = root / "sql" / "schema.sql"
    schema_sql = schema_path.read_text(encoding='utf-8')
    ensure_schema(engine, schema_sql)

    # Load
    upsert_customers(engine, customers.to_dict(orient='records'))
    upsert_products(engine, products.to_dict(orient='records'))
    upsert_sales(engine, sales_clean)

    logger.info("ETL finished")


if __name__ == '__main__':
    run_etl()
