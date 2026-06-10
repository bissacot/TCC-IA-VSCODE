# Troubleshooting Guide

Common issues and solutions for the Sales ETL Dashboard.

## Database Issues

### Issue: "Connection refused" or "Failed to connect to PostgreSQL"

**Symptoms**:
```
DatabaseException: Connection pool initialization failed
psycopg2.OperationalError: could not connect to server
```

**Solutions**:
1. **Check PostgreSQL is running**:
   ```bash
   # Windows
   net start postgresql

   # macOS
   brew services start postgresql

   # Linux
   sudo systemctl start postgresql
   ```

2. **Verify connection settings**:
   ```bash
   # Check .env file
   cat .env | grep DB_

   # Test connection
   psql -h localhost -U postgres -d sales_etl_db
   ```

3. **Check firewall**:
   - Ensure port 5432 is open
   - Check Windows Defender Firewall settings
   - Allow PostgreSQL through firewall

4. **Reset database password**:
   ```bash
   # Connect as admin
   psql -U postgres

   # Reset password
   ALTER USER postgres WITH PASSWORD 'new_password';
   ```

### Issue: "Relation does not exist"

**Symptoms**:
```
ProgrammingError: relation "customers" does not exist
```

**Solutions**:
1. **Initialize database schema**:
   ```bash
   python etl_cli.py setup
   ```

2. **Verify tables exist**:
   ```bash
   psql -h localhost -U postgres -d sales_etl_db
   \dt
   ```

3. **Check permissions**:
   ```bash
   # Connect to database
   psql -U postgres -d sales_etl_db
   
   # Grant permissions
   GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
   ```

### Issue: "Column does not exist" after migration

**Symptoms**:
```
ProgrammingError: column "new_column" does not exist
```

**Solutions**:
1. **Update schema**:
   ```bash
   # Backup database
   pg_dump sales_etl_db > backup.sql
   
   # Reset and recreate
   python etl_cli.py setup --drop
   ```

2. **Verify model definitions**:
   - Check `src/database/models.py`
   - Ensure columns match ORM definitions

## ETL Pipeline Issues

### Issue: "CSV file not found" or "JSON file not found"

**Symptoms**:
```
ExtractionException: CSV file not found: ./data/sales.csv
FileNotFoundError: File not found
```

**Solutions**:
1. **Verify file paths**:
   ```bash
   # Check data directory
   ls -la data/
   
   # Check absolute path
   pwd
   ```

2. **Update data file paths**:
   - Edit `config/settings.py`
   - Set correct `SALES_CSV_PATH` and `CUSTOMERS_JSON_PATH`

3. **Create sample files if missing**:
   ```bash
   # Provided in data/ directory
   cp data/sales.csv data/sales.csv.backup
   ```

### Issue: "API request failed" or "Connection timeout"

**Symptoms**:
```
ExtractionException: API request failed
requests.exceptions.Timeout: Connection timeout
```

**Solutions**:
1. **Check API endpoint**:
   ```bash
   # Test endpoint
   curl https://api.example.com/products

   # Update .env if needed
   API_BASE_URL=https://correct-url.com
   ```

2. **Increase timeout**:
   ```bash
   # Edit .env
   API_TIMEOUT=60
   ```

3. **Check authentication**:
   - Verify API credentials
   - Check authentication headers
   - Update `extractor.py` if needed

4. **Network connectivity**:
   ```bash
   # Test internet connection
   ping api.example.com
   
   # Check proxy settings
   ```

### Issue: "Data validation failed" - Invalid records

**Symptoms**:
```
Invalid email: user@invalid
Invalid price: -100
Invalid date: 2024-13-45
```

**Solutions**:
1. **Check source data format**:
   - Verify CSV has correct columns
   - Check JSON structure
   - Validate API response

2. **Update validation rules** if needed:
   - Edit `src/utils/validators.py`
   - Modify `validate_email()`, `validate_currency()` etc.

3. **Review data quality report**:
   ```bash
   # Check recent reports
   ls -lart reports/
   
   # View latest report
   cat reports/etl_report_*.json | jq '.'
   ```

### Issue: "No data loaded" - Zero records

**Symptoms**:
```
Successfully loaded 0 records
Dashboard shows no data
```

**Solutions**:
1. **Run ETL pipeline again**:
   ```bash
   python etl_cli.py run
   ```

2. **Check for errors in logs**:
   ```bash
   tail -100 logs/etl.log | grep -i error
   ```

3. **Verify data exists**:
   ```bash
   # Check database
   psql -U postgres -d sales_etl_db
   SELECT COUNT(*) FROM customers;
   SELECT COUNT(*) FROM sales;
   ```

4. **Add sample data manually**:
   ```bash
   psql -U postgres -d sales_etl_db < sql/sample_data.sql
   ```

## Dashboard Issues

### Issue: "Streamlit app crashed" or "Connection refused"

**Symptoms**:
```
StreamlitAPIException: Connection refused
ConnectionError: Unable to connect to server
```

**Solutions**:
1. **Restart dashboard**:
   ```bash
   # Stop current process (Ctrl+C)
   
   # Start again
   streamlit run src/dashboard/app.py
   ```

2. **Change port if in use**:
   ```bash
   # Edit .env
   DASHBOARD_PORT=8502
   
   # Start on new port
   streamlit run src/dashboard/app.py --server.port=8502
   ```

