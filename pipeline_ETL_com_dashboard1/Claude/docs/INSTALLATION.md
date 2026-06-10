# Installation Guide

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (any distribution)
- **Python**: 3.9 or higher
- **RAM**: 1 GB minimum (2 GB recommended)
- **Storage**: 5 GB free space
- **Database**: PostgreSQL 12+ (or use Docker)

### Recommended Requirements
- **Python**: 3.11 or higher
- **RAM**: 4 GB or more
- **Storage**: 10 GB free space
- **Docker**: 20.10+ (for containerized deployment)

## Installation Methods

### Method 1: Local Development Setup (Recommended for Development)

#### Step 1: Clone Repository

```bash
git clone <repository-url>
cd pipeline-etl-dashboard
```

#### Step 2: Create Python Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Step 4: PostgreSQL Setup

**Option A: Using Docker (Easiest)**

```bash
docker run -d \
  --name sales_db \
  -e POSTGRES_DB=sales_db \
  -e POSTGRES_USER=etl_user \
  -e POSTGRES_PASSWORD=etl_password \
  -p 5432:5432 \
  postgres:15-alpine
```

Wait 5 seconds for database to start, then initialize:

```bash
psql -h localhost -U etl_user -d sales_db -f database/init.sql
```

**Option B: Local PostgreSQL Installation**

**macOS (Homebrew)**:
```bash
brew install postgresql
brew services start postgresql
createdb -U postgres sales_db
psql -U postgres -d sales_db -f database/init.sql
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb sales_db
sudo -u postgres psql -d sales_db -f database/init.sql
```

**Windows (MSI Installer)**:
1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer, remember password for postgres user
3. Open Command Prompt and run:
```bash
psql -U postgres
CREATE DATABASE sales_db;
\q
psql -U postgres -d sales_db -f database/init.sql
```

#### Step 5: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
# Update database connection if different from defaults
```

#### Step 6: Verify Installation

```bash
# Test database connection
python -c "from src.database.models import DatabaseConnection; DatabaseConnection.get_engine().connect()"

# Run tests
pytest tests/ -v --tb=short

# Run ETL pipeline
python -m src.etl.pipeline

# Start dashboard
streamlit run src/dashboard/app.py
```

---

### Method 2: Docker Compose Setup (Recommended for Production)

#### Step 1: Prerequisites

```bash
# Check Docker version
docker --version  # Should be 20.10+

# Check Docker Compose version
docker-compose --version  # Should be 1.29+
```

#### Step 2: Clone Repository

```bash
git clone <repository-url>
cd pipeline-etl-dashboard
```

#### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
```

#### Step 4: Build and Start Services

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### Step 5: Verify Installation

```bash
# Check logs
docker-compose logs -f

# Test dashboard
open http://localhost:8501  # macOS
xdg-open http://localhost:8501  # Linux
start http://localhost:8501  # Windows

# Test pgAdmin
open http://localhost:5050  # macOS
```

---

### Method 3: Kubernetes Deployment

#### Step 1: Prerequisites

```bash
# Check kubectl
kubectl version

# Check Helm
helm version
```

#### Step 2: Create Namespace

```bash
kubectl create namespace etl-pipeline
```

#### Step 3: Deploy PostgreSQL

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --set auth.username=etl_user \
  --set auth.password=etl_password \
  --set auth.database=sales_db \
  -n etl-pipeline
```

#### Step 4: Deploy Application

```bash
# Create ConfigMap and Secrets
kubectl apply -f k8s/configmap.yaml -n etl-pipeline
kubectl apply -f k8s/secrets.yaml -n etl-pipeline

# Deploy services
kubectl apply -f k8s/deployment.yaml -n etl-pipeline
kubectl apply -f k8s/service.yaml -n etl-pipeline

# Check status
kubectl get pods -n etl-pipeline
kubectl get svc -n etl-pipeline
```

#### Step 5: Access Application

```bash
# Port forward to dashboard
kubectl port-forward svc/dashboard 8501:8501 -n etl-pipeline

