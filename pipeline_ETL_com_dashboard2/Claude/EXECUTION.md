# Execution Instructions

## Table of Contents
1. [Local Setup](#local-setup)
2. [Docker Setup](#docker-setup)
3. [Configuration](#configuration)
4. [Running ETL](#running-etl)
5. [Running Dashboard](#running-dashboard)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Local Setup

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### 2. Clone Repository
```bash
git clone <repository-url>
cd etl_dashboard
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 6. Initialize Database
```bash
python main.py init
```

### 7. Prepare Data Files
Place your data files in the `data/` directory:
- `sales.csv` - Sales transactions
- `customers.json` - Customer data
- `products.json` or API endpoint for products

## Docker Setup

### 1. Prerequisites
- Docker
- Docker Compose

### 2. Build and Start Services
```bash
docker-compose up -d
```

### 3. Verify Services
```bash
docker-compose ps
```

### 4. View Logs
```bash
docker-compose logs -f dashboard
docker-compose logs -f postgres
```

### 5. Stop Services
```bash
docker-compose down
```

## Configuration

### Database Connection

Update `.env`:
```env
DB_HOST=your-postgres-host
DB_PORT=5432
DB_NAME=sales_db
DB_USER=etl_user
DB_PASSWORD=your-secure-password
```

Test connection:
```bash
python -c "from src.database.connection import DatabaseManager; print('OK' if DatabaseManager.health_check() else 'FAILED')"
```

### API Configuration

For REST API data source:
```env
API_BASE_URL=https://api.example.com
API_KEY=your_api_key
API_TIMEOUT=30
```

### Logging Configuration

Customize logging:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/etl.log
```

### Scheduler Configuration

For automated ETL:
```env
SCHEDULE_INTERVAL=daily
SCHEDULE_TIME=02:00
```

## Running ETL

### Basic Execution

```bash
python main.py etl \
  --csv data/sample_sales.csv \
  --json data/sample_customers.json \
  --api-url https://api.example.com \
  --api-endpoint /v1/products \
  --api-key your_api_key
```

### With Docker

```bash
docker-compose exec dashboard python main.py etl \
  --csv data/sample_sales.csv \
  --json data/sample_customers.json \
  --api-url https://api.example.com \
  --api-endpoint /v1/products
```

### Expected Output

```
================================================================================
Starting ETL Pipeline Execution
================================================================================

[STEP 1] EXTRACTION PHASE
----
Initialized multi-source extractor
Registered extractor: csv_sales
Registered extractor: json_customers
Registered extractor: api_products
Extracting from source: csv_sales
Successfully extracted 100 rows from CSV...

[STEP 2] TRANSFORMATION PHASE
----
Transforming sales data: 100 rows
Sales transformation complete: {...}
Transforming customer data: 50 rows
Customer transformation complete: {...}
Transforming product data: 10 rows
Product transformation complete: {...}

[STEP 3] LOADING PHASE
----
Successfully loaded 50 customer records
Successfully loaded 10 product records
Successfully loaded 95 sales records

[STEP 4] DATA QUALITY REPORTING
----
Quality report generated: {...}

[STEP 5] FINALIZING
----
Last run time saved to data/last_run.txt

================================================================================
ETL Pipeline Execution Summary
================================================================================
Total Execution Time: 45.23 seconds
Customers Loaded: 50
Products Loaded: 10
Sales Loaded: 95
Quality Report Status: success
================================================================================
```

## Running Dashboard

### Local

```bash
python main.py dashboard
# Or directly:
streamlit run src/dashboard/app.py
```

Access at: `http://localhost:8501`

### Docker

```bash
docker-compose up dashboard
```

Access at: `http://localhost:8501`

### Dashboard Features

1. **KPIs**
   - Total Revenue
   - Number of Sales
   - Average Ticket Size
   - Unique Customers

2. **Filters**
   - Date Range
   - State
   - Product Category
   - Product

3. **Visualizations**
   - Revenue by Month (Line Chart)
   - Revenue by Category (Bar Chart)
   - Top 10 Products (Horizontal Bar)
   - Sales by State (Top 10)
   - Sales Trends Over Time (Dual Axis)
   - Quarterly Distribution (Pie Chart)

4. **Data Quality Report**
   - Total Records Processed
   - Invalid Records
   - Missing Values %
   - Duplicates Removed
   - Transformation Time

## Monitoring

### View Logs

```bash
# Local
tail -f logs/etl.log

# Docker
docker-compose logs -f dashboard
docker-compose logs -f postgres
```

### Check Database Health

```bash
# Local
python -c "from src.database.connection import DatabaseManager; print(DatabaseManager.health_check())"

# Docker
docker-compose exec postgres pg_isready
```

### Generate Reports

```python
from src.utils.report_generator import ReportGenerator

gen = ReportGenerator()
excel_path = gen.generate_excel_report()
pdf_path = gen.generate_pdf_report()
print(f"Excel: {excel_path}")
print(f"PDF: {pdf_path}")
```

### Database Queries

```bash
# Connect to database
psql -h localhost -U etl_user -d sales_db

# View sales count
SELECT COUNT(*) FROM sales;

# View monthly revenue
SELECT year, month, SUM(total_value) as revenue FROM sales GROUP BY year, month;

# View by category
SELECT category, SUM(total_value) as revenue FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY category;
```

## Automated Scheduling

### Using APScheduler

```python
from src.scheduler.etl_scheduler import ETLScheduler
from src.etl.pipeline import ETLPipeline

scheduler = ETLScheduler()

# Schedule daily at 2 AM
def run_etl():
    pipeline = ETLPipeline()
    pipeline.setup_database()
    pipeline.register_data_sources(...)
    pipeline.run()

scheduler.schedule_daily(run_etl, hour=2, minute=0)
scheduler.start()

# Check running jobs
for job in scheduler.get_jobs():
    print(f"{job.id}: {job.name}")
```

### Using Cron

```bash
# Edit crontab
crontab -e

# Add entry for 2 AM daily
0 2 * * * cd /path/to/etl_dashboard && python main.py etl --csv data/sales.csv --json data/customers.json --api-url https://api.example.com --api-endpoint /v1/products
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run src/dashboard/app.py --server.port 8502
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
# Linux/Mac:
brew services list

# Docker:
docker-compose ps postgres

# Test connection
psql -h localhost -U etl_user -d sales_db
```

### Import Errors

```bash
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in development mode
pip install -e .
```

### No Data in Dashboard

```bash
# Check if ETL has run
python -c "from src.database.connection import DatabaseManager; from src.database.models import Sale; s = DatabaseManager.get_session(); print(f'Sales count: {s.query(Sale).count()}')"

# Run ETL if empty
python main.py etl --csv data/sample_sales.csv --json data/sample_customers.json --api-url https://api.example.com --api-endpoint /v1/products

# Clear dashboard cache
rm -rf ~/.streamlit/cache
```

### Performance Issues

```bash
# Check slow queries (PostgreSQL)
postgres -c log_min_duration_statement=1000

# Monitor system resources
top
free -h
df -h

# Optimize database
python -c "from src.database.initialization import get_table_statistics; from src.database.connection import DatabaseManager; s = DatabaseManager.get_session(); print(get_table_statistics(s))"
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_etl.py::test_extract_valid_csv -v
```

### With Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

## Backup and Restore

### Backup Database

```bash
# Local
pg_dump sales_db > backup_$(date +%Y%m%d).sql

# Docker
docker-compose exec postgres pg_dump -U etl_user sales_db > backup.sql
```

### Restore Database

```bash
# Local
psql sales_db < backup.sql

# Docker
docker-compose exec -T postgres psql -U etl_user sales_db < backup.sql
```

## Performance Tuning

### Increase Batch Size

```env
BATCH_SIZE=5000
```

### Enable Incremental Mode

```env
INCREMENTAL_MODE=true
```

### Database Connection Pooling

Edit `src/database/connection.py`:
```python
pool_size=30  # Increase from 10
max_overflow=50  # Increase from 20
```

---

For detailed documentation, see:
- [README.md](docs/README.md)
- [Quick Start](docs/QUICKSTART.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)