3. **Check database connectivity**:
   ```bash
   # Dashboard needs active database connection
   # Verify PostgreSQL is running
   ```

### Issue: "No data displayed" in dashboard

**Symptoms**:
- Dashboard loads but shows empty tables
- "No data available for selected filters"

**Solutions**:
1. **Verify database has data**:
   ```bash
   psql -U postgres -d sales_etl_db
   SELECT COUNT(*) FROM sales;
   ```

2. **Check filter settings**:
   - Adjust date range (extend to include all data)
   - Select all states/categories
   - Clear product filters

3. **Clear Streamlit cache**:
   ```bash
   # Delete cache files
   rm -rf ~/.streamlit
   
   # Restart dashboard
   streamlit run src/dashboard/app.py --logger.level=debug
   ```

### Issue: "Chart rendering error" or "Plotly error"

**Symptoms**:
```
PlotlyException: Error rendering figure
ValueError: x and y must be same length
```

**Solutions**:
1. **Check data integrity**:
   ```bash
   # Verify no missing values in key columns
   SELECT * FROM sales WHERE total_value IS NULL LIMIT 10;
   ```

2. **Update Plotly**:
   ```bash
   pip install --upgrade plotly
   ```

3. **Restart dashboard and clear cache**:
   ```bash
   streamlit cache clear
   streamlit run src/dashboard/app.py
   ```

## Docker Issues

### Issue: "Docker build failed"

**Symptoms**:
```
ERROR: Service 'etl' failed to build
failed to solve with frontend dockerfile.v0
```

**Solutions**:
1. **Clean Docker cache**:
   ```bash
   docker system prune -a
   docker volume prune
   ```

2. **Rebuild with no cache**:
   ```bash
   docker-compose -f docker/docker-compose.yml build --no-cache
   ```

3. **Check Dockerfile syntax**:
   - Verify `FROM`, `RUN`, `COPY` commands
   - Check indentation

4. **Update Docker and Docker Compose**:
   ```bash
   docker --version
   docker-compose --version
   ```

### Issue: "Container failed to start"

**Symptoms**:
```
docker: Error response from daemon: driver failed
container exited with code 1
```

**Solutions**:
1. **Check logs**:
   ```bash
   docker-compose -f docker/docker-compose.yml logs etl
   docker-compose -f docker/docker-compose.yml logs postgres
   ```

2. **Verify volumes**:
   ```bash
   docker volume ls
   docker volume inspect sales_etl_dashboard_postgres_data
   ```

3. **Reset Docker**:
   ```bash
   docker-compose -f docker/docker-compose.yml down -v
   docker-compose -f docker/docker-compose.yml up -d
   ```

### Issue: "Port already in use"

**Symptoms**:
```
Error: bind: address already in use
```

**Solutions**:
1. **Kill process using port**:
   ```bash
   # Find process
   lsof -i :5432
   lsof -i :8501
   
   # Kill process
   kill -9 <PID>
   ```

2. **Use different port**:
   ```bash
   # Edit docker-compose.yml
   ports:
     - "5433:5432"  # Change external port
   ```

## Performance Issues

### Issue: "Slow ETL execution" or "Dashboard is slow"

**Symptoms**:
- ETL takes too long
- Dashboard queries are slow
- High database CPU usage

**Solutions**:
1. **Check database indexes**:
   ```sql
   -- List indexes
   SELECT * FROM pg_indexes WHERE tablename = 'sales';
   ```

2. **Analyze query performance**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM sales WHERE sale_date > '2024-01-01';
   ```

3. **Reduce batch size**:
   ```bash
   # Edit .env
   BATCH_SIZE=500
   ```

4. **Increase database resources**:
   - Allocate more RAM to PostgreSQL
   - Increase connection pool size

5. **Clear old reports**:
   ```bash
   rm -f reports/etl_report_*.json
   ```

## Logging & Debugging

### Enable Debug Logging

```bash
# Edit .env
LOG_LEVEL=DEBUG

# Run pipeline
python etl_cli.py run
```

### View Logs

```bash
# Real-time logs
tail -f logs/etl.log

# Last 100 lines
tail -100 logs/etl.log

# Search for errors
grep -i "error" logs/etl.log
```

### Debug Database Queries

```bash
# Enable SQLAlchemy echo
# In loader.py or connection.py, set:
engine = create_engine(DB_URL, echo=True)
```

### Check Application Status

```python
# Run diagnostic script
python -c """
from config.settings import DB_URL, SALES_CSV_PATH, CUSTOMERS_JSON_PATH
print(f'Database: {DB_URL}')
print(f'Sales file: {SALES_CSV_PATH.exists()}')
print(f'Customers file: {CUSTOMERS_JSON_PATH.exists()}')
"""
```

## Getting Help

### Before Asking for Help, Try:
1. Check logs for error messages
2. Review this troubleshooting guide
3. Search GitHub issues
4. Check documentation

### When Reporting Issues:
Include:
- Error message (full stack trace)
- Steps to reproduce
- Operating system
- Python version
- PostgreSQL version
- Docker version (if applicable)
- Relevant log files
- Environment configuration (sanitized)

### Resources:
- 📖 Main Documentation: [README.md](../README.md)
- 🚀 Quick Start: [QUICKSTART.md](../QUICKSTART.md)
- 🏗️ Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 📝 API Reference: [API.md](./API.md)
