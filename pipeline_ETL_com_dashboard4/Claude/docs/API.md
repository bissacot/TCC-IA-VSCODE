# API Reference

Complete API documentation for the Sales ETL Dashboard.

## ETL CLI

Command-line interface for managing the ETL pipeline.

### Commands

#### `setup` - Initialize Database

Initialize database schema and tables.

**Usage**:
```bash
python etl_cli.py setup [--drop]
```

**Options**:
- `--drop`: Drop existing tables before creating new ones (WARNING: deletes data)

**Output**:
```
Setting up database schema
Database setup completed
```

**Example**:
```bash
# Fresh setup
python etl_cli.py setup

# Reset database
python etl_cli.py setup --drop
```

#### `run` - Execute ETL Pipeline

Run the complete ETL pipeline.

**Usage**:
```bash
python etl_cli.py run
```

**Output**:
```
ETL Pipeline Execution Completed Successfully
Status: success
ETL Run ID: abc-123-def
Records Processed: 25
Records Invalid: 2
Duplicates Removed: 1
Records Loaded: 22
Records Failed: 0
Duration: 2.45 seconds
```

**Execution Flow**:
1. Initialize database
2. Extract data from sources
3. Transform and validate data
4. Load into database
5. Generate reports

## Extractor Classes

### CSVExtractor

Extract data from CSV files.

```python
from src.etl.extractor import CSVExtractor
from pathlib import Path

extractor = CSVExtractor(Path("data/sales.csv"))
data = extractor.extract()  # Returns: List[Dict[str, Any]]
```

**Methods**:
- `extract()` → `List[Dict[str, Any]]`: Extract data from CSV file

**Raises**:
- `ExtractionException`: If extraction fails

### JSONExtractor

Extract data from JSON files.

```python
from src.etl.extractor import JSONExtractor
from pathlib import Path

extractor = JSONExtractor(Path("data/customers.json"))
data = extractor.extract()  # Returns: List[Dict[str, Any]]
```

**Methods**:
- `extract()` → `List[Dict[str, Any]]`: Extract data from JSON file

**Raises**:
- `ExtractionException`: If extraction fails

### APIExtractor

Extract data from REST APIs.

```python
from src.etl.extractor import APIExtractor

extractor = APIExtractor(
    endpoint="https://api.example.com/products",
    timeout=30,
    headers={"Authorization": "Bearer token"}
)
data = extractor.extract()  # Returns: List[Dict[str, Any]]
```

**Constructor**:
- `endpoint` (str): API endpoint URL
- `timeout` (int): Request timeout in seconds (default: 30)
- `headers` (Dict[str, str]): HTTP headers (default: JSON content-type)

**Methods**:
- `extract()` → `List[Dict[str, Any]]`: Extract data from API

**Raises**:
- `ExtractionException`: If API request fails

## Transformer Classes

### SalesTransformer

Transform and validate sales data.

```python
from src.etl.transformer import SalesTransformer

transformer = SalesTransformer()
data, report = transformer.transform(raw_sales_data)
```

**Methods**:
- `transform(raw_data)` → `Tuple[List[Dict], DataQualityReport]`: Transform sales data

**Validation Rules**:
- Required fields: customer_id, product_id, quantity, unit_price, sale_date
- Valid quantity: positive integer
- Valid price: positive float
- Valid date: ISO format (YYYY-MM-DD)
- Duplicate detection: by customer_id + product_id + sale_date

### CustomerTransformer

Transform and validate customer data.

```python
from src.etl.transformer import CustomerTransformer

transformer = CustomerTransformer()
data, report = transformer.transform(raw_customer_data)
```

**Methods**:
- `transform(raw_data)` → `Tuple[List[Dict], DataQualityReport]`: Transform customer data

**Validation Rules**:
- Required fields: name, email, state
- Valid email: RFC compliant format
- Unique email: duplicate detection enabled
- Valid state: 2-character code
- Data cleaning: strip whitespace, handle None values

### ProductTransformer

Transform and validate product data.

```python
from src.etl.transformer import ProductTransformer

transformer = ProductTransformer()
data, report = transformer.transform(raw_product_data)
```

**Methods**:
- `transform(raw_data)` → `Tuple[List[Dict], DataQualityReport]`: Transform product data

**Validation Rules**:
- Required fields: name, category, price
- Valid price: positive float
- Duplicate detection: by name + category

## DataQualityReport

Track data quality metrics.

