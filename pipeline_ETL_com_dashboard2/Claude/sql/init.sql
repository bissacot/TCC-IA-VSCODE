-- Create schema for sales analytics
-- PostgreSQL initialization script

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    state VARCHAR(2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on customers
CREATE INDEX IF NOT EXISTS ix_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS ix_customers_state ON customers(state);
CREATE INDEX IF NOT EXISTS ix_customers_created_at ON customers(created_at);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    description VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on products
CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);
CREATE INDEX IF NOT EXISTS ix_products_created_at ON products(created_at);

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    total_value NUMERIC(12, 2) NOT NULL,
    sale_date TIMESTAMP NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    quarter INTEGER NOT NULL CHECK (quarter >= 1 AND quarter <= 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on sales
CREATE INDEX IF NOT EXISTS ix_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS ix_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS ix_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS ix_sales_year_month ON sales(year, month);
CREATE INDEX IF NOT EXISTS ix_sales_created_at ON sales(created_at);

-- Create data quality metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_records_processed INTEGER NOT NULL,
    invalid_records INTEGER NOT NULL,
    missing_values_percentage NUMERIC(5, 2) NOT NULL,
    duplicates_removed INTEGER NOT NULL,
    transformation_time_seconds NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details VARCHAR(2000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on data quality metrics
CREATE INDEX IF NOT EXISTS ix_dqm_extraction_timestamp ON data_quality_metrics(extraction_timestamp);
CREATE INDEX IF NOT EXISTS ix_dqm_status ON data_quality_metrics(status);

-- Create views for analytics

-- View: Sales by State
CREATE OR REPLACE VIEW sales_by_state AS
SELECT 
    c.state,
    COUNT(s.sale_id) as num_sales,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as avg_sale_value,
    MAX(s.sale_date) as last_sale_date
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.state
ORDER BY total_revenue DESC;

-- View: Sales by Category
CREATE OR REPLACE VIEW sales_by_category AS
SELECT 
    p.category,
    COUNT(s.sale_id) as num_sales,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as avg_sale_value,
    SUM(s.quantity) as total_quantity
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- View: Monthly Sales Summary
CREATE OR REPLACE VIEW monthly_sales_summary AS
SELECT 
    s.year,
    s.month,
    COUNT(s.sale_id) as num_sales,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as avg_sale_value,
    COUNT(DISTINCT s.customer_id) as unique_customers
FROM sales s
GROUP BY s.year, s.month
ORDER BY s.year DESC, s.month DESC;

-- View: Product Performance
CREATE OR REPLACE VIEW product_performance AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    p.price,
    COUNT(s.sale_id) as num_sales,
    SUM(s.quantity) as total_quantity,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as avg_sale_value
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.name, p.category, p.price
ORDER BY total_revenue DESC;

-- View: Customer Lifetime Value
CREATE OR REPLACE VIEW customer_lifetime_value AS
SELECT 
    c.customer_id,
    c.name,
    c.state,
    COUNT(s.sale_id) as num_purchases,
    SUM(s.total_value) as total_spent,
    AVG(s.total_value) as avg_purchase_value,
    MAX(s.sale_date) as last_purchase_date,
    MIN(s.sale_date) as first_purchase_date
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.state
ORDER BY total_spent DESC;
