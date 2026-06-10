# Sales ETL Dashboard - Complete Guide

A production-ready ETL (Extract, Transform, Load) and Dashboard solution for sales analysis using Python.

## Features

### ✅ Data Extraction
- **CSV Files**: Load sales data from CSV format
- **JSON Files**: Extract customer data from JSON files
- **REST APIs**: Fetch product data from external APIs
- Error handling and retry logic

### ✅ Data Transformation
- **Duplicate Removal**: Identify and remove duplicate records
- **Missing Value Handling**: Handle and report missing values
- **Data Validation**: Type checking and business rule validation
- **Date Standardization**: Convert dates to ISO format
- **Derived Metrics**: Calculate total value, year, month, quarter

### ✅ Data Quality Reporting
- Records processed and invalid counts
- Percentage of missing values
- Duplicates removed tracking
- Processing time metrics

### ✅ Database Loading
- PostgreSQL support with connection pooling
- Relational schema: Customers, Products, Sales
- Foreign key relationships and constraints
- Atomic transactions with rollback support

### ✅ Interactive Dashboard
- Streamlit-based web interface
- KPIs: Total revenue, sales count, average ticket, unique customers
- Visualizations: Revenue trends, category distribution, top products, geographic analysis
- Dynamic filtering by date range, state, category, and product
- Real-time data quality metrics

### ✅ Advanced Features
- **Incremental Processing**: Process only new/changed data
- **Docker Support**: Containerized deployment with Docker Compose
- **Automated Scheduling**: Scheduled ETL runs using APScheduler
- **PDF Reports**: Generate data quality and sales reports
- **Excel Export**: Export dashboards to Excel format
- **Comprehensive Logging**: Structured logging to files and console
- **Unit Tests**: Full test coverage
- **Type Hints**: Full type annotations for IDE support

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the Repository**
   ```bash
   cd sales-etl-dashboard
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database**
   ```bash
   python etl_cli.py setup
   ```

5. **Run ETL Pipeline**
   ```bash
   python etl_cli.py run
   ```

6. **Launch Dashboard**
   ```bash
   streamlit run src/dashboard/app.py
   ```

## Docker Deployment

### Run with Docker Compose

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

Services:
- PostgreSQL: `localhost:5432`
- Dashboard: `http://localhost:8501`
- Logs: `./logs/`

## Project Structure

```
sales-etl-dashboard/
├── src/
│   ├── etl/              # ETL pipeline
│   ├── database/         # Database models and connections
│   ├── dashboard/        # Streamlit dashboard
│   └── utils/            # Utilities and helpers
├── tests/                # Unit tests
├── sql/                  # Database scripts
├── docker/               # Docker configuration
├── data/                 # Sample data files
├── config/               # Configuration settings
├── docs/                 # Documentation
├── etl_cli.py            # ETL command-line interface
├── scheduler.py          # ETL scheduler
└── requirements.txt      # Python dependencies
```

## Usage

### ETL Pipeline

**Setup Database**
```bash
python etl_cli.py setup
```

**Run ETL Pipeline**
```bash
python etl_cli.py run
```

Output:
- Processed records count
- Invalid records count
- Duplicates removed
- Processing time
- ETL run ID

### Dashboard

Access at `http://localhost:8501`

Features:
- KPI cards showing key metrics
- Interactive charts and visualizations
- Dynamic filtering
- Data export capabilities
- Quality metrics dashboard

### Scheduling

Run scheduled ETL jobs (2 AM daily):
```bash
python scheduler.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Dashboard
```
GET http://localhost:8501
```

## Data Models

### Customers Table
- `customer_id`: Primary key
- `name`: Customer name
- `email`: Email (unique constraint)
- `phone`: Phone number
- `state`: US state code
- `city`: City
- `zipcode`: Postal code

### Products Table
- `product_id`: Primary key
- `name`: Product name
- `category`: Product category
- `price`: Unit price
- `description`: Product description

### Sales Table
- `sale_id`: Primary key
- `customer_id`: Foreign key to customers
- `product_id`: Foreign key to products
- `quantity`: Units sold
- `unit_price`: Price per unit
- `total_value`: Total sale value
- `sale_date`: Date of sale
- `year`: Sale year (derived)
- `month`: Sale month (derived)
- `quarter`: Sale quarter (derived)

### Data Quality Metrics
- `metrics_id`: Primary key
- `etl_run_id`: ETL execution ID
- `processed_records`: Total records processed
- `invalid_records`: Records with validation errors
- `duplicates_removed`: Duplicate records detected
- `missing_values_percentage`: Percentage of missing data
- `processing_time_seconds`: ETL execution time
- `status`: Execution status (success/failed)

## Configuration

### Environment Variables (.env)

```properties
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_etl_db
DB_USER=postgres
DB_PASSWORD=postgres

# API
API_BASE_URL=https://api.example.com
API_TIMEOUT=30

# Paths
DATA_PATH=./data
REPORTS_PATH=./reports
LOGS_PATH=./logs

# Logging
LOG_LEVEL=INFO

# ETL Settings
BATCH_SIZE=1000
INCREMENTAL_PROCESSING=true

# Scheduler
SCHEDULE_INTERVAL=0 2 * * *  # 2 AM daily

# Dashboard
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0
```

## Testing

Run unit tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Performance Optimization

### Indexing
All frequently queried columns are indexed:
- Customer email, state
- Product category, name
- Sales date, customer, product
- Quality metrics ETL run ID, creation date

### Connection Pooling
- Min connections: 1
- Max connections: 10
- Automatic connection reuse

### Batch Processing
- Default batch size: 1000 records
- Configurable via `BATCH_SIZE` environment variable

### Query Optimization
- Use views for aggregated data
- Prepared statements for repeated queries
- Pagination for large result sets

## Monitoring

### Logs
- Location: `./logs/etl.log`
- Structured logging with timestamps
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)

### Reports
- Location: `./reports/`
- JSON format with execution metrics
- Timestamped filenames
- Complete error tracking

### Dashboard Metrics
- Real-time data quality dashboard
- Historical metrics tracking
- Performance trend analysis

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check PostgreSQL is running
- Verify connection credentials in `.env`
- Check firewall rules

**Data Extraction Fails**
- Verify source files exist and format is correct
- Check API endpoint availability
- Review logs for specific errors

**Dashboard Not Loading**
- Ensure database is accessible
- Check Streamlit configuration
- Review application logs

**Performance Issues**
- Monitor database connections
- Check disk space for logs
- Review indexing strategy

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review [API.md](docs/API.md)
3. Check application logs
4. Open an issue on GitHub
