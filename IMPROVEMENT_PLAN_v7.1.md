# ZeroSite v7.1 - Critical Improvement Plan

**Status**: Implementation Roadmap  
**Priority**: High  
**Target Completion**: 3-5 business days

---

## 📋 Executive Summary

Based on comprehensive testing feedback, ZeroSite v7.0 requires 7 critical improvements (A-G) before achieving full production stability. This document outlines the implementation plan for v7.1.

---

## ✅ Completed (v7.0 → v7.1 Partial)

### Frontend POI Distance Classification (Issue A - PARTIAL FIX)
**Status**: ✅ 40% Complete

**Completed**:
- ✅ Added LH standard-based distance thresholds
- ✅ POI-specific color coding (excellent/good/fair/poor)
- ✅ Improved popup displays with LH criteria
- ✅ Fixed distance label accuracy

**Remaining**:
- ⏳ Real address validation with actual data
- ⏳ POI fallback logic for API failures
- ⏳ Automated test suite for 20 real addresses

---

## 🔄 In Progress

### Issue A: Frontend POI Display Stability

**Current Implementation**: 40% Complete  
**Remaining Work**:

```python
# 1. Create POI Validation & Fallback System
frontend/js/poi-validator.js:
  - Validate POI data completeness
  - Implement fallback for missing data
  - Cache POI results for performance
  - Add retry logic for API failures

# 2. Create Address Test Suite
tests/test_frontend_poi_accuracy.js:
  - Test 20 real Seoul/Gyeonggi addresses
  - Validate POI distances against Google Maps
  - Check color coding accuracy
  - Verify popup content correctness
```

**Implementation Steps**:
1. Add POI data validation layer
2. Implement fallback to mock data
3. Create automated test suite
4. Add POI accuracy metrics to dashboard

---

## ⏳ Pending Issues

### Issue B: Type Demand Score Differentiation

**Problem**: Housing type scores (청년/신혼/고령자) are too similar  
**Target**: 15+ point spread between types  
**Current**: 5-8 point spread

**Root Cause Analysis**:
```python
# Current calculation in app/main.py (lines 650-670)
type_demand_scores = {
    "청년": base_score * 0.95,      # Too similar
    "신혼": base_score * 0.92,      # Need more differentiation
    "고령자": base_score * 0.88     # Insufficient weighting
}
```

**Proposed Solution**:
```python
# New calculation with LH-based weights
def calculate_type_demand_score(base_data, housing_type):
    """
    Calculate housing type-specific demand score with proper differentiation
    
    Weights by type:
    - 청년 (Youth): POI schools low priority, transport high
    - 신혼 (Newlywed): POI schools high priority, childcare focus
    - 고령자 (Senior): POI hospital high priority, accessibility focus
    - 다자녀 (Multi-child): POI schools very high, space priority
    """
    weights = {
        "청년": {
            "poi_school": 0.1,
            "poi_hospital": 0.15,
            "poi_transport": 0.35,
            "poi_convenience": 0.25,
            "demographics": 0.15
        },
        "신혼·신생아 I": {
            "poi_school": 0.35,
            "poi_hospital": 0.20,
            "poi_transport": 0.20,
            "poi_convenience": 0.15,
            "demographics": 0.10
        },
        "고령자": {
            "poi_school": 0.05,
            "poi_hospital": 0.40,
            "poi_transport": 0.25,
            "poi_convenience": 0.20,
            "demographics": 0.10
        },
        "다자녀": {
            "poi_school": 0.45,
            "poi_hospital": 0.15,
            "poi_transport": 0.15,
            "poi_convenience": 0.15,
            "demographics": 0.10
        }
    }
    
    type_weight = weights.get(housing_type, weights["청년"])
    
    score = (
        poi_school_score * type_weight["poi_school"] * 100 +
        poi_hospital_score * type_weight["poi_hospital"] * 100 +
        poi_transport_score * type_weight["poi_transport"] * 100 +
        poi_convenience_score * type_weight["poi_convenience"] * 100 +
        demographic_score * type_weight["demographics"] * 100
    )
    
    return round(score, 1)
```

