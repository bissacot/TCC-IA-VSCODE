from typing import Iterable
import sqlalchemy
from sqlalchemy import text
from .config import get_settings
from .logger import logger
import json


def get_engine():
    s = get_settings()
    url = f"postgresql+psycopg2://{s.postgres_user}:{s.postgres_password}@{s.postgres_host}:{s.postgres_port}/{s.postgres_db}"
    engine = sqlalchemy.create_engine(url)
    return engine


def ensure_schema(engine: sqlalchemy.engine.Engine, schema_sql: str):
    with engine.begin() as conn:
        logger.info("Creating DB schema if not exists")
        conn.execute(text(schema_sql))


def upsert_customers(engine: sqlalchemy.engine.Engine, customers_iter: Iterable[dict]):
    with engine.begin() as conn:
        for c in customers_iter:
            stmt = text(
                "INSERT INTO customers(customer_id, name, email, state, raw) VALUES (:id, :name, :email, :state, :raw) "
                "ON CONFLICT (customer_id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, state = EXCLUDED.state"
            )
            conn.execute(stmt, {
                'id': c.get('id') or c.get('customer_id'),
                'name': c.get('name'),
                'email': c.get('email'),
                'state': c.get('state'),
                'raw': json.dumps(c)
            })


def upsert_products(engine: sqlalchemy.engine.Engine, products_iter: Iterable[dict]):
    with engine.begin() as conn:
        for p in products_iter:
            stmt = text(
                "INSERT INTO products(product_id, title, category, price, raw) VALUES (:id, :title, :category, :price, :raw) "
                "ON CONFLICT (product_id) DO UPDATE SET title = EXCLUDED.title, category = EXCLUDED.category, price = EXCLUDED.price"
            )
            conn.execute(stmt, {
                'id': str(p.get('id')),
                'title': p.get('title'),
                'category': p.get('category'),
                'price': p.get('price'),
                'raw': json.dumps(p)
            })


def upsert_sales(engine: sqlalchemy.engine.Engine, sales_df):
    with engine.begin() as conn:
        for _, row in sales_df.iterrows():
            stmt = text(
                "INSERT INTO sales(sale_id, customer_id, product_id, quantity, unit_price, total_value, sale_date, state, raw) "
                "VALUES (:sale_id, :customer_id, :product_id, :quantity, :unit_price, :total_value, :sale_date, :state, :raw) "
                "ON CONFLICT (sale_id) DO NOTHING"
            )
            conn.execute(stmt, {
                'sale_id': str(row.get('sale_id') or row.name),
                'customer_id': row.get('customer_id'),
                'product_id': row.get('product_id'),
                'quantity': int(row.get('quantity') or 0),
                'unit_price': float(row.get('unit_price') or 0.0),
                'total_value': float(row.get('total_value') or 0.0),
                'sale_date': row.get('sale_date').date() if hasattr(row.get('sale_date'), 'date') else row.get('sale_date'),
                'state': row.get('state'),
                'raw': json.dumps(row.to_dict(), default=str)
            })
