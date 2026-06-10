# Sales ETL & Dashboard - Quick Reference

## Project Summary

A production-ready ETL (Extract, Transform, Load) and Analytics Dashboard solution featuring:
- **Multi-source extraction**: CSV, JSON, REST API
- **Advanced transformation**: Validation, deduplication, standardization
- **PostgreSQL backend**: Optimized schema with materialized views
- **Interactive Streamlit dashboard**: Real-time analytics and KPIs
- **Data quality reporting**: Comprehensive metrics and tracking
- **Docker deployment**: Complete containerization
- **Automated scheduling**: Airflow DAG included
- **Production-ready**: Type hints, logging, error handling, testing

---

## Quick Commands

```bash
# 1. Setup (first time)
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database credentials

# 2. Create database
createdb -U postgres sales_etl_db
psql -U postgres -d sales_etl_db -f sql/schema.sql

# 3. Generate sample data
python main.py setup

# 4. Run ETL pipeline
python main.py run

# 5. Start dashboard
streamlit run src/dashboard/app.py
# Access at: http://localhost:8501

# 6. Run tests
pytest

# 7. Generate reports
python main.py reports
```

## Docker Quick Start

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec postgres psql -U etl_user -d sales_etl_db -f /docker-entrypoint-initdb.d/schema.sql

# Generate sample data
docker-compose run etl python main.py setup

# Run ETL
docker-compose run etl python main.py run

# Access dashboard at http://localhost:8501
```

---

## Project Structure

```
sales_etl_dashboard/
├── src/
│   ├── etl/           # Extraction, transformation, pipeline
│   ├── database/      # Database connection and loading
│   ├── dashboard/     # Streamlit dashboard
│   ├── models/        # Data models and schemas
│   └── utils/         # Utilities, validators, config
├── tests/             # Unit tests
├── sql/               # Database schema
├── data/              # Input/output data
├── dags/              # Airflow DAG
├── main.py            # CLI entry point
└── requirements.txt   # Dependencies
```

---

## Key Features

### ETL Pipeline
- **Extract**: CSV, JSON, REST API with retry logic
- **Transform**: Validation, deduplication, date standardization
- **Load**: Bulk operations, UPSERT logic, referential integrity
- **Quality**: Comprehensive data quality metrics

### Dashboard
- **KPIs**: Revenue, sales count, avg ticket, unique customers
- **Charts**: Revenue trends, category breakdown, top products, state distribution
- **Filters**: Date range, state, category, product
- **Data**: Detailed sales records with export

### Database
- **Tables**: Customers, products, sales, quality reports
- **Views**: Summary, monthly revenue, product performance, state distribution
- **Indexes**: Optimized for common queries
- **Transactions**: ACID compliance

---

## Configuration Files

### .env
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_etl_db
DB_USER=etl_user
DB_PASSWORD=secure_password
LOG_LEVEL=INFO
INCREMENTAL_MODE=true
```

### docker-compose.yml
- PostgreSQL service
- Streamlit dashboard service
- ETL pipeline service
- pgAdmin (optional)

### schema.sql
- Table definitions with constraints
- Indexes for performance
- Materialized views
- Refresh functions

---

## Data Flow

```
┌─────────────────────────────────────┐
│    Data Sources                     │
│ (CSV, JSON, API)                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    ETL Pipeline                     │
│ ┌──────────┐  ┌──────────────────┐  │
│ │ Extractor├─→│ Transformer      │  │
│ └──────────┘  │ (Validate, Clean)│  │
│               └────────┬─────────┘  │
│                        │            │
│               ┌────────▼─────────┐  │
│               │ Loader           │  │
│               │ (UPSERT to DB)   │  │
│               └────────┬─────────┘  │
└────────────────────────┼────────────┘
                         │
┌────────────────────────▼────────────┐
│    PostgreSQL Database              │
│ (Customers, Products, Sales)        │
└────────────────────────┬────────────┘
                         │
        ┌────────────────┼────────────┐
        │                │            │
    ┌───▼──┐        ┌────▼────┐  ┌──▼──┐
    │ View │        │Dashboard│  │Rpt  │
    │Refresh        │          │  │Gen  │
    └──────┘        └──────────┘  └─────┘
```

---

## Database Schema Highlights

### Customers Table
```sql
customer_id (PK)
name, email (UNIQUE), phone
address, city, state, zip_code, country
created_at, updated_at
```

### Products Table
```sql
product_id (PK)
name, category, subcategory, price
description, manufacturer
created_at, updated_at
```

### Sales Table
```sql
sale_id (PK)
customer_id (FK), product_id (FK)
quantity, unit_price, total_value
sale_date, year, month, quarter
state, payment_method
created_at, updated_at
```

