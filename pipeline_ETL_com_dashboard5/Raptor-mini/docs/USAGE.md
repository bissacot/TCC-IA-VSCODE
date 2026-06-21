# Sales Analytics ETL Usage Guide

## Prerequisites
- Python 3.10+
- PostgreSQL or Docker
- `pip` installed

## Install dependencies
```powershell
python -m pip install -r requirements.txt
```

## Configure environment
Copy `.env.example` to `.env` and update values.

## Initialize database
```powershell
psql "$(cat .env | select-string DATABASE_URL).ToString().Split('=')[1]" -f sql/schema.sql
```

## Run ETL
```powershell
python -m src.etl.main
```

## Run dashboard
```powershell
streamlit run src/dashboard/app.py
```

## Run scheduled ETL
```powershell
python -m src.etl.scheduler
```

## Docker
```powershell
docker compose up --build
```

## Export reports
Run the ETL and then use the `src.etl.reporting` module functions to export PDF and Excel files from the loaded data.
