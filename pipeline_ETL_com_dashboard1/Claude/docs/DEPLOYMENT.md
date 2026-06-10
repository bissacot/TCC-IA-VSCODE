# Deployment Guide

## Prerequisites

- Docker & Docker Compose 20.10+
- PostgreSQL 12+ (for local development)
- Python 3.9+ (for local development)
- Git
- 2GB minimum RAM
- 5GB minimum disk space

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd pipeline-etl-dashboard
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

### 5. Database Setup

#### Using PostgreSQL directly:

```bash
# Create database
psql -U postgres -h localhost
CREATE DATABASE sales_db;
CREATE USER etl_user WITH PASSWORD 'etl_password';
GRANT ALL PRIVILEGES ON DATABASE sales_db TO etl_user;

# Run initialization script
psql -U etl_user -d sales_db -f database/init.sql
```

#### Using Docker:

```bash
docker run -d \
  --name sales_postgres \
  -e POSTGRES_DB=sales_db \
  -e POSTGRES_USER=etl_user \
  -e POSTGRES_PASSWORD=etl_password \
  -p 5432:5432 \
  postgres:15-alpine
```

### 6. Run ETL Pipeline

```bash
python -m src.etl.pipeline
```

### 7. Start Dashboard

```bash
streamlit run src/dashboard/app.py
```

Access dashboard at: http://localhost:8501

## Docker Deployment

### Quick Start

```bash
# Copy environment template
cp .env.example .env

# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Services

- **PostgreSQL**: localhost:5432
- **Streamlit Dashboard**: http://localhost:8501
- **pgAdmin**: http://localhost:5050
- **ETL Service**: Runs automatically on schedule

### Environment Variables

Edit `.env` file to customize:

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=etl_user
DB_PASSWORD=etl_password
DB_NAME=sales_db

# Execution
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False

# Performance
CACHE_TTL_SECONDS=3600
BATCH_SIZE=1000
```

### Database Management with pgAdmin

1. Access pgAdmin: http://localhost:5050
2. Login: admin@example.com / admin
3. Add Server:
   - Host: postgres
   - Port: 5432
   - Username: etl_user
   - Password: etl_password

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard
docker-compose logs -f etl-service

# Follow only errors
docker-compose logs -f | grep ERROR
```

## Kubernetes Deployment

### Prerequisites

- kubectl configured
- Helm 3.0+
- Docker images pushed to registry

### Create Namespace

```bash
kubectl create namespace etl-pipeline
```

### Create Secrets

```bash
kubectl create secret generic db-credentials \
  --from-literal=username=etl_user \
  --from-literal=password=etl_password \
  -n etl-pipeline
```

### Deploy PostgreSQL

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --set auth.username=etl_user \
  --set auth.password=etl_password \
  --set auth.database=sales_db \
  -n etl-pipeline
```

### Deploy Application

Create `deployment.yaml` and apply:

```bash
kubectl apply -f deployment.yaml -n etl-pipeline
```

### Monitor Deployment

```bash
kubectl get pods -n etl-pipeline
kubectl logs deployment/dashboard -n etl-pipeline
kubectl port-forward svc/dashboard 8501:8501 -n etl-pipeline
```

## Production Considerations

### Security

- [ ] Use strong passwords
- [ ] Enable SSL/TLS for connections
- [ ] Implement network policies
- [ ] Use secrets management (Vault, K8s Secrets)
- [ ] Restrict database access
- [ ] Enable audit logging

### Performance

- [ ] Enable caching
- [ ] Configure connection pooling
- [ ] Optimize database indexes
- [ ] Use read replicas for analytics
- [ ] Implement query optimization

### Monitoring

- [ ] Set up centralized logging
- [ ] Configure alerting
- [ ] Monitor disk usage
- [ ] Track ETL execution times
- [ ] Monitor database performance

### Backup Strategy

```bash
# Backup PostgreSQL
docker exec sales_db pg_dump -U etl_user sales_db > backup.sql

# Restore PostgreSQL
docker exec -i sales_db psql -U etl_user sales_db < backup.sql

# Backup data volumes
docker run --rm -v etl_pipeline_postgres_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Scaling

- Use database replication for high availability
- Implement horizontal scaling for ETL workers
- Use message queues for async processing
- Cache frequently accessed data

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U etl_user -d sales_db -c "SELECT 1"

# Check logs
docker logs sales_db
```

### ETL Pipeline Failures

```bash
# View detailed logs
tail -f logs/etl.log

# Run with debug mode
ENVIRONMENT=development DEBUG=True python -m src.etl.pipeline
```

### Dashboard Not Loading

```bash
# Check Streamlit logs
streamlit run src/dashboard/app.py --logger.level=debug

# Clear cache
streamlit cache clear
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8501

# Kill process (macOS/Linux)
kill -9 <PID>

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

## Maintenance

### Regular Tasks

- Review logs weekly
- Update dependencies monthly
- Run database maintenance
- Verify backup integrity
- Monitor disk space

### Update Procedure

```bash
# Backup current state
docker-compose exec postgres pg_dump -U etl_user sales_db > backup_$(date +%Y%m%d).sql

# Update code
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose down
docker-compose up -d

# Verify
docker-compose logs -f dashboard
```

## Performance Tuning

### Database Optimization

```sql
-- Analyze tables for query optimization
ANALYZE customers;
ANALYZE products;
ANALYZE sales;
ANALYZE data_quality_report;

-- Vacuum for maintenance
VACUUM ANALYZE customers;
VACUUM ANALYZE products;
VACUUM ANALYZE sales;
```

### Connection Pooling

Configure in `config.py`:

```python
pool_size = 20  # Maximum connections
max_overflow = 40  # Additional connections when pool exhausted
pool_recycle = 3600  # Recycle connections after 1 hour
```

## Disaster Recovery

### Recovery Plan

1. **Database Failure**:
   - Restore from backup
   - Verify data integrity
   - Rerun ETL pipeline

2. **Data Corruption**:
   - Restore from backup
   - Investigate root cause
   - Implement preventive measures

3. **Complete System Failure**:
   - Restore backup to new server
   - Update configuration
   - Rebuild Docker images
   - Deploy to new infrastructure

---

**For support or issues, refer to the main README.md or create an issue in the repository.**
