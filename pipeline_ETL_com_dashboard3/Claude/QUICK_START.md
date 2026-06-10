# Getting Started Guide

## Quick Start (5 minutes)

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your database details
```

### 3. Initialize Database
```bash
psql -U postgres -d sales_db -f database/init.sql
```

### 4. Prepare Sample Data
Copy sample files from `data/input/`:
- `sales_sample.csv` → `sales.csv`
- `customers_sample.json` → `customers.json`

### 5. Run
```bash
# ETL Pipeline
python run_etl.py

# Dashboard (in new terminal)
streamlit run src/dashboard/app.py
```

### 6. Access
Open `http://localhost:8501` in your browser

---

## Project Overview

This is a **complete, production-ready** ETL and Analytics solution featuring:

- **Multi-source data extraction** (CSV, JSON, REST API)
- **Comprehensive data transformation** with validation
- **PostgreSQL database** with optimized schema
- **Interactive Streamlit dashboard** with KPIs and visualizations
- **Advanced features**: scheduling, report generation, Docker support
- **Production-quality code**: type hints, logging, tests, error handling

---

## Key Components

### 1. **ETL Pipeline** (`src/etl_pipeline.py`)
Orchestrates the complete extraction, transformation, and loading process.

### 2. **Data Extractors** (`src/extractors/`)
- `CSVExtractor`: Loads CSV files
- `JSONExtractor`: Parses JSON files
- `APIExtractor`: Fetches from REST APIs

### 3. **Data Transformation** (`src/transformers/transformer.py`)
- Removes duplicates
- Handles missing values
- Validates data types
- Standardizes dates
- Creates derived metrics
- Validates business rules

### 4. **Database Layer** (`src/loaders/`)
- Connection pooling
- Batch processing
- Transaction management
- Query execution

### 5. **Dashboard** (`src/dashboard/app.py`)
Interactive Streamlit application with:
- KPI cards
- Advanced visualizations
- Real-time filtering
- Data export

### 6. **Utilities** (`src/utils/`)
- Configuration management
- Logging setup
- Custom exceptions
- Data models
- Report generation
- Job scheduling

---

## Directory Structure

```
sales_etl_dashboard/
├── src/                      # Source code
│   ├── etl_pipeline.py      # Main orchestrator
│   ├── extractors/          # Data extraction
│   ├── transformers/        # Data transformation
│   ├── loaders/             # Database loading
│   ├── dashboard/           # Streamlit app
│   └── utils/               # Utilities
├── tests/                    # Unit tests
├── database/                 # SQL scripts
├── data/                     # Data files
├── config/                   # Configuration
├── logs/                     # Application logs
├── run_etl.py               # Main entry point
├── requirements.txt         # Dependencies
├── Dockerfile               # Container image
├── docker-compose.yml       # Multi-container setup
└── README.md                # Full documentation
```

---

## Usage Examples

### Extract Data
```python
from src.extractors import CSVExtractor, JSONExtractor, APIExtractor

# From CSV
csv_extractor = CSVExtractor("data/input/sales.csv")
df_sales = csv_extractor.extract()

# From JSON
json_extractor = JSONExtractor("data/input/customers.json")
df_customers = json_extractor.extract()

# From API
api_config = APIConfig(base_url="https://api.example.com")
api_extractor = APIExtractor(api_config, endpoint="/products")
df_products = api_extractor.extract()
```

### Transform Data
```python
from src.transformers import DataTransformer

transformer = DataTransformer()
df_transformed, quality_report = transformer.transform_sales_data(df_sales)

# Access quality metrics
print(f"Records processed: {quality_report.total_records_processed}")
print(f"Duplicates removed: {quality_report.duplicates_removed}")
print(f"Missing values: {quality_report.missing_values_percentage}")
```

### Load Data
```python
from src.loaders import DataLoader
from src.utils.config import load_config_from_env

config = load_config_from_env()
loader = DataLoader(config.db_config)

rows_loaded = loader.load_sales(df_sales)
print(f"Loaded {rows_loaded} sales records")
```

### Query Database
```python
from src.loaders import DatabaseManager

db_manager = DatabaseManager(config.db_config)

# Execute query
results = db_manager.execute_query(
    "SELECT * FROM sales WHERE sale_year = %s",
    (2024,)
)

for row in results:
    print(row)
```

---

## Configuration

### Via Environment Variables
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=password
API_BASE_URL=https://api.example.com
CSV_PATH=data/input/sales.csv
JSON_PATH=data/input/customers.json
```

### Via JSON File
```bash
python run_etl.py --config config/etl_config.json
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_extractors.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Run ETL
docker-compose run etl_pipeline python run_etl.py

# Access dashboard
# http://localhost:8501
```

---

## Advanced Features

### 1. Automated Scheduling
```python
from src.utils.scheduler import ETLScheduler

scheduler = ETLScheduler()
scheduler.schedule_daily_job("02:00")
scheduler.run_scheduler()
```

### 2. Report Generation
```python
from src.utils.report_generator import ReportGenerator

generator = ReportGenerator(config.db_config)
pdf_path = generator.generate_pdf_report()
excel_path = generator.generate_excel_report()
```

### 3. Data Quality Reports
Automatically generated after each ETL run:
- `data/output/quality_report.json`
- `data/output/execution_summary.json`

---

## Performance Tips

1. **Increase batch size** for faster loading
   ```
   BATCH_SIZE=5000
   ```

2. **Optimize database queries** with proper indexes
   ```sql
   CREATE INDEX idx_sales_customer ON sales(customer_id);
   ```

3. **Use connection pooling**
   ```python
   manager = DatabaseManager(config.db_config, pool_size=10)
   ```

4. **Monitor resource usage**
   ```bash
   top
   free -h
   df -h
   ```

---

## Next Steps

1. **Customize data sources** - Add your own CSV, JSON, or API sources
2. **Extend transformation** - Add custom validation or metrics
3. **Enhance dashboard** - Add more visualizations and filters
4. **Deploy to production** - Use Docker Compose or cloud platform
5. **Set up scheduling** - Automate ETL job execution
6. **Configure monitoring** - Track pipeline health and performance

---

## Documentation

- **README.md** - Full project documentation
- **API.md** - Detailed API reference
- **DEPLOYMENT.md** - Production deployment guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **STRUCTURE.md** - Project structure overview

---

## Support

For issues:
1. Check **TROUBLESHOOTING.md**
2. Review logs in **logs/** directory
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Check database connectivity

---

Happy analyzing! 📊
