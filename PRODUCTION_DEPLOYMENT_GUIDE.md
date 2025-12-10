# 🚀 ZeroSite v3 Production Deployment Guide

**버전**: v3.0.0  
**작성일**: 2025-12-10  
**상태**: PRODUCTION READY ✅

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment Options](#deployment-options)
5. [API Integration](#api-integration)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+) / macOS 10.15+ / Windows 10+
- **Python**: 3.10+
- **RAM**: 2GB
- **Disk**: 500MB
- **CPU**: 2 cores

### Recommended Requirements
- **OS**: Linux (Ubuntu 22.04+)
- **Python**: 3.12+
- **RAM**: 4GB+
- **Disk**: 1GB+
- **CPU**: 4+ cores

### Dependencies
```
Python 3.10+
plotly>=6.5.0
weasyprint (optional, for PDF)
jinja2>=3.1.0
```

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/hellodesignthinking-png/LHproject.git
cd LHproject
git checkout feature/expert-report-generator  # or main after PR merge
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Or install manually
pip install plotly>=6.5.0 jinja2>=3.1.0 weasyprint
```

### 4. Verify Installation
```bash
python generate_v3_full_report.py
# Should generate report in < 2 seconds
```

---

## ⚙️ Configuration

### Environment Variables
Create `.env` file:
```bash
# Report Configuration
REPORT_OUTPUT_DIR=generated_reports
REPORT_TEMPLATE_DIR=app/services_v13/report_full

# Chart Configuration
CHART_WIDTH=1200
CHART_HEIGHT=500
PLOTLY_CDN_VERSION=2.27.0

# Performance
MAX_CONCURRENT_REPORTS=5
CACHE_ENABLED=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=zerosite.log
```

### Config File (config.yaml)
```yaml
report:
  output_dir: "generated_reports"
  template_dir: "app/services_v13/report_full"
  default_format: "html"
  enable_pdf: true

charts:
  enabled: true
  width: 1200
  height: 500
  interactive: true
  cdn_version: "2.27.0"

performance:
  max_concurrent: 5
  cache_enabled: true
  cache_ttl: 3600

security:
  api_key_required: true
  rate_limit: 100  # requests per hour
  allowed_origins: ["*"]
```

---

## 🚀 Deployment Options

### Option 1: Standalone Application

#### Quick Start
```bash
cd /path/to/LHproject
python generate_v3_full_report.py
```

#### Batch Processing
```python
# batch_generate.py
from generate_v3_full_report import V3FullReportGenerator

generator = V3FullReportGenerator()

projects = [
    {"address": "서울특별시 강남구 테헤란로 123", "land_area": 1000, ...},
    {"address": "서울특별시 마포구 월드컵북로 120", "land_area": 1500, ...},
    # ... more projects
]

for project in projects:
    try:
        html = generator.generate_report(**project)
        output = generator.save_report(html)
        print(f"✅ Generated: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

---

### Option 2: Web API (FastAPI)

#### Setup
```bash
pip install fastapi uvicorn
```

#### API Server (`app_api.py`)
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from generate_v3_full_report import V3FullReportGenerator
import os

app = FastAPI(title="ZeroSite Report API", version="3.0.0")
generator = V3FullReportGenerator()

class ReportRequest(BaseModel):
    address: str
    land_area: float
    land_params: dict
    unit_type: str = "청년"
    land_price_per_sqm: float = 5_000_000

@app.post("/api/v3/report/generate", response_class=HTMLResponse)
async def generate_report(request: ReportRequest):
    """Generate v3 Full Complete Report"""
    try:
        html = generator.generate_report(
            address=request.address,
            land_area=request.land_area,
            land_params=request.land_params,
            unit_type=request.unit_type,
            land_price_per_sqm=request.land_price_per_sqm
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/report/generate-pdf")
async def generate_pdf_report(request: ReportRequest):
    """Generate v3 Report and return PDF"""
    try:
        html = generator.generate_report(**request.dict())
        output_path = generator.save_report(html)
        
        # Convert to PDF
        from weasyprint import HTML
        pdf_path = output_path.replace(".html", ".pdf")
        HTML(output_path).write_pdf(pdf_path)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "3.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Run API Server
```bash
python app_api.py

# Or with uvicorn directly
uvicorn app_api:app --host 0.0.0.0 --port 8000 --reload
```

#### API Usage Examples
```bash
# 1. Generate HTML Report
curl -X POST "http://localhost:8000/api/v3/report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 1000,
    "land_params": {"bcr": 60, "far": 200, "max_floors": 8, "zone_type": "제2종일반주거지역"},
    "unit_type": "청년",
    "land_price_per_sqm": 5000000
  }' > report.html

# 2. Generate PDF Report
curl -X POST "http://localhost:8000/api/v3/report/generate-pdf" \
  -H "Content-Type: application/json" \
  -d '{ ... }' > report.pdf

# 3. Health Check
curl "http://localhost:8000/api/v3/health"
```

---

### Option 3: Docker Container

#### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run
```bash
# Build image
docker build -t zerosite-v3:latest .

# Run container
docker run -d -p 8000:8000 --name zerosite-v3 zerosite-v3:latest

# Check logs
docker logs zerosite-v3

# Stop container
docker stop zerosite-v3
```

#### Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  zerosite-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - CACHE_ENABLED=true
    volumes:
      - ./generated_reports:/app/generated_reports
    restart: unless-stopped
```

```bash
docker-compose up -d
```

---

## 🔌 API Integration

### Python Client
```python
import requests

class ZeroSiteClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def generate_report(self, project_data):
        response = requests.post(
            f"{self.base_url}/api/v3/report/generate",
            json=project_data
        )
        response.raise_for_status()
        return response.text
    
    def generate_pdf(self, project_data):
        response = requests.post(
            f"{self.base_url}/api/v3/report/generate-pdf",
            json=project_data
        )
        response.raise_for_status()
        return response.content

# Usage
client = ZeroSiteClient()
html = client.generate_report({
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 1000,
    "land_params": {"bcr": 60, "far": 200, "max_floors": 8},
    "unit_type": "청년"
})
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

async function generateReport(projectData) {
  const response = await axios.post(
    'http://localhost:8000/api/v3/report/generate',
    projectData,
    { headers: { 'Content-Type': 'application/json' } }
  );
  return response.data;
}

// Usage
const report = await generateReport({
  address: "서울특별시 강남구 테헤란로 123",
  land_area: 1000,
  land_params: { bcr: 60, far: 200, max_floors: 8 },
  unit_type: "청년"
});
```

---

## ⚡ Performance Optimization

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_cached_report(address, land_area, unit_type):
    # Cache report generation for same inputs
    return generator.generate_report(address, land_area, ...)
```

### 2. Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def generate_multiple_reports(projects):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(generator.generate_report, **project)
            for project in projects
        ]
        results = [f.result() for f in futures]
    return results
```

### 3. Chart Optimization
```python
# Reduce chart resolution for faster rendering
context["charts"]["cashflow_30year"] = self.chart_generator.generate_cashflow_chart(
    data,
    width=800,  # Reduced from 1200
    height=400   # Reduced from 500
)
```

---

## 📊 Monitoring & Maintenance

### Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zerosite.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Report generated successfully")
```

### Metrics Collection
```python
import time

def track_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@track_performance
def generate_report(...):
    ...
```

### Health Monitoring
```bash
# Check API health
curl http://localhost:8000/api/v3/health

# Monitor logs
tail -f zerosite.log

# Check system resources
htop
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Import Error
```
ModuleNotFoundError: No module named 'plotly'
```
**Solution**:
```bash
pip install plotly>=6.5.0
```

#### Issue 2: Template Not Found
```
jinja2.exceptions.TemplateNotFound: lh_expert_edition_v3.html.jinja2
```
**Solution**:
```bash
# Ensure template directory exists
ls app/services_v13/report_full/lh_expert_edition_v3.html.jinja2
```

#### Issue 3: PDF Generation Fails
```
OSError: cannot load library 'cairo'
```
**Solution** (Ubuntu/Debian):
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0
pip install weasyprint
```

#### Issue 4: Slow Chart Generation
**Solution**: Reduce chart resolution or disable some charts
```python
# In generate_v3_full_report.py
ENABLE_CHARTS = False  # Temporarily disable for faster generation
```

---

## 📚 Additional Resources

- **Documentation**: `/docs`
- **API Reference**: `/api/v3/docs` (when API server running)
- **GitHub Issues**: https://github.com/hellodesignthinking-png/LHproject/issues
- **Support**: 프로젝트 팀 문의

---

## ✅ Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Configuration file created (`.env` or `config.yaml`)
- [ ] Test report generation (`python generate_v3_full_report.py`)
- [ ] API server tested (if using API option)
- [ ] Docker image built (if using Docker)
- [ ] Monitoring setup (logging, metrics)
- [ ] Backup strategy configured
- [ ] Security measures applied (API keys, rate limiting)
- [ ] Documentation reviewed

---

**🎯 Ready for Production!**

**Last Updated**: 2025-12-10  
**Version**: v3.0.0  
**Status**: ✅ PRODUCTION READY