**Files to Modify**:
- `app/main.py`: Update type demand calculation (lines 650-670)
- `app/services/demand_analyzer.py`: Create if doesn't exist
- `tests/test_type_demand_differentiation.py`: New test file

**Expected Results After Fix**:
```
Address: 서울특별시 마포구 월드컵북로 120
- 청년: 88점 (high transport, low school dependency)
- 신혼: 72점 (moderate school, childcare focus)
- 고령자: 65점 (high hospital, low transport)
- 다자녀: 79점 (very high school dependency)

Spread: 23 points ✅ (Target: 15+ points)
```

---

### Issue C: LH Notice Loader PDF Parsing Accuracy

**Problem**: PDF→JSON conversion accuracy 60-70%  
**Target**: 90%+ accuracy

**Current Issues**:
1. Table structures not properly extracted
2. Page layout varies by announcement
3. Section headers not recognized
4. Numeric values mis-parsed

**Proposed Enhancement: v2.1**

```python
# app/services/lh_notice_loader_v2.1.py

class LHNoticeLoaderV21:
    """Enhanced PDF parsing with dual-engine approach"""
    
    def __init__(self):
        self.parsers = {
            'pdfplumber': PDFPlumberParser(),
            'pymupdf': PyMuPDFParser(),
            'tabula': TabulaParser()  # Best for tables
        }
    
    async def parse_pdf_enhanced(self, pdf_path):
        """
        Multi-engine PDF parsing with validation
        
        Strategy:
        1. Use pdfplumber for text
        2. Use PyMuPDF for layout
        3. Use tabula-py for tables
        4. Cross-validate results
        5. Apply LH-specific post-processing
        """
        
        # Extract with all engines
        text_pdfplumber = await self.parsers['pdfplumber'].extract(pdf_path)
        layout_pymupdf = await self.parsers['pymupdf'].extract_layout(pdf_path)
        tables_tabula = await self.parsers['tabula'].extract_tables(pdf_path)
        
        # Combine and validate
        combined = self._combine_results(
            text_pdfplumber,
            layout_pymupdf,
            tables_tabula
        )
        
        # LH-specific post-processing
        validated = self._validate_lh_rules(combined)
        
        return validated
    
    def _validate_lh_rules(self, extracted_data):
        """
        Validate extracted rules against known LH patterns
        
        Checks:
        - Distance values are reasonable (50-2000m)
        - Floor counts are valid (3-20층)
        - Unit counts make sense (10-500세대)
        - Income limits match known LH brackets
        """
        validation_rules = {
            'subway_distance': (50, 2000),
            'school_distance': (50, 1500),
            'max_floors': (3, 20),
            'min_units': (10, 500),
            'income_limit': (50, 150)  # % of median
        }
        
        for rule_name, (min_val, max_val) in validation_rules.items():
            if rule_name in extracted_data['rules']:
                value = extracted_data['rules'][rule_name]
                if not (min_val <= value <= max_val):
                    logging.warning(f"Rule {rule_name} value {value} outside valid range")
                    # Apply correction logic
                    extracted_data['rules'][rule_name] = self._correct_value(
                        rule_name, value, min_val, max_val
                    )
        
        return extracted_data
```

**New Dependencies**:
```bash
pip install tabula-py PyMuPDF
```

**Testing Strategy**:
```python
# tests/test_lh_notice_loader_v2.1.py

async def test_parse_accuracy():
    """Test PDF parsing accuracy with 20 real LH notices"""
    
    test_files = [
        "서울25-8차공고문.pdf",
        "경기24-3차공고문.pdf",
        # ... 18 more files
    ]
    
    results = []
    for pdf_file in test_files:
        extracted = await loader.parse_pdf_enhanced(pdf_file)
        accuracy = calculate_accuracy(extracted, ground_truth[pdf_file])
        results.append(accuracy)
    
    average_accuracy = sum(results) / len(results)
    assert average_accuracy >= 0.90, f"Accuracy {average_accuracy} below 90% threshold"
```

---

### Issue D: Report Expansion to v6.3 (65 pages)

**Current**: 57 pages  
**Target**: 65 pages  
**Gap**: 8 pages

**Content to Add**:

#### 1. Risk Management Tables (10 tables) - 3 pages

