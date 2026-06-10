-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    state VARCHAR(2) NOT NULL,
    city VARCHAR(100),
    zipcode VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS ix_customers_state ON customers(state);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    description VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);
CREATE INDEX IF NOT EXISTS ix_products_name ON products(name);

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    unit_price FLOAT NOT NULL,
    total_value FLOAT NOT NULL,
    sale_date DATE NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS ix_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS ix_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS ix_sales_year_month ON sales(year, month);

-- Create data quality metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metrics_id SERIAL PRIMARY KEY,
    etl_run_id VARCHAR(50) NOT NULL,
    processed_records INT NOT NULL,
    invalid_records INT NOT NULL,
    duplicates_removed INT NOT NULL,
    missing_values_percentage FLOAT NOT NULL,
    processing_time_seconds FLOAT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_quality_metrics_etl_run_id ON data_quality_metrics(etl_run_id);
CREATE INDEX IF NOT EXISTS ix_quality_metrics_created_at ON data_quality_metrics(created_at);

-- Create useful views

-- Monthly sales summary
CREATE OR REPLACE VIEW v_monthly_sales AS
SELECT 
    year,
    month,
    COUNT(*) as number_of_sales,
    SUM(total_value) as total_revenue,
    AVG(total_value) as average_sale_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- Product sales summary
CREATE OR REPLACE VIEW v_product_sales AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    COUNT(*) as number_of_sales,
    SUM(s.quantity) as total_quantity_sold,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as average_sale_value
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY total_revenue DESC;

-- Customer sales summary
CREATE OR REPLACE VIEW v_customer_sales AS
SELECT 
    c.customer_id,
    c.name,
    c.state,
    COUNT(*) as number_of_purchases,
    SUM(s.total_value) as total_spent,
    AVG(s.total_value) as average_purchase_value,
    MAX(s.sale_date) as last_purchase_date
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.state
ORDER BY total_spent DESC;

-- State sales summary
CREATE OR REPLACE VIEW v_state_sales AS
SELECT 
    c.state,
    COUNT(*) as number_of_sales,
    COUNT(DISTINCT c.customer_id) as unique_customers,
    SUM(s.total_value) as total_revenue,
    AVG(s.total_value) as average_sale_value
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.state
ORDER BY total_revenue DESC;
