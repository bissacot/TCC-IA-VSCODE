-- Database Schema for Sales ETL Pipeline
-- PostgreSQL SQL Script

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS data_quality_reports CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_state ON customers(state);
CREATE INDEX idx_customers_city ON customers(city);

-- Products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    description TEXT,
    manufacturer VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_subcategory ON products(subcategory);
CREATE INDEX idx_products_manufacturer ON products(manufacturer);

-- Sales table
CREATE TABLE sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_value DECIMAL(12, 2) NOT NULL CHECK (total_value >= 0),
    sale_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    state VARCHAR(50),
    payment_method VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_sales_year ON sales(year);
CREATE INDEX idx_sales_month ON sales(month);
CREATE INDEX idx_sales_quarter ON sales(quarter);
CREATE INDEX idx_sales_state ON sales(state);

-- Data Quality Reports table
CREATE TABLE data_quality_reports (
    report_id SERIAL PRIMARY KEY,
    report_timestamp TIMESTAMP NOT NULL,
    total_records_processed INTEGER,
    valid_records INTEGER,
    invalid_records INTEGER,
    duplicates_removed INTEGER,
    missing_values_count INTEGER,
    missing_values_percentage DECIMAL(5, 2),
    data_type_errors INTEGER,
    date_conversion_errors INTEGER,
    processing_time_seconds DECIMAL(10, 3),
    report_details JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quality_reports_timestamp ON data_quality_reports(report_timestamp DESC);

-- Materialized Views for Dashboard Performance

-- Sales Summary View
CREATE MATERIALIZED VIEW sales_summary AS
SELECT
    s.sale_id,
    s.customer_id,
    c.name AS customer_name,
    s.product_id,
    p.name AS product_name,
    p.category,
    p.subcategory,
    s.quantity,
    s.unit_price,
    s.total_value,
    s.sale_date,
    s.year,
    s.month,
    s.quarter,
    s.state,
    s.payment_method
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN products p ON s.product_id = p.product_id
ORDER BY s.sale_date DESC;

-- Monthly Revenue View
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
    s.year,
    s.month,
    DATE_TRUNC('month', s.sale_date)::DATE AS month_date,
    SUM(s.total_value) AS total_revenue,
    SUM(s.quantity) AS total_units_sold,
    COUNT(DISTINCT s.sale_id) AS number_of_sales,
    COUNT(DISTINCT s.customer_id) AS unique_customers,
    AVG(s.total_value) AS average_sale_value
FROM sales s
GROUP BY s.year, s.month, DATE_TRUNC('month', s.sale_date)::DATE
ORDER BY s.year DESC, s.month DESC;

-- Product Performance View
CREATE MATERIALIZED VIEW product_performance AS
SELECT
    p.product_id,
    p.name,
    p.category,
    p.subcategory,
    COUNT(DISTINCT s.sale_id) AS times_sold,
    SUM(s.quantity) AS total_units_sold,
    SUM(s.total_value) AS total_revenue,
    AVG(s.total_value) AS average_sale_value,
    MAX(s.sale_date) AS last_sale_date
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.name, p.category, p.subcategory
ORDER BY total_revenue DESC;

-- State Sales Distribution View
CREATE MATERIALIZED VIEW state_sales_distribution AS
SELECT
    s.state,
    COUNT(DISTINCT s.sale_id) AS number_of_sales,
    SUM(s.total_value) AS total_revenue,
    COUNT(DISTINCT s.customer_id) AS unique_customers,
    AVG(s.total_value) AS average_sale_value,
    SUM(s.quantity) AS total_units_sold
FROM sales s
WHERE s.state IS NOT NULL
GROUP BY s.state
ORDER BY total_revenue DESC;

-- Category Performance View
CREATE MATERIALIZED VIEW category_performance AS
SELECT
    p.category,
    COUNT(DISTINCT s.sale_id) AS number_of_sales,
    SUM(s.total_value) AS total_revenue,
    COUNT(DISTINCT s.customer_id) AS unique_customers,
    COUNT(DISTINCT p.product_id) AS number_of_products,
    AVG(s.total_value) AS average_sale_value
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Create refresh function for materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY state_sales_distribution;
    REFRESH MATERIALIZED VIEW CONCURRENTLY category_performance;
    RAISE NOTICE 'Materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- Create indexes on materialized views for better query performance
CREATE UNIQUE INDEX idx_sales_summary_sale_id ON sales_summary(sale_id);
CREATE INDEX idx_monthly_revenue_date ON monthly_revenue(month_date DESC);
CREATE INDEX idx_product_performance_category ON product_performance(category);
CREATE INDEX idx_state_sales_state ON state_sales_distribution(state);

COMMIT;