```markdown
## Risk Management Tables

### Table 1: Location Risk Matrix
| Risk Factor | Probability | Impact | Mitigation | Priority |
|-------------|-------------|--------|------------|----------|
| 학교 거리 초과 | Medium | High | 인근 학교 확인 | High |
| 병원 접근성 부족 | Low | High | 응급의료 체계 | Medium |
...

### Table 2: Financial Risk Matrix
| Risk Factor | Probability | Impact | Mitigation | Priority |
|-------------|-------------|--------|------------|----------|
| 사업비 초과 | High | High | 예비비 15% 확보 | Critical |
| 금리 상승 | Medium | High | 금리 헷지 전략 | High |
...

[8 more tables...]
```

#### 2. PF/IRR/NPV Sensitivity Analysis (ASCII graphs) - 2 pages

```markdown
## Financial Sensitivity Analysis

### IRR Sensitivity to Unit Price
```
IRR (%)
  12 │                          ╱
  11 │                      ╱
  10 │                  ╱
   9 │              ╱
   8 │          ╱
   7 │      ╱
   6 │  ╱
     └─────────────────────────────
     -20% -10%  0%  +10% +20%  Unit Price Change

Base IRR: 9.2%
Sensitivity: High (±2% per 10% price change)
```

[4 more ASCII sensitivity graphs...]
```

#### 3. 2026 Policy Change Scenario - 1.5 pages

```markdown
## 2026 LH Policy Change Impact Analysis

### Scenario A: Stricter Income Limits
- Current: 70% median income
- Proposed 2026: 60% median income
- Impact on target market: -15% applicant pool
- Mitigation: Focus on low-income segments

### Scenario B: Enhanced Green Building Requirements
- Current: Green Standard Level 3
- Proposed 2026: Level 2 or higher
- Additional cost: ₩2,500/㎡
- Benefit: +5 LH points

[More scenarios...]
```

#### 4. LH Legal Appendix - 1 page

```markdown
## Appendix A: LH Legal Framework

### Primary Legislation
1. 공공주택 특별법 (Public Housing Special Act)
   - Article 2: Definitions
   - Article 50-54: 신축매입임대 regulations

2. 주택법 (Housing Act)
   - Article 15: Development standards

[More legal references...]
```

#### 5. UI Mockups (ASCII) - 0.5 pages

```markdown
## UI Mockups

### Mockup 1: Main Dashboard
┌─────────────────────────────────────────────────────┐
│ ZeroSite v7.0          [지도] [다중] [보고서] [설정]  │
├─────────────┬───────────────────────────────────────┤
│  SIDEBAR    │         MAP VIEW                      │
│             │                                       │
│  📍 주소     │     [Interactive Leaflet Map]         │
│  📏 면적     │                                       │
│  🏠 유형     │     • POI Markers                     │
│             │     • Distance Lines                  │
│  [분석시작]  │     • Recommendations                │
└─────────────┴───────────────────────────────────────┘

[4 more mockups...]
```

**Implementation**:
```bash
# Generate expanded report
python generate_report_v6.3.py --sections all --output ZeroSite_Report_v6.3.md
```

---

### Issue E: Complete Branding Cleanup

**Remaining "Antenna Holdings" References**: ~20 instances

**Search and Replace Strategy**:
```bash
# 1. Find all remaining references
grep -r "Antenna Holdings" . --exclude-dir=.git > antenna_refs.txt

# 2. Automated replacement
python rebrand_to_zerosite_v2.py --thorough --include-comments --include-pdfs

# 3. Manual review of 
- PDF templates
- Image watermarks
- API response metadata
- Database schema comments
```

**Files to Check**:
- Comments in Python files (12 locations)
- Markdown footnotes (8 locations)
- Config file descriptions (3 locations)
- PDF generation templates (2 locations)

---

### Issue F: Security Hardening

**Problem**: API keys hardcoded in 7-9 files

**Solution: Environment Variable Standardization**

