-- Database initialization script
-- Run this script to set up PostgreSQL database for sales analytics

-- Create database
CREATE DATABASE sales_db
    WITH ENCODING 'UTF8'
    LOCALE 'en_US.UTF-8';

-- Connect to the database
\c sales_db;

-- Create customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    state VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_customer_state ON customers(state);

-- Create products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_category ON products(category);
CREATE INDEX idx_product_active ON products(active);

-- Create sales table
CREATE TABLE sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    total_value NUMERIC(12, 2) NOT NULL,
    sale_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_sale_customer_id ON sales(customer_id);
CREATE INDEX idx_sale_product_id ON sales(product_id);
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_sale_year_month ON sales(year, month);
CREATE UNIQUE CONSTRAINT uq_sale_id ON sales(sale_id);

-- Create data quality report table
CREATE TABLE data_quality_report (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_records_processed INTEGER NOT NULL,
    invalid_records INTEGER NOT NULL,
    duplicate_records_removed INTEGER NOT NULL,
    missing_values_percentage FLOAT NOT NULL,
    sales_records INTEGER NOT NULL,
    customer_records INTEGER NOT NULL,
    product_records INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    execution_time_seconds FLOAT NOT NULL
);

CREATE INDEX idx_quality_execution_date ON data_quality_report(execution_date);
CREATE INDEX idx_quality_status ON data_quality_report(status);

-- Create incremental load log table
CREATE TABLE incremental_load_log (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) NOT NULL,
    last_loaded_id VARCHAR(255),
    last_loaded_timestamp TIMESTAMP,
    last_modified_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    records_loaded INTEGER NOT NULL,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_name)
);

CREATE INDEX idx_incremental_source ON incremental_load_log(source_name);

-- Create user for ETL processes (optional, for production)
-- CREATE USER etl_user WITH PASSWORD 'etl_password';
-- GRANT CONNECT ON DATABASE sales_db TO etl_user;
-- GRANT USAGE ON SCHEMA public TO etl_user;
-- GRANT CREATE ON SCHEMA public TO etl_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO etl_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO etl_user;

-- Create materialized view for sales summary
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    s.year,
    s.month,
    p.category,
    c.state,
    COUNT(DISTINCT s.sale_id) as total_sales,
    COUNT(DISTINCT s.customer_id) as unique_customers,
    COUNT(DISTINCT s.product_id) as unique_products,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as avg_sale_value,
    MIN(s.total_value) as min_sale_value,
    MAX(s.total_value) as max_sale_value
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN products p ON s.product_id = p.product_id
GROUP BY s.year, s.month, p.category, c.state;

CREATE INDEX idx_sales_summary_date ON sales_summary(year, month);
CREATE INDEX idx_sales_summary_category ON sales_summary(category);
CREATE INDEX idx_sales_summary_state ON sales_summary(state);

-- Grant permissions for dashboard
-- GRANT SELECT ON sales_summary TO etl_user;
-- GRANT SELECT ON customers, products, sales, data_quality_report TO etl_user;
