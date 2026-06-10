"""Database initialization and migrations."""

-- Drop existing tables if they exist
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Create customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    registration_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sales table
CREATE TABLE sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_value DECIMAL(12, 2) NOT NULL CHECK (total_value >= 0),
    sale_date TIMESTAMP NOT NULL,
    sale_year INTEGER,
    sale_month INTEGER,
    sale_quarter INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_year_month ON sales(sale_year, sale_month);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_customers_state ON customers(state);
CREATE INDEX idx_customers_email ON customers(email);

-- Create view for sales summary
CREATE VIEW sales_summary AS
SELECT 
    DATE_TRUNC('month', s.sale_date) AS month,
    p.category,
    COUNT(*) AS sales_count,
    SUM(s.total_value) AS total_revenue,
    AVG(s.total_value) AS avg_value,
    COUNT(DISTINCT s.customer_id) AS customers
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY DATE_TRUNC('month', s.sale_date), p.category;

-- Create view for top products
CREATE VIEW top_products AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    p.price,
    COUNT(*) AS sales_count,
    SUM(s.quantity) AS total_quantity,
    SUM(s.total_value) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category, p.price
ORDER BY total_revenue DESC;

-- Create view for customer analysis
CREATE VIEW customer_analysis AS
SELECT 
    c.customer_id,
    c.name,
    c.email,
    c.state,
    COUNT(s.sale_id) AS purchase_count,
    SUM(s.total_value) AS total_spent,
    AVG(s.total_value) AS avg_purchase,
    MAX(s.sale_date) AS last_purchase_date
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.email, c.state;
