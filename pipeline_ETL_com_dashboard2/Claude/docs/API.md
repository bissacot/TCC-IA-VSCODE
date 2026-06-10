# API Documentation

## Overview

This document provides comprehensive API documentation for the ETL and Dashboard solution.

## Module APIs

### ETL Extractors

#### CSVExtractor

```python
from src.etl.extractor import CSVExtractor

extractor = CSVExtractor(file_path="data/sales.csv")
df = extractor.extract()
```

**Methods:**
- `extract() -> pd.DataFrame`: Extract data from CSV file

**Raises:**
- `ExtractionException`: If file not found or extraction fails

#### JSONExtractor

```python
from src.etl.extractor import JSONExtractor

extractor = JSONExtractor(
    file_path="data/customers.json",
    json_path="data.customers"  # Optional: nested path
)
df = extractor.extract()
```

**Methods:**
- `extract() -> pd.DataFrame`: Extract data from JSON file
- Supports nested JSON paths using dot notation

#### APIExtractor

```python
from src.etl.extractor import APIExtractor

extractor = APIExtractor(
    base_url="https://api.example.com",
    endpoint="/v1/products",
    api_key="your_key",
    timeout=30,
    headers={"Custom-Header": "value"}
)
df = extractor.extract()
extractor.close()
```

**Methods:**
- `extract() -> pd.DataFrame`: Fetch data from REST API
- `close()`: Close session

**Features:**
- Automatic retry on network failures
- Support for custom headers
- Configurable timeout

#### MultiSourceExtractor

```python
from src.etl.extractor import MultiSourceExtractor, CSVExtractor, JSONExtractor

extractor = MultiSourceExtractor()
extractor.register_extractor("csv", CSVExtractor(...))
extractor.register_extractor("json", JSONExtractor(...))

results = extractor.extract_all()  # Dict[str, DataFrame]
```

### Data Transformer

```python
from src.etl.transformer import DataTransformer

transformer = DataTransformer()

# Transform sales
sales_df, metrics = transformer.transform_sales_data(df)

# Transform customers
customers_df, metrics = transformer.transform_customer_data(df)

# Transform products
products_df, metrics = transformer.transform_product_data(df)

# Generate quality report
report = transformer.generate_quality_report(
    metrics=[...],
    transformation_time=10.5
)
```

**Methods:**
- `transform_sales_data(df) -> Tuple[DataFrame, dict]`
- `transform_customer_data(df) -> Tuple[DataFrame, dict]`
- `transform_product_data(df) -> Tuple[DataFrame, dict]`
- `generate_quality_report(metrics, transformation_time) -> DataQualityReport`

### Data Loader

```python
from src.etl.loader import DataLoader
from src.database.connection import DatabaseManager

session = DatabaseManager.get_session()
loader = DataLoader(session)

# Load data
customers_count = loader.load_customers(df_customers)
products_count = loader.load_products(df_products)
sales_count = loader.load_sales(df_sales)

# Store quality report
loader.store_quality_report(quality_report)

# Delete old data
loader.delete_old_data(days=365)
```

**Methods:**
- `load_customers(df, incremental=False) -> int`
- `load_products(df, incremental=False) -> int`
- `load_sales(df) -> int`
- `store_quality_report(report) -> None`
- `delete_old_data(days=365) -> None`

### ETL Pipeline

```python
from src.etl.pipeline import ETLPipeline

pipeline = ETLPipeline()

# Setup database
pipeline.setup_database()

# Register sources
pipeline.register_data_sources(
    csv_path="data/sales.csv",
    json_path="data/customers.json",
    api_config={
        "base_url": "https://api.example.com",
        "endpoint": "/v1/products",
        "api_key": "key"
    }
)

# Run
success, report, error_msg = pipeline.run()

if success:
    print(f"Status: {report.status}")
    print(f"Records: {report.total_records_processed}")
```

**Methods:**
- `setup_database() -> bool`
- `register_data_sources(csv_path, json_path, api_config) -> None`
- `run() -> Tuple[bool, DataQualityReport, Optional[str]]`
- `get_last_run_time() -> Optional[datetime]`

### Database Connection

```python
from src.database.connection import DatabaseManager

# Initialize
engine = DatabaseManager.initialize()

# Get session
session = DatabaseManager.get_session()
try:
    # Use session
    pass
finally:
    session.close()

# Health check
is_healthy = DatabaseManager.health_check()

# Close all
DatabaseManager.close()
```

**Methods:**
- `initialize(config) -> Engine`
- `get_engine() -> Engine`
- `get_session() -> Session`
- `get_session_generator() -> Generator[Session, None, None]`
- `close() -> None`
- `health_check() -> bool`

