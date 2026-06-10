# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (or Docker)
- Git

### Step 1: Clone & Setup (2 min)

```bash
# Clone repository
git clone <repo-url>
cd pipeline-etl-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env (or use defaults)
# nano .env
```

### Step 3: Start Database (1 min)

**Option A: Using Docker (Recommended)**

```bash
docker run -d \
  --name postgres-sales \
  -e POSTGRES_PASSWORD=etl_password \
  -e POSTGRES_USER=etl_user \
  -e POSTGRES_DB=sales_db \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database
sleep 5  # Wait for DB to start
psql -h localhost -U etl_user -d sales_db -f database/init.sql
```

**Option B: Using Docker Compose (Easiest)**

```bash
docker-compose up -d postgres
docker-compose exec postgres psql -U etl_user -d sales_db -f /docker-entrypoint-initdb.d/01-init.sql
```

### Step 4: Run ETL Pipeline (1 min)

```bash
python -m src.etl.pipeline
```

Expected output:
```
[INFO] Starting ETL Pipeline Execution
[INFO] Extracted 100 records from CSV
[INFO] Transformed 100 sales records
[INFO] Loaded 100 sales records
[INFO] ETL Pipeline Completed Successfully!
```

## View Dashboard (5 seconds)

```bash
streamlit run src/dashboard/app.py
```

Access at: **http://localhost:8501**

## 🎉 You're Done!

The dashboard is now live with sample data. You should see:
- ✅ KPI metrics (Revenue, Sales, Customers)
- ✅ Revenue trend chart
- ✅ Product category breakdown
- ✅ Top 10 products
- ✅ State distribution
- ✅ Data quality report

---

## What's Next?

### 1. **Replace Sample Data**

Prepare your own CSV and JSON files:

```
data/
├── sales_data.csv          # Your sales data
└── customers.json          # Your customer data
```

Then run ETL again:
```bash
python -m src.etl.pipeline
```

### 2. **Schedule Daily ETL**

Using Cron (Linux/macOS):
```bash
# Edit crontab
crontab -e

# Add daily ETL at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/python -m src.etl.pipeline
```

Or using Windows Task Scheduler:
1. Task Scheduler → New Task
2. Trigger: Daily at 2 AM
3. Action: Run Python script

### 3. **Deploy to Docker**

```bash
# Build and start all services
docker-compose up -d

# Services will be available:
# Dashboard: http://localhost:8501
# PostgreSQL: localhost:5432
# pgAdmin: http://localhost:5050
```

### 4. **Run Tests**

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### 5. **Explore Documentation**

- [Architecture Guide](docs/ARCHITECTURE.md)
- [ETL Pipeline](docs/ETL.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Dashboard Guide](docs/DASHBOARD.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## Common Commands

```bash
# Run ETL
make etl-run

# Start dashboard
make dashboard-run

# Run tests
make test

# Check code quality
make lint

# Start Docker services
make docker-up

# Stop Docker services
make docker-down

# View help
make help
```

---

## Troubleshooting

### "Database connection refused"
```bash
# Check if PostgreSQL is running
psql -h localhost -U etl_user -d sales_db

# If using Docker, check container
docker ps | grep postgres
```

### "No such file or directory: 'sales_data.csv'"
```bash
# Ensure data files exist
ls -la data/

# If missing, copy sample files
cp database/samples/*.csv data/
cp database/samples/*.json data/
```

### "Port 8501 already in use"
```bash
# Kill process on port 8501
# macOS/Linux
lsof -i :8501 | tail -1 | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.9 | 3.11+ |
| RAM | 1GB | 4GB |
| Storage | 2GB | 10GB |
| PostgreSQL | 12 | 15+ |

---

## Architecture at a Glance

```
Data Sources (CSV, JSON, API)
           ↓
    ETL Pipeline
    - Extract
    - Transform
    - Load
           ↓
   PostgreSQL Database
           ↓
   Streamlit Dashboard
```

---

## Sample Data Included

✅ 30 sales transactions
✅ 21 customers across Brazil
✅ 6 products
✅ Date range: January - March 2024

---

## Features Overview

| Feature | Status |
|---------|--------|
| CSV/JSON/API extraction | ✅ Complete |
| Data transformation & validation | ✅ Complete |
| PostgreSQL integration | ✅ Complete |
| Streamlit dashboard | ✅ Complete |
| KPI metrics | ✅ Complete |
| Interactive visualizations | ✅ Complete |
| Data quality reports | ✅ Complete |
| Incremental loading | ✅ Complete |
| Docker support | ✅ Complete |
| Automated testing | ✅ Complete |
| PDF export | 🔄 Planned |
| Excel export | 🔄 Planned |
| Advanced scheduling | 🔄 Planned |

---

## Performance Metrics

| Operation | Time |
|-----------|------|
| Extract data | ~2s |
| Transform data | ~5s |
| Load to DB | ~10s |
| Dashboard query | ~1s (cached) |
| Total ETL | ~20-30s |

---

## Next Steps

1. ✅ **Congratulations!** System is running
2. 📊 **Explore Dashboard**: Interact with visualizations
3. 📁 **Add Your Data**: Replace sample data with real data
4. ⏰ **Schedule ETL**: Set up automated runs
5. 🚀 **Scale Up**: Deploy to production

---

## Getting Help

### Documentation
- 📖 [Full Documentation](README.md)
- 🏗️ [Architecture](docs/ARCHITECTURE.md)
- 🔄 [ETL Guide](docs/ETL.md)
- 📊 [Dashboard](docs/DASHBOARD.md)

### Community
- 🐛 [Report Issues](../../issues)
- 💬 [Discussions](../../discussions)
- 📝 [Wiki](../../wiki)

---

**Happy analyzing! 📈**
