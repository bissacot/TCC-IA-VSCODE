# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+ or Docker
- PostgreSQL 12+ (or use Docker)

### Step 1: Clone and Configure

```bash
cd etl_dashboard
cp .env.example .env
```

### Step 2: Install Dependencies

**Local:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Docker:**
```bash
docker-compose up -d
```

### Step 3: Initialize Database

**Local:**
```bash
python main.py init
```

**Docker:**
Database automatically initializes via `sql/init.sql`

### Step 4: Run ETL Pipeline

```bash
python main.py etl \
  --csv data/sample_sales.csv \
  --json data/sample_customers.json \
  --api-url https://api.example.com \
  --api-endpoint /v1/products
```

### Step 5: Start Dashboard

**Local:**
```bash
python main.py dashboard
# Or: streamlit run src/dashboard/app.py
```

**Docker:**
```bash
docker-compose up dashboard
# Access at http://localhost:8501
```

## Common Commands

```bash
# Run tests
pytest tests/ -v

# Check database
python -c "from src.database.connection import DatabaseManager; print(DatabaseManager.health_check())"

# Generate reports
python -c "from src.utils.report_generator import ReportGenerator; r = ReportGenerator(); print(r.generate_excel_report())"

# View logs
tail -f logs/etl.log
```

## Docker Quick Commands

```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose up -d --build

# Access PostgreSQL
docker-compose exec postgres psql -U etl_user -d sales_db
```

## Sample Data

Sample files provided in `data/` folder:
- `sample_sales.csv` - Sales transactions
- `sample_customers.json` - Customer information
- `sample_products.json` - Product catalog

## Accessing Services

- **Dashboard**: http://localhost:8501
- **PgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432

## Troubleshooting

### Database connection fails
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -h localhost -U etl_user -d sales_db
```

### Dashboard doesn't show data
```bash
# Check database has data
docker-compose exec postgres psql -U etl_user -d sales_db -c "SELECT COUNT(*) FROM sales;"

# Clear cache and restart
rm -rf ~/.streamlit/cache
docker-compose restart dashboard
```

### Import errors
```bash
# Install in development mode
pip install -e .

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Next Steps

1. Customize `.env` with your configuration
2. Update data sources in the ETL pipeline
3. Deploy to production environment
4. Set up automated scheduling
5. Configure monitoring and alerts

For detailed documentation, see [docs/README.md](README.md)
