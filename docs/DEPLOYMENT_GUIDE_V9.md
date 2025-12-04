# ZeroSite v9.0 Deployment Guide

> **Production 배포 가이드 - Docker, 환경 설정, 보안**

---

## 📋 목차

- [배포 전 체크리스트](#-배포-전-체크리스트)
- [Docker 배포](#-docker-배포)
- [환경 변수 설정](#-환경-변수-설정)
- [Nginx 설정](#-nginx-설정)
- [HTTPS 설정](#-https-설정)
- [모니터링 설정](#-모니터링-설정)
- [백업 전략](#-백업-전략)
- [트러블슈팅](#-트러블슈팅)

---

## ✅ 배포 전 체크리스트

### 필수 사항

- [ ] Python 3.12+ 설치
- [ ] Docker & Docker Compose 설치
- [ ] Kakao API Key 발급
- [ ] OpenAI/Anthropic API Key 발급 (선택)
- [ ] 도메인 설정 (HTTPS용)
- [ ] SSL 인증서 준비
- [ ] 방화벽 설정 (포트 80, 443 오픈)

### 권장 사항

- [ ] Redis 설치 (POI 캐싱용)
- [ ] PostgreSQL 설치 (분석 이력 저장용)
- [ ] Nginx 설치 (리버스 프록시)
- [ ] Let's Encrypt 설정 (무료 SSL)
- [ ] Sentry 설정 (에러 모니터링)

---

## 🐳 Docker 배포

### 1. Dockerfile 생성

`Dockerfile`:

```dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./app /app/app
COPY ./frontend_v9 /app/frontend_v9

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/docs')"

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. docker-compose.yml 생성

```yaml
version: '3.8'

services:
  zerosite:
    build: .
    container_name: zerosite-v9
    ports:
      - "8000:8000"
    environment:
      - KAKAO_REST_API_KEY=${KAKAO_REST_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DEBUG=False
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - zerosite-network
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    container_name: zerosite-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - zerosite-network

  postgres:
    image: postgres:16-alpine
    container_name: zerosite-postgres
    environment:
      - POSTGRES_DB=zerosite
      - POSTGRES_USER=zerosite
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - zerosite-network

  nginx:
    image: nginx:alpine
    container_name: zerosite-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - zerosite
    restart: unless-stopped
    networks:
      - zerosite-network

volumes:
  redis-data:
  postgres-data:

networks:
  zerosite-network:
    driver: bridge
```

### 3. 빌드 및 실행

```bash
# 이미지 빌드
docker-compose build

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f zerosite

# 상태 확인
docker-compose ps
```

### 4. 컨테이너 관리

```bash
# 재시작
docker-compose restart zerosite

# 중지
docker-compose stop

# 완전 삭제
docker-compose down -v

# 이미지 업데이트
docker-compose pull
docker-compose up -d
```

---

## 🔐 환경 변수 설정

### Production .env 파일

```env
# ===== Kakao API =====
KAKAO_REST_API_KEY=your_production_kakao_key

# ===== LLM APIs (Optional) =====
OPENAI_API_KEY=sk-your-production-openai-key
ANTHROPIC_API_KEY=sk-ant-your-production-anthropic-key

# ===== Database =====
DATABASE_URL=postgresql://zerosite:password@postgres:5432/zerosite

# ===== Redis =====
REDIS_URL=redis://redis:6379/0

# ===== Application Settings =====
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your-very-long-and-random-secret-key-here

# ===== CORS =====
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===== Rate Limiting =====
RATE_LIMIT_PER_MINUTE=60

# ===== Monitoring =====
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# ===== Email (Notifications) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 환경 변수 보안

```bash
# .env 파일 권한 설정
chmod 600 .env

# Git에서 .env 제외
echo ".env" >> .gitignore

# 환경 변수 암호화 (선택)
# AWS Secrets Manager, Vault 등 사용 권장
```

---

## 🌐 Nginx 설정

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    # 기본 설정
    include mime.types;
    default_type application/octet-stream;
    
    # 로그 설정
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 성능 최적화
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    # Upstream
    upstream zerosite_backend {
        server zerosite:8000;
    }
    
    # HTTP → HTTPS 리다이렉트
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    # HTTPS 서버
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        
        # SSL 인증서
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # SSL 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        
        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # 프록시 설정
        location / {
            proxy_pass http://zerosite_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 타임아웃 설정 (POI API 호출 고려)
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # API Rate Limiting
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://zerosite_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 정적 파일 캐싱
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            proxy_pass http://zerosite_backend;
        }
    }
}
```

---

## 🔒 HTTPS 설정

### Let's Encrypt (무료 SSL)

```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run

# Cron으로 자동 갱신 설정
sudo crontab -e
# 매월 1일 오전 3시 갱신
0 3 1 * * certbot renew --quiet
```

### 수동 SSL 인증서 설치

```bash
# SSL 디렉토리 생성
mkdir -p /etc/nginx/ssl

# 인증서 복사
cp fullchain.pem /etc/nginx/ssl/
cp privkey.pem /etc/nginx/ssl/

# 권한 설정
chmod 600 /etc/nginx/ssl/privkey.pem
chmod 644 /etc/nginx/ssl/fullchain.pem
```

---

## 📊 모니터링 설정

### 1. Prometheus + Grafana

`prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zerosite'
    static_configs:
      - targets: ['zerosite:8000']
```

`docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: zerosite-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - zerosite-network

  grafana:
    image: grafana/grafana:latest
    container_name: zerosite-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - zerosite-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  zerosite-network:
    external: true
```

### 2. Sentry (에러 모니터링)

`app/config.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=1.0,
        integrations=[FastApiIntegration()]
    )
```

### 3. 헬스체크 엔드포인트

```bash
# 헬스체크
curl http://localhost:8000/health

# 응답
{
  "status": "healthy",
  "version": "v9.0",
  "timestamp": "2025-12-04T12:00:00Z",
  "dependencies": {
    "kakao_api": "ok",
    "redis": "ok",
    "postgres": "ok"
  }
}
```

---

## 💾 백업 전략

### 1. 데이터베이스 백업

```bash
#!/bin/bash
# backup_postgres.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
FILENAME="zerosite_${DATE}.sql"

# PostgreSQL 백업
docker exec zerosite-postgres pg_dump -U zerosite zerosite > "${BACKUP_DIR}/${FILENAME}"

# 압축
gzip "${BACKUP_DIR}/${FILENAME}"

# 30일 이상 된 백업 삭제
find ${BACKUP_DIR} -name "*.gz" -mtime +30 -delete

echo "Backup completed: ${FILENAME}.gz"
```

### 2. Redis 백업

```bash
#!/bin/bash
# backup_redis.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/redis"

# Redis RDB 파일 복사
docker exec zerosite-redis redis-cli SAVE
docker cp zerosite-redis:/data/dump.rdb "${BACKUP_DIR}/dump_${DATE}.rdb"

# 압축
gzip "${BACKUP_DIR}/dump_${DATE}.rdb"

echo "Redis backup completed"
```

### 3. Cron 설정

```bash
# Crontab 편집
crontab -e

# 매일 새벽 2시 백업
0 2 * * * /opt/zerosite/backup_postgres.sh >> /var/log/backup.log 2>&1
0 2 * * * /opt/zerosite/backup_redis.sh >> /var/log/backup.log 2>&1
```

---

## 🔧 트러블슈팅

### 1. 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs zerosite

# 일반적인 원인:
# - 환경 변수 누락
# - 포트 충돌
# - 의존성 설치 실패

# 해결:
docker-compose down
docker-compose up --build
```

### 2. API 응답 느림

```bash
# Redis 캐싱 확인
docker exec -it zerosite-redis redis-cli
> KEYS *

# Nginx 로그 확인
docker exec -it zerosite-nginx tail -f /var/log/nginx/access.log

# 해결:
# - POI API 캐싱 활성화
# - 비동기 처리 적용
# - 타임아웃 증가
```

### 3. SSL 인증서 오류

```bash
# 인증서 유효성 확인
openssl x509 -in /etc/nginx/ssl/fullchain.pem -text -noout

# 인증서 갱신
sudo certbot renew

# Nginx 재시작
docker-compose restart nginx
```

### 4. 메모리 부족

```bash
# 메모리 사용량 확인
docker stats

# 컨테이너 메모리 제한 설정
# docker-compose.yml
services:
  zerosite:
    mem_limit: 2g
    mem_reservation: 1g
```

---

## 📝 배포 체크리스트

### Pre-deployment

- [ ] 모든 테스트 통과
- [ ] 환경 변수 설정 완료
- [ ] SSL 인증서 준비
- [ ] 도메인 DNS 설정
- [ ] 백업 전략 수립

### Deployment

- [ ] Docker 이미지 빌드
- [ ] 컨테이너 시작
- [ ] 헬스체크 확인
- [ ] API 테스트
- [ ] 프론트엔드 접속 확인

### Post-deployment

- [ ] 모니터링 설정
- [ ] 로그 확인
- [ ] 성능 테스트
- [ ] 백업 테스트
- [ ] 문서 업데이트

---

## 📞 지원

- **문서**: https://docs.zerosite.ai
- **이메일**: devops@zerosite.ai
- **Slack**: #zerosite-devops

---

*Last Updated: 2025-12-04*
