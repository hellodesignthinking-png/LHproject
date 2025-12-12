# ZeroSite v24 - Deployment Guide

## Quick Start

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn app.api.v24.main:app --reload --port 8000

# Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Dashboard: open public/dashboard/index.html
```

### 2. Docker Compose (Recommended)
```bash
# Start all services
cd deployment
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Production Deployment

#### Prerequisites
- Docker & Docker Compose
- PostgreSQL 15+
- Nginx (optional, included in docker-compose)

#### Environment Variables
```bash
export DB_PASSWORD=your_secure_password
export DATABASE_URL=postgresql://zerosite:password@localhost:5432/zerosite_v24
```

#### Deploy
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Initialize database
docker exec zerosite-postgres psql -U zerosite -d zerosite_v24 -f /docker-entrypoint-initdb.d/schema.sql
```

### 4. Cloud Deployment (AWS/GCP/Azure)

#### AWS Elastic Beanstalk
```bash
eb init -p docker zerosite-v24
eb create zerosite-v24-prod
eb deploy
```

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/zerosite-v24
gcloud run deploy zerosite-v24 --image gcr.io/PROJECT_ID/zerosite-v24 --platform managed
```

#### Azure Container Instances
```bash
az container create --resource-group zerosite-rg --name zerosite-v24 \
  --image zerosite-v24:latest --cpu 2 --memory 4 --port 8000
```

## Database Setup

### PostgreSQL
```sql
-- Create database
CREATE DATABASE zerosite_v24;

-- Run schema
\i deployment/schema.sql

-- Verify
\dt
SELECT * FROM projects;
```

## Monitoring

### Health Checks
- API: `curl http://localhost:8000/`
- Database: `docker exec zerosite-postgres pg_isready -U zerosite`

### Logs
```bash
# API logs
docker logs zerosite-api

# Database logs
docker logs zerosite-postgres

# Nginx logs
docker logs zerosite-nginx
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

### Load Balancing
- Nginx already configured for upstream backend
- Add more API replicas as needed

## Security

### SSL/TLS
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

### Database Security
- Change default password
- Enable SSL connections
- Configure firewall rules

## Backup

### Database Backup
```bash
# Backup
docker exec zerosite-postgres pg_dump -U zerosite zerosite_v24 > backup.sql

# Restore
docker exec -i zerosite-postgres psql -U zerosite zerosite_v24 < backup.sql
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Change ports in docker-compose.yml
2. **Database connection failed**: Check DATABASE_URL
3. **API not responding**: Check logs with `docker logs zerosite-api`

### Support
- GitHub Issues: https://github.com/hellodesignthinking-png/LHproject/issues
- Documentation: See PHASE_3_4_5_COMPLETE_REPORT.md
