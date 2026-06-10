# ETL Pipeline Documentation

## Overview

The ETL (Extract, Transform, Load) pipeline is the core data processing engine that:
- Extracts data from multiple sources (CSV, JSON, API)
- Transforms and validates data
- Loads data into PostgreSQL database
- Generates quality metrics and reports

## Pipeline Architecture

```
┌──────────────────┐
│  Data Sources    │
├──────────────────┤
│ • CSV (Sales)    │
│ • JSON (Custs)   │
│ • API (Products) │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  Extract Phase               │
├──────────────────────────────┤
│ • Source validation          │
│ • Data fetching              │
│ • Error handling             │
│ • Incremental load support   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Transform Phase             │
├──────────────────────────────┤
│ • Validation                 │
│ • Cleaning                   │
│ • Deduplication              │
│ • Type conversion            │
│ • Derived metrics            │
│ • Date standardization       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Load Phase                  │
├──────────────────────────────┤
│ • Database insert            │
│ • Transaction management     │
│ • Error recovery             │
│ • Quality report generation  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  PostgreSQL Database         │
├──────────────────────────────┤
│ • Customers (Dimension)      │
│ • Products (Dimension)       │
│ • Sales (Fact Table)         │
│ • Quality Reports            │
│ • Load Logs                  │
└──────────────────────────────┘
```

## Extraction

### CSV Extractor

**Purpose**: Extract sales data from CSV files

**Configuration**:
```env
CSV_SALES_FILE=sales_data.csv
```

**Expected Format**:
```
sale_id,customer_id,product_id,quantity,unit_price,sale_date
S001,C001,P001,2,50.00,2024-01-15
S002,C002,P002,1,120.00,2024-01-16
```

**Features**:
- Automatic CSV validation
- Pandas-based parsing
- Incremental load support
- Error handling with detailed messages

**Usage**:
```python
from src.etl.extractors import ExtractorFactory

extractor = ExtractorFactory.create_csv_extractor(Path("data/sales_data.csv"))
sales_data = extractor.extract()
```

### JSON Extractor

**Purpose**: Extract customer data from JSON files

**Configuration**:
```env
JSON_CUSTOMERS_FILE=customers.json
```

**Expected Format**:
```json
[
  {
    "customer_id": "C001",
    "name": "João Silva",
    "email": "joao@example.com",
    "state": "SP",
    "city": "São Paulo"
  }
]
```

**Features**:
- JSON schema validation
- Flexible structure support
- Error handling for malformed JSON

**Usage**:
```python
extractor = ExtractorFactory.create_json_extractor(Path("data/customers.json"))
customers_data = extractor.extract()
```

### API Extractor

**Purpose**: Extract product data from REST APIs

**Configuration**:
```env
PRODUCT_API_URL=https://api.example.com/products
API_TIMEOUT=30
API_RETRIES=3
```

**Features**:
- Connection pooling
- Automatic retry with exponential backoff
- Timeout handling
- SSL/TLS support
- Status code validation

**Usage**:
```python
extractor = ExtractorFactory.create_api_extractor(
    "https://api.example.com/products",
    timeout=30,
    retries=3
)
products_data = extractor.extract()
extractor.close()
```

## Transformation

### Sales Transformation

**Input Validation**:
- Required fields: sale_id, customer_id, product_id, quantity, unit_price, sale_date
- Quantity must be positive integer
- Unit price must be positive number

**Transformations**:
1. **Date Standardization**: Convert to ISO format (YYYY-MM-DD)
2. **Derived Metrics**:
   - total_value = quantity × unit_price
   - year, month, quarter extraction
3. **Type Conversion**: Ensure correct data types
4. **Deduplication**: Check for duplicate sale_ids

**Output Example**:
```python
{
    "sale_id": "S001",
    "customer_id": "C001",
    "product_id": "P001",
    "quantity": 2,
    "unit_price": 50.00,
    "total_value": 100.00,
    "sale_date": "2024-01-15",
    "year": 2024,
    "month": 1,
    "quarter": 1
}
```

### Customer Transformation

**Input Validation**:
- Required fields: customer_id, name, state
- Email format validation (if provided)

**Transformations**:
1. **Name Cleaning**: Title case, trim whitespace
2. **State Standardization**: Uppercase, validate
3. **Email Normalization**: Lowercase

**Output Example**:
```python
{
    "customer_id": "C001",
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "(11) 98765-4321",
    "state": "SP",
    "city": "São Paulo"
}
```

### Product Transformation

**Input Validation**:
- Required fields: id, name, price
- Price must be positive

**Transformations**:
1. **Name Cleaning**: Trim whitespace
2. **Category Standardization**: Provide default if missing
3. **Price Conversion**: Ensure numeric type

**Output Example**:
```python
{
    "product_id": "P001",
    "name": "Laptop",
    "category": "Electronics",
    "price": 3000.00,
    "description": "High-performance laptop",
    "active": True
}
```

## Data Quality Metrics

### Tracked Metrics

