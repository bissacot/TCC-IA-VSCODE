# ETL Raptor 2

A complete Python ETL and Streamlit dashboard solution for sales analysis. The project extracts sales data from CSV, customer data from JSON, and product data from a REST API. It transforms, validates, and loads the data into PostgreSQL, and provides interactive reporting with advanced export and scheduling features.

## Features
- Extract from CSV, JSON and REST API
- Deduplicate and validate inputs
- Standardize dates to ISO format
- Create derived metrics: total sale, year, month, quarter
- Generate data quality reports
- Load data into PostgreSQL relational tables
- Incremental processing with ETL metadata tracking
- Streamlit dashboard with filters and visualizations
- PDF summary report generation
- Excel export of transformed data
- Docker and Docker Compose support
- Automated scheduling via Python scheduler
- Unit tests with `pytest`

## Getting Started

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)

### Local Setup
1. Copy `.env.example` to `.env` and update if needed.
2. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Initialize PostgreSQL and create tables:
   - Use Docker Compose or install PostgreSQL locally.
   - If using Docker Compose, run:
     ```powershell
     docker compose up --build -d
     ```
4. Run the ETL pipeline once:
   ```powershell
   python -m src.pipeline
   ```
5. Start the dashboard:
   ```powershell
   streamlit run dashboard/app.py
   ```

### Docker Compose
```powershell
docker compose up --build
```
- The Streamlit dashboard will be available at `http://localhost:8501`
- The mock product API is exposed at `http://localhost:5000/products`

## Project Layout
- `src/`: ETL application modules
- `dashboard/`: Streamlit dashboard
- `sql/`: PostgreSQL schema creation scripts
- `sample_data/`: sample CSV and JSON source files
- `tests/`: unit tests
- `mock_api.py`: local product REST API mock

## Testing
Run unit tests with:
```powershell
pytest
```

## Execution
- `python -m src.pipeline` — run ETL once
- `python -m src.scheduler` — run ETL with daily scheduling
- `streamlit run dashboard/app.py` — start the dashboard
- `python mock_api.py` — start the mock product API

## Notes
- Environment variables are managed via `.env` using `python-dotenv`.
- The ETL uses incremental processing and stores metadata in PostgreSQL.
- Output files are generated under `output/`.