```python
# config/secrets.py (NEW FILE)

import os
from pathlib import Path
from cryptography.fernet import Fernet

class SecureConfig:
    """Centralized secure configuration management"""
    
    def __init__(self):
        self.env_file = Path('.env')
        self.secrets_dir = Path('secrets')
        self.secrets_dir.mkdir(exist_ok=True)
        
    def get_api_key(self, service_name):
        """Securely retrieve API key"""
        # Try environment variable first
        key = os.getenv(f'{service_name.upper()}_API_KEY')
        if key:
            return key
        
        # Fall back to encrypted secrets file
        secrets_file = self.secrets_dir / f'{service_name}.enc'
        if secrets_file.exists():
            return self._decrypt_secret(secrets_file)
        
        raise ValueError(f"No API key found for {service_name}")
    
    def _decrypt_secret(self, file_path):
        """Decrypt secret from file"""
        # Implementation using Fernet encryption
        pass

# Usage
config = SecureConfig()
kakao_key = config.get_api_key('kakao')
naver_key = config.get_api_key('naver')
```

**Environment Variables to Add**:
```bash
# .env.sample
KAKAO_API_KEY=your_kakao_key_here
NAVER_API_KEY=your_naver_key_here
VWORLD_API_KEY=your_vworld_key_here
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
GOOGLE_DRIVE_CREDENTIALS_PATH=secrets/google-drive-sa.json
DATABASE_URL=postgresql://user:pass@localhost/zerosite
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key_here
```

**Git Security**:
```bash
# Install git-secrets
brew install git-secrets  # macOS
apt-get install git-secrets  # Ubuntu

# Configure
git secrets --install
git secrets --register-aws
git secrets --add '(?i)(api[_-]?key|secret|password|token).*[=:]\s*["\047]?[0-9a-zA-Z]{20,}'
```

---

### Issue G: Enterprise Pack v1.0

**Required Documents** (5 documents, ~50 pages total):

#### 1. Security Architecture (ISO27001-based) - 15 pages

```markdown
# ZeroSite Security Architecture v1.0

## 1. Executive Summary
## 2. Security Governance
## 3. Risk Management Framework
## 4. Access Control (RBAC)
## 5. Data Protection
## 6. Incident Response
## 7. Business Continuity
## 8. Compliance (PIPA, ISO27001)
## 9. Security Monitoring
## 10. Appendix: Security Controls Matrix
```

#### 2. Privacy Policy (PIPA Compliance) - 8 pages

```markdown
# ZeroSite Privacy Policy

## 1. Overview
## 2. Information Collection
   - Personal data types
   - Collection methods
   - Legal basis (PIPA Article 15)
## 3. Use of Information
## 4. Information Sharing
## 5. Data Retention
## 6. User Rights (PIPA Article 35-38)
## 7. Security Measures
## 8. International Transfers
## 9. Contact Information
```

#### 3. Service Level Agreement (SLA) v1.0 - 10 pages

```markdown
# ZeroSite SLA v1.0

## 1. Service Description
## 2. Availability Commitment
   - Uptime: 99.5% monthly
   - Planned maintenance: 4 hours/month
## 3. Performance Metrics
   - API response time: <500ms (95th percentile)
   - Report generation: <10 seconds
## 4. Support Tiers
   - Basic: 9-6 business hours
   - Pro: 24/7 support
   - Enterprise: Dedicated support manager
## 5. Incident Response Times
## 6. Credits and Remedies
## 7. Limitations and Exclusions
```

#### 4. Pricing Model (B2B SaaS) - 5 pages

```markdown
# ZeroSite Pricing v1.0

## Tier 1: Starter (₩300,000/month)
- 50 analyses/month
- Basic POI data
- Email support
- 1 user account

## Tier 2: Professional (₩800,000/month)
- 200 analyses/month
- Full POI + GeoOptimizer
- Priority support
- 5 user accounts
- Custom reports
- API access

## Tier 3: Enterprise (Custom)
- Unlimited analyses
- White-label option
- Dedicated support
- Unlimited users
- Custom integrations
- SLA guarantee
- Training included

## Add-ons
- LH Notice Loader: +₩200,000/month
- Multi-parcel analysis: +₩150,000/month
- Custom development: ₩2,000,000/project
```

#### 5. Cloud Deployment Architecture - 12 pages