| Metric | Description |
|--------|-------------|
| total_records_processed | Total records attempted |
| invalid_records | Records failing validation |
| duplicate_records_removed | Duplicate records detected |
| missing_values_percentage | % of missing/null values |
| sales_records | Successfully loaded sales |
| customer_records | Successfully loaded customers |
| product_records | Successfully loaded products |

### Quality Report Example

```python
{
    "total_records_processed": 1050,
    "invalid_records": 15,
    "duplicate_records_removed": 5,
    "missing_values_percentage": 2.3,
    "sales_records": 600,
    "customer_records": 300,
    "product_records": 150,
    "status": "SUCCESS",
    "execution_time_seconds": 45.2
}
```

## Loading

### Load Strategy

1. **Dimension Tables First**: Load customers and products
2. **Fact Table**: Load sales with referential integrity
3. **Quality Report**: Record metrics and execution details

### Error Handling

- **Duplicate Customers/Products**: Update existing records
- **Foreign Key Violation**: Log error and skip record
- **Transaction Rollback**: On critical errors

### Batch Processing

```env
BATCH_SIZE=1000
```

Records are processed in batches for memory efficiency.

## Incremental Loading

### How It Works

1. **Track Last Load**: Store last_loaded_id and timestamp
2. **Filter New Records**: Extract only records since last load
3. **Update Log**: Record load completion

### Configuration

```env
INCREMENTAL_LOAD=True
```

### Implementation

```python
# Check incremental load log
log = repo.get_by_source("sales")
if log:
    data = extractor.extract_incremental(log.last_loaded_id)
else:
    data = extractor.extract()
```

## Running the Pipeline

### Command Line

```bash
# Run once
python -m src.etl.pipeline

# Run with debug logging
ENVIRONMENT=development LOG_LEVEL=DEBUG python -m src.etl.pipeline

# Run with different environment
ENVIRONMENT=production python -m src.etl.pipeline
```

### Python API

```python
from src.etl.pipeline import run_etl_pipeline

result = run_etl_pipeline(use_incremental=True)

if result["success"]:
    print(f"Loaded {result['load_results']['sales_loaded']} sales")
    print(f"Execution time: {result['execution_time_seconds']:.2f}s")
else:
    print(f"Error: {result['error']}")
```

### Docker

```bash
# Single run
docker-compose run etl-service

# Scheduled runs (via scheduler)
docker-compose up etl-service
```

## Logging

### Log Files

- `logs/etl.log`: ETL execution details
- `logs/errors.log`: Error tracking
- Console output with INFO level

### Log Configuration

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Example Logs

```
2024-01-15 10:30:45 - src.etl.pipeline - INFO - Starting ETL Pipeline Execution
2024-01-15 10:30:45 - src.etl.extractors - INFO - Extracted 100 records from CSV
2024-01-15 10:30:46 - src.etl.transformers - INFO - Transformed 100 sales records
2024-01-15 10:30:47 - src.etl.loaders - INFO - Loaded 100 sales records
2024-01-15 10:30:47 - src.etl.pipeline - INFO - ETL Pipeline Completed Successfully!
```

## Performance

### Execution Time Breakdown

| Operation | Time |
|-----------|------|
| Extract (CSV + JSON + API) | ~5s |
| Transform (validation + cleaning) | ~10s |
| Load (database inserts) | ~20s |
| Quality Report | ~2s |
| **Total** | **~37s** |

### Optimization Tips

1. **Increase Batch Size**: Faster database inserts
2. **Enable Caching**: Avoid repeated API calls
3. **Use Incremental Load**: Process only new data
4. **Optimize Queries**: Use prepared statements
5. **Database Indexes**: Ensure proper indexing

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
```
Error: could not connect to server
```
Solution:
- Verify DATABASE_URL
- Check PostgreSQL is running
- Verify credentials

**2. File Not Found**
```
Error: CSV file not found
```
Solution:
- Verify file path in .env
- Check file exists in data/ directory
- Use absolute paths if needed

**3. Data Validation Errors**
```
WARNING: Invalid sales record: Quantity must be positive
```
Solution:
- Check source data for inconsistencies
- Review validation rules
- Update data quality rules if needed

**4. Memory Error with Large Files**
```
MemoryError: Unable to allocate memory
```
Solution:
- Reduce BATCH_SIZE
- Use incremental load
- Process in chunks

## Advanced Features

### Custom Transformers

```python
from src.etl.transformers import BaseTransformer

class CustomTransformer(BaseTransformer):
    def transform(self, data):
        # Your custom logic here
        return transformed_data, metrics
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(extract_sales),
        executor.submit(extract_customers),
        executor.submit(extract_products)
    ]
```

### Data Quality Rules

Customize validation thresholds in `config.py`:

```python
MISSING_VALUE_THRESHOLD = 0.1  # 10%
DUPLICATE_THRESHOLD = 0.05     # 5%
```

## Best Practices

1. **Always backup data before ETL**
2. **Test with sample data first**
3. **Monitor execution times**
4. **Review quality reports regularly**
5. **Keep audit logs of all changes**
6. **Use version control for scripts**
7. **Document any customizations**
8. **Set up alerts for failures**
