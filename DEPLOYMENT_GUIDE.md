# ZeroSite v4.0 - Complete Deployment Guide

**🚀 Production-Ready Enterprise System**

---

## 📦 Quick Start Options

### Option 1: Docker Compose (Recommended for Development)

```bash
# 1. Clone repository
git clone https://github.com/hellodesignthinking-png/LHproject.git
cd LHproject

# 2. Create environment file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://zerosite:zerosite123@db:5432/zerosite_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
EOF

# 3. Start services
docker-compose up -d

# 4. Initialize database
docker-compose exec web python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"

# 5. Access application
echo "✅ Application running at http://localhost:80"
```

### Option 2: Kubernetes (Production)

```bash
# 1. Set up kubectl and connect to cluster
kubectl cluster-info

# 2. Create namespace
kubectl create namespace zerosite

# 3. Apply configurations
kubectl apply -f k8s/config.yaml -n zerosite
kubectl apply -f k8s/postgres.yaml -n zerosite
kubectl apply -f k8s/redis.yaml -n zerosite
kubectl apply -f k8s/deployment.yaml -n zerosite

# 4. Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/zerosite-api -n zerosite

# 5. Get external IP
kubectl get service zerosite-service -n zerosite
```

### Option 3: Manual Installation

```bash
# 1. Install Python 3.9+
python3 --version

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL & Redis
# Install PostgreSQL 14
sudo apt-get install postgresql-14

# Install Redis
sudo apt-get install redis-server

# 5. Create database
sudo -u postgres psql
CREATE DATABASE zerosite_db;
CREATE USER zerosite WITH PASSWORD 'zerosite123';
GRANT ALL PRIVILEGES ON DATABASE zerosite_db TO zerosite;
\q

# 6. Initialize database
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"

# 7. Run application
uvicorn api_server_secured:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔐 Security Configuration

### 1. Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=generate-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (optional)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@zerosite.com

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn
```

### 2. Generate Secret Key

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. SSL Certificates

```bash
# Using Let's Encrypt
sudo certbot certonly --nginx -d your-domain.com

# Certificates will be in:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

---

## 📊 Monitoring & Logging

### 1. Prometheus Metrics

Add to `api_server_secured.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 2. Grafana Dashboard

```yaml
# docker-compose.yml - add services
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. ELK Stack

```yaml
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test
pytest tests/test_auth.py -v
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

### API Testing

```bash
# Install httpie
pip install httpie

# Test login
http POST localhost:8000/api/v1/auth/token username=admin password=admin123

# Test with token
http GET localhost:8000/api/v1/auth/me "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Maintenance

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current version
alembic current
```

### Backup & Restore

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U zerosite zerosite_db > backup.sql

# Restore
docker-compose exec -T db psql -U zerosite zerosite_db < backup.sql

# Backup Redis
docker-compose exec redis redis-cli SAVE
docker cp zerosite-redis:/data/dump.rdb ./redis_backup.rdb
```

### Log Rotation

```bash
# /etc/logrotate.d/zerosite
/var/log/zerosite/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload zerosite
    endscript
}
```

---

## 📈 Scaling

### Horizontal Scaling (Kubernetes)

```bash
# Scale up
kubectl scale deployment zerosite-api --replicas=10 -n zerosite

# Auto-scaling (already configured in HPA)
kubectl get hpa zerosite-hpa -n zerosite
```

### Database Read Replicas

```yaml
# Add to k8s/postgres.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-read
spec:
  selector:
    app: postgres
    role: replica
  ports:
  - port: 5432
```

### Redis Cluster

```bash
# Redis Cluster setup
docker-compose -f docker-compose.redis-cluster.yml up -d
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check PostgreSQL status
docker-compose ps db

# Check logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U zerosite -d zerosite_db -c "SELECT 1;"
```

#### 2. Redis Connection Error
```bash
# Check Redis status
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

#### 3. High Memory Usage
```bash
# Check container stats
docker stats

# Limit memory
docker-compose up -d --scale web=2 --memory=2g
```

#### 4. Slow API Response
```bash
# Check logs
docker-compose logs web | grep "slow"

# Profile endpoint
python -m cProfile -o profile.stats api_server_secured.py

# Analyze
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

---

## 📋 Checklist

### Pre-Deployment
- [ ] Update `SECRET_KEY` in environment variables
- [ ] Configure database credentials
- [ ] Set up SSL certificates
- [ ] Configure CORS origins
- [ ] Enable firewall rules
- [ ] Set up backup strategy

### Post-Deployment
- [ ] Verify health endpoint: `/health`
- [ ] Test authentication: `/api/v1/auth/token`
- [ ] Monitor logs for errors
- [ ] Set up alerts (Prometheus/Grafana)
- [ ] Configure auto-scaling
- [ ] Schedule regular backups

### Security
- [ ] Change default passwords
- [ ] Enable HTTPS only
- [ ] Configure rate limiting
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable audit logging
- [ ] Regular security scans

---

## 🎯 Performance Tuning

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);

-- Analyze tables
ANALYZE users;
ANALYZE analysis_jobs;

-- Vacuum
VACUUM ANALYZE;
```

### Redis Optimization

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Uvicorn Workers

```bash
# Production setup
uvicorn api_server_secured:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --log-level info
```

---

## 📞 Support

- **Documentation**: https://github.com/hellodesignthinking-png/LHproject
- **Issues**: https://github.com/hellodesignthinking-png/LHproject/issues
- **Email**: support@zerosite.com

---

## 📄 License

© 2025 ZeroSite. All Rights Reserved.

---

*Last Updated: 2025-12-27*
