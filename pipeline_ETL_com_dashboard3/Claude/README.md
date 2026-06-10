# 📊 Sales ETL & Dashboard Solution

A complete, production-ready ETL (Extract, Transform, Load) and Interactive Dashboard solution for comprehensive sales data analysis using Python.

## 🎯 Features

### ETL Pipeline
- **Multi-Source Data Extraction**
  - CSV files (Sales data)
  - JSON files (Customer data)
  - REST APIs (Product data)
  
- **Data Transformation**
  - Automatic duplicate removal
  - Missing value handling with intelligent imputation
  - Data type validation and correction
  - ISO 8601 date standardization
  - Derived metrics calculation (total values, date components)
  
- **Data Quality Management**
  - Comprehensive quality reports
  - Record validation and error tracking
  - Missing value percentage analysis
  - Duplicate tracking
  
- **Database Loading**
  - PostgreSQL integration
  - Connection pooling for performance
  - Batch processing with configurable sizes
  - Upsert operations for incremental updates

### Interactive Dashboard
- **Real-time KPIs**
  - Total revenue
  - Number of sales
  - Average ticket size
  - Unique customer count
  
- **Advanced Visualizations**
  - Revenue trends by month
  - Revenue distribution by product category
  - Top 10 best-selling products
  - Sales distribution by state
  - Daily sales trends
  
- **Interactive Filtering**
  - Date range selection
  - State filtering
  - Product category filtering
  - Individual product selection

### Advanced Features
- **Automated Scheduling**
  - Daily ETL jobs
  - Weekly batch processing
  - Flexible job configuration
  
- **Report Generation**
  - PDF report creation
  - Excel export with multiple sheets
  - Executive summaries
  - Data quality metrics
  
- **Docker & Containerization**
  - Docker Compose orchestration
  - Multi-container deployment
  - Environment-based configuration
  
- **Production Ready**
  - Comprehensive logging
  - Exception handling
  - Type hints throughout
  - Unit tests
  - Clean architecture
  - Configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- PostgreSQL 12+ (if not using Docker)
- Git

### Local Installation

#### 1. Clone and Setup
```bash
cd sales_etl_dashboard
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

#### 4. Database Setup
```bash
# Create database and tables
psql -U postgres -h localhost -f database/init.sql
# Load sample data (optional)
psql -U postgres -h localhost -d sales_db -f database/sample_data.sql
```

#### 5. Prepare Data Files
Place your data files in `data/input/`:
- `sales.csv` - Sales data
- `customers.json` - Customer data

#### 6. Run ETL Pipeline
```bash
python run_etl.py

# Or with custom configuration
python run_etl.py --config config/etl_config.json
```

#### 7. Launch Dashboard
```bash
streamlit run src/dashboard/app.py
```

Open browser: `http://localhost:8501`

### Docker Deployment

#### 1. Build and Start Containers
```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 2. Access Services
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432

#### 3. Run ETL in Docker
```bash
docker-compose run etl_pipeline python run_etl.py
```

#### 4. Stop Services
```bash
docker-compose down
```

## 📋 Data Format Specifications

### CSV Sales Data (sales.csv)
```csv
sale_id,customer_id,product_id,quantity,unit_price,total_value,sale_date
SALE001,CUST001,PROD001,2,100.00,200.00,2024-01-15
```

**Required Columns:**
- `sale_id`: Unique sale identifier
- `customer_id`: Reference to customer
- `product_id`: Reference to product
- `quantity`: Number of items (positive integer)
- `unit_price`: Price per item
- `total_value`: Total sale amount
- `sale_date`: Sale timestamp (ISO 8601 format)

### JSON Customer Data (customers.json)
```json
[
  {
    "customer_id": "CUST001",
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "555-0001",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "registration_date": "2024-01-15"
  }
]
```

**Required Fields:**
- `customer_id`: Unique customer identifier
- `name`: Customer name
- `email`: Unique email address
- `state`: Customer state

### API Response Format
```json
{
  "data": [
    {
      "product_id": "PROD001",
      "name": "Product Name",
      "category": "Category",
      "price": 99.99,
      "description": "Product description",
      "sku": "SKU-12345"
    }
  ]
}
```

Or:
```json
[
  {
    "product_id": "PROD001",
    "name": "Product Name",
    "category": "Category",
    "price": 99.99
  }
]
```

## 🔧 Configuration

### Environment Variables (.env)

```properties
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=password

