# 🚀 STARTUP COMMANDS

Quick reference for all important commands.

## 📋 Installation & Setup

```bash
# 1. Navigate to project
cd sales-etl-dashboard

# 2. Copy environment file
cp .env.example .env

# 3. Edit environment (Windows: use notepad or editor)
# Update DB_PASSWORD and other credentials

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Initialize database
python etl_cli.py setup

# Verify setup
python -c "from config.settings import DB_URL; print(f'Database configured: {DB_URL}')"
```

## 🔄 Running ETL Pipeline

```bash
# Run complete ETL pipeline
python etl_cli.py run

# Output shows:
# - Records processed
# - Invalid records
# - Duplicates removed
# - Records loaded
# - Processing time

# Check results
tail -f logs/etl.log
cat reports/etl_report_*.json | python -m json.tool
```

## 📊 Starting Dashboard

```bash
# Launch Streamlit dashboard
streamlit run src/dashboard/app.py

# Access at: http://localhost:8501

# To change port:
streamlit run src/dashboard/app.py --server.port=8502

# Debug mode:
streamlit run src/dashboard/app.py --logger.level=debug
```

## ⏰ Running Scheduler

```bash
# Start ETL scheduler (runs daily at 2 AM)
python scheduler.py

# Stop scheduler: Ctrl+C

# View scheduled logs
tail -f logs/etl.log | grep "Scheduled"
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_extractor.py -v

# Run specific test
pytest tests/unit/test_extractor.py::TestCSVExtractor::test_extract_valid_csv -v
```

## 🐳 Docker Commands

```bash
# Build containers
docker-compose -f docker/docker-compose.yml build

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View services
docker-compose -f docker/docker-compose.yml ps

# View logs (all services)
docker-compose -f docker/docker-compose.yml logs -f

# View specific service logs
docker-compose -f docker/docker-compose.yml logs -f etl
docker-compose -f docker/docker-compose.yml logs -f postgres
docker-compose -f docker/docker-compose.yml logs -f dashboard

# Stop services
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes
docker-compose -f docker/docker-compose.yml down -v

# Rebuild without cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

## 🗄️ Database Commands

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d sales_etl_db

# Within psql:
\dt                              # List tables
\dv                              # List views
SELECT COUNT(*) FROM customers;  # Count records
SELECT * FROM v_monthly_sales;   # View monthly summary
\q                               # Quit

# Backup database
pg_dump -h localhost -U postgres sales_etl_db > backup.sql

# Restore database
psql -h localhost -U postgres sales_etl_db < backup.sql
```

## 📝 Logging & Debugging

```bash
# View live logs
tail -f logs/etl.log

# View last 50 lines
tail -50 logs/etl.log

# Search for errors
grep -i "error" logs/etl.log

# Search for specific date/time
grep "2024-01-15" logs/etl.log

# Full log stream
tail -f logs/etl.log | grep -E "ERROR|WARNING"

# View reports
ls -lart reports/
cat reports/etl_report_*.json | python -m json.tool
```

## 🔧 Configuration

```bash
# Edit environment variables
nano .env          # Linux/macOS
notepad .env       # Windows

# Key variables:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=sales_etl_db
# DB_USER=postgres
# DB_PASSWORD=postgres
# LOG_LEVEL=INFO
# API_BASE_URL=https://api.example.com
```

## 🔄 Database Reset

```bash
# Drop all tables (WARNING: deletes data)
python etl_cli.py setup --drop

# Reinitialize
python etl_cli.py setup

# Load sample data
psql -h localhost -U postgres sales_etl_db < sql/sample_data.sql
```

## 📦 Dependency Management

```bash
# List installed packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated

# Check for security vulnerabilities
pip install safety
safety check

# Export current environment
pip freeze > requirements-current.txt
```

## 🌐 Network & Ports

```bash
# Check if ports are available
lsof -i :5432    # PostgreSQL
lsof -i :8501    # Streamlit
lsof -i :80      # Nginx (if deployed)
lsof -i :443     # HTTPS (if deployed)

# Kill process on port
kill -9 <PID>

# Linux firewall
sudo ufw allow 5432
sudo ufw allow 8501
sudo ufw allow 80
sudo ufw allow 443
```

## 📊 Monitoring

