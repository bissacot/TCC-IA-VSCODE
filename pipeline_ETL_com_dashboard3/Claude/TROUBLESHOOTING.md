# Troubleshooting Guide

## Common Issues and Solutions

## 1. Database Issues

### Error: "Connection refused"

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Check listening port
sudo netstat -tlnp | grep 5432

# Verify credentials in .env
echo $DB_PASSWORD

# Test connection directly
psql -h localhost -U postgres -d sales_db
```

### Error: "database does not exist"

**Symptoms:**
```
psycopg2.OperationalError: database "sales_db" does not exist
```

**Solutions:**
```bash
# Create database
createdb -U postgres sales_db

# Initialize schema
psql -U postgres -d sales_db -f database/init.sql

# Verify tables exist
psql -U postgres -d sales_db -c "\dt"
```

### Error: "FATAL: role does not exist"

**Symptoms:**
```
psycopg2.OperationalError: role "etl_user" does not exist
```

**Solutions:**
```bash
# Create user as superuser
sudo -u postgres psql

# In psql:
CREATE USER etl_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE sales_db TO etl_user;
\q

# Update .env with correct credentials
DB_USER=etl_user
DB_PASSWORD=password
```

### Error: "permission denied"

**Symptoms:**
```
psycopg2.ProgrammingError: permission denied for schema public
```

**Solutions:**
```bash
# Grant privileges
psql -U postgres -d sales_db

# In psql:
GRANT ALL PRIVILEGES ON SCHEMA public TO etl_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO etl_user;
\q
```

## 2. Data Extraction Issues

### Error: "FileNotFoundError: CSV file not found"

**Symptoms:**
```
ExtractionException: CSV file not found: data/input/sales.csv
```

**Solutions:**
```bash
# Check file exists
ls -la data/input/

# Create directory if missing
mkdir -p data/input

# Verify CSV path in .env
cat .env | grep CSV_PATH

# Ensure file has correct name
mv sales_data.csv data/input/sales.csv
```

### Error: "Invalid JSON format"

**Symptoms:**
```
ExtractionException: JSON parsing failed: Expecting value
```

**Solutions:**
```bash
# Validate JSON file
python -m json.tool data/input/customers.json

# If error, check file format
cat data/input/customers.json | head -20

# Reformat JSON
python -c "
import json
with open('data/input/customers.json', 'r') as f:
    data = json.load(f)
