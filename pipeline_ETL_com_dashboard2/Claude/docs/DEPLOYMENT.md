# Deployment Guide

## Production Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backed up
- [ ] SSL/TLS certificates ready
- [ ] Load balancer configured
- [ ] Monitoring setup
- [ ] Alert rules defined
- [ ] Security policies applied
- [ ] Capacity planning completed

## Docker Compose Production Setup

### 1. Environment Configuration

Create `.env` with production values:

```env
DB_HOST=prod-postgres.example.com
DB_PORT=5432
DB_NAME=sales_db_prod
DB_USER=etl_prod_user
DB_PASSWORD=<strong_random_password>

LOG_LEVEL=WARNING

INCREMENTAL_MODE=true
BATCH_SIZE=5000

DASHBOARD_PORT=8501
DEBUG_MODE=false

# Email alerts
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=alerts@example.com
REPORT_RECIPIENTS=admin@example.com
```

### 2. Docker Compose Override

Create `docker-compose.override.yml` for production:

```yaml
version: '3.8'

services:
  postgres:
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U etl_prod_user"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  pgadmin:
    restart: always
```

### 3. Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: etl-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: etl-dashboard
  template:
    metadata:
      labels:
        app: etl-dashboard
    spec:
      containers:
      - name: dashboard
        image: etl-dashboard:latest
        ports:
        - containerPort: 8501
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: host
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## Monitoring & Logging

### Prometheus Metrics

Add prometheus client to track:
- ETL execution time
- Data quality metrics
- Database query times
- API request latency

### Structured Logging

All logs include:
- Timestamp
- Log level
- Module name
- Function name
- Line number
- Message

### Log Aggregation

Send logs to:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch
- Loki + Grafana

### Example: Grafana Dashboard

Queries for key metrics:
```prometheus
# ETL Success Rate
rate(etl_runs_total{status="success"}[1h])

# Average Processing Time
avg(etl_processing_time_seconds)

# Database Query Times
histogram_quantile(0.95, etl_db_query_duration_seconds)
```

## Security Best Practices

### Database Security

```sql
-- Create restricted user
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE sales_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

### Environment Variables

- Never commit `.env` files
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Rotate passwords regularly
- Use environment-specific secrets

### Network Security

- Enable PostgreSQL SSL/TLS
- Use VPC for private communication
- Implement firewall rules
- Setup intrusion detection
- Regular security audits

### Application Security

- Keep dependencies updated (`pip audit`)
- Sanitize inputs
- Validate data
- Use prepared statements
- Implement rate limiting
- Setup CORS properly

## Performance Optimization

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT ... FROM sales WHERE year = 2024;

-- Create indexes for frequent queries
CREATE INDEX idx_sales_year_month ON sales(year, month);

-- Vacuum and analyze
VACUUM ANALYZE;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public';
```

### Connection Pooling

```python
# Configure connection pool
engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### Query Optimization

- Use batch processing
- Limit result sets
- Pagination for large datasets
- Cache frequently accessed data

### Resource Allocation

```yaml
# Docker resource limits
docker-compose:
  dashboard:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
```

## Backup & Recovery

### PostgreSQL Backup

```bash
# Full backup
pg_dump sales_db > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump sales_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Scheduled backup
0 2 * * * pg_dump sales_db | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Docker Volume Backup

```bash
# Backup database volume
docker run --rm -v sales_db:/data -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz /data

# Restore
docker run --rm -v sales_db:/data -v $(pwd):/backup \
  alpine tar xzf /backup/db_backup.tar.gz -C /
```

## Disaster Recovery Plan

### RTO (Recovery Time Objective): 4 hours
### RPO (Recovery Point Objective): 1 hour

### Recovery Procedures

1. **Database Failure**
   - Restore from latest backup
   - Validate data integrity
   - Run quality checks

2. **Application Failure**
   - Restart container
   - Check logs for errors
   - Restore from snapshot if needed

3. **Data Corruption**
   - Restore from backup
   - Identify corruption point
   - Implement preventive measures

## Scaling Strategy

### Horizontal Scaling

```yaml
# Multiple dashboard instances
docker-compose:
  dashboard-1:
    ...
  dashboard-2:
    ...
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Vertical Scaling

- Increase machine CPU/RAM
- Database optimization
- Connection pooling tuning

### Data Archiving

```python
# Archive old data
from datetime import datetime, timedelta

def archive_old_data(days=365):
    cutoff = datetime.now() - timedelta(days=days)
    # Move old sales to archive table
    # Delete from main table
```

## Monitoring Dashboards

### Key Metrics to Monitor

1. **System Health**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

2. **Application Health**
   - ETL execution time
   - Data quality metrics
   - API response time
   - Error rates

3. **Database Health**
   - Connection pool usage
   - Query execution time
   - Transaction rate
   - Lock wait time

4. **Business Metrics**
   - Total revenue
   - Sales count
   - Average ticket size
   - Customer acquisition

## Alerting Rules

### Critical Alerts

```yaml
- name: ETLFailure
  condition: etl_runs_total{status="failed"} > 2
  duration: 15m
  action: notify_ops_team

- name: DatabaseDown
  condition: pg_up == 0
  duration: 5m
  action: page_on_call

- name: HighErrorRate
  condition: rate(errors_total[5m]) > 0.05
  duration: 10m
  action: notify_devops
```

## Maintenance Windows

- Schedule: Weekly Sundays 02:00-04:00 UTC
- Database maintenance: Monthly
- Dependency updates: Quarterly
- Security audits: Quarterly
- Disaster recovery drills: Semi-annually

---

For more information, see the [Architecture Documentation](ARCHITECTURE.md)
