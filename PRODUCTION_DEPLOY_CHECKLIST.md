# 🚀 ZeroSite v37.0 - Production Deployment Checklist

**Version**: 37.0 ULTIMATE  
**Date**: 2025-12-13  
**Target**: Production Environment

---

## ✅ Pre-Deployment Checklist

### 1. Code Quality & Testing

- [ ] All unit tests passing (5/5 regions)
- [ ] Integration tests completed
- [ ] PDF generation tested (36 pages)
- [ ] No linting errors
- [ ] Security scan completed
- [ ] Code reviewed and approved

### 2. Configuration

- [ ] `.env.production` created from `.env.production.example`
- [ ] All API keys updated with production values
  - [ ] Kakao REST API key
  - [ ] V-World API key
  - [ ] MOLIT API key
- [ ] `SECRET_KEY` generated (min 32 characters)
- [ ] `ALLOWED_HOSTS` configured
- [ ] `DEBUG=false` confirmed
- [ ] Log paths configured

### 3. Infrastructure

- [ ] Server provisioned (minimum 2 CPU, 4GB RAM)
- [ ] Domain name configured
- [ ] DNS records set up
  - [ ] A record pointing to server IP
  - [ ] CNAME for www subdomain
- [ ] Firewall rules configured
  - [ ] Port 80 (HTTP) open
  - [ ] Port 443 (HTTPS) open
  - [ ] Port 22 (SSH) restricted to admin IPs

### 4. SSL Certificate

- [ ] SSL certificate obtained (Let's Encrypt or commercial)
- [ ] Certificate files placed in `./ssl/`
  - [ ] `fullchain.pem`
  - [ ] `privkey.pem`
- [ ] Auto-renewal configured

### 5. Docker Setup

- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Docker network created
- [ ] Volumes prepared
  - [ ] `./logs` directory
  - [ ] `./uploads` directory
  - [ ] `./backups` directory

---

## 🔧 Deployment Steps

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
# Clone
git clone https://github.com/hellodesignthinking-png/LHproject.git
cd LHproject
git checkout v24.1_gap_closing

# Create necessary directories
mkdir -p logs uploads backups ssl nginx/conf.d
```

### Step 3: Configure Environment

```bash
# Copy and edit production environment
cp .env.production.example .env.production
nano .env.production

# Update:
# - All API keys
# - SECRET_KEY
# - ALLOWED_HOSTS
# - Domain names in nginx config
```

### Step 4: SSL Certificate

```bash
# Option A: Let's Encrypt (Recommended)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/
sudo chmod 644 ./ssl/*.pem

# Option B: Self-signed (Development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./ssl/privkey.pem -out ./ssl/fullchain.pem
```

### Step 5: Build and Deploy

```bash
# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### Step 6: Verify Deployment

```bash
# Health check
curl http://localhost:8000/api/v24.1/health

# Test appraisal endpoint
curl -X POST http://localhost:8000/api/v24.1/appraisal/v37 \
  -H "Content-Type: application/json" \
  -d '{"address": "서울 강남구 역삼동 680-11", "land_area_sqm": 400}'

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## 📊 Post-Deployment Verification

### 1. Functional Tests

- [ ] Health endpoint responding (200 OK)
- [ ] Appraisal endpoint working
  - [ ] Seoul address
  - [ ] Busan address
  - [ ] Jeju address
- [ ] PDF generation working
- [ ] API documentation accessible

### 2. Performance Tests

- [ ] Response time < 500ms (health check)
- [ ] Response time < 10s (appraisal)
- [ ] PDF generation < 10s
- [ ] Concurrent requests handled (10+ users)

### 3. Security Tests

- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Security headers present
- [ ] Sensitive endpoints protected
- [ ] Rate limiting active

### 4. Monitoring Setup

- [ ] Log aggregation working
- [ ] Error alerts configured
- [ ] Performance monitoring active
- [ ] Backup script scheduled

---

## 🔄 Maintenance Commands

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f zerosite

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 zerosite
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart zerosite
```

### Update Application

```bash
# Pull latest code
git pull origin v24.1_gap_closing

# Rebuild and restart
docker-compose -f docker-compose.production.yml build zerosite
docker-compose -f docker-compose.production.yml up -d zerosite
```

### Backup

```bash
# Manual backup
tar -czf zerosite_backup_$(date +%Y%m%d).tar.gz \
  app/ logs/ uploads/ .env.production

# Copy to safe location
cp zerosite_backup_*.tar.gz /path/to/backup/
```

### Troubleshooting

```bash
# Check container status
docker ps -a

# Enter container
docker exec -it zerosite-app /bin/bash

# Check resource usage
docker stats

# View Docker logs
docker logs zerosite-app
```

---

## 🚨 Rollback Procedure

### If deployment fails:

```bash
# Stop new version
docker-compose -f docker-compose.production.yml down

# Restore backup
tar -xzf zerosite_backup_YYYYMMDD.tar.gz

# Start previous version
docker-compose -f docker-compose.production.yml up -d
```

---

## 📞 Support Contacts

- **Technical Lead**: [email@domain.com]
- **DevOps**: [devops@domain.com]
- **Emergency**: [phone number]

---

## 📝 Deployment Sign-off

- [ ] Deployment completed by: `___________`
- [ ] Date/Time: `___________`
- [ ] Verified by: `___________`
- [ ] Issues noted: `___________`

---

**Status**: ✅ Ready for Production Deployment
