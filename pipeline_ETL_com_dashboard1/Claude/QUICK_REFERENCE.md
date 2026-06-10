# Quick Reference Guide

## 🚀 Quick Commands

### Setup (First Time)
```bash
# 1. Clone and navigate
git clone <repo-url>
cd pipeline-etl-dashboard

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env if needed

# 5. Start database (Docker)
docker run -d --name postgres-sales -e POSTGRES_PASSWORD=etl_password \
  -e POSTGRES_USER=etl_user -e POSTGRES_DB=sales_db -p 5432:5432 \
  postgres:15-alpine

# 6. Initialize database
psql -h localhost -U etl_user -d sales_db -f database/init.sql

# 7. Run ETL pipeline
python -m src.etl.pipeline

# 8. Start dashboard
streamlit run src/dashboard/app.py
```

### Common Development Commands
```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src tests

# Lint code
flake8 src tests

# Type checking
mypy src

# Run ETL
python -m src.etl.pipeline

# Start dashboard
streamlit run src/dashboard/app.py

# Docker commands
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f        # View logs
```

### Makefile Commands
```bash
make help              # Show all commands
make install           # Install dependencies
make test              # Run tests
make test-cov          # Run tests with coverage
make lint              # Lint code
make format            # Format code
make docker-build      # Build Docker images
make docker-up         # Start Docker
make docker-down       # Stop Docker
make etl-run           # Run ETL
make dashboard-run     # Run dashboard
```

---

## 📊 File Organization

### Core Source Code
```
src/
├── config.py              # Configuration
├── logger.py              # Logging setup
├── etl/
│   ├── extractors.py      # Extract data
│   ├── transformers.py    # Transform data
│   ├── loaders.py         # Load data
│   └── pipeline.py        # Orchestrate
├── database/
│   ├── models.py          # ORM models
│   └── repository.py      # Data access
├── dashboard/
│   └── app.py             # Streamlit app
└── utils/
    └── __init__.py
```

### Documentation
```
docs/
├── QUICKSTART.md          # 5-min setup
├── INSTALLATION.md        # Full setup
├── ARCHITECTURE.md        # Design
├── DATABASE_SCHEMA.md     # Database
├── ETL.md                 # Pipeline
├── DASHBOARD.md           # UI guide
└── DEPLOYMENT.md          # Deploy
```

### Configuration & Tests
```
├── requirements.txt       # Dependencies
├── .env.example          # Env template
├── pytest.ini            # Test config
├── conftest.py           # Test fixtures
├── Makefile              # Commands
└── docker-compose.yml    # Docker setup
```

---

## 🔧 Configuration Reference

### Environment Variables (`.env`)

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=etl_user
DB_PASSWORD=etl_password
DB_NAME=sales_db

# Environment
ENVIRONMENT=development
DEBUG=False
LOG_LEVEL=INFO

# ETL
BATCH_SIZE=1000
INCREMENTAL_LOAD=True

# API
PRODUCT_API_URL=https://jsonplaceholder.typicode.com/products
API_TIMEOUT=30
API_RETRIES=3

# Dashboard
DASHBOARD_PORT=8501
CACHE_TTL_SECONDS=3600
```

---

## 📈 Database Access

### Using Repositories

```python
from src.database.models import DatabaseConnection
from src.database.repository import SaleRepository

session = DatabaseConnection.get_session()
repo = SaleRepository(session)

# Query data
total_revenue = repo.get_total_revenue()
sales_by_month = repo.get_revenue_by_month()
top_products = repo.get_top_products(10)
```

### Direct SQL

```bash
psql -h localhost -U etl_user -d sales_db

# View data
SELECT * FROM sales LIMIT 10;
SELECT SUM(total_value) FROM sales;
SELECT category, SUM(quantity) FROM sales 
  JOIN products ON sales.product_id = products.product_id
  GROUP BY category;
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_etl_pipeline.py::TestSalesTransformer::test_validate_record_valid -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Markers
```bash
pytest -m unit         # Run unit tests
pytest -m integration  # Run integration tests
pytest -m slow         # Run slow tests
```

---

## 🐳 Docker Operations

### Build Services
```bash
docker-compose build
```

