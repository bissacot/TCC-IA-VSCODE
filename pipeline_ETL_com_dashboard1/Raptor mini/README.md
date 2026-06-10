# Sales ETL and Dashboard Solution

This repository contains a complete ETL pipeline, PostgreSQL data warehouse, and interactive Streamlit dashboard for sales analysis.

## Features

- Extract data from:
  - CSV file (`data/sample_sales.csv`)
  - JSON file (`data/sample_customers.json`)
  - REST API (`scripts/mock_api.py` serving product data)
- Transform data by:
  - removing duplicates
  - handling missing values
  - validating data types
  - standardizing dates to ISO format
  - deriving metrics: total sale value, year, month, quarter
- Load transformed data into PostgreSQL tables
- Data quality reporting and incremental processing
- Interactive Streamlit dashboard with filters and visualizations
- PDF export and Excel export support
- Docker and Docker Compose support
- Automated ETL scheduling with `schedule`
- Unit tests with `pytest`

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ for local development

### Local setup

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Start the mock API service and database with Docker Compose:

```bash
docker compose up --build -d postgres mock_api
```

4. Initialize the database schema:

```bash
python scripts/run_etl.py --init-db
```

5. Run a one-time ETL load:

```bash
python scripts/run_etl.py
```

6. Start the dashboard:

```bash
streamlit run src/dashboard/app.py
```

### Docker setup

1. Build and start all services:

```bash
docker compose up --build
```

2. Open the Streamlit dashboard at `http://localhost:8501`

## Files and folders

- `src/etl_app/`: ETL modules, config, logging, and quality utilities
- `src/dashboard/app.py`: Streamlit dashboard application
- `sql/schema.sql`: PostgreSQL table definitions
- `scripts/run_etl.py`: ETL orchestration script
- `scripts/mock_api.py`: Local mock product REST API
- `scripts/generate_reports.py`: PDF report generator
- `tests/`: Automated unit tests
- `data/`: Sample input files and incremental tracking file

## ETL scheduling

Run the scheduler locally with:

```bash
python scripts/scheduler.py
```

The scheduler executes the ETL pipeline every day at 02:00.

## Testing

Run unit tests with:

```bash
pytest
```

## Exporting

- Excel export is available in the Streamlit dashboard
- PDF summary export is available via `scripts/generate_reports.py`