with open('data/input/customers.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

### Error: "API connection timeout"

**Symptoms:**
```
APIException: API extraction failed: HTTPConnectionPool
```

**Solutions:**
```bash
# Check API endpoint
curl -I https://api.example.com/api/products

# Verify credentials
echo $API_BASE_URL

# Increase timeout in .env
API_TIMEOUT=60

# Check network connectivity
ping api.example.com
```

### Error: "API returns 401 Unauthorized"

**Symptoms:**
```
ExtractionException: API extraction failed: 401 Unauthorized
```

**Solutions:**
```bash
# Verify API token
echo $API_TOKEN

# Check token expiration
# Regenerate token if needed

# Test with curl
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.example.com/api/products
```

## 3. Data Transformation Issues

### Error: "No data to transform"

**Symptoms:**
```
TransformationException: Transformation returned empty DataFrame
```

**Solutions:**
```python
# Debug in Python
import pandas as pd
from src.extractors import CSVExtractor

extractor = CSVExtractor("data/input/sales.csv")
df = extractor.extract()
print(f"Rows: {len(df)}, Columns: {df.columns.tolist()}")
print(df.head())
```

### Error: "Column not found in DataFrame"

**Symptoms:**
```
KeyError: 'expected_column'
```

**Solutions:**
```python
# Check available columns
import pandas as pd

df = pd.read_csv("data/input/sales.csv")
print(df.columns.tolist())

# Update column names if needed
df.rename(columns={'old_name': 'new_name'}, inplace=True)
```

### Error: "Invalid date format"

**Symptoms:**
```
TransformationException: Could not standardize dates
```

**Solutions:**
```python
# Check date format in CSV
df['sale_date'].head()

# Convert to ISO format manually if needed
df['sale_date'] = pd.to_datetime(df['sale_date'], format='%d/%m/%Y')
df['sale_date'] = df['sale_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
df.to_csv("data/input/sales.csv", index=False)
```

## 4. Data Loading Issues

### Error: "Duplicate key value violates unique constraint"

**Symptoms:**
```
DatabaseException: duplicate key value violates unique constraint
```

**Solutions:**
```sql
-- Check for duplicates
SELECT customer_id, COUNT(*) FROM customers 
GROUP BY customer_id HAVING COUNT(*) > 1;

-- Remove duplicates
DELETE FROM customers 
WHERE ctid NOT IN (
  SELECT min(ctid) FROM customers GROUP BY customer_id
);

-- Or restart fresh
TRUNCATE TABLE customers CASCADE;
TRUNCATE TABLE sales CASCADE;
```

### Error: "Foreign key constraint violation"

**Symptoms:**
```
DatabaseException: insert or update on table violates foreign key
```

**Solutions:**
```sql
-- Check if referenced records exist
SELECT DISTINCT customer_id FROM sales 
WHERE customer_id NOT IN (SELECT customer_id FROM customers);

-- Load customers first, then sales
-- Or use ON CONFLICT in upsert

-- Temporarily disable constraints (DEV ONLY)
ALTER TABLE sales DISABLE TRIGGER ALL;
ALTER TABLE sales ENABLE TRIGGER ALL;
```

### Error: "Out of memory during batch load"

**Symptoms:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**
```bash
# Reduce batch size in .env
BATCH_SIZE=500

# Or in code
loader.load_sales(df, batch_size=500)

# Monitor memory
free -h
```

## 5. Dashboard Issues

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions:**
```bash
# Install dependencies
pip install -r requirements.txt

# Or specific module
pip install streamlit
```

### Error: "ConnectionRefusedError" in dashboard

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solutions:**
```bash
# Verify database is running
sudo systemctl status postgresql

# Check .env variables
env | grep DB_

# Test connection in Python
python -c "
from src.utils.config import load_config_from_env
config = load_config_from_env()
print(config.db_config.get_connection_string())
"

# Manually test connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### Error: "No data displayed in dashboard"

**Symptoms:**
- Empty visualizations
- No KPI values shown

**Solutions:**
```bash
# Check data in database
psql -d sales_db -c "SELECT COUNT(*) FROM sales;"

# Run ETL pipeline first
python run_etl.py

# Check logs
tail -f logs/etl_pipeline.log

# Verify SQL queries
psql -d sales_db -c "SELECT * FROM sales LIMIT 5;"
```

### Error: "Streamlit port already in use"

**Symptoms:**
```
Address already in use
```

**Solutions:**
```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill the process
sudo kill -9 <PID>

# Or use different port
streamlit run src/dashboard/app.py --server.port=8502
```

## 6. Docker Issues

### Error: "docker-compose: command not found"

**Symptoms:**
```
docker-compose: command not found
```

**Solutions:**
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

### Error: "Cannot connect to Docker daemon"

**Symptoms:**
```
Cannot connect to Docker daemon at unix:///var/run/docker.sock
```

**Solutions:**
```bash
# Start Docker service
sudo systemctl start docker

# Or enable at startup
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "Port already allocated"

**Symptoms:**
```
Error response from daemon: driver failed to initialize: Port already allocated
```

**Solutions:**
```bash
# Stop and remove containers
docker-compose down

# Or change port in docker-compose.yml
# ports:
#   - "8502:8501"
```

### Error: "Database container won't start"

**Symptoms:**
```
docker-compose up fails for postgres container
```

**Solutions:**
```bash
# Check logs
docker-compose logs postgres

# Remove old volume
docker-compose down -v

# Rebuild
docker-compose build --no-cache postgres

# Start fresh
docker-compose up -d postgres
```

## 7. Performance Issues

### Problem: ETL pipeline runs very slowly

**Symptoms:**
- Takes hours for normal data size
- High CPU/memory usage

**Solutions:**
```bash
# Check system resources
top
free -h
df -h

# Reduce batch size for less memory usage
BATCH_SIZE=500

# Increase connection pool if database is bottleneck
# In src/loaders/database.py:
manager = DatabaseManager(db_config, pool_size=10)

# Check database performance
psql -d sales_db -c "
SELECT schemaname, tablename, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
"
```

### Problem: Dashboard is slow to load

**Symptoms:**
- Takes long to display data
- Slow filter updates

**Solutions:**
```bash
# Cache query results
# Add caching to dashboard

# Optimize database queries
# Add more indexes

# Check network connectivity
ping database-host

# Monitor Streamlit
streamlit run src/dashboard/app.py --logger.level=debug
```

## 8. Logging and Debugging

### Enable Debug Logging

```bash
# Set log level in .env
LOG_LEVEL=DEBUG

# Run pipeline with debug
python run_etl.py

# Check logs
cat logs/etl_pipeline.log
```

### Check Specific Logs

```bash
# ETL pipeline logs
tail -f logs/etl_pipeline.log

# Main entry point logs
tail -f logs/etl_main.log

# Search for errors
grep "ERROR" logs/*.log

# Last 50 lines of specific log
tail -50 logs/etl_pipeline.log
```

### Python Debugging

```python
# Use pdb for debugging
python -m pdb run_etl.py

# Basic commands
# l (list current code)
# n (next line)
# s (step into)
# c (continue)
# p variable_name (print value)
```

## 9. Getting Help

### Collect Debug Information

```bash
# System info
uname -a
python --version
pip list | grep -E "pandas|psycopg2|streamlit"

# Database info
psql -U postgres -d sales_db -c "SELECT version();"

# Docker info (if applicable)
docker --version
docker-compose --version
docker ps -a

# Relevant logs
tail -100 logs/etl_pipeline.log > debug.log

# Config (sanitized)
cat .env | grep -v PASSWORD
```

### Report Issues

Include:
1. Error message (full traceback)
2. Steps to reproduce
3. Environment (OS, Python version, etc.)
4. Relevant log files
5. Configuration (sanitized .env)
6. Data samples (if possible)

---

## Quick Reference

| Issue | Solution |
|-------|----------|
| No database connection | Check PostgreSQL is running, verify credentials |
| CSV file not found | Verify file path exists in data/input/ |
| Invalid JSON | Run through `python -m json.tool` |
| Out of memory | Reduce BATCH_SIZE |
| Port in use | Kill existing process or change port |
| No data in dashboard | Run ETL pipeline first |
| Slow performance | Check indexes, increase pool size |
| Docker issues | Rebuild with `--no-cache` |

For more help, check logs and refer to documentation files.
