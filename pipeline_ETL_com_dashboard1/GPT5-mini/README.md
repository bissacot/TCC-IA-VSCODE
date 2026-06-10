# ETL + Dashboard for Sales Analysis

This repository contains a complete ETL pipeline and interactive dashboard for sales analysis using Python, PostgreSQL, and Streamlit.

Quickstart (local, with Docker Compose):

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Start services:

```bash
docker-compose up --build
```

3. Services:
- Streamlit dashboard: http://localhost:8501
- Mock product API: http://localhost:8000/products

Run ETL manually (once):

```bash
python src/app/etl/etl_runner.py --once
```

Run tests:

```bash
pytest -q
```

See `src/` for implementation details and `docs/` for more instructions.
