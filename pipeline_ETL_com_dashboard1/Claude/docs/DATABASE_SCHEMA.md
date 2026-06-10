# Database Schema Documentation

## Overview

The database schema is designed using dimensional modeling (star schema) with fact and dimension tables for optimal OLAP (Online Analytical Processing) performance.

## Schema Diagram

```
┌─────────────────────┐
│  Customers          │ (Dimension)
│─────────────────────│
│ PK customer_id      │
│    name             │
│    email            │
│    phone            │
│    state            │
│    city             │
│    created_at       │
│    updated_at       │
└─────────────────────┘
        │ FK
        │
        ├─ (1 : N) ──┐
                      │
┌─────────────────────────────────────┐
│  Sales (Fact Table)                 │
│─────────────────────────────────────│
│ PK sale_id                          │
│ FK customer_id (→ customers)        │
│ FK product_id (→ products)          │
│    quantity                         │
│    unit_price                       │
│    total_value                      │
│    sale_date                        │
│    year                             │
│    month                            │
│    quarter                          │
│    created_at                       │
└─────────────────────────────────────┘
        │ FK
        │
        ├─ (1 : N) ──┐
                      │
┌─────────────────────┐
│  Products           │ (Dimension)
│─────────────────────│
│ PK product_id       │
│    name             │
│    category         │
│    price            │
│    description      │
│    active           │
│    created_at       │
│    updated_at       │
└─────────────────────┘

Supporting Tables:

┌──────────────────────────────────────┐
│  data_quality_report                 │
│──────────────────────────────────────│
│ PK id                                │
│    execution_date                    │
│    total_records_processed           │
│    invalid_records                   │
│    duplicate_records_removed         │
│    missing_values_percentage         │
│    sales_records                     │
│    customer_records                  │
│    product_records                   │
│    status                            │
│    error_message                     │
│    execution_time_seconds            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  incremental_load_log                │
│──────────────────────────────────────│
│ PK id                                │
│ UQ source_name                       │
│    last_loaded_id                    │
│    last_loaded_timestamp             │
│    last_modified_timestamp           │
│    records_loaded                    │
│    load_timestamp                    │
└──────────────────────────────────────┘
```

## Table Specifications

### 1. CUSTOMERS (Dimension Table)

**Purpose**: Store customer information

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| customer_id | VARCHAR(50) | PRIMARY KEY | Unique customer identifier |
| name | VARCHAR(255) | NOT NULL | Customer full name |
| email | VARCHAR(255) | NULLABLE | Customer email address |
| phone | VARCHAR(20) | NULLABLE | Customer phone number |
| state | VARCHAR(50) | NOT NULL | State code (UF) |
| city | VARCHAR(100) | NULLABLE | City name |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes**:
```sql
CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_customer_state ON customers(state);
```

**Sample Data**:
```
C001 | João Silva | joao@example.com | (11) 98765-4321 | SP | São Paulo
C002 | Maria Santos | maria@example.com | (21) 99876-5432 | RJ | Rio de Janeiro
```

### 2. PRODUCTS (Dimension Table)

**Purpose**: Store product catalog

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_id | VARCHAR(50) | PRIMARY KEY | Unique product identifier |
| name | VARCHAR(255) | NOT NULL | Product name |
| category | VARCHAR(100) | NOT NULL | Product category |
| price | NUMERIC(12,2) | NOT NULL | Product unit price |
| description | TEXT | NULLABLE | Product description |
| active | BOOLEAN | DEFAULT TRUE | Product status |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Record update timestamp |

**Indexes**:
```sql
CREATE INDEX idx_product_category ON products(category);
CREATE INDEX idx_product_active ON products(active);
```

**Sample Data**:
```
P001 | Laptop | Electronics | 3000.00 | High-performance laptop
P002 | Mouse | Electronics | 50.00 | Wireless mouse
P003 | Keyboard | Electronics | 150.00 | Mechanical keyboard
```

### 3. SALES (Fact Table)

**Purpose**: Store all sales transactions

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | VARCHAR(50) | PRIMARY KEY | Unique sale identifier |
| customer_id | VARCHAR(50) | FK NOT NULL | Reference to customers table |
| product_id | VARCHAR(50) | FK NOT NULL | Reference to products table |
| quantity | INTEGER | NOT NULL | Number of units sold |
| unit_price | NUMERIC(12,2) | NOT NULL | Price per unit at sale time |
| total_value | NUMERIC(12,2) | NOT NULL | Quantity × Unit Price |
| sale_date | DATE | NOT NULL | Date of sale |
| year | INTEGER | NOT NULL | Year extracted from sale_date |
| month | INTEGER | NOT NULL | Month extracted from sale_date |
| quarter | INTEGER | NOT NULL | Quarter extracted from sale_date |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |

**Indexes**:
```sql
CREATE INDEX idx_sale_customer_id ON sales(customer_id);
CREATE INDEX idx_sale_product_id ON sales(product_id);
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_sale_year_month ON sales(year, month);
CREATE UNIQUE CONSTRAINT uq_sale_id ON sales(sale_id);
```

**Foreign Keys**:
```sql
ALTER TABLE sales ADD CONSTRAINT fk_customer_id 
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE sales ADD CONSTRAINT fk_product_id 
  FOREIGN KEY (product_id) REFERENCES products(product_id);
```

