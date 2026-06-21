-- Schema for sales ETL
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    state TEXT,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    price NUMERIC,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers(customer_id),
    product_id TEXT REFERENCES products(product_id),
    quantity INTEGER,
    unit_price NUMERIC,
    total_value NUMERIC,
    sale_date TIMESTAMP,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    state TEXT,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS etl_metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