```markdown
# ZeroSite Cloud Architecture

## 1. Infrastructure Overview
   - AWS/Azure/GCP architecture
   - Multi-region deployment
   - CDN configuration

## 2. Application Layer
   - FastAPI servers (auto-scaling)
   - Redis cache layer
   - PostgreSQL database (RDS)

## 3. Security Layer
   - WAF (Web Application Firewall)
   - DDoS protection
   - SSL/TLS encryption

## 4. Monitoring & Logging
   - CloudWatch/DataDog
   - Sentry error tracking
   - ELK stack for logs

## 5. Disaster Recovery
   - RPO: 1 hour
   - RTO: 4 hours
   - Backup strategy

## 6. Cost Optimization
   - Reserved instances
   - Spot instances for batch jobs
   - S3 lifecycle policies
```

---

## 📊 Implementation Timeline

### Week 1 (Days 1-3): Core Fixes
- ✅ Day 1: Frontend POI fixes (DONE)
- ⏳ Day 2: Type demand score differentiation
- ⏳ Day 3: LH Notice Loader v2.1

### Week 2 (Days 4-5): Content & Security
- ⏳ Day 4: Report v6.3 expansion
- ⏳ Day 5: Security hardening + branding cleanup

### Week 3 (Days 6-7): Enterprise Pack
- ⏳ Day 6-7: Enterprise Pack documents (5 docs)

---

## 🧪 Testing Strategy

### Automated Tests
```bash
# Run all v7.1 tests
pytest tests/test_v7.1_improvements.py -v

# Test categories:
- test_poi_accuracy_20_addresses()
- test_type_demand_differentiation()
- test_lh_loader_parsing_accuracy()
- test_security_no_hardcoded_keys()
- test_branding_complete()
```

### Manual QA Checklist
- [ ] Test 20 real addresses with POI display
- [ ] Verify type demand scores have 15+ point spread
- [ ] Parse 20 LH PDFs and validate accuracy
- [ ] Scan for hardcoded API keys
- [ ] Search for "Antenna Holdings" references
- [ ] Review all 5 Enterprise Pack documents

---

## 📈 Success Metrics

| Metric | Current (v7.0) | Target (v7.1) | Status |
|--------|----------------|---------------|--------|
| POI Distance Accuracy | 75% | 95% | ⏳ In Progress |
| Type Demand Spread | 5-8 points | 15+ points | ⏳ Pending |
| LH Loader Accuracy | 60-70% | 90%+ | ⏳ Pending |
| Report Pages | 57p | 65p | ⏳ Pending |
| Branding Completeness | 98% | 100% | ⏳ Pending |
| Security Score | 70% | 95% | ⏳ Pending |
| Enterprise Readiness | 60% | 100% | ⏳ Pending |

---

## 💼 Resource Requirements

### Development Resources
- Senior Backend Developer: 20 hours (Type demand, LH loader)
- Frontend Developer: 12 hours (POI fixes, testing)
- DevOps Engineer: 8 hours (Security hardening)
- Technical Writer: 16 hours (Enterprise Pack)

### Testing Resources
- QA Engineer: 12 hours (Manual testing)
- Automated test development: 8 hours

### Total Estimated Effort
- Development: 40 hours
- Testing: 20 hours
- Documentation: 16 hours
- **Total: 76 hours (2 weeks with 2-person team)**

---

## 🚀 Deployment Plan

### Pre-Deployment Checklist
- [ ] All tests passing (pytest, frontend tests)
- [ ] Security scan clean (no hardcoded keys)
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Changelog prepared

### Deployment Steps
1. Deploy to staging environment
2. Run full regression test suite
3. Perform load testing (1000 concurrent users)
4. Security penetration testing
5. User acceptance testing (UAT)
6. Deploy to production (blue-green deployment)
7. Monitor for 24 hours
8. Release announcement

### Rollback Plan
- Keep v7.0 environment warm
- Database migration scripts reversible
- Feature flags for new functionality
- Automatic rollback if error rate > 5%

---

## 📞 Contact & Support

**Project Lead**: ZeroSite Development Team  
**Technical Lead**: Senior Backend Engineer  
**Questions**: See individual issue sections for detailed implementation guidance

---

**Document Version**: 1.0  
**Last Updated**: December 1, 2025  
**Status**: Active Implementation Plan
