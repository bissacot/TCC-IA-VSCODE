# Quick Start Guide

Get the Sales ETL Dashboard up and running in 5 minutes!

## Option 1: Local Installation (Fastest)

### 1. Setup Environment

```bash
# Clone/navigate to project
cd sales-etl-dashboard

# Copy environment file
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python etl_cli.py setup
```

This will:
- Create all database tables
- Create views for aggregated data
- Set up indexes

### 3. Run ETL Pipeline

```bash
python etl_cli.py run
```

Expected output:
```
ETL Pipeline Execution Completed Successfully
Status: success
Records Processed: 12
Records Loaded: 12
Duration: 2.45 seconds
```

### 4. Launch Dashboard

```bash
streamlit run src/dashboard/app.py
```

Open browser to: `http://localhost:8501`

## Option 2: Docker Deployment (Recommended for Production)

### 1. Start Services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 2. Verify Services

```bash
# Check running containers
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### 3. Access Dashboard

```
http://localhost:8501
```

### 4. Stop Services

```bash
docker-compose -f docker/docker-compose.yml down
```

## Dashboard Usage

### KPI Section
- **Total Revenue**: Sum of all sales
- **Number of Sales**: Count of transactions
- **Average Ticket Size**: Mean sale value
- **Unique Customers**: Distinct customer count

### Filtering
- **Date Range**: Filter by start and end date
- **States**: Select one or more states
- **Categories**: Filter by product category
- **Products**: Filter by specific products

### Visualizations
- Revenue trends over time
- Revenue distribution by category
- Top 10 best-selling products
- Sales by state (geographic distribution)
- Monthly revenue comparison

### Data Export
- View raw data in table format
- Download as CSV or Excel
- Copy to clipboard

## Scheduling ETL Runs

### Run Daily (2 AM)

```bash
python scheduler.py
```

This will:
- Check for scheduled jobs every minute
- Execute ETL pipeline at configured time
- Log all execution details
- Continue running indefinitely

### Stop Scheduler

```
Ctrl+C
```

## Sample Data

The project includes sample data:
- **Sales**: 12 transactions (data/sales.csv)
- **Customers**: 5 customers (data/customers.json)
- **Products**: API endpoint (configured in settings)

### Load Additional Data

1. Add CSV/JSON files to `data/` directory
2. Run ETL pipeline: `python etl_cli.py run`
3. Refresh dashboard to see new data

## File Locations

```
./logs/etl.log              # Application logs
./reports/etl_report_*.json # ETL execution reports
./data/                     # Source data files
```

## Verify Setup

Check if everything is working:

```bash
# 1. Check database connection
python -c "from config.settings import DB_URL; print(f'DB: {DB_URL}')"

# 2. Check logs
tail -f logs/etl.log

# 3. Verify database tables
# Connect to PostgreSQL and run:
# \dt  (list tables)
```

## Next Steps

1. **Customize Data Sources**
   - Update `data/sales.csv` with your data
   - Modify API endpoint in `config/settings.py`

2. **Modify Dashboard**
   - Edit `src/dashboard/app.py`
   - Add custom visualizations

3. **Configure Scheduling**
   - Edit `SCHEDULE_INTERVAL` in `.env`
   - Set your preferred run time

4. **Deploy to Production**
   - Use Docker Compose for containerized deployment
   - Set up reverse proxy (nginx/Apache)
   - Configure SSL/TLS certificates

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Port already in use | Change `DASHBOARD_PORT` in .env |
| Database connection failed | Check PostgreSQL is running |
| No data in dashboard | Run `python etl_cli.py run` |
| Scheduler not running | Use `python scheduler.py` |

## Help & Support

- 📖 Full documentation: See [README.md](README.md)
- 🐛 Issues: Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 📝 API Guide: See [API.md](docs/API.md)

## Commands Quick Reference

```bash
# Setup
python etl_cli.py setup                    # Initialize database
python etl_cli.py setup --drop             # Drop and recreate tables

# ETL
python etl_cli.py run                      # Run ETL pipeline

# Dashboard
streamlit run src/dashboard/app.py         # Start dashboard

# Scheduling
python scheduler.py                        # Start ETL scheduler

# Testing
pytest tests/                              # Run unit tests
pytest tests/ --cov=src                    # With coverage

# Docker
docker-compose -f docker/docker-compose.yml up -d      # Start
docker-compose -f docker/docker-compose.yml down       # Stop
docker-compose -f docker/docker-compose.yml logs -f    # Logs
```

Enjoy using the Sales ETL Dashboard! 🚀
