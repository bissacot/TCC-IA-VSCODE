# ETL RAPTOR 3

Sales analysis ETL pipeline with dashboard, incremental processing, Docker support, automated scheduling, PDF reporting, and Excel export.

## Components

- `src/etl_raptor`: ETL modules and orchestration
- `src/dashboard`: Streamlit dashboard
- `src/api`: sample REST API mock server for product data
- `sql`: schema creation scripts and sample data scripts
- `tests`: unit tests

## Requirements

- Python 3.11+
- PostgreSQL
- Docker / Docker Compose

## Setup

1. Copy `.env.example` to `.env` and update values as needed.
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Ensure sample input files exist in `data/`:
   - `data/sales.csv`
   - `data/customers.json`
4. Initialize PostgreSQL schema:
   ```powershell
   psql "postgresql://etl_user:etl_password@localhost:5432/etl_raptor" -f sql/schema.sql
   ```
5. Start PostgreSQL, API mock, ETL, and dashboard:
   ```powershell
   docker compose up -d
   ```
6. Run ETL locally:
   ```powershell
   python -m src.etl_raptor.cli --run
   ```
7. Open the dashboard at `http://localhost:8501`

## Files

- `src/etl_raptor/main.py`: ETL orchestration
- `src/etl_raptor/extract.py`: extract from CSV, JSON, REST API
- `src/etl_raptor/transform.py`: data validation and metrics
- `src/etl_raptor/load.py`: load to PostgreSQL
- `src/etl_raptor/quality.py`: data quality report
- `src/etl_raptor/config.py`: environment variable loading
- `src/dashboard/app.py`: Streamlit dashboard
- `src/api/mock_api.py`: sample FastAPI mock service
- `sql/schema.sql`: PostgreSQL schema
- `docker-compose.yml`: PostgreSQL, API mock
- `Dockerfile`: containerize ETL and dashboard
- `tests/test_etl.py`: unit tests
