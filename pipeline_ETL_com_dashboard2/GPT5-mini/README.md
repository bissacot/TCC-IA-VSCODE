Sales ETL and Dashboard

Complete ETL and interactive dashboard for sales analysis.

Quick start:

1. Copy `.env.example` to `.env` and edit values.
2. Start services with Docker Compose:

```bash
docker-compose up --build
```

3. The Streamlit dashboard will be at http://localhost:8501

Project layout:
- `src/etl` ETL modules (extract, transform, load, runner)
- `src/dashboard` Streamlit app
- `src/mock_api` mock product REST API used for local runs
- `sql/create_tables.sql` initial schema
- `tests` unit tests (pytest)

See documentation in this README for running tests and scheduled ETL.
