# Design Overview

## Architecture
- Extraction: CSV file for sales, JSON file for customers, REST API or fallback JSON for products.
- Transformation: deduplication, validation, date standardization, derived metrics.
- Load: PostgreSQL tables for customers, products, and sales using SQLAlchemy.
- Dashboard: Streamlit app with filtering and Plotly visualizations.
- Reporting: Excel workbook export and PDF data quality report.
- Scheduling: `schedule`-based ETL runner for daily and hourly execution.

## Data Quality
The ETL produces per-entity data quality reports with:
- processed records
- invalid records
- duplicates removed
- missing values
- missing value percentage

## Deployment
- `Dockerfile` for container build
- `docker-compose.yml` with PostgreSQL and dashboard service
