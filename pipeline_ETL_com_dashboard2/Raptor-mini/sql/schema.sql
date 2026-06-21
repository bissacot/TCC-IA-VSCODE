CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR,
    state VARCHAR
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category VARCHAR,
    unit_price DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR NOT NULL REFERENCES customers(customer_id),
    product_id VARCHAR NOT NULL REFERENCES products(product_id),
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    total_sale_value DOUBLE PRECISION NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    state VARCHAR
);

CREATE TABLE IF NOT EXISTS etl_metadata (
    source_name VARCHAR PRIMARY KEY,
    last_processed_at TIMESTAMP,
    records_processed INTEGER NOT NULL DEFAULT 0
);