### Start Services
```bash
docker-compose up -d
# View logs: docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Access Services
```
PostgreSQL:    localhost:5432
pgAdmin:       http://localhost:5050
Dashboard:     http://localhost:8501
```

---

## 📋 Key Features

### ✅ ETL Pipeline
- CSV, JSON, and API extraction
- Validation and transformation
- Duplicate detection
- Quality reporting
- Incremental processing

### ✅ Dashboard
- KPI metrics
- Interactive charts
- Multi-select filters
- Date range filtering
- Real-time caching

### ✅ Database
- Star schema design
- Dimension tables (customers, products)
- Fact table (sales)
- Quality tracking
- Incremental log

### ✅ DevOps
- Docker containerization
- Docker Compose orchestration
- Kubernetes ready
- Health checks
- Environment configuration

### ✅ Code Quality
- Type hints
- Comprehensive logging
- Exception handling
- Unit tests
- Clean code principles

---

## 🐛 Troubleshooting Quick Tips

### Database Connection Failed
```bash
# Check PostgreSQL is running
psql -h localhost -U etl_user -d sales_db -c "SELECT 1"

# Or check Docker container
docker ps | grep postgres
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8501        # Dashboard
lsof -i :5432        # Database

# Kill process
kill -9 <PID>
```

### ModuleNotFoundError
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### No Data in Dashboard
```bash
# Check ETL ran successfully
python -m src.etl.pipeline

# Verify data in database
psql -h localhost -U etl_user -d sales_db -c "SELECT COUNT(*) FROM sales"

# Refresh dashboard cache
# Click "🔄 Refresh Data" in Streamlit
```

---

## 📞 Key Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Quick Start | docs/QUICKSTART.md | 5-minute setup |
| Installation | docs/INSTALLATION.md | Detailed setup |
| Architecture | docs/ARCHITECTURE.md | System design |
| Database Schema | docs/DATABASE_SCHEMA.md | DB structure |
| ETL Guide | docs/ETL.md | Pipeline details |
| Dashboard Guide | docs/DASHBOARD.md | UI guide |
| Deployment | docs/DEPLOYMENT.md | Production deploy |
| Contributing | CONTRIBUTING.md | Dev guidelines |

---

## 🎯 Project Timeline

### Phase 1: Setup (Day 1)
- [ ] Clone repository
- [ ] Set up virtual environment
- [ ] Configure .env file
- [ ] Start database

### Phase 2: Testing (Day 1)
- [ ] Run ETL pipeline
- [ ] Access dashboard
- [ ] Explore sample data
- [ ] Run tests

### Phase 3: Customization (Days 2-3)
- [ ] Replace sample data
- [ ] Customize transformers
- [ ] Modify dashboard
- [ ] Add custom queries

### Phase 4: Deployment (Day 4)
- [ ] Set up Docker
- [ ] Configure scheduling
- [ ] Deploy to production
- [ ] Monitor execution

---

## 💡 Tips & Best Practices

### Performance
- Use date filters to limit data
- Increase BATCH_SIZE for faster loads
- Enable caching in dashboard
- Optimize database queries

### Maintenance
- Review quality reports weekly
- Update dependencies monthly
- Monitor disk usage
- Backup database regularly

### Security
- Change default passwords
- Use strong .env credentials
- Enable SSL/TLS for production
- Restrict database access

### Development
- Follow PEP 8 style guide
- Add type hints to new code
- Write unit tests
- Update documentation

---

## 📖 Learn More

- **Python Best Practices**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **SQLAlchemy Docs**: [sqlalchemy.org](https://www.sqlalchemy.org)
- **Streamlit Docs**: [streamlit.io](https://streamlit.io)
- **PostgreSQL Docs**: [postgresql.org](https://www.postgresql.org/docs)
- **Docker Docs**: [docker.com](https://docs.docker.com)

---

## ⚡ Emergency Commands

```bash
# Reset everything
docker-compose down -v
rm -rf venv logs
git clean -fdx

# Fresh start
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker-compose up -d
python -m src.etl.pipeline
streamlit run src/dashboard/app.py
```

---

**Happy analyzing! 📈**
