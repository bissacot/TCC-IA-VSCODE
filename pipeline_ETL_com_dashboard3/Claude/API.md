# API Documentation

## Extractor Classes

### BaseExtractor
Abstract base class for all data extractors.

**Methods:**
- `extract() -> pd.DataFrame`: Extract and return data
- `validate_source() -> bool`: Validate data source accessibility

### CSVExtractor

**Initialization:**
```python
from src.extractors import CSVExtractor

extractor = CSVExtractor(
    file_path="data/input/sales.csv",
    encoding="utf-8"
)
```

**Parameters:**
- `file_path` (str): Path to CSV file
- `encoding` (str): File encoding (default: utf-8)

**Methods:**
- `extract() -> pd.DataFrame`: Load CSV and return DataFrame
- `validate_source() -> bool`: Check file exists and is readable

**Raises:**
- `ExtractionException`: If file invalid or reading fails

**Example:**
```python
try:
    extractor = CSVExtractor("data/input/sales.csv")
    df = extractor.extract()
    print(f"Loaded {len(df)} rows")
except ExtractionException as e:
    print(f"Error: {e}")
```

### JSONExtractor

**Initialization:**
```python
from src.extractors import JSONExtractor

extractor = JSONExtractor(
    file_path="data/input/customers.json",
    encoding="utf-8"
)
```

**Parameters:**
- `file_path` (str): Path to JSON file
- `encoding` (str): File encoding (default: utf-8)

**Methods:**
- `extract() -> pd.DataFrame`: Load JSON and return DataFrame
- `validate_source() -> bool`: Check file exists and is readable

**JSON Format Support:**
- Direct list: `[{...}, {...}]`
- Wrapped in data key: `{"data": [{...}, {...}]}`

**Raises:**
- `ExtractionException`: If JSON invalid or reading fails

### APIExtractor

**Initialization:**
```python
from src.extractors import APIExtractor
from src.utils.config import APIConfig

api_config = APIConfig(
    base_url="https://api.example.com",
    timeout=30,
    retry_attempts=3,
    retry_delay=5
)

extractor = APIExtractor(
    api_config=api_config,
    endpoint="/api/products",
    params={"limit": 100},
    headers={"Authorization": "Bearer TOKEN"}
)
```

**Parameters:**
- `api_config` (APIConfig): API configuration
- `endpoint` (str): API endpoint path
- `params` (Dict): Query parameters (optional)
- `headers` (Dict): Custom headers (optional)

**Methods:**
- `extract() -> pd.DataFrame`: Call API and return DataFrame
- `validate_source() -> bool`: Test API connectivity
- `close()`: Close session

**Raises:**
- `ExtractionException`: If API call fails
- `APIException`: If connectivity issues

## Transformer Class

### DataTransformer

**Initialization:**
```python
from src.transformers import DataTransformer

transformer = DataTransformer()
```

**Methods:**

#### transform_sales_data
```python
df_transformed, quality_report = transformer.transform_sales_data(df_raw)
```

Applies all transformations to sales data:
- Remove duplicates
- Handle missing values
- Validate data types
- Standardize dates
- Create derived metrics
- Validate business rules

**Parameters:**
- `df` (pd.DataFrame): Raw sales DataFrame

**Returns:**
- Tuple of (transformed DataFrame, DataQualityReport)

**Raises:**
- `TransformationException`: If transformation fails

#### transform_customer_data
```python
df_transformed, quality_report = transformer.transform_customer_data(df_raw)
```

Applies transformations to customer data.

#### transform_product_data
```python
df_transformed, quality_report = transformer.transform_product_data(df_raw)
```

Applies transformations to product data.

## Loader Classes

### DatabaseManager

**Initialization:**
```python
from src.loaders import DatabaseManager
from src.utils.config import DatabaseConfig

db_config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="sales_db",
    user="postgres",
    password="password"
)

manager = DatabaseManager(db_config, pool_size=5)
```

**Methods:**

#### execute_query
```python
results = manager.execute_query(
    "SELECT * FROM customers WHERE state = %s",
    ("NY",)
)
```

Execute SELECT query. Returns list of dictionaries.

#### execute_update
```python
rows_affected = manager.execute_update(
    "UPDATE customers SET name = %s WHERE customer_id = %s",
    ("New Name", "CUST001")
)
```

Execute INSERT/UPDATE/DELETE. Returns affected row count.