### Quality Reports Table
```sql
report_id (PK)
report_timestamp
total_records_processed, valid_records, invalid_records
duplicates_removed, missing_values_count, missing_values_percentage
data_type_errors, date_conversion_errors
processing_time_seconds, report_details (JSONB)
```

---

## Common Tasks

### Run ETL Pipeline
```bash
python main.py run
# Extracts all data sources, transforms, loads to DB
```

### Generate Sample Data
```bash
python main.py setup
# Creates sample CSV, JSON, and API data
```

### Export Data to Excel
```bash
python main.py reports
# Exports sales data and summary statistics
```

### Refresh Dashboard Views
```bash
psql -U etl_user -d sales_etl_db -c "SELECT refresh_materialized_views();"
```

### Run Tests
```bash
pytest -v
# Runs all unit tests with verbose output
```

### Check Logs
```bash
tail -f logs/etl.log
# Shows real-time ETL logs
```

### Database Connection
```bash
psql -U etl_user -d sales_etl_db
# Connects to database for queries
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection failed | Check PostgreSQL running, verify .env credentials |
| Module not found | Ensure in project root, run `pip install -r requirements.txt` |
| Dashboard won't start | Check if port 8501 available, verify DB connection |
| ETL fails to run | Check data files exist in data/input/, verify permissions |
| Tests fail | Run `pip install -r requirements.txt` first |
| Docker issues | Run `docker-compose build --no-cache` |

---

## Performance Tips

1. **Batch Processing**: Increase BATCH_SIZE in .env for faster loading
2. **Incremental Mode**: Enable INCREMENTAL_MODE to process only new data
3. **Materialized Views**: Pre-computed for dashboard queries
4. **Indexes**: Applied on foreign keys and commonly filtered columns
5. **Connection Pooling**: Reused database connections

---

## Security Best Practices

- ✅ Environment variables for sensitive data (.env)
- ✅ SQL parameterized queries (prevent injection)
- ✅ Input validation on all data
- ✅ Type hints for code clarity
- ✅ Comprehensive error handling
- ✅ Logging for audit trail
- ✅ Database constraints and transactions

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Database | PostgreSQL 12+ |
| Web Framework | Streamlit |
| Visualization | Plotly |
| Data Processing | Pandas |
| Task Scheduling | Apache Airflow |
| Containerization | Docker |
| Testing | pytest |
| Logging | Python logging |

---

## Deployment Options

### Local Development
```bash
python main.py run
streamlit run src/dashboard/app.py
```

### Docker Single Container
```bash
docker build -t sales-etl .
docker run -p 8501:8501 --env-file .env sales-etl
```

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Production
- Use managed PostgreSQL (AWS RDS, Azure Database)
- Deploy dashboard on cloud platform (AWS, GCP, Azure)
- Schedule ETL with production Airflow
- Use secrets management (AWS Secrets Manager, etc.)
- Implement monitoring and alerting

---

## File Formats

### Input CSV (sales.csv)
```
sale_id,customer_id,product_id,quantity,unit_price,sale_date,state,payment_method
SALE-000001,CUST-00001,PROD-00001,5,99.99,2024-01-15,CA,Credit Card
```

### Input JSON (customers.json)
```json
[
  {
    "customer_id": "CUST-00001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "5551234567",
    "state": "CA"
  }
]
```

### Output Excel (sales_export_*.xlsx)
```
Columns: sale_id, customer_id, customer_name, product_id, product_name,
         category, quantity, unit_price, total_value, sale_date, state,
         payment_method
```

---

## API Endpoints (Potential Extension)

```python
# Could be extended with FastAPI:
GET /api/sales          # List sales
GET /api/sales/{id}     # Get specific sale
POST /api/sales         # Create sale
GET /api/products       # List products
GET /api/customers      # List customers
GET /api/reports        # Get quality reports
```

---

## Monitoring Queries

```sql
-- Total records
SELECT 'Customers' as table, COUNT(*) FROM customers
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Sales', COUNT(*) FROM sales;

-- Recent quality report
SELECT * FROM data_quality_reports 
ORDER BY report_timestamp DESC LIMIT 1;

-- Monthly revenue
SELECT * FROM monthly_revenue ORDER BY month DESC LIMIT 12;

-- Top products
SELECT * FROM product_performance ORDER BY total_revenue DESC LIMIT 10;
```

---

## Documentation

- **README.md**: Full project documentation
- **EXECUTION_GUIDE.md**: Step-by-step setup instructions
- **This file**: Quick reference guide
- **Code comments**: Inline documentation
- **Type hints**: Function signatures with types
- **Docstrings**: Module and function documentation

---

## Contact & Support

For issues or questions:
1. Check EXECUTION_GUIDE.md for setup help
2. Review README.md for detailed documentation
3. Check logs/ directory for error messages
4. Run tests to verify installation
5. Consult source code comments

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready ✅
