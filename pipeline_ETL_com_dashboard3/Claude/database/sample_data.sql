"""Sample data for testing."""

-- Insert sample customers
INSERT INTO customers (customer_id, name, email, phone, city, state, country, registration_date)
VALUES 
    ('CUST001', 'John Smith', 'john.smith@example.com', '555-0001', 'New York', 'NY', 'USA', '2024-01-15'),
    ('CUST002', 'Jane Doe', 'jane.doe@example.com', '555-0002', 'Los Angeles', 'CA', 'USA', '2024-01-20'),
    ('CUST003', 'Bob Johnson', 'bob.johnson@example.com', '555-0003', 'Chicago', 'IL', 'USA', '2024-02-01'),
    ('CUST004', 'Alice Brown', 'alice.brown@example.com', '555-0004', 'Houston', 'TX', 'USA', '2024-02-10'),
    ('CUST005', 'Charlie Wilson', 'charlie.wilson@example.com', '555-0005', 'Phoenix', 'AZ', 'USA', '2024-02-15')
ON CONFLICT (customer_id) DO NOTHING;

-- Insert sample products
INSERT INTO products (product_id, name, category, price, description, sku)
VALUES 
    ('PROD001', 'Laptop Pro', 'Electronics', 1299.99, 'Professional laptop for developers', 'SKU-LP001'),
    ('PROD002', 'Wireless Mouse', 'Electronics', 29.99, 'Ergonomic wireless mouse', 'SKU-WM001'),
    ('PROD003', 'USB-C Cable', 'Accessories', 19.99, 'High-speed USB-C cable', 'SKU-UC001'),
    ('PROD004', 'Desk Lamp', 'Office', 49.99, 'LED desk lamp with adjustable brightness', 'SKU-DL001'),
    ('PROD005', 'Office Chair', 'Furniture', 299.99, 'Ergonomic office chair', 'SKU-OC001')
ON CONFLICT (product_id) DO NOTHING;

-- Insert sample sales
INSERT INTO sales (sale_id, customer_id, product_id, quantity, unit_price, total_value, sale_date, sale_year, sale_month, sale_quarter)
VALUES 
    ('SALE001', 'CUST001', 'PROD001', 1, 1299.99, 1299.99, '2024-03-01 10:30:00', 2024, 3, 1),
    ('SALE002', 'CUST001', 'PROD002', 2, 29.99, 59.98, '2024-03-05 14:15:00', 2024, 3, 1),
    ('SALE003', 'CUST002', 'PROD003', 5, 19.99, 99.95, '2024-03-10 09:45:00', 2024, 3, 1),
    ('SALE004', 'CUST002', 'PROD004', 1, 49.99, 49.99, '2024-03-15 11:20:00', 2024, 3, 1),
    ('SALE005', 'CUST003', 'PROD005', 1, 299.99, 299.99, '2024-03-20 13:00:00', 2024, 3, 1),
    ('SALE006', 'CUST004', 'PROD001', 1, 1299.99, 1299.99, '2024-04-01 08:30:00', 2024, 4, 2),
    ('SALE007', 'CUST005', 'PROD002', 3, 29.99, 89.97, '2024-04-05 15:45:00', 2024, 4, 2)
ON CONFLICT (sale_id) DO NOTHING;
