-- Insert sample customers
INSERT INTO customers (name, email, phone, state, city, zipcode) VALUES
('John Smith', 'john.smith@example.com', '(555) 123-4567', 'CA', 'San Francisco', '94102'),
('Mary Johnson', 'mary.johnson@example.com', '(555) 234-5678', 'NY', 'New York', '10001'),
('Robert Williams', 'robert.williams@example.com', '(555) 345-6789', 'TX', 'Houston', '77001'),
('Linda Brown', 'linda.brown@example.com', '(555) 456-7890', 'FL', 'Miami', '33101'),
('Michael Davis', 'michael.davis@example.com', '(555) 567-8901', 'PA', 'Philadelphia', '19101'),
('Patricia Miller', 'patricia.miller@example.com', '(555) 678-9012', 'IL', 'Chicago', '60601'),
('James Wilson', 'james.wilson@example.com', '(555) 789-0123', 'OH', 'Columbus', '43085'),
('Jennifer Moore', 'jennifer.moore@example.com', '(555) 890-1234', 'GA', 'Atlanta', '30303'),
('David Taylor', 'david.taylor@example.com', '(555) 901-2345', 'NC', 'Charlotte', '28202'),
('Barbara Anderson', 'barbara.anderson@example.com', '(555) 012-3456', 'AZ', 'Phoenix', '85001')
ON CONFLICT (email) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, category, price, description) VALUES
('Laptop', 'Electronics', 899.99, 'High-performance laptop with SSD storage'),
('Mouse', 'Electronics', 29.99, 'Wireless mouse with ergonomic design'),
('Keyboard', 'Electronics', 79.99, 'Mechanical keyboard with RGB lighting'),
('Monitor', 'Electronics', 299.99, '27 inch 4K monitor'),
('USB-C Cable', 'Accessories', 14.99, 'High-speed USB-C cable'),
('Phone Case', 'Accessories', 24.99, 'Protective phone case'),
('Screen Protector', 'Accessories', 9.99, 'Tempered glass screen protector'),
('Headphones', 'Audio', 199.99, 'Noise-cancelling wireless headphones'),
('Speaker', 'Audio', 149.99, 'Portable Bluetooth speaker'),
('Desk Lamp', 'Furniture', 59.99, 'LED desk lamp with adjustable brightness')
ON CONFLICT DO NOTHING;

-- Insert sample sales
INSERT INTO sales (customer_id, product_id, quantity, unit_price, total_value, sale_date, year, month, quarter) VALUES
(1, 1, 1, 899.99, 899.99, '2024-01-15', 2024, 1, 1),
(1, 2, 2, 29.99, 59.98, '2024-01-15', 2024, 1, 1),
(2, 3, 1, 79.99, 79.99, '2024-02-10', 2024, 2, 1),
(3, 4, 1, 299.99, 299.99, '2024-02-20', 2024, 2, 1),
(4, 8, 1, 199.99, 199.99, '2024-03-05', 2024, 3, 1),
(5, 9, 2, 149.99, 299.98, '2024-03-15', 2024, 3, 1),
(6, 1, 1, 899.99, 899.99, '2024-04-01', 2024, 4, 2),
(7, 5, 3, 14.99, 44.97, '2024-04-10', 2024, 4, 2),
(8, 6, 2, 24.99, 49.98, '2024-05-05', 2024, 5, 2),
(9, 7, 1, 9.99, 9.99, '2024-05-20', 2024, 5, 2),
(10, 10, 1, 59.99, 59.99, '2024-06-01', 2024, 6, 2),
(1, 3, 1, 79.99, 79.99, '2024-06-15', 2024, 6, 2)
ON CONFLICT DO NOTHING;