```python
from src.etl.transformer import DataQualityReport

report = DataQualityReport()
report.processed_records = 100
report.invalid_records = 5
report.duplicates_removed = 2
report.missing_values_percentage = 1.5
report.set_processing_time(2.45)

metrics = report.to_dict()
# Returns:
# {
#     'processed_records': 100,
#     'invalid_records': 5,
#     'duplicates_removed': 2,
#     'missing_values_percentage': 1.5,
#     'processing_time_seconds': 2.45
# }
```

**Attributes**:
- `processed_records` (int): Total records processed
- `invalid_records` (int): Records with errors
- `duplicates_removed` (int): Duplicate records
- `missing_values_percentage` (float): Percentage of missing data
- `processing_time` (float): Execution time in seconds

**Methods**:
- `to_dict()` → `Dict[str, Any]`: Convert report to dictionary

## DataLoader

Load transformed data into PostgreSQL.

```python
from src.etl.loader import DataLoader

loader = DataLoader()
loader.load_customers(customers_data)
loader.load_products(products_data)
loader.load_sales(sales_data)
loader.save_quality_metrics(quality_report)
```

**Methods**:
- `load_customers(data)` → `int`: Load customer records (returns count)
- `load_products(data)` → `int`: Load product records (returns count)
- `load_sales(data)` → `int`: Load sales records (returns count)
- `save_quality_metrics(report, status)` → `None`: Save quality metrics
- `get_status_summary()` → `Dict`: Get execution summary

**Raises**:
- `LoadingException`: If loading fails
- `IntegrityError`: If unique/foreign key constraints violated

## Database Models

### Customer

```python
from src.database import Customer

# Create
customer = Customer(
    name="John Smith",
    email="john@example.com",
    phone="(555) 123-4567",
    state="CA",
    city="San Francisco",
    zipcode="94102"
)

# Attributes
customer.customer_id          # int
customer.name                 # str
customer.email                # str (unique)
customer.phone                # str (optional)
customer.state                # str
customer.city                 # str (optional)
customer.zipcode              # str (optional)
customer.created_at           # datetime
customer.updated_at           # datetime
```

### Product

```python
from src.database import Product

# Create
product = Product(
    name="Laptop",
    category="Electronics",
    price=899.99,
    description="High-performance laptop"
)

# Attributes
product.product_id            # int
product.name                  # str
product.category              # str
product.price                 # float
product.description           # str (optional)
product.created_at            # datetime
product.updated_at            # datetime
```

### Sale

```python
from src.database import Sale
from datetime import date

# Create
sale = Sale(
    customer_id=1,
    product_id=1,
    quantity=2,
    unit_price=899.99,
    total_value=1799.98,
    sale_date=date(2024, 1, 15),
    year=2024,
    month=1,
    quarter=1
)

# Attributes
sale.sale_id                  # int
sale.customer_id              # int (FK)
sale.product_id               # int (FK)
sale.quantity                 # int
sale.unit_price               # float
sale.total_value              # float
sale.sale_date                # date
sale.year                     # int
sale.month                    # int
sale.quarter                  # int
sale.created_at               # datetime
sale.updated_at               # datetime

# Relationships
sale.customer                 # Customer object
sale.product                  # Product object
```

### DataQualityMetrics

```python
from src.database import DataQualityMetrics

# Attributes
metrics.metrics_id             # int
metrics.etl_run_id             # str
metrics.processed_records      # int
metrics.invalid_records        # int
metrics.duplicates_removed     # int
metrics.missing_values_percentage  # float
metrics.processing_time_seconds    # float
metrics.status                 # str (success/failed)
metrics.created_at             # datetime
```

## Validators

### DataValidator

```python
from src.utils import DataValidator

# Email validation
DataValidator.validate_email("john@example.com")  # True
DataValidator.validate_email("invalid")           # False

# Date validation
DataValidator.validate_date("2024-01-15", "%Y-%m-%d")  # True

# Numeric validation
DataValidator.validate_numeric("123.45")          # True
DataValidator.validate_positive_numeric("100")    # True

# Currency validation
DataValidator.validate_currency("99.99")          # True
DataValidator.validate_currency("-50")            # False

# Phone validation
DataValidator.validate_phone("+1-555-123-4567")   # True

# Required fields validation
record = {"name": "John", "email": "john@example.com"}
DataValidator.validate_required_fields(
    record,
    ["name", "email"]
)  # True

# String sanitization
DataValidator.sanitize_string("  John  ")         # "John"
DataValidator.sanitize_string(None)               # None
```

### DataTypeValidator

