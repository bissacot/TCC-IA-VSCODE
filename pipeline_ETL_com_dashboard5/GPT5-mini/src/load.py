from sqlalchemy import Table, Column, String, Integer, Numeric, Date, MetaData, JSON
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from .db import engine
from .logger import get_logger

logger = get_logger(__name__)
metadata = MetaData()

customers_table = Table(
    'customers', metadata,
    Column('customer_id', String, primary_key=True),
    Column('name', String),
    Column('email', String),
    Column('state', String),
    Column('raw', JSON)
)

products_table = Table(
    'products', metadata,
    Column('product_id', String, primary_key=True),
    Column('title', String),
    Column('category', String),
    Column('price', Numeric),
    Column('raw', JSON)
)

sales_table = Table(
    'sales', metadata,
    Column('sale_id', String, primary_key=True),
    Column('customer_id', String),
    Column('product_id', String),
    Column('sale_date', Date),
    Column('quantity', Integer),
    Column('unit_price', Numeric),
    Column('total_value', Numeric),
    Column('year', Integer),
    Column('month', Integer),
    Column('quarter', Integer),
    Column('state', String)
)


def upsert_table(table: Table, rows: list, pk: str):
    if not rows:
        return 0
    conn = engine.connect()
    inserted = 0
    for r in rows:
        try:
            stmt = pg_insert(table).values(**r)
            upd = {c.name: stmt.excluded[c.name] for c in table.c if c.name != pk}
            stmt = stmt.on_conflict_do_update(index_elements=[pk], set_=upd)
            conn.execute(stmt)
            inserted += 1
        except SQLAlchemyError as e:
            logger.exception('Upsert error: %s', e)
    conn.commit()
    conn.close()
    return inserted


def load_customers(df):
    rows = []
    for _, r in df.iterrows():
        rows.append({
            'customer_id': str(r.get('customer_id')),
            'name': r.get('name'),
            'email': r.get('email'),
            'state': r.get('state'),
            'raw': r.to_dict()
        })
    return upsert_table(customers_table, rows, 'customer_id')


def load_products(df):
    rows = []
    for _, r in df.iterrows():
        rows.append({
            'product_id': str(r.get('product_id')),
            'title': r.get('title'),
            'category': r.get('category'),
            'price': r.get('price'),
            'raw': r.to_dict()
        })
    return upsert_table(products_table, rows, 'product_id')


def load_sales(df):
    rows = []
    for _, r in df.iterrows():
        rows.append({
            'sale_id': str(r.get('sale_id')),
            'customer_id': str(r.get('customer_id')),
            'product_id': str(r.get('product_id')),
            'sale_date': r.get('sale_date'),
            'quantity': int(r.get('quantity')) if r.get('quantity') is not None else None,
            'unit_price': r.get('unit_price'),
            'total_value': r.get('total_value'),
            'year': int(r.get('year')) if r.get('year') is not None else None,
            'month': int(r.get('month')) if r.get('month') is not None else None,
            'quarter': int(r.get('quarter')) if r.get('quarter') is not None else None,
            'state': r.get('state')
        })
    return upsert_table(sales_table, rows, 'sale_id')