# Access at http://localhost:8501
```

---

## Verification Checklist

After installation, verify everything works:

- [ ] Python virtual environment created and activated
- [ ] Dependencies installed (pip list shows streamlit, pandas, sqlalchemy, etc.)
- [ ] PostgreSQL running and accessible
- [ ] Database tables created
- [ ] `.env` file configured correctly
- [ ] Sample data files exist in `data/` directory
- [ ] ETL pipeline executes successfully
- [ ] Dashboard loads at http://localhost:8501
- [ ] Tests pass (pytest tests/ -v)
- [ ] All services running in Docker (if using Docker Compose)

---

## Troubleshooting Installation Issues

### Python Issues

**Problem**: `python: command not found`
```bash
# Solution: Use python3
python3 --version
python3 -m venv venv
```

**Problem**: `ModuleNotFoundError` when importing packages
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### PostgreSQL Issues

**Problem**: `psycopg2.OperationalError: could not connect to server`
```bash
# Solution: Check PostgreSQL is running
# macOS
brew services list

# Linux
sudo systemctl status postgresql

# Windows - Check Services in Task Manager
```

**Problem**: `FATAL: password authentication failed`
```bash
# Solution: Check credentials in .env
# Default: user=etl_user, password=etl_password

# Reset PostgreSQL password (macOS)
psql -U postgres
ALTER USER etl_user WITH PASSWORD 'new_password';
```

### Docker Issues

**Problem**: `permission denied while trying to connect to Docker daemon`
```bash
# Solution: Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
docker ps
```

**Problem**: `Port 5432 already in use`
```bash
# Solution: Find and stop existing container
docker ps | grep postgres
docker stop <container-id>
```

### Memory Issues

**Problem**: `MemoryError` during ETL
```bash
# Solution: Reduce batch size in .env
BATCH_SIZE=500  # Reduced from 1000
```

---

## Post-Installation

### 1. Load Sample Data

Sample data is included in `data/`:
- `sales_data.csv`: 30 sales transactions
- `customers.json`: 21 customers
- Products from API (JSONPlaceholder)

Run ETL to load:
```bash
python -m src.etl.pipeline
```

### 2. Access Dashboard

```bash
streamlit run src/dashboard/app.py
```

Dashboard available at: **http://localhost:8501**

### 3. Schedule ETL Runs

**Linux/macOS Cron**:
```bash
crontab -e
# Add: 0 2 * * * cd /path/to/project && /path/to/venv/bin/python -m src.etl.pipeline
```

**Windows Task Scheduler**:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily 2 AM
4. Set action to run Python script

### 4. Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### 5. Monitor Logs

```bash
tail -f logs/etl.log
tail -f logs/errors.log
```

---

## Uninstall

### Local Setup

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir venv   # Windows

# Remove database (optional)
psql -U postgres -c "DROP DATABASE sales_db;"
```

### Docker Setup

```bash
# Stop and remove containers
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all
```

---

## Getting Help

If you encounter issues:

1. Check [Troubleshooting Guide](docs/DEPLOYMENT.md#troubleshooting)
2. Review [Quick Start](docs/QUICKSTART.md)
3. Check logs in `logs/` directory
4. Create GitHub issue with:
   - OS and Python version
   - Error message
   - Steps to reproduce
   - `pip list` output

---

## Next Steps

After successful installation:

1. ✅ Read [Quick Start Guide](docs/QUICKSTART.md)
2. 📖 Review [Architecture Guide](docs/ARCHITECTURE.md)
3. 📊 Explore [Dashboard Guide](docs/DASHBOARD.md)
4. 🔄 Learn [ETL Pipeline](docs/ETL.md)
5. 💾 Review [Database Schema](docs/DATABASE_SCHEMA.md)

---

**Happy analyzing! 📈**