#### execute_batch
```python
data = [
    ("CUST001", "John", "john@example.com"),
    ("CUST002", "Jane", "jane@example.com")
]

rows_affected = manager.execute_batch(
    "INSERT INTO customers (customer_id, name, email) VALUES (%s, %s, %s)",
    data,
    batch_size=1000
)
```

Execute batch operations efficiently.

#### table_exists
```python
exists = manager.table_exists("sales")
```

Check if table exists in database.

#### close
```python
manager.close()
```

Close all connections in pool.

### DataLoader

**Initialization:**
```python
from src.loaders import DataLoader

loader = DataLoader(db_config)
```

**Methods:**

#### load_customers
```python
rows = loader.load_customers(customers_df, incremental=False)
```

Load customer data with upsert logic.

#### load_products
```python
rows = loader.load_products(products_df, incremental=False)
```

Load product data with upsert logic.

#### load_sales
```python
rows = loader.load_sales(sales_df, incremental=False)
```

Load sales data with upsert logic.

#### close
```python
loader.close()
```

Close database connections.

## ETL Pipeline

### ETLPipeline

**Initialization:**
```python
from src.etl_pipeline import ETLPipeline
from src.utils.config import load_config_from_env

config = load_config_from_env()
pipeline = ETLPipeline(config)
```

**Methods:**

#### run
```python
summary = pipeline.run()
```

Execute complete ETL pipeline:
1. Extract data from all sources
2. Transform data
3. Load data to database
4. Generate quality report

**Returns:**
Dictionary with execution summary:
```python
{
    'status': 'success',
    'start_time': '2024-01-15T10:30:00',
    'end_time': '2024-01-15T10:45:00',
    'duration_seconds': 900,
    'total_records_processed': 10000,
    'total_invalid_records': 5,
    'duplicates_removed': 10,
    'records_by_source': {...},
    'missing_values_percentage': {...}
}
```

**Raises:**
- `ETLException`: If any stage fails

## Configuration Management

### load_config_from_env
```python
from src.utils.config import load_config_from_env

config = load_config_from_env()
```

Load configuration from environment variables.

### load_config_from_file
```python
from src.utils.config import load_config_from_file

config = load_config_from_file("config/etl_config.json")
```

Load configuration from JSON file.

## Models

### Customer
```python
from src.utils.models import Customer

customer = Customer(
    customer_id="CUST001",
    name="John Smith",
    email="john@example.com",
    phone="555-0001",
    city="New York",
    state="NY",
    country="USA",
    registration_date=datetime.now()
)

customer_dict = customer.to_dict()
```

### Product
```python
from src.utils.models import Product
from decimal import Decimal

product = Product(
    product_id="PROD001",
    name="Laptop",
    category="Electronics",
    price=Decimal("1299.99"),
    description="Professional laptop",
    sku="SKU-001"
)

product_dict = product.to_dict()
```

### Sale
```python
from src.utils.models import Sale
from decimal import Decimal
from datetime import datetime

sale = Sale(
    sale_id="SALE001",
    customer_id="CUST001",
    product_id="PROD001",
    quantity=2,
    unit_price=Decimal("1299.99"),
    total_value=Decimal("2599.98"),
    sale_date=datetime.now()
)

# Derived fields automatically calculated
print(sale.sale_month)  # 1-12
print(sale.sale_year)   # 2024
print(sale.sale_quarter)  # 1-4

sale_dict = sale.to_dict()
```

### DataQualityReport
```python
from src.utils.models import DataQualityReport

report = DataQualityReport()
report.total_records_processed = 1000
report.duplicates_removed = 5
report.total_invalid_records = 2
report.missing_values_percentage = {"email": 1.5}
report.records_by_source = {"csv": 500, "json": 500}

report_dict = report.to_dict()
```

## Exceptions

### Exception Hierarchy
```
ETLException (base)
├── ExtractionException
├── TransformationException
├── LoadingException
├── ValidationException
├── DatabaseException
├── APIException
└── ConfigException
```

### Usage
```python
from src.utils.exceptions import *

try:
    extractor = CSVExtractor("data.csv")
    df = extractor.extract()
except ExtractionException as e:
    print(f"Extraction failed: {e}")
except ETLException as e:
    print(f"ETL error: {e}")
```

## Logging

### Setup Logger
```python
from src.utils.logger import setup_logger

logger = setup_logger(
    name="my_module",
    log_file="logs/my_module.log",
    level="INFO"
)

logger.info("Processing started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Log Levels
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

---

For more examples and usage patterns, see the test files in `tests/`.