```bash
# System resource usage
top              # CPU and memory
df -h            # Disk space
du -sh .         # Current directory size

# Database size
psql -U postgres -d sales_etl_db -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
  FROM pg_tables 
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Process monitoring
ps aux | grep python
ps aux | grep postgres
ps aux | grep streamlit
```

## 🚨 Troubleshooting

```bash
# Check database connection
python -c "from src.database import DatabaseConnection; DatabaseConnection.initialize()"

# Test extract
python -c "from src.etl.extractor import CSVExtractor; from pathlib import Path; 
CSVExtractor(Path('data/sales.csv')).extract()"

# Test validator
python -c "from src.utils import DataValidator; 
print(DataValidator.validate_email('test@example.com'))"

# Full debug run
export LOG_LEVEL=DEBUG
python etl_cli.py run

# View Python version
python --version

# Check imports
python -c "import pandas, sqlalchemy, streamlit, plotly; print('All imports OK')"
```

## 🔐 Backup & Restore

```bash
# Full backup
pg_dump -h localhost -U postgres sales_etl_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific table
pg_dump -h localhost -U postgres -t sales sales_etl_db > sales_backup.sql

# Restore from backup
psql -h localhost -U postgres sales_etl_db < backup_20240115_120000.sql

# Backup Docker volumes
docker run --rm -v sales_etl_dashboard_postgres_data:/data \
  -v $(pwd):/backup ubuntu tar czf /backup/db_backup.tar.gz /data
```

## 📈 Performance Tuning

```bash
# Analyze query performance
psql -U postgres -d sales_etl_db
EXPLAIN ANALYZE SELECT * FROM sales WHERE sale_date > '2024-01-01';

# Reindex tables
REINDEX DATABASE sales_etl_db;

# Vacuum and analyze
VACUUM ANALYZE;

# Check index usage
SELECT * FROM pg_stat_user_indexes;
```

## 🔄 Common Workflows

### Complete Setup from Scratch
```bash
cd sales-etl-dashboard
cp .env.example .env
# Edit .env with credentials
pip install -r requirements.txt
python etl_cli.py setup
python etl_cli.py run
streamlit run src/dashboard/app.py
```

### Docker Development
```bash
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d
# Access dashboard at http://localhost:8501
docker-compose -f docker/docker-compose.yml logs -f
```

### Production Deployment
```bash
# See DEPLOYMENT.md for detailed instructions
# Quick summary:
sudo mkdir -p /opt/sales-etl-dashboard
# Copy files
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python etl_cli.py setup
# Setup systemd services (see DEPLOYMENT.md)
# Setup Nginx reverse proxy (see DEPLOYMENT.md)
```

### Testing Workflow
```bash
# Run tests
pytest tests/ -v --cov=src

# Add new test
# 1. Create test file in tests/unit/
# 2. Write test functions
# 3. Run: pytest tests/unit/test_new.py -v

# Check coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

## 📞 Getting Help

```bash
# View project documentation
open README.md              # Project overview
open QUICKSTART.md          # Quick start guide
open docs/ARCHITECTURE.md   # System design
open docs/TROUBLESHOOTING.md # Issues & solutions

# CLI help
python etl_cli.py --help

# Check logs for errors
grep -i "error" logs/etl.log
tail -f logs/etl.log

# Python help
python -c "from src.etl import ETLPipeline; help(ETLPipeline.run)"
```

## 🎯 Essential Commands Summary

```bash
# Setup
python etl_cli.py setup

# ETL
python etl_cli.py run

# Dashboard
streamlit run src/dashboard/app.py

# Scheduler
python scheduler.py

# Tests
pytest tests/ -v

# Docker
docker-compose -f docker/docker-compose.yml up -d

# Database
psql -h localhost -U postgres -d sales_etl_db

# Logs
tail -f logs/etl.log

# Configuration
nano .env
```

---

**Quick Tips**:
- All commands assume you're in project root
- Check .env for database credentials
- View logs when commands fail: `tail -f logs/etl.log`
- Use `--help` flag for more command options
- Docker commands require Docker/Docker Compose installed
- Database commands require PostgreSQL installed locally

**For More Help**:
- See [QUICKSTART.md](QUICKSTART.md) for setup
- See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production
- See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for issues
