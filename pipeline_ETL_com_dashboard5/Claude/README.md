# Sales ETL & Dashboard Solution - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Features](#features)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [ETL Pipeline](#etl-pipeline)
9. [Dashboard](#dashboard)
10. [Database](#database)
11. [Testing](#testing)
12. [Docker Deployment](#docker-deployment)
13. [Advanced Features](#advanced-features)
14. [Troubleshooting](#troubleshooting)
15. [API Reference](#api-reference)

---

## Project Overview

A comprehensive, production-ready ETL (Extract, Transform, Load) and Analytics Dashboard solution for sales data analysis built with Python, PostgreSQL, and Streamlit.

### Key Features
- **Multi-source data extraction**: CSV, JSON, REST API
- **Advanced data transformation**: Validation, deduplication, date standardization
- **Interactive Streamlit dashboard**: Real-time KPIs and visualizations
- **PostgreSQL database**: Optimized schema with materialized views
- **Data quality reporting**: Comprehensive metrics and validation
- **Docker support**: Easy containerization and deployment
- **Airflow scheduling**: Automated ETL pipeline execution
- **Report generation**: PDF and Excel exports
- **Unit testing**: Comprehensive test coverage
- **Clean code architecture**: Type hints, logging, error handling

---

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Sources                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │   CSV    │  │   JSON   │  │   API    │                       │
│  │  (Sales) │  │(Customers)│  │(Products)│                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                    ETL Pipeline                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Extractor   │→ │  Transformer │→ │    Loader    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                  PostgreSQL Database                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Tables: customers, products, sales, quality_reports      │  │
│  │ Views: sales_summary, monthly_revenue, product_perf...   │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────────┐  ┌─────▼──────┐  ┌───────▼─────┐
│ Streamlit  │  │   Report   │  │   Export    │
│ Dashboard  │  │ Generation │  │  (Excel/PDF)│
└────────────┘  └────────────┘  └─────────────┘
```

### Component Responsibilities

**Extractor Module**
- Reads from CSV, JSON, and REST API
- Implements retry logic and error handling
- Returns structured data

**Transformer Module**
- Validates data types and formats
- Removes duplicates and handles missing values
- Creates derived metrics (year, month, quarter)
- Generates data quality reports

**Loader Module**
- Connects to PostgreSQL
- Implements UPSERT operations
- Maintains referential integrity

**Dashboard**
- Real-time data visualization
- Interactive filtering
- KPI calculation and display

---

## Project Structure

```
sales_etl_dashboard/
├── src/
│   ├── etl/
│   │   ├── extractor.py       # Data extraction from multiple sources
│   │   ├── transformer.py     # Data transformation & validation
│   │   ├── pipeline.py        # Main ETL orchestration
│   │   └── __init__.py
│   ├── database/
│   │   ├── connection.py      # PostgreSQL connection management
│   │   ├── loader.py          # Data loading operations
│   │   └── __init__.py
│   ├── dashboard/
│   │   ├── app.py             # Streamlit dashboard application
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py         # Data models and schemas
│   │   └── __init__.py
│   └── utils/
│       ├── config.py          # Configuration management
│       ├── logger.py          # Logging setup
│       ├── validators.py      # Data validation utilities
│       ├── sample_data.py     # Sample data generation
│       ├── report_export.py   # Report & export generation
│       └── __init__.py
├── tests/
│   ├── test_etl.py            # Unit tests
│   └── __init__.py
├── sql/
│   └── schema.sql             # PostgreSQL schema
├── data/
│   ├── input/                 # Input data files
│   ├── output/                # Output data files
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── dags/
│   └── etl_pipeline_dag.py    # Airflow DAG
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Docker Compose configuration
├── .dockerignore              # Docker ignore patterns
├── .gitignore                 # Git ignore patterns
├── README.md                  # This file
└── CONTRIBUTING.md            # Contribution guidelines
```

---

## Features

### 1. Data Extraction
- **CSV Files**: Sales data with automatic parsing
- **JSON Files**: Customer data with flexible structure
- **REST API**: Product data with pagination and retry logic
- **Error Handling**: Graceful failure with detailed logging

### 2. Data Transformation
- **Validation**: Email, phone, numeric, date formats
- **Deduplication**: Automatic duplicate detection and removal
- **Missing Values**: Identification and handling
- **Date Standardization**: Conversion to ISO format
- **Derived Metrics**: Year, month, quarter calculation

### 3. Data Loading
- **Bulk Operations**: Efficient batch inserts
- **UPSERT Logic**: Insert or update existing records
- **Referential Integrity**: Foreign key constraints
- **Transaction Support**: Rollback on errors

### 4. Interactive Dashboard
- **KPI Cards**: Total revenue, sales count, avg ticket size, unique customers
- **Visualizations**:
  - Revenue trends over time (line chart)
  - Revenue by category (pie chart)
  - Top 10 products (bar chart)
  - Sales by state (bar chart)
- **Filtering**: Date range, state, category, product
- **Data Export**: Download filtered data

### 5. Data Quality Reporting
- **Metrics Tracked**:
  - Total records processed
  - Valid vs. invalid records
  - Duplicates removed
  - Missing value statistics
  - Data type errors
  - Date conversion errors
- **Report Formats**: HTML, JSON

### 6. Advanced Features
- **Incremental Processing**: Track last run timestamp
- **Materialized Views**: Performance optimization
- **Automated Scheduling**: Airflow DAG included
- **Report Generation**: PDF and Excel exports
- **Docker Support**: Containerized deployment

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (optional)
- Git

### Local Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd sales_etl_dashboard
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Create database**
```bash
createdb -U postgres sales_etl_db
```

6. **Initialize database schema**
```bash
psql -U postgres -d sales_etl_db -f sql/schema.sql
```

7. **Generate sample data**
```bash
python main.py setup
```

8. **Run ETL pipeline**
```bash
python main.py run
```

9. **Start dashboard**
```bash
streamlit run src/dashboard/app.py
```

### Docker Installation

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Access services**
- Dashboard: http://localhost:8501
- pgAdmin: http://localhost:5050 (optional)

3. **Run ETL pipeline**
```bash
docker-compose run etl
```

---

## Configuration

### Environment Variables (.env)

```ini
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_etl_db
DB_USER=etl_user
DB_PASSWORD=secure_password

# API Configuration
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# Data Paths
CSV_SALES_PATH=data/input/sales.csv
JSON_CUSTOMERS_PATH=data/input/customers.json

# Processing
BATCH_SIZE=1000
INCREMENTAL_MODE=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/etl.log
```

### Configuration Management

Edit `src/utils/config.py` to:
- Add new configuration options
- Set default values
- Validate configuration
- Create database URL

---

## Usage

### Command Line Interface

```bash
# Generate sample data
python main.py setup

# Run ETL pipeline
python main.py run

# Generate reports
python main.py reports

# Run everything
python main.py all
```

### Python API

```python
from src.etl.pipeline import ETLPipeline

pipeline = ETLPipeline()
result = pipeline.run()

print(f"Status: {result['status']}")
print(f"Records loaded: {result['loading']}")
```

### Dashboard Access

1. **Local**
```bash
streamlit run src/dashboard/app.py
```

2. **Docker**
```bash
docker-compose up -d
# Access at http://localhost:8501
```

---

## ETL Pipeline

### Pipeline Stages

#### 1. Extraction
```python
from src.etl.extractor import DataExtractor

extractor = DataExtractor()
data = extractor.extract_all()
# Returns: {'sales': [...], 'customers': [...], 'products': [...]}
```

#### 2. Transformation
```python
from src.etl.transformer import DataTransformer

transformer = DataTransformer()
customers, errors = transformer.transform_customers(raw_data)
```

#### 3. Loading
```python
from src.database.loader import DataLoader

loader = DataLoader()
loaded_count = loader.load_customers(customers)
```

### Data Quality Checks

- **Type Validation**: Ensures correct data types
- **Format Validation**: Email, phone, date formats
- **Range Validation**: Numeric bounds
- **Duplicate Detection**: Identifies duplicate records
- **Referential Integrity**: Foreign key validation

### Error Handling

All modules include comprehensive error handling:
- Specific exception types
- Detailed error logging
- Graceful degradation
- Error recovery mechanisms

---

## Dashboard

### Features

1. **KPI Cards**
   - Total Revenue
   - Number of Sales
   - Average Ticket Size
   - Unique Customers

2. **Visualizations**
   - Revenue trend (line chart)
   - Revenue by category (pie chart)
   - Top 10 products (bar chart)
   - Sales by state (map chart)

3. **Filters**
   - Date range selector
   - State multi-select
   - Category multi-select
   - Product search

4. **Data Table**
   - Detailed sales records
   - Sortable columns
   - Export capability

### Customization

Edit `src/dashboard/app.py` to:
- Add new visualizations
- Modify KPIs
- Change color schemes
- Add new filters

---

## Database

### Schema Design

#### Tables
- **customers**: Customer information with contact details
- **products**: Product catalog with pricing
- **sales**: Transaction records with metrics
- **data_quality_reports**: ETL execution reports

#### Indexes
- Primary keys on IDs
- Indexes on foreign keys
- Indexes on frequently filtered columns
- Composite indexes for common queries

#### Materialized Views
- `sales_summary`: Denormalized sales data
- `monthly_revenue`: Aggregated monthly metrics
- `product_performance`: Product statistics
- `state_sales_distribution`: State-level metrics
- `category_performance`: Category statistics

### Query Examples

```sql
-- Total revenue by month
SELECT month, SUM(total_value) FROM monthly_revenue GROUP BY month;

-- Top products
SELECT name, total_revenue FROM product_performance LIMIT 10;

-- Sales by state
SELECT state, COUNT(*), SUM(total_value) FROM sales GROUP BY state;
```

### View Refresh

```sql
-- Refresh materialized views
SELECT refresh_materialized_views();
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_etl.py::TestValidators::test_validate_email
```

### Test Coverage

- Validators: Email, phone, numeric, date formats
- Models: Customer, Product, Sale, Report
- Transformer: Data transformation logic
- Extractor: Data extraction from sources

### Adding Tests

Create test files in `tests/` directory:
```python
def test_my_feature():
    assert True
```

---

## Docker Deployment

### Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build dashboard
```

### Run Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop services
docker-compose down
```

### Volume Mounting

```yaml
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
```

### Environment Variables in Docker

Set in `.env` or `docker-compose.yml`:
```yaml
environment:
  DB_HOST: postgres
  DB_PORT: 5432
  DB_NAME: sales_etl_db
```

---

## Advanced Features

### 1. Incremental Processing

Track last run and only process new data:
```python
# Configured in .env
INCREMENTAL_MODE=true
LAST_RUN_TIMESTAMP_FILE=data/.last_run
```

### 2. Airflow Scheduling

DAG configuration in `dags/etl_pipeline_dag.py`:
```python
schedule_interval='0 2 * * *'  # Daily at 2 AM
```

Set up Airflow:
```bash
export AIRFLOW_HOME=./airflow
airflow db init
airflow dags list
airflow scheduler
```

### 3. Report Generation

Generate reports after ETL:
```python
from src.utils.report_export import ReportGenerator

gen = ReportGenerator()
gen.save_quality_report(report_data)
```

### 4. Excel Exports

Export data to Excel:
```python
from src.utils.report_export import ExcelExporter

exporter = ExcelExporter()
exporter.export_sales_data()
exporter.export_summary_statistics()
```

### 5. PDF Reports

Generate PDF reports:
```python
from src.utils.report_export import PDFReportGenerator

gen = PDFReportGenerator()
gen.generate_sales_report()
```

---

## Troubleshooting

### Common Issues

**Issue**: Database connection refused
```
Solution: Ensure PostgreSQL is running
- Linux/Mac: brew services start postgresql
- Windows: Start PostgreSQL service
- Docker: Check postgres container status
```

**Issue**: Dashboard not loading
```
Solution: Check database configuration
- Verify .env file
- Test connection: psql -U etl_user -d sales_etl_db
- Check logs: cat logs/etl.log
```

**Issue**: ETL pipeline fails
```
Solution: Check data files and logs
- Verify CSV/JSON file paths
- Check file permissions
- Review logs for specific errors
- Validate data format
```

**Issue**: Docker build fails
```
Solution: Rebuild without cache
- docker-compose build --no-cache
- docker system prune
- Check internet connection
```

### Debugging

Enable verbose logging:
```ini
LOG_LEVEL=DEBUG
```

Check logs:
```bash
tail -f logs/etl.log
```

Run with debug mode:
```python
Config.DEBUG = True
```

---

## API Reference

### ETLPipeline Class

```python
class ETLPipeline:
    def __init__()
    def initialize_database() -> None
    def run() -> Dict[str, Any]
```

### DataExtractor Class

```python
class DataExtractor:
    def extract_sales() -> List[Dict]
    def extract_customers() -> List[Dict]
    def extract_products() -> List[Dict]
    def extract_all() -> Dict[str, List]
```

### DataTransformer Class

```python
class DataTransformer:
    def transform_customers() -> Tuple[List, List]
    def transform_products() -> Tuple[List, List]
    def transform_sales() -> Tuple[List, List]
    def remove_duplicates() -> Tuple[List, int]
```

### DataLoader Class

```python
class DataLoader:
    def load_customers() -> int
    def load_products() -> int
    def load_sales() -> int
    def load_quality_report() -> int
```

### DatabaseConnection Class

```python
class DatabaseConnection:
    def connect() -> None
    def disconnect() -> None
    def execute_query() -> List[Dict]
    def execute_update() -> int
    def execute_batch() -> int
```

---

## Best Practices

### Code Quality
- Type hints on all functions
- Comprehensive error handling
- Detailed logging
- DRY principle
- SOLID principles

### Data Quality
- Validate all inputs
- Handle missing values
- Remove duplicates
- Generate quality reports
- Monitor data metrics

### Performance
- Use batch operations
- Index frequently queried columns
- Implement materialized views
- Use connection pooling
- Monitor query performance

### Security
- Use environment variables for secrets
- Parameterized SQL queries
- Input validation
- Secure database connections
- Access control

### Maintenance
- Keep dependencies updated
- Regular backups
- Monitor logs
- Performance tuning
- Documentation updates

---

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
