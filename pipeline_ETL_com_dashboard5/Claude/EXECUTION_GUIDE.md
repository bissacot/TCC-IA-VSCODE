# Execution Instructions

## Quick Start (5 minutes)

### Option 1: Local Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Create PostgreSQL database
createdb -U postgres sales_etl_db

# 5. Initialize schema
psql -U postgres -d sales_etl_db -f sql/schema.sql

# 6. Generate sample data
python main.py setup

# 7. Run ETL
python main.py run

# 8. Start dashboard (in another terminal)
streamlit run src/dashboard/app.py
```

**Dashboard URL**: http://localhost:8501

### Option 2: Docker Compose (Recommended)

```bash
# 1. Build and start services
docker-compose up -d

# 2. Wait for database to be ready
sleep 10

# 3. Initialize database
docker-compose exec postgres psql -U etl_user -d sales_etl_db -f /docker-entrypoint-initdb.d/schema.sql

# 4. Generate sample data
docker-compose run etl python main.py setup

# 5. Run ETL
docker-compose run etl python main.py run
```

**Dashboard URL**: http://localhost:8501

---

## Step-by-Step Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (for Docker option)
- Recommended: 4GB RAM, 2 CPU cores

### Part 1: Environment Setup

```bash
# Create project directory
mkdir sales_etl_dashboard
cd sales_etl_dashboard

# Clone/download the project files
# (Or use: git clone <repo-url>)

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Part 2: Database Setup

**Option A: PostgreSQL on Local Machine**

```bash
# Install PostgreSQL (if not already installed)
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
createdb -U postgres sales_etl_db

# Create user (if needed)
psql -U postgres -c "CREATE USER etl_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sales_etl_db TO etl_user;"

# Initialize schema
psql -U postgres -d sales_etl_db -f sql/schema.sql
```

**Option B: Docker Database**

```bash
# Start PostgreSQL container
docker run -d \
  --name postgres_etl \
  -e POSTGRES_DB=sales_etl_db \
  -e POSTGRES_USER=etl_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:16-alpine

# Wait for container to start
sleep 5

# Initialize schema
docker exec postgres_etl psql -U etl_user -d sales_etl_db -f /schema.sql
```

### Part 3: Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# For local PostgreSQL:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_etl_db
DB_USER=etl_user
DB_PASSWORD=secure_password

# For Docker:
DB_HOST=postgres  # (Docker service name)
DB_PORT=5432
```

### Part 4: Run ETL Pipeline

```bash
# Generate sample data
python main.py setup
# Output: Files created in data/input/

# Run ETL pipeline
python main.py run
# Output: Logs to logs/etl.log and displays summary

# Expected output:
# ================================================================================
# ETL EXECUTION SUMMARY
# ================================================================================
# Status: SUCCESS
# Processing Time: X.XXs
# 
# Extraction:
#   customers: 100
#   products: 50
#   sales: 500
# 
# Transformation:
#   customers_valid: 100
#   products_valid: 50
#   sales_valid: 500
# 
# Loading:
#   customers_loaded: 100
#   products_loaded: 50
#   sales_loaded: 500
```

### Part 5: Start Dashboard

```bash
# In a new terminal (with venv activated):
streamlit run src/dashboard/app.py

# Output:
# You can now view your Streamlit app in your browser.
# 
# Local URL: http://localhost:8501
```

Open browser to http://localhost:8501

---

## Docker Compose Full Stack

### Start Everything

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# Check services
docker-compose ps

# Expected output:
# NAME         STATUS    PORTS
# sales_etl_db     Up    5432/tcp
# sales_dashboard  Up    0.0.0.0:8501->8501/tcp
```

### Initialize Database

```bash
# Wait for database to be ready
sleep 10

# Copy schema to container
docker cp sql/schema.sql sales_etl_db:/

# Initialize schema
docker-compose exec postgres psql -U etl_user -d sales_etl_db -f /schema.sql
```

### Generate Sample Data & Run ETL

```bash
# Enter ETL container
docker-compose run etl bash

# Inside container:
python main.py setup  # Generate sample data
python main.py run    # Run ETL pipeline
exit
```

### Access Services

- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432
- **pgAdmin** (optional): http://localhost:5050
  - Email: admin@example.com
  - Password: admin

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_etl.py

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Test Commands

```bash
# Check validators
pytest tests/test_etl.py::TestValidators

# Check models
pytest tests/test_etl.py::TestDataModels

# Check transformer
pytest tests/test_etl.py::TestDataTransformer
```

---

## Generate Reports

### Quality Report

```bash
python main.py run
# Generates: logs/etl.log with quality metrics
```

### Excel Exports

