# Deployment Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- Docker & Docker Compose (for containerized deployment)
- 2GB minimum RAM
- 5GB minimum disk space

## Local Deployment

### Step 1: Environment Setup

```bash
# Create project directory
mkdir -p /opt/etl_dashboard
cd /opt/etl_dashboard

# Clone or download project
git clone <repository-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Database Setup

```bash
# Create database
createdb -U postgres sales_db

# Initialize tables and schema
psql -U postgres -d sales_db -f database/init.sql

# Load sample data (optional)
psql -U postgres -d sales_db -f database/sample_data.sql
```

### Step 4: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Key configuration:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
API_BASE_URL=https://your-api.com
```

### Step 5: Data Preparation

Create data files in `data/input/`:

**sales.csv:**
```csv
sale_id,customer_id,product_id,quantity,unit_price,total_value,sale_date
SALE001,CUST001,PROD001,2,100.00,200.00,2024-01-15T10:30:00
```

**customers.json:**
```json
[
  {
    "customer_id": "CUST001",
    "name": "John Smith",
    "email": "john@example.com",
    "state": "NY",
    "country": "USA"
  }
]
```

### Step 6: Run ETL Pipeline

```bash
# First time run
python run_etl.py

# Verify logs
tail -f logs/etl_pipeline.log
```

### Step 7: Launch Dashboard

```bash
# In new terminal
streamlit run src/dashboard/app.py
```

Access at: `http://localhost:8501`

## Docker Deployment

### Step 1: Prepare Environment

```bash
cd /opt/etl_dashboard
cp .env.example .env
```

### Step 2: Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build postgres
docker-compose build etl_pipeline
docker-compose build streamlit
```

### Step 3: Start Services

```bash
# Start all in background
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f etl_pipeline
docker-compose logs -f streamlit
```

### Step 4: Verify Deployment

```bash
# Check running containers
docker-compose ps

# Test database
docker-compose exec postgres psql -U postgres -d sales_db -c "SELECT * FROM customers LIMIT 1;"

# Check application health
curl http://localhost:8501
```

### Step 5: Run ETL

```bash
# Once in container
docker-compose run etl_pipeline python run_etl.py

# Or exec into running container
docker-compose exec etl_pipeline python run_etl.py
```

### Step 6: Access Dashboard

Open browser: `http://localhost:8501`

## Production Deployment

### 1. Server Preparation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip postgresql postgresql-contrib

# Enable PostgreSQL service
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2. Secure Configuration

```bash
# Create application user
sudo useradd -m -s /bin/bash etl_app
sudo mkdir -p /opt/etl_dashboard
sudo chown -R etl_app:etl_app /opt/etl_dashboard

# Set permissions
sudo chmod 700 /opt/etl_dashboard
```

### 3. PostgreSQL Setup

```bash
# As postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE sales_db;
CREATE USER etl_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE sales_db TO etl_user;
\q

# Initialize schema
sudo -u postgres psql -d sales_db -f /opt/etl_dashboard/database/init.sql
```

### 4. Application Setup

```bash
sudo su - etl_app
cd /opt/etl_dashboard

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update .env with secure values
nano .env
```

### 5. Systemd Service

Create `/etc/systemd/system/etl-pipeline.service`:

```ini
[Unit]
Description=ETL Pipeline Service
After=postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=etl_app
WorkingDirectory=/opt/etl_dashboard
ExecStart=/opt/etl_dashboard/venv/bin/python run_etl.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/etl-dashboard.service`:

```ini
[Unit]
Description=ETL Dashboard Service
After=etl-pipeline.service
Wants=etl-pipeline.service

[Service]
Type=simple
User=etl_app
WorkingDirectory=/opt/etl_dashboard
ExecStart=/opt/etl_dashboard/venv/bin/streamlit run src/dashboard/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable etl-pipeline.service etl-dashboard.service
sudo systemctl start etl-pipeline.service etl-dashboard.service
```

### 6. Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt-get install -y nginx
```

Configure `/etc/nginx/sites-available/etl-dashboard`:

```nginx
upstream streamlit {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://streamlit;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/etl-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL/TLS Setup

Using Let's Encrypt:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 8. Monitoring & Logging

Check service status:
```bash
sudo systemctl status etl-pipeline.service
sudo systemctl status etl-dashboard.service

# View logs
sudo journalctl -u etl-pipeline.service -f
sudo journalctl -u etl-dashboard.service -f
```

## Database Backup Strategy

### Automated Backup

Create backup script `/opt/etl_dashboard/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/etl_dashboard/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="sales_db_${DATE}.sql.gz"

mkdir -p $BACKUP_DIR

pg_dump -U postgres sales_db | gzip > $BACKUP_DIR/$FILENAME

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/etl_dashboard/backup.sh
```

### Restore Backup

```bash
gunzip < backups/sales_db_20240115_020000.sql.gz | psql -U postgres sales_db
```

## Performance Tuning

### PostgreSQL Configuration

Edit `/etc/postgresql/15/main/postgresql.conf`:

```ini
# Memory
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 64MB

# Connections
max_connections = 200

# WAL
wal_buffers = 16MB

# Checkpoints
checkpoint_completion_target = 0.9
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Application Optimization

In `.env`:
```
BATCH_SIZE=5000
POOL_SIZE=10
```

## Monitoring

### Resource Usage

```bash
# CPU and Memory
top

# Disk Space
df -h

# Database Size
psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('sales_db'));"
```

### Logs

Monitor for errors:
```bash
tail -f logs/etl_pipeline.log
tail -f logs/etl_main.log
```

## Troubleshooting

### Database Connection Refused

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials
psql -U postgres -h localhost
```

### Out of Memory

```bash
# Check memory usage
free -h

# Reduce batch size in .env
BATCH_SIZE=1000
```

### Dashboard Not Accessible

```bash
# Check service status
sudo systemctl status etl-dashboard.service

# Check port
sudo netstat -tlnp | grep 8501
```

## Security Checklist

- [ ] Database passwords set to strong values
- [ ] PostgreSQL configured for local connections only
- [ ] Firewall rules configured
- [ ] SSL/TLS enabled for Nginx
- [ ] Regular backups configured
- [ ] Log rotation configured
- [ ] Non-root service user created
- [ ] File permissions properly set
- [ ] API credentials in environment variables only
- [ ] Regular security updates applied

## Rollback Procedure

If deployment fails:

```bash
# Stop services
docker-compose down

# Restore database backup
gunzip < backups/sales_db_backup.sql.gz | psql -U postgres sales_db

# Start fresh
docker-compose up -d
```

---

For additional support, consult logs and documentation files.
