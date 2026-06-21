-- Create schema for customers, products, sales

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    state TEXT,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    title TEXT,
    category TEXT,
    price NUMERIC,
    raw JSONB
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers(customer_id),
    product_id TEXT REFERENCES products(product_id),
    sale_date DATE,
    quantity INTEGER,
    unit_price NUMERIC,
    total_value NUMERIC,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    state TEXT
);
