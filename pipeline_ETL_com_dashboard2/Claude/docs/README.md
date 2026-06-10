# ETL and Dashboard Solution for Sales Analysis

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Architecture](#architecture)
8. [API Documentation](#api-documentation)
9. [Database Schema](#database-schema)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)

## Overview

This is a comprehensive ETL (Extract, Transform, Load) and Dashboard solution for sales data analysis. The system extracts data from multiple sources (CSV, JSON, REST API), performs data quality checks, transformation, and loads it into a PostgreSQL database. It then provides an interactive Streamlit dashboard for real-time sales analytics.

### Key Features

- **Multi-source ETL**: Extract from CSV, JSON, and REST APIs
- **Data Quality Reporting**: Automatic quality metrics and validation
- **Interactive Dashboard**: Real-time analytics with Streamlit
- **Scheduled Execution**: Automated ETL runs with APScheduler
- **Report Generation**: PDF and Excel exports
- **Docker Support**: Complete containerization with Docker Compose
- **Type Hints & Clean Code**: Full type annotations and modern Python patterns
- **Comprehensive Testing**: Unit tests with pytest
- **Production Ready**: Logging, error handling, and monitoring

## Project Structure

```
etl_dashboard/
├── src/
│   ├── config.py                 # Configuration management
│   ├── database/
│   │   ├── connection.py         # Database connection handling
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── initialization.py     # Database setup and migrations
│   ├── etl/
│   │   ├── extractor.py          # Data extraction from sources
│   │   ├── transformer.py        # Data transformation logic
│   │   ├── loader.py             # Data loading to database
│   │   └── pipeline.py           # Main ETL orchestration
│   ├── dashboard/
│   │   └── app.py               # Streamlit dashboard
│   ├── scheduler/
│   │   └── etl_scheduler.py     # Automated scheduling
│   └── utils/
│       ├── logging_config.py     # Logging configuration
│       ├── exceptions.py         # Custom exceptions
│       ├── models.py             # Pydantic data models
│       └── report_generator.py   # Report generation
├── tests/
│   └── test_etl.py              # Unit tests
├── sql/
│   └── init.sql                 # Database initialization
├── data/
│   ├── sample_sales.csv         # Sample data
│   ├── sample_customers.json    # Sample data
│   └── sample_products.json     # Sample data
├── logs/                        # Application logs
├── reports/                     # Generated reports
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
├── Dockerfile                   # Docker image configuration
├── docker-compose.yml           # Docker Compose orchestration
└── docs/                        # Additional documentation
```

## Prerequisites

### System Requirements

- Python 3.9+
- PostgreSQL 12+ (or Docker)
- Docker & Docker Compose (for containerized deployment)
- 4GB RAM minimum
- 20GB disk space

### Python Dependencies

All dependencies are listed in `requirements.txt` and include:

- pandas: Data manipulation
- numpy: Numerical operations
- sqlalchemy: ORM and database toolkit
- psycopg2: PostgreSQL adapter
- requests: HTTP library
- streamlit: Dashboard framework
- plotly: Interactive visualizations
- pydantic: Data validation
- apscheduler: Task scheduling
- reportlab: PDF generation
- openpyxl: Excel generation

## Installation

### Option 1: Local Installation

1. **Clone the repository**

```bash
cd etl_dashboard
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

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**

```bash
python main.py init
```

### Option 2: Docker Installation

1. **Build and start containers**

```bash
docker-compose up -d
```

2. **Verify services**

```bash
docker-compose ps
docker-compose logs postgres
docker-compose logs dashboard
```

## Configuration

### Environment Variables (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
DB_USER=etl_user
DB_PASSWORD=secure_password_here

# API Configuration
API_BASE_URL=https://api.example.com
API_KEY=your_api_key_here
API_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/etl.log

# ETL
BATCH_SIZE=1000
INCREMENTAL_MODE=true
LAST_RUN_FILE=data/last_run.txt

# Scheduler
SCHEDULE_INTERVAL=daily
SCHEDULE_TIME=02:00

# Dashboard
DASHBOARD_PORT=8501
DEBUG_MODE=false

# Email (for reports)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
REPORT_RECIPIENTS=admin@example.com
```

## Usage

### Running ETL Pipeline

```bash
# From CSV, JSON, and API
python main.py etl \
  --csv data/sample_sales.csv \
  --json data/sample_customers.json \
  --api-url https://api.example.com \
  --api-endpoint /v1/products \
  --api-key your_api_key
```

### Running Dashboard

```bash
# Local
python main.py dashboard

# Docker
docker-compose up dashboard

# Streamlit directly
streamlit run src/dashboard/app.py
```

### Running Tests

```bash
pytest tests/ -v --cov=src
```

### Database Initialization

```bash
python main.py init
```

## Architecture

### ETL Pipeline Phases

```
┌─────────────┐
│ EXTRACTION  │  ← CSV, JSON, REST API
└──────┬──────┘
       ↓
┌─────────────────────────────────────┐
│ TRANSFORMATION                      │
│ • Remove duplicates                 │
│ • Handle missing values             │
│ • Validate data types               │
│ • Create derived metrics            │
└──────┬──────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ QUALITY VALIDATION                   │
│ • Record counts                      │
│ • Missing values %                   │
│ • Duplicate detection                │
│ • Type validation                    │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ LOADING                              │
│ → PostgreSQL Database                │
└──────┬───────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ REPORTING                            │
│ • Data Quality Report                │
│ • Metrics Storage                    │
│ • Alert Generation (Optional)        │
└──────────────────────────────────────┘
```

### Database Schema

```
Customers
├─ customer_id (PK)
├─ name
├─ email (UNIQUE)
├─ phone
├─ state
└─ timestamps

Products
├─ product_id (PK)
├─ name
├─ category
├─ price
├─ description
└─ timestamps

Sales
├─ sale_id (PK)
├─ customer_id (FK)
├─ product_id (FK)
├─ quantity
├─ unit_price
├─ total_value
├─ sale_date
├─ year, month, quarter
└─ timestamps

DataQualityMetrics
├─ id (PK)
├─ extraction_timestamp
├─ total_records_processed
├─ invalid_records
├─ missing_values_percentage
├─ duplicates_removed
├─ transformation_time_seconds
├─ status
└─ timestamps
```

## Dashboard Features

### KPIs Displayed

- **Total Revenue**: Sum of all sale values
- **Number of Sales**: Total transaction count
- **Average Ticket**: Mean sale value
- **Unique Customers**: Count of distinct customers

### Visualizations

1. **Revenue by Month**: Line chart showing trends
2. **Revenue by Category**: Bar chart comparison
3. **Top 10 Products**: Horizontal bar chart
4. **Sales by State**: Top states by revenue
5. **Sales Trends**: Combined line and bar chart
6. **Quarterly Distribution**: Pie chart

### Filters

- Date Range (from/to dates)
- State (dropdown)
- Product Category (dropdown)
- Product (dynamic)

## Advanced Features

### Automated Scheduling

```python
from src.scheduler.etl_scheduler import ETLScheduler
from src.etl.pipeline import ETLPipeline

scheduler = ETLScheduler()
pipeline = ETLPipeline()

# Schedule daily at 2 AM
scheduler.schedule_daily(
    job_func=lambda: pipeline.run(),
    hour=2,
    minute=0,
    job_id="daily_etl"
)

scheduler.start()
```

### Report Generation

```python
from src.utils.report_generator import ReportGenerator

generator = ReportGenerator()

# Generate Excel report
excel_path = generator.generate_excel_report()

# Generate PDF report
pdf_path = generator.generate_pdf_report()
```

### Incremental Processing

Enable incremental mode in `.env`:

```env
INCREMENTAL_MODE=true
```

This will:
- Track last successful run
- Process only new/updated records
- Maintain data consistency
- Improve performance for large datasets

### Docker Deployment

```bash
# Build custom image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f dashboard
docker-compose logs -f postgres

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from src.database.connection import DatabaseManager; print(DatabaseManager.health_check())"

# View connection string
python -c "from src.config import DatabaseConfig; print(DatabaseConfig.connection_string)"
```

### Import Errors

```bash
# Ensure package structure
python -m pip install -e .

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Dashboard Not Displaying

```bash
# Check Streamlit cache
rm -rf ~/.streamlit/cache

# Run with explicit port
streamlit run src/dashboard/app.py --server.port 8501

# Debug mode
streamlit run src/dashboard/app.py --logger.level=debug
```

### Performance Optimization

- Adjust `BATCH_SIZE` in `.env` for memory
- Use database connection pooling
- Enable incremental processing for large datasets
- Index frequently queried columns
- Archive old data periodically

## API Documentation

See individual module docstrings for detailed API documentation.

### Example: Custom ETL Pipeline

```python
from src.etl.pipeline import ETLPipeline
from src.config import DatabaseConfig

# Initialize
pipeline = ETLPipeline()
pipeline.setup_database()

# Register sources
pipeline.register_data_sources(
    csv_path="data/sales.csv",
    json_path="data/customers.json",
    api_config={
        "base_url": "https://api.example.com",
        "endpoint": "/v1/products",
        "api_key": "your_key"
    }
)

# Run
success, report, error = pipeline.run()

if success:
    print(f"Processed: {report.total_records_processed}")
    print(f"Status: {report.status}")
```

## Support & Maintenance

For issues, feature requests, or contributions, please refer to the project's issue tracker.

## License

[License information here]

## Contributors

[Contributors list]

---

**Last Updated**: 2024
**Version**: 1.0.0
