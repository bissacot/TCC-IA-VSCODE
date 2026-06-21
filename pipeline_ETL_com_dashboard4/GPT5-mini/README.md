Sales ETL + Dashboard
=====================

Complete ETL pipeline and Streamlit dashboard for sales analysis.

Quick start
-----------

- Copy `.env.example` to `.env` and adjust DB and API settings.
- Build and run with Docker Compose: `docker-compose up --build`
- Or run locally with Python 3.9+: `pip install -r requirements.txt` then `python -m src.etl.run`
- Start dashboard: `streamlit run src/dashboard/app.py --server.port 8501`

Project Layout
--------------
- `src/` Python package with ETL code and dashboard
- `docker/` Dockerfiles and compose
- `tests/` unit tests
- `sql/` database schema