```python
from src.utils import DataTypeValidator

# Float conversion
DataTypeValidator.to_float("123.45")              # 123.45
DataTypeValidator.to_float("invalid", 0.0)       # 0.0

# Integer conversion
DataTypeValidator.to_int("123.45")                # 123
DataTypeValidator.to_int("invalid", 0)            # 0

# Boolean conversion
DataTypeValidator.to_bool("true")                 # True
DataTypeValidator.to_bool("1")                    # True
DataTypeValidator.to_bool(0)                      # False
```

## Configuration

### Settings

```python
from config.settings import *

# Database
DB_HOST          # "localhost"
DB_PORT          # 5432
DB_NAME          # "sales_etl_db"
DB_USER          # "postgres"
DB_PASSWORD      # "postgres"
DB_URL           # Full connection string

# Paths
PROJECT_ROOT     # Project root directory
DATA_PATH        # "./data"
REPORTS_PATH     # "./reports"
LOGS_PATH        # "./logs"

# ETL
BATCH_SIZE       # 1000
INCREMENTAL_PROCESSING  # True

# API
API_BASE_URL     # "https://api.example.com"
API_TIMEOUT      # 30

# Logging
LOG_LEVEL        # "INFO"
LOG_FORMAT       # Format string
LOG_FILE         # Path to log file
```

## Database Queries

### View: v_monthly_sales

Monthly sales summary.

```sql
SELECT * FROM v_monthly_sales;

-- Output:
-- year | month | number_of_sales | total_revenue | average_sale_value | unique_customers
```

### View: v_product_sales

Product sales summary.

```sql
SELECT * FROM v_product_sales
ORDER BY total_revenue DESC;

-- Output:
-- product_id | name | category | number_of_sales | total_quantity_sold | total_revenue | average_sale_value
```

### View: v_customer_sales

Customer sales summary.

```sql
SELECT * FROM v_customer_sales
WHERE total_spent > 1000;

-- Output:
-- customer_id | name | state | number_of_purchases | total_spent | average_purchase_value | last_purchase_date
```

### View: v_state_sales

State sales summary.

```sql
SELECT * FROM v_state_sales
ORDER BY total_revenue DESC;

-- Output:
-- state | number_of_sales | unique_customers | total_revenue | average_sale_value
```

## Error Handling

### Exception Hierarchy

```
ETLException (base)
├── ExtractionException
├── TransformationException
├── LoadingException
├── ValidationException
├── DatabaseException
├── APIException
├── ConfigurationException
└── FileException
```

### Usage

```python
from src.utils import ETLException, ExtractionException

try:
    data = extractor.extract()
except ExtractionException as e:
    logger.error(f"Extraction failed: {e}")
except ETLException as e:
    logger.error(f"ETL error: {e}")
```

## Logging

### Get Logger

```python
from src.utils import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

# Log at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Log Output

Logs are written to:
- Console: Real-time output
- File: `./logs/etl.log`

Format: `timestamp - name - level - message`

## Rate Limits & Constraints

| Item | Limit |
|------|-------|
| Max records per batch | No hard limit |
| API timeout | 30 seconds |
| Max missing value percentage | 30% |
| Min record count | 100 |
| DB connection pool | 1-10 connections |
| Max bulk insert size | Database dependent |

## Example Usage

### Complete ETL Pipeline

```python
from src.etl import ETLPipeline

# Run pipeline
pipeline = ETLPipeline()
results = pipeline.run()

# Access results
print(f"Status: {results['status']}")
print(f"Records processed: {results['records_processed']}")
print(f"Duration: {results['duration_seconds']}s")
```

### Manual Data Processing

```python
from src.etl.extractor import CSVExtractor
from src.etl.transformer import SalesTransformer
from src.etl.loader import DataLoader
from pathlib import Path

# Extract
extractor = CSVExtractor(Path("data/sales.csv"))
raw_data = extractor.extract()

# Transform
transformer = SalesTransformer()
transformed_data, quality_report = transformer.transform(raw_data)

# Load
loader = DataLoader()
loader.load_sales(transformed_data)
loader.save_quality_metrics(quality_report)
```

### Query Examples

```sql
-- Top 10 customers by revenue
SELECT c.customer_id, c.name, SUM(s.total_value) as total_spent
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 10;

-- Monthly revenue trend
SELECT CONCAT(year, '-', LPAD(month::TEXT, 2, '0')) as month,
       SUM(total_value) as revenue,
       COUNT(*) as num_sales
FROM sales
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- Product performance
SELECT p.category, p.name, COUNT(*) as times_sold, SUM(s.total_value) as revenue
FROM products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.category, p.name
ORDER BY revenue DESC;
```