```bash
python main.py reports
# Generates: data/output/exports/*.xlsx
#   - sales_export_*.xlsx
#   - summary_statistics_*.xlsx
```

### PDF Reports

```bash
python main.py reports
# Generates: data/output/reports/*.pdf (if enabled in .env)
```

---

## Airflow Scheduling

### Setup Airflow

```bash
# Install Airflow
pip install apache-airflow

# Set Airflow home
export AIRFLOW_HOME=./airflow

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com

# Start scheduler
airflow scheduler

# In another terminal, start webserver
airflow webserver --port 8080
```

### Access Airflow

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### Trigger DAG

```bash
# List DAGs
airflow dags list

# Trigger DAG
airflow dags trigger sales_etl_pipeline

# Check DAG status
airflow dags list-runs sales_etl_pipeline
```

---

## Monitoring & Troubleshooting

### View Logs

```bash
# ETL logs
tail -f logs/etl.log

# Dashboard logs
docker-compose logs -f dashboard

# Database logs
docker-compose logs -f postgres
```

### Database Connection Test

```bash
# Test local connection
psql -U etl_user -h localhost -d sales_etl_db -c "SELECT COUNT(*) FROM customers;"

# Test Docker connection
docker-compose exec postgres psql -U etl_user -d sales_etl_db -c "SELECT COUNT(*) FROM sales;"
```

### Query Database Directly

```bash
# Connect to database
psql -U etl_user -d sales_etl_db

# Useful queries
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales;
SELECT * FROM data_quality_reports ORDER BY report_timestamp DESC LIMIT 1;
```

### Check Data Files

```bash
# View generated files
ls -la data/input/
ls -la data/output/

# Check CSV content
head -5 data/input/sales.csv
wc -l data/input/sales.csv

# Check JSON content
cat data/input/customers.json | jq . | head -20
```

---

## Common Issues & Solutions

### Issue: Database Connection Error

```
Error: could not connect to server: Connection refused
```

**Solution**:
```bash
# Check if PostgreSQL is running
psql --version

# Start PostgreSQL (if on Docker)
docker-compose up -d postgres

# Verify connection
psql -U etl_user -h localhost -d sales_etl_db
```

### Issue: Module Not Found

```
ModuleNotFoundError: No module named 'src'
```

**Solution**:
```bash
# Ensure you're in project root
cd sales_etl_dashboard

# Reinstall dependencies
pip install -r requirements.txt

# Or run as module
python -m src.etl.pipeline
```

### Issue: Dashboard Not Accessible

```
Connection refused at http://localhost:8501
```

**Solution**:
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Restart dashboard
streamlit run src/dashboard/app.py --server.port 8501

# Or with Docker
docker-compose logs dashboard
docker-compose restart dashboard
```

### Issue: Sample Data Not Generated

```
FileNotFoundError: [Errno 2] No such file or directory: 'data/input/sales.csv'
```

**Solution**:
```bash
# Create directories
mkdir -p data/input data/output

# Generate sample data
python main.py setup

# Verify files
ls -la data/input/
```

---

## Performance Optimization

### Database Indexes

The schema includes optimized indexes. To verify:

```bash
psql -U etl_user -d sales_etl_db -c "\di"
```

### Materialized Views Refresh

```bash
# Refresh manually
psql -U etl_user -d sales_etl_db -c "SELECT refresh_materialized_views();"

# Or schedule in Airflow
```

### Batch Processing

Edit `.env`:
```ini
BATCH_SIZE=5000
CHUNK_SIZE=20000
```

---

## Data File Formats

### CSV Format (sales.csv)
```
sale_id,customer_id,product_id,quantity,unit_price,sale_date,state,payment_method
SALE-000001,CUST-00001,PROD-00001,5,99.99,2024-01-15,CA,Credit Card
```

### JSON Format (customers.json)
```json
[
  {
    "customer_id": "CUST-00001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "state": "CA"
  }
]
```

### API Response Format
```json
{
  "results": [
    {
      "product_id": "PROD-00001",
      "name": "Widget",
      "category": "Electronics",
      "price": 99.99
    }
  ]
}
```

---

## Cleanup

### Remove Everything (Local)

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Drop database
dropdb sales_etl_db

# Remove project files
cd ..
rm -rf sales_etl_dashboard
```

### Clean Docker

```bash
# Stop and remove all containers
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a
```

---

## Next Steps

1. **Customize Data**: Modify `src/utils/sample_data.py` to generate realistic data
2. **Add Filters**: Extend dashboard filtering in `src/dashboard/app.py`
3. **Create API**: Build REST API around the database
4. **Scale Up**: Move to production database, add caching
5. **Monitor**: Implement alerting for failed ETL runs

---

**Questions or Issues?** Check README.md for detailed documentation.
