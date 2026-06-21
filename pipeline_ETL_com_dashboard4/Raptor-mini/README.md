# ETL RAPTOR 4

Sales analysis ETL and dashboard solution built with Python.

## Features

- Extract from CSV, JSON, and REST API sources
- Transform with deduplication, missing value handling, type validation, and derived metrics
- Load into PostgreSQL database with customer, product, and sales tables
- Data quality reporting and incremental processing
- Interactive Streamlit dashboard with filters, KPIs, and charts
- Docker and Docker Compose support
- PDF report generation and Excel export
- Automated ETL scheduling via Airflow or cron

## Project Structure

- `src/`: application code
- `tests/`: unit tests
- `docker-compose.yml`: local database and app orchestration
- `Dockerfile`: container image definition
- `requirements.txt`: Python dependencies
- `data/`: sample input file references

## Setup

1. Install Docker Desktop.
2. Copy `env.example` to `.env` and set database credentials.
3. Run `docker compose up --build`.
4. Access Streamlit dashboard at `http://localhost:8501`.

## Local development

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python src/etl/main.py
streamlit run src/dashboard/app.py
```

## Tests

```bash
pytest
```
