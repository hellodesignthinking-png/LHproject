# ZeroSite v7.0 - Complete Documentation

<div align="center">

![ZeroSite Logo](https://via.placeholder.com/200x80/2563eb/ffffff?text=ZeroSite)

**Enterprise-Grade LH Land Diagnosis System**

[![Version](https://img.shields.io/badge/version-7.0-blue.svg)](https://github.com/your repo/releases)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Commercial-yellow.svg)](LICENSE)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [API](#api) • [Contributing](#contributing)

</div>

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Frontend UI](#frontend-ui)
7. [LH Notice Loader v2.0](#lh-notice-loader-v20)
8. [API Reference](#api-reference)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)
13. [FAQ](#faq)
14. [Changelog](#changelog)
15. [License](#license)

---

## 🌟 Overview

**ZeroSite v7.0** is a production-ready, enterprise-grade land diagnosis system specifically designed for **LH (Korea Land & Housing Corporation)** new construction rental housing projects. It provides comprehensive analysis, automated notice processing, and interactive visualization tools.

### What's New in v7.0?

- 🗺️ **Complete Frontend UI** with interactive Leaflet maps
- 🤖 **Automated LH Notice Processing** via Google Drive integration
- 📊 **Real-time POI Analysis** with distance calculations
- 🎯 **GeoOptimizer** for alternative location recommendations
- 📦 **Multi-Parcel Analysis** with clustering
- 📄 **PDF Preview System** for instant report viewing
- 🏢 **Full Rebranding** to ZeroSite (from Antenna Holdings)

---

## 🚀 Key Features

### 1. Interactive Frontend UI

#### 🗺️ Leaflet Map Integration
- Real-time interactive maps with custom markers
- POI visualization (schools, hospitals, convenience stores, subway stations)
- Distance calculations with color-coded indicators
- Marker clustering for multi-parcel analysis
- Custom popups with detailed information

#### 🎯 GeoOptimizer
- AI-powered location recommendations
- Top 3 alternative sites with scoring
- Comparative analysis with base location
- Feature tagging and advantages/disadvantages

#### 📦 Multi-Parcel Analysis
- Batch processing of up to 10 parcels
- Visual comparison matrix
- Auto-ranking by LH score
- Color-coded grade representation

#### 📄 PDF Preview
- Real-time report preview
- Download integration
- Format support (PDF/HTML)
- Customizable sections

### 2. LH Notice Loader v2.0

#### 📥 Google Drive Sync
- Automatic PDF download from Google Drive
- Service account authentication
- Batch processing with progress tracking
- Error recovery and retry logic

#### 📜 PDF Auto-Parse
- Dual parser support (PyPDF2 + pdfplumber)
- Intelligent rule extraction
- Structured JSON output
- Multi-category classification

#### 🔄 Version Recognition
- 5 filename pattern support
- Auto-detect region, year, and round
- Version ID generation
- Processing history tracking

#### 🔧 Auto-Update LH Rules
- Automatic rule conversion
- Version management
- Latest rules API
- Backward compatibility

### 3. Core Analysis Features

#### 🏘️ Location Analysis
- POI proximity scoring
- Transportation access evaluation
- School district assessment
- Commercial facility analysis

#### 📊 Demographic Analysis
- Population statistics
- Age distribution
- Income levels
- Household composition

#### 💰 Financial Analysis
- ROI calculation
- PF (Project Financing) modeling
- IRR (Internal Rate of Return)
- NPV (Net Present Value)

#### ⚖️ LH Scoring System
- 350-point comprehensive scoring
- Grade classification (A/B/C/D)
- Exclusion criteria checking
- Approval prediction

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ZeroSite v7.0                            │
│                   Enterprise LH System                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼─────┐          ┌────▼─────┐        ┌─────▼────┐
   │ Frontend │          │  Backend │        │  External│
   │    UI    │          │   API    │        │   APIs   │
   └────┬─────┘          └────┬─────┘        └─────┬────┘
        │                     │                     │
   ┌────▼─────────────────────▼─────────────────────▼────┐
   │                                                      │
   │  • Leaflet Maps        • FastAPI         • Kakao   │
   │  • POI Visualization   • Analysis Engine • Naver   │
   │  • GeoOptimizer        • LH Rules        • OpenAPI │
   │  • Multi-Parcel        • Report Gen      • GDrive  │
   │  • PDF Preview         • Notice Loader   •         │
   │                                                      │
   └──────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Leaflet.js** - Interactive maps
- **Leaflet.markercluster** - Marker clustering
- **Font Awesome** - Icon library

#### Backend
- **Python 3.9+** - Core language
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **AsyncIO** - Async operations
- **Jinja2** - Template engine

#### Data Processing
- **PyPDF2** - PDF parsing
- **pdfplumber** - Advanced PDF extraction
- **Google Drive API** - Cloud storage integration
- **Pandas** - Data manipulation

#### External APIs
- **Kakao Maps API** - Map data
- **Naver Maps API** - Location services
- **Korea Open Data Portal** - Government data
- **LH Corporation API** - Official LH data

---

## 💻 Installation

### Prerequisites

```bash
# System Requirements
- Python 3.9 or higher
- Node.js 14.x or higher (optional, for frontend development)
- 4GB RAM minimum
- 10GB free disk space

# External Dependencies
- Google Cloud credentials (for LH Notice Loader)
- API keys for Kakao/Naver Maps (optional)
```

### Step 1: Clone Repository

```bash
git clone https://github.com/yourorg/zerosite.git
cd zerosite
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional PDF parsing libraries
pip install PyPDF2 pdfplumber

# Install Google Drive API libraries
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Required environment variables:
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google-drive-credentials.json
KAKAO_API_KEY=your_kakao_key_here (optional)
NAVER_API_KEY=your_naver_key_here (optional)
```

### Step 5: Setup Google Drive (Optional)

```bash
# Create service account in Google Cloud Console
# Download credentials JSON file
# Place in credentials/ directory
mkdir -p credentials
mv ~/Downloads/your-credentials.json credentials/google-drive-credentials.json
```

---

## ⚡ Quick Start

### Start Development Server

```bash
# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Server will be available at:
# http://localhost:8000
```

### Access Frontend UI

```bash
# Open browser to:
http://localhost:8000/frontend/

# Or use static HTML:
http://localhost:8000/static/
```

### Run LH Notice Loader Test

```bash
# Test LH Notice Loader v2.0
python test_lh_notice_loader_v2.py

# This will:
# - Test filename parsing
# - Check library availability
# - Test rule extraction
# - Sync from Google Drive (if configured)
```

### Perform Land Analysis

```bash
# Via API (curl)
curl -X POST http://localhost:8000/api/analyze-land \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "area_sqm": 1000,
    "unit_type": "신축매입임대"
  }'

# Via Frontend UI
# 1. Open http://localhost:8000/frontend/
# 2. Enter address in search box
# 3. Set area and unit type
# 4. Click "분석 시작" button
```

---

## 🗺️ Frontend UI

### Components

#### Main Interface
```
┌─────────────────────────────────────────────────────────┐
│  ZeroSite v7.0              [지도] [다중] [보고서] [대시보드] │
├─────────────┬───────────────────────────┬───────────────┤
│             │                           │               │
│  SIDEBAR    │        MAP VIEW           │  INFO PANEL   │
│             │                           │   (optional)  │
│  - Search   │  • Interactive Leaflet    │               │
│  - Options  │  • POI Markers           │  - Details    │
│  - Results  │  • Distance Lines        │  - Scores     │
│             │  • Recommendations       │  - Charts     │
│             │                           │               │
└─────────────┴───────────────────────────┴───────────────┘
```

#### Key Features

1. **Address Search**
   - Auto-complete suggestions
   - Multiple format support
   - Recent searches history

2. **Analysis Options**
   - POI Analysis toggle
   - GeoOptimizer toggle
   - Demographic Analysis toggle
   - Financial Analysis toggle

3. **Map Controls**
   - Zoom in/out
   - Layer selection
   - Distance measurement
   - Current location

4. **Results Panel**
   - LH Grade display
   - Total score
   - Demand prediction
   - Top recommendation

### Files

```
frontend/
├── index.html              # Main HTML file
├── css/
│   ├── main.css           # Core styles
│   ├── map.css            # Map styles
│   └── sidebar.css        # Sidebar styles
└── js/
    ├── config.js          # Configuration
    ├── api.js             # API service
    ├── map.js             # Map manager
    ├── poi.js             # POI handler
    ├── geooptimizer.js    # GeoOptimizer
    ├── multiparcel.js     # Multi-parcel manager
    ├── pdf-preview.js     # PDF preview
    └── main.js            # Main app
```

---

## 🤖 LH Notice Loader v2.0

### Overview

Automatically downloads, parses, and processes LH notice PDFs from Google Drive.

### Usage

#### Command Line

```bash
# Run full sync
python -c "
from app.services.lh_notice_loader_v2 import LHNoticeLoaderV2
import asyncio

loader = LHNoticeLoaderV2()
result = asyncio.run(loader.sync_from_drive())
print(result)
"

# Force resync all files
python -c "
from app.services.lh_notice_loader_v2 import LHNoticeLoaderV2
import asyncio

loader = LHNoticeLoaderV2()
result = asyncio.run(loader.sync_from_drive(force_resync=True))
print(result)
"
```

#### Python API

```python
from app.services.lh_notice_loader_v2 import LHNoticeLoaderV2
import asyncio

# Initialize loader
loader = LHNoticeLoaderV2(
    storage_dir="data/lh_notices",
    auto_update=True
)

# Sync from Google Drive
async def main():
    result = await loader.sync_from_drive()
    print(f"Synced: {result['synced_files']} files")
    print(f"New versions: {result['new_versions']}")
    
    # Get latest rules
    latest = await loader.get_latest_rules()
    print(f"Latest version: {latest['version']}")

asyncio.run(main())
```

### Filename Patterns

The loader recognizes these patterns:

```
✅ 서울25-8차민간신축매입약정방식공고문.pdf
✅ 경기24-3차_공고문_최종.pdf
✅ 부산_2025_12차_공고.pdf
✅ LH_서울_2025년_3차_공고.pdf
✅ 2025-서울-3차.pdf
```

### Output Format

```json
{
  "success": true,
  "version_id": "서울_2025_8차",
  "region": "서울",
  "year": 2025,
  "round": "8차",
  "rules": {
    "location": {
      "subway_distance": 500,
      "school_distance": 300
    },
    "building": {
      "max_floors": 15,
      "min_units": 100
    },
    "eligibility": {
      "income_limit": 70
    },
    "pricing": {
      "deposit_limit": "5,000만원"
    },
    "scoring": {
      "total_points": 150
    }
  }
}
```

---

## 📡 API Reference

### Core Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "7.0",
  "timestamp": "2025-12-01T12:00:00Z"
}
```

#### Analyze Land
```http
POST /api/analyze-land
```

**Request Body:**
```json
{
  "address": "서울특별시 마포구 월드컵북로 120",
  "area_sqm": 1000,
  "unit_type": "신축매입임대",
  "options": {
    "poi_analysis": true,
    "geo_optimizer": true,
    "demographic_analysis": true,
    "financial_analysis": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "address": "서울특별시 마포구 월드컵북로 120",
  "lh_grade": "B",
  "total_score": 315,
  "demand_prediction": "높음",
  "poi_analysis": { ... },
  "geo_recommendations": [ ... ],
  "demographics": { ... },
  "financial_analysis": { ... }
}
```

#### Multi-Parcel Analysis
```http
POST /api/analyze-multi-parcel
```

**Request Body:**
```json
{
  "parcels": [
    {
      "address": "서울특별시 마포구 월드컵북로 120",
      "area_sqm": 1000,
      "unit_type": "신축매입임대"
    },
    {
      "address": "서울특별시 송파구 올림픽로 300",
      "area_sqm": 1200,
      "unit_type": "신축매입임대"
    }
  ]
}
```

#### Generate Report
```http
POST /api/generate-report
```

**Request Body:**
```json
{
  "analysis_data": { ... },
  "format": "PDF",
  "options": {
    "include_maps": true,
    "include_charts": true,
    "include_appendix": true
  }
}
```

### LH Notice Endpoints

#### List Notices
```http
GET /api/lh-notices/list
```

#### Sync from Drive
```http
POST /api/lh-notices/sync
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Application
PORT=8000
HOST=0.0.0.0
DEBUG=False

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google-drive-credentials.json

# External APIs (Optional)
KAKAO_API_KEY=your_kakao_key
NAVER_API_KEY=your_naver_key
VWORLD_API_KEY=your_vworld_key

# Database (Future)
DATABASE_URL=postgresql://user:pass@localhost/zerosite

# Redis (Future)
REDIS_URL=redis://localhost:6379
```

### Configuration Files

```
config/
├── development.yaml    # Development settings
├── production.yaml     # Production settings
└── test.yaml          # Test settings
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run pytest
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest test_lh_notice_loader_v2.py
```

### Test LH Notice Loader

```bash
python test_lh_notice_loader_v2.py
```

Expected output:
```
======================================================================
   ZeroSite v7.0 - LH Notice Loader v2.0 Test Suite
======================================================================

1. Filename Parsing Test:
   ✅ 서울25-8차민간신축매입약정방식공고문.pdf
   ✅ 경기24-3차_공고문_최종.pdf
   ...

2. Google Drive Sync Test:
   Status: success
   Synced: 3 files
   ...
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Update environment variables
- [ ] Configure HTTPS/SSL
- [ ] Set up database connection
- [ ] Configure Redis cache
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Load testing
- [ ] Security audit

### Docker Deployment

```bash
# Build image
docker build -t zerosite:v7.0 .

# Run container
docker run -d -p 8000:8000 \
  --env-file .env \
  --name zerosite \
  zerosite:v7.0
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name zerosite.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /frontend/ {
        alias /path/to/webapp/frontend/;
    }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. PDF Parsing Fails
```bash
# Install PDF libraries
pip install PyPDF2 pdfplumber

# Verify installation
python -c "import PyPDF2; import pdfplumber; print('OK')"
```

#### 2. Google Drive Authentication Error
```bash
# Check credentials file exists
ls -l credentials/google-drive-credentials.json

# Verify file permissions
chmod 600 credentials/google-drive-credentials.json

# Test authentication
python -c "
from google.oauth2 import service_account
creds = service_account.Credentials.from_service_account_file(
    'credentials/google-drive-credentials.json'
)
print('Credentials valid')
"
```

#### 3. Frontend Not Loading
```bash
# Check if server is running
curl http://localhost:8000/health

# Check file permissions
ls -la frontend/

# Clear browser cache
# Open DevTools > Application > Clear storage
```

---

## ❓ FAQ

**Q: Do I need Google Drive for basic features?**  
A: No. Google Drive is only required for automated LH notice processing. Core analysis features work without it.

**Q: Can I use this for non-LH projects?**  
A: While designed for LH, the core analysis engine can be adapted for general real estate analysis.

**Q: What's the difference between v6.2 and v7.0?**  
A: v7.0 adds complete frontend UI, automated notice processing, and full commercial branding.

**Q: Is this open source?**  
A: No. This is commercial software. Contact ZeroSite for licensing.

**Q: How do I get API keys?**  
A: Kakao/Naver API keys can be obtained from their developer portals.

---

## 📄 Changelog

See [CHANGELOG_v7.0.md](CHANGELOG_v7.0.md) for detailed version history.

---

## 📞 Support

- **Documentation**: This README and inline code documentation
- **Email**: support@zerosite.example.com
- **Website**: https://zerosite.example.com

---

## 📜 License

© 2025 ZeroSite. All rights reserved.

Commercial license. Contact for licensing information.

---

**ZeroSite v7.0** - Enterprise-Grade LH Land Diagnosis System  
*Built with ❤️ by the ZeroSite Team*
