# Sales Analytics ETL and Dashboard

## Overview
This repository contains a Python-based ETL solution for sales analysis with:
- data extraction from CSV, JSON, and REST API
- transformation and validation with data quality reporting
- loading into PostgreSQL
- interactive Streamlit dashboard
- Docker + Docker Compose support
- automated ETL scheduling via cron
- PDF reporting and Excel export

## Structure
- `src/etl/` - ETL pipeline modules
- `src/dashboard/` - Streamlit dashboard app
- `src/api/` - REST API client and simulation utilities
- `tests/` - unit tests
- `sql/` - database schema and seed scripts
- `docs/` - documentation and usage guides

## Setup
1. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and update values.
3. Start PostgreSQL and run schema script:
   ```powershell
   psql %DATABASE_URL% -f sql/schema.sql
   ```
4. Run ETL:
   ```powershell
   python -m src.etl.main
   ```
5. Start dashboard:
   ```powershell
   streamlit run src/dashboard/app.py
   ```

## Docker
```powershell
docker compose up --build
```

## Testing
```powershell
pytest --cov=src tests
```

## Data
Place sample files under `data/`:
- `sales.csv`
- `customers.json`

The API client is configured via `src/api/product_service.py`.
