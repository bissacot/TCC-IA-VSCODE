# Deployment Guide

Complete guide for deploying the Sales ETL Dashboard to production.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] SSL certificates ready
- [ ] Monitoring configured
- [ ] Rollback plan documented

## Single Server Deployment

### 1. Server Setup

**Requirements**:
- OS: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- RAM: 4GB minimum, 8GB recommended
- Disk: 50GB minimum
- Network: Internet access for API calls

**Install Dependencies**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv postgresql postgresql-contrib
sudo apt-get install -y build-essential libpq-dev

# CentOS
sudo yum install -y python311 postgresql-server postgresql-contrib
```

### 2. Database Setup

```bash
# Create database
sudo su - postgres
psql
CREATE DATABASE sales_etl_db;
CREATE USER etl_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE sales_etl_db TO etl_user;
\q
exit
```

### 3. Application Deployment

```bash
# Create app directory
sudo mkdir -p /opt/sales-etl-dashboard
sudo chown $USER:$USER /opt/sales-etl-dashboard

# Clone or copy application
cd /opt/sales-etl-dashboard
# Copy files here

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with actual credentials

# Initialize database
python etl_cli.py setup

# Run ETL to verify
python etl_cli.py run
```

### 4. Create Systemd Service

**ETL Service**: `/etc/systemd/system/etl-pipeline.service`
```ini
[Unit]
Description=Sales ETL Pipeline
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=etl_user
WorkingDirectory=/opt/sales-etl-dashboard
Environment="PATH=/opt/sales-etl-dashboard/venv/bin"
ExecStart=/opt/sales-etl-dashboard/venv/bin/python /opt/sales-etl-dashboard/etl_cli.py run
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Scheduler Service**: `/etc/systemd/system/etl-scheduler.service`
```ini
[Unit]
Description=Sales ETL Scheduler
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=etl_user
WorkingDirectory=/opt/sales-etl-dashboard
Environment="PATH=/opt/sales-etl-dashboard/venv/bin"
ExecStart=/opt/sales-etl-dashboard/venv/bin/python /opt/sales-etl-dashboard/scheduler.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Dashboard Service**: `/etc/systemd/system/etl-dashboard.service`
```ini
[Unit]
Description=Sales ETL Dashboard
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=etl_user
WorkingDirectory=/opt/sales-etl-dashboard
Environment="PATH=/opt/sales-etl-dashboard/venv/bin"
ExecStart=/opt/sales-etl-dashboard/venv/bin/streamlit run src/dashboard/app.py --server.port=8501 --server.address=0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable etl-pipeline.service
sudo systemctl enable etl-scheduler.service
sudo systemctl enable etl-dashboard.service
sudo systemctl start etl-dashboard.service
sudo systemctl start etl-scheduler.service
```

### 5. Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt-get install -y nginx
```

Configure: `/etc/nginx/sites-available/etl-dashboard`
```nginx
upstream streamlit {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/etl_access.log;
    error_log /var/log/nginx/etl_error.log;

    # Streamlit Dashboard
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

    # Cache static files
    location ~* ^/_stcore/static {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/etl-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate

Using Let's Encrypt:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
sudo certbot renew --dry-run  # Test renewal
```

### 7. Monitoring & Logging

Setup log rotation: `/etc/logrotate.d/etl-dashboard`
```
/opt/sales-etl-dashboard/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 etl_user etl_user
    sharedscripts
    postrotate
        systemctl reload etl-dashboard.service
    endscript
}
```

Monitor services:
```bash
sudo systemctl status etl-pipeline.service
sudo systemctl status etl-scheduler.service
sudo systemctl status etl-dashboard.service

# View logs
sudo journalctl -u etl-dashboard.service -f
tail -f /opt/sales-etl-dashboard/logs/etl.log
```

## Docker Compose Deployment

### 1. Server Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Prepare Deployment

```bash
# Create deployment directory
sudo mkdir -p /opt/sales-etl-dashboard
sudo chown $USER:$USER /opt/sales-etl-dashboard

# Copy files
cd /opt/sales-etl-dashboard
# Copy all files here

# Configure environment
cp .env.example .env
nano .env  # Edit credentials
```