### 4. DATA_QUALITY_REPORT (Logging Table)

**Purpose**: Track ETL execution quality metrics

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing identifier |
| execution_date | TIMESTAMP | DEFAULT NOW() | When ETL executed |
| total_records_processed | INTEGER | NOT NULL | Total records attempted |
| invalid_records | INTEGER | NOT NULL | Records that failed validation |
| duplicate_records_removed | INTEGER | NOT NULL | Duplicate records detected |
| missing_values_percentage | FLOAT | NOT NULL | % of missing values |
| sales_records | INTEGER | NOT NULL | Sales records loaded |
| customer_records | INTEGER | NOT NULL | Customers records loaded |
| product_records | INTEGER | NOT NULL | Products records loaded |
| status | VARCHAR(20) | NOT NULL | SUCCESS, PARTIAL, FAILED |
| error_message | TEXT | NULLABLE | Error details if failed |
| execution_time_seconds | FLOAT | NOT NULL | Total execution duration |

**Indexes**:
```sql
CREATE INDEX idx_quality_execution_date ON data_quality_report(execution_date);
CREATE INDEX idx_quality_status ON data_quality_report(status);
```

### 5. INCREMENTAL_LOAD_LOG (Control Table)

**Purpose**: Track incremental data loads

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing identifier |
| source_name | VARCHAR(50) | UNIQUE NOT NULL | Data source identifier |
| last_loaded_id | VARCHAR(255) | NULLABLE | Last record ID loaded |
| last_loaded_timestamp | TIMESTAMP | NULLABLE | Timestamp of last load |
| last_modified_timestamp | TIMESTAMP | NOT NULL | When this log was updated |
| records_loaded | INTEGER | NOT NULL | Count of records in last load |
| load_timestamp | TIMESTAMP | DEFAULT NOW() | When load occurred |

**Indexes**:
```sql
CREATE INDEX idx_incremental_source ON incremental_load_log(source_name);
```

**Sample Data**:
```
source_name=sales, last_loaded_id=S100, records_loaded=50
source_name=customers, last_loaded_id=C50, records_loaded=10
source_name=products, last_loaded_id=P20, records_loaded=5
```

## Views

### sales_summary (Materialized View)

**Purpose**: Pre-aggregated data for faster dashboard queries

**Query**:
```sql
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
```

**Indexes**:
```sql
CREATE INDEX idx_sales_summary_date ON sales_summary(year, month);
CREATE INDEX idx_sales_summary_category ON sales_summary(category);
CREATE INDEX idx_sales_summary_state ON sales_summary(state);
```

## Key Queries

### Total Revenue
```sql
SELECT SUM(total_value) as total_revenue FROM sales;
```

### Revenue by Month
```sql
SELECT 
    year,
    month,
    SUM(total_value) as revenue,
    COUNT(*) as sales_count
FROM sales
GROUP BY year, month
ORDER BY year DESC, month DESC;
```

### Revenue by Category
```sql
SELECT 
    p.category,
    SUM(s.total_value) as revenue,
    COUNT(s.sale_id) as sales_count
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

### Top Products
```sql
SELECT 
    p.product_id,
    p.name,
    SUM(s.quantity) as quantity_sold,
    SUM(s.total_value) as revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY quantity_sold DESC
LIMIT 10;
```

### Revenue by State
```sql
SELECT 
    c.state,
    SUM(s.total_value) as revenue,
    COUNT(s.sale_id) as sales_count,
    COUNT(DISTINCT s.customer_id) as unique_customers
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.state
ORDER BY revenue DESC;
```

## Performance Optimization

### Index Strategy

1. **Fact Table Indexes**: On foreign keys and date columns
2. **Dimension Table Indexes**: On commonly filtered columns
3. **Query Optimization**: Use EXPLAIN to analyze queries
4. **Statistics**: ANALYZE tables regularly

### Query Examples with EXPLAIN

```sql
-- Analyze query performance
EXPLAIN ANALYZE 
SELECT SUM(total_value) FROM sales 
WHERE year = 2024 AND month = 1;

-- With JOIN
EXPLAIN ANALYZE
SELECT SUM(s.total_value)
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
WHERE c.state = 'SP' AND s.year = 2024;
```

## Data Types Rationale

| Type | Usage | Reason |
|------|-------|--------|
| VARCHAR(50) | IDs | Flexible for alphanumeric codes |
| VARCHAR(255) | Names | Standard text field length |
| NUMERIC(12,2) | Prices/Money | Precise decimal for financial data |
| DATE | Dates | Optimize storage vs. TIMESTAMP |
| TIMESTAMP | Audit columns | Track record changes |
| INTEGER | Counts/Year/Month | Efficient integer storage |
| BOOLEAN | Flags | Binary choice storage |
| TEXT | Descriptions | Unlimited text |

## Maintenance Tasks

### Regular Maintenance

```sql
-- Vacuum and analyze (weekly)
VACUUM ANALYZE;

-- Check table size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check indexes
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname != 'pg_catalog';
```

## Backup Strategy

```bash
# Full backup
pg_dump sales_db > sales_db_backup.sql

# Compressed backup
pg_dump -Fc sales_db > sales_db_backup.dump

# Restore from backup
psql sales_db < sales_db_backup.sql
# or
pg_restore -d sales_db sales_db_backup.dump
```
