Project: Sales ETL and Dashboard

Overview
- Python-based ETL extracting from CSV, JSON, and REST API, transforming and loading into PostgreSQL.
- Interactive Streamlit dashboard with KPIs, filters, PDF/Excel export.
- Dockerized services with docker-compose, incremental processing, scheduler, and tests.

Getting started
- Copy `.env.example` to `.env` and edit DB and API settings.
- Build and run with Docker Compose: `docker-compose up --build`
- Run ETL once: `python -m src.etl.pipeline --run-now`
- Open dashboard: http://localhost:8501

See docs in the `docs/` folder for detailed instructions.