### 3. Deploy

```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Verify
docker-compose -f docker/docker-compose.yml ps

# Check logs
docker-compose -f docker/docker-compose.yml logs -f
```

### 4. Nginx Proxy (same as above)

## Production Considerations

### Security

**Database Security**:
```bash
# Use strong password
# Configure PostgreSQL to require authentication
# Use SSL connections
# Restrict network access
```

**Application Security**:
```bash
# Use environment variables for secrets
# Enable HTTPS/SSL
# Use strong API keys
# Implement rate limiting
# Regular security updates
```

**Access Control**:
```bash
# Use firewall rules
# Restrict port access
# Use VPN for admin access
# Enable logging and monitoring
```

### Performance Optimization

```bash
# Database
- Increase max_connections in postgresql.conf
- Configure shared_buffers
- Enable query logging for analysis

# Application
- Use connection pooling (configured)
- Enable caching
- Optimize database queries

# Infrastructure
- Use CDN for static files
- Load balance across servers
- Monitor resource usage
```

### Backup & Recovery

**Daily Backup**:
```bash
#!/bin/bash
# /etc/cron.daily/backup-etl

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/etl"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U postgres sales_etl_db > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

**Restore from Backup**:
```bash
# Restore database
gunzip -c /backups/etl/db_20240115.sql.gz | psql -U postgres sales_etl_db
```

### Scaling

**Horizontal Scaling**:
```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx)           │
└─────────────────────┬───────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ App 1   │  │ App 2   │  │ App 3   │
   └─────────┘  └─────────┘  └─────────┘
        └─────────────┬─────────────┘
                      ↓
            ┌─────────────────────┐
            │   PostgreSQL DB     │
            │  (Shared Instance)  │
            └─────────────────────┘
```

**Database Scaling**:
- Read replicas for dashboard queries
- Connection pooling (PgBouncer)
- Partitioning large tables
- Archive old data

### Monitoring

Setup monitoring dashboard:
```bash
# Install Prometheus client (optional)
pip install prometheus-client

# Configure alerts for:
# - Database connection errors
# - ETL failures
# - High response times
# - Disk space issues
```

## Troubleshooting Deployment

### Common Issues

**Services not starting**:
```bash
sudo journalctl -u etl-dashboard.service -n 50
sudo systemctl restart etl-dashboard.service
```

**Database connection issues**:
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U etl_user -d sales_etl_db
```

**Nginx proxy issues**:
```bash
# Check configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/etl_error.log
```

**Port conflicts**:
```bash
# Find process using port
sudo lsof -i :8501
sudo lsof -i :80
sudo lsof -i :443

# Kill process if needed
sudo kill -9 <PID>
```

## Post-Deployment

1. **Verify Services**:
   ```bash
   curl https://yourdomain.com  # Should work
   ```

2. **Run Tests**:
   ```bash
   pytest tests/ --cov=src
   ```

3. **Check Logs**:
   ```bash
   tail -f logs/etl.log
   ```

4. **Monitor Performance**:
   ```bash
   systemctl status etl-dashboard
   docker-compose ps  # If Docker
   ```

5. **Setup Alerts**:
   - Monitor ETL failures
   - Track database performance
   - Alert on high errors

## Rollback Procedure

If issues occur:

```bash
# Stop current deployment
docker-compose -f docker/docker-compose.yml down
# OR
sudo systemctl stop etl-dashboard.service

# Restore from backup
gunzip -c /backups/etl/db_PREVIOUS.sql.gz | psql -U postgres sales_etl_db

# Revert code
git checkout HEAD~1
# OR
cp -r /backups/code/previous /opt/sales-etl-dashboard

# Restart services
docker-compose -f docker/docker-compose.yml up -d
# OR
sudo systemctl start etl-dashboard.service
```

## Maintenance

### Regular Tasks

- **Weekly**: Check logs, verify backups
- **Monthly**: Update dependencies, security patches
- **Quarterly**: Performance review, scaling assessment
- **Yearly**: Disaster recovery testing

### Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose -f docker/docker-compose.yml pull
docker-compose -f docker/docker-compose.yml up -d
```

See [README.md](../README.md) and [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more help.