# API
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3
API_RETRY_DELAY=5

# ETL
CSV_PATH=data/input/sales.csv
JSON_PATH=data/input/customers.json
BATCH_SIZE=1000
LOG_LEVEL=INFO
INCREMENTAL=false
```

### JSON Configuration (config/etl_config.json)
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "sales_db",
    "user": "postgres",
    "password": "password"
  },
  "api": {
    "base_url": "https://api.example.com",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5
  },
  "csv_path": "data/input/sales.csv",
  "json_path": "data/input/customers.json",
  "batch_size": 1000,
  "log_level": "INFO",
  "incremental": false
}
```

## 📊 Database Schema

### Tables

#### customers
```sql
customer_id (PK) | name | email (UNIQUE) | phone | city | state | country | registration_date | created_at | updated_at
```

#### products
```sql
product_id (PK) | name | category | price | description | sku (UNIQUE) | created_at | updated_at
```

#### sales
```sql
sale_id (PK) | customer_id (FK) | product_id (FK) | quantity | unit_price | total_value | sale_date | sale_year | sale_month | sale_quarter | created_at | updated_at
```

### Indexes
- `sales.customer_id` for customer queries
- `sales.product_id` for product queries
- `sales.sale_date` for date range queries
- `sales.sale_year, sale_month` for time-based aggregations
- `products.category` for category analysis
- `customers.state` for state-based filtering
- `customers.email` for unique email constraint

### Views
- `sales_summary`: Monthly sales by category
- `top_products`: Product performance metrics
- `customer_analysis`: Customer purchase behavior

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_extractors.py -v
pytest tests/test_transformers.py::TestDataTransformer::test_remove_duplicates -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## 📈 ETL Pipeline Details

### Extraction Phase
1. **CSV Extractor**: Loads sales data with error handling
2. **JSON Extractor**: Parses customer data with schema flexibility
3. **API Extractor**: Fetches product data with retry logic

### Transformation Phase
1. **Deduplication**: Removes exact row duplicates
2. **Missing Value Handling**:
   - Numeric: Median imputation
   - Categorical: "Unknown" fill
3. **Data Type Validation**: Ensures correct types
4. **Date Standardization**: Converts to ISO 8601
5. **Derived Metrics**: Calculates totals, date parts
6. **Business Rules Validation**: Enforces constraints

### Loading Phase
1. **Connection Pooling**: Maintains efficient connections
2. **Batch Processing**: Configurable batch sizes
3. **Upsert Operations**: Updates or inserts on conflict
4. **Transaction Management**: Ensures data integrity

### Quality Reporting
- Records processed count
- Invalid records count
- Duplicates removed count
- Missing values percentage by column
- Records by source breakdown
- Validation errors details

## 📊 Dashboard Features

### KPI Cards
- Total Revenue (sum of all sales)
- Total Sales (count of transactions)
- Average Ticket Size (avg sale value)
- Unique Customers (count of distinct customers)

### Visualizations
- Bar chart: Monthly revenue trends
- Pie chart: Revenue by product category
- Horizontal bar: Top 10 best-selling products
- Bar chart: Top 10 states by revenue
- Line chart: Daily sales trends

### Filters
- Date range picker (start/end dates)
- State dropdown (All/State options)
- Category dropdown (All/Category options)
- Product dropdown (All/Product options)

### Data Export
- Real-time data table view
- Download capability through Streamlit

## 🔄 Scheduling

### Using Built-in Scheduler
```bash
python -c "from src.utils.scheduler import main; main()"
```

### Configuration in scheduler.py
```python
scheduler = ETLScheduler()
scheduler.schedule_daily_job("02:00")      # Run at 2 AM
scheduler.schedule_weekly_job("sunday")    # Run on Sundays
scheduler.run_scheduler()
```