### Report Generator

```python
from src.utils.report_generator import ReportGenerator
from pathlib import Path

generator = ReportGenerator(output_dir=Path("reports"))

# Generate Excel
excel_path = generator.generate_excel_report(filename="report.xlsx")

# Generate PDF
pdf_path = generator.generate_pdf_report(filename="report.pdf")

generator.close()
```

**Methods:**
- `generate_excel_report(filename=None) -> Path`
- `generate_pdf_report(filename=None) -> Path`

### Scheduler

```python
from src.scheduler.etl_scheduler import ETLScheduler

scheduler = ETLScheduler()

# Schedule daily at 2 AM
scheduler.schedule_daily(
    job_func=my_etl_function,
    hour=2,
    minute=0,
    job_id="daily_etl"
)

# Schedule every 4 hours
scheduler.schedule_interval(
    job_func=my_etl_function,
    hours=4,
    job_id="interval_etl"
)

# Schedule with cron
scheduler.schedule_cron(
    job_func=my_etl_function,
    cron_expression="0 2 * * *",  # 2 AM daily
    job_id="cron_etl"
)

# Start scheduler
scheduler.start()

# Check jobs
for job in scheduler.get_jobs():
    print(f"{job.id}: {job.name}")

# Stop scheduler
scheduler.stop()
```

**Methods:**
- `schedule_daily(func, hour, minute, job_id) -> None`
- `schedule_interval(func, hours, job_id) -> None`
- `schedule_cron(func, cron_expression, job_id) -> None`
- `start() -> None`
- `stop() -> None`
- `get_jobs() -> list`
- `remove_job(job_id) -> None`
- `pause_job(job_id) -> None`
- `resume_job(job_id) -> None`
- `is_running() -> bool`

## Data Models

### Pydantic Models

```python
from src.utils.models import Customer, Product, Sale, DataQualityReport

# Customer
customer = Customer(
    customer_id="CUST001",
    name="John Doe",
    email="john@example.com",
    phone="+55 11 98765-4321",
    state="SP"
)

# Product
product = Product(
    product_id="PROD001",
    name="Laptop",
    category="Electronics",
    price=1999.99,
    description="High-performance laptop"
)

# Sale
sale = Sale(
    sale_id="SALE001",
    customer_id="CUST001",
    product_id="PROD001",
    quantity=2,
    unit_price=1999.99,
    total_value=3999.98,
    sale_date=datetime.now(),
    year=2024,
    month=1,
    quarter=1
)

# Quality Report
report = DataQualityReport(
    total_records_processed=10000,
    invalid_records=50,
    missing_values_percentage=2.5,
    duplicates_removed=100,
    sources_processed={"csv": 5000, "json": 3000, "api": 2000},
    transformation_time_seconds=125.5,
    status="success"
)
```

### SQLAlchemy Models

```python
from src.database.models import Customer, Product, Sale, DataQualityMetric

# All models are instances of SQLAlchemy declarative models
# with automatic relationships and indexes
```

## Configuration

```python
from src.config import (
    DatabaseConfig,
    APIConfig,
    LoggingConfig,
    ETLConfig,
    SchedulerConfig,
    DashboardConfig,
    EmailConfig
)

# Access configuration
print(DatabaseConfig.HOST)
print(APIConfig.BASE_URL)
print(LoggingConfig.LEVEL)
```

## Exception Handling

```python
from src.utils.exceptions import (
    ETLException,
    ExtractionException,
    TransformationException,
    LoadException,
    ValidationException,
    DatabaseException,
    APIException,
    ConfigurationException
)

try:
    extractor.extract()
except ExtractionException as e:
    print(f"Extraction failed: {e}")
except ETLException as e:
    print(f"ETL error: {e}")
```

## Logging

```python
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## Best Practices

1. **Always close database sessions**
   ```python
   session = DatabaseManager.get_session()
   try:
       # Use session
   finally:
       session.close()
   ```

2. **Use context managers**
   ```python
   from src.database.connection import DatabaseManager
   session = next(DatabaseManager.get_session_generator())
   ```

3. **Handle exceptions appropriately**
   ```python
   try:
       pipeline.run()
   except ETLException as e:
       logger.error(f"ETL failed: {e}")
       # Implement recovery logic
   ```

4. **Validate input data**
   ```python
   from pydantic import ValidationError
   try:
       customer = Customer(**data)
   except ValidationError as e:
       logger.error(f"Validation failed: {e}")
   ```

5. **Use type hints**
   ```python
   def process_data(df: pd.DataFrame, batch_size: int) -> Tuple[int, dict]:
       # Implementation
       return count, metrics
   ```

---

For more information, see inline docstrings in the source code.