### Using External Schedulers

#### APScheduler Integration
```python
from apscheduler.schedulers.background import BackgroundScheduler
from src.etl_pipeline import ETLPipeline

scheduler = BackgroundScheduler()
config = load_config_from_env()

def etl_job():
    pipeline = ETLPipeline(config)
    pipeline.run()

scheduler.add_job(etl_job, 'cron', hour=2, minute=0)
scheduler.start()
```

#### Cron Job (Linux/macOS)
```bash
0 2 * * * cd /path/to/project && /path/to/venv/bin/python run_etl.py
```

#### Windows Task Scheduler
1. Create basic task
2. Set trigger to daily at 02:00
3. Set action: `python run_etl.py`
4. Working directory: project root

## 📄 Report Generation

### Generate PDF Report
```python
from src.utils.report_generator import ReportGenerator
from src.utils.config import load_config_from_env

config = load_config_from_env()
generator = ReportGenerator(config.db_config)
pdf_path = generator.generate_pdf_report(
    filename="sales_report.pdf",
    quality_report_path="data/output/quality_report.json"
)
```

### Generate Excel Report
```python
excel_path = generator.generate_excel_report(filename="sales_report.xlsx")
```

Reports include:
- Executive summary
- KPI metrics
- Data quality metrics
- Sales data
- Customer analysis
- Product performance

## 🏗️ Architecture

### Design Patterns
- **Factory Pattern**: Extractor creation
- **Strategy Pattern**: Different extraction strategies
- **Builder Pattern**: Configuration construction
- **Singleton Pattern**: Logger and config instances
- **Repository Pattern**: Database access

### Modular Design
- **Separation of Concerns**: Each module has single responsibility
- **Dependency Injection**: Configuration passed to components
- **Abstraction**: Base classes for extensibility
- **Interface Segregation**: Minimal dependencies between modules

### Error Handling
- Custom exception hierarchy
- Try-catch blocks at module boundaries
- Logging at each critical point
- Graceful degradation where possible

## 🔐 Security Best Practices

- **Environment Variables**: Sensitive data not in code
- **Password Hashing**: Use environment secrets
- **SQL Injection Prevention**: Parameterized queries
- **Input Validation**: All inputs validated
- **Error Messages**: No sensitive data in logs
- **Connection Security**: SSL/TLS ready

## 📚 Code Quality

### Type Hints
- All functions include type hints
- Return types specified
- Optional parameters marked

### Documentation
- Module docstrings
- Function docstrings
- Inline comments for complex logic
- README with examples

### Testing
- Unit tests for core modules
- Test fixtures for data
- Test configuration
- Coverage reporting

### Logging
- Structured logging
- Multiple log levels
- File and console output
- Rotating log files

## 🐛 Troubleshooting

### Database Connection Issues
```python
# Check connection
from src.loaders.database import DatabaseManager
from src.utils.config import load_config_from_env

config = load_config_from_env()
manager = DatabaseManager(config.db_config)
# If successful, tables exist
```

### ETL Pipeline Errors
- Check `logs/etl_pipeline.log`
- Verify data file formats
- Check database connectivity
- Review API endpoint accessibility

### Dashboard Connection Issues
- Ensure PostgreSQL is running
- Verify credentials in .env
- Check network connectivity
- Review dashboard logs

### Docker Issues
```bash
# View logs
docker-compose logs postgres
docker-compose logs etl_pipeline
docker-compose logs streamlit

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📦 Deployment Checklist

- [ ] Environment variables configured (.env)
- [ ] Database initialized and accessible
- [ ] Data files in correct locations
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Logs directory created
- [ ] Database backups configured
- [ ] Monitoring/alerts set up
- [ ] Documentation reviewed
- [ ] Security review completed

## 📞 Support & Contributing

For issues and feature requests, please refer to documentation and logs.

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎓 Learning Resources

- **Python**: Clean Code principles, Type Hints
- **PostgreSQL**: Query optimization, Indexing
- **Docker**: Container orchestration
- **Streamlit**: Interactive dashboards
- **Data Engineering**: ETL best practices

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Author**: ETL Team
