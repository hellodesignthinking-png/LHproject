# 🚀 ZeroSite 4.0 - Staging Deployment & Visual QA Guide

**Date**: 2025-12-27  
**Version**: 4.0 (Post Emergency Fix)  
**Commit**: 83d30e7  
**Repository**: https://github.com/hellodesignthinking-png/LHproject

---

## 📋 Quick Start

```bash
# 1. Pull latest code
cd /home/user/webapp
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start staging server
python app/main.py --env=staging --port=8001
```

---

## 🔧 STEP 1: Staging Environment Setup

### 1.1 Create Staging Configuration

Create `.env.staging` file:

```bash
cat > .env.staging << 'EOF'
# ========================================
# ZeroSite 4.0 Staging Environment
# Date: 2025-12-27
# ========================================

# Application
APP_ENV=staging
APP_NAME=ZeroSite v4.0 (Staging)
DEBUG=True
LOG_LEVEL=DEBUG

# Server
HOST=0.0.0.0
PORT=8001
WORKERS=4
RELOAD=True

# Database (Use staging database)
DATABASE_URL=postgresql://zerosite_staging:staging_pass@localhost:5432/zerosite_staging

# Redis (Use staging Redis)
REDIS_URL=redis://localhost:6380/0
REDIS_CACHE_TTL=3600

# Context Storage
CONTEXT_STORAGE_BACKEND=redis
CONTEXT_TTL_SECONDS=7200

# External APIs (Use test/sandbox keys)
GOOGLE_MAPS_API_KEY=<your-staging-google-key>
KAKAO_API_KEY=<your-staging-kakao-key>
KAKAO_REST_API_KEY=<your-staging-kakao-rest-key>

# Monitoring (Optional)
SENTRY_DSN=<your-staging-sentry-dsn>
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=1.0

# CORS (Allow staging domains)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001,https://staging.zerosite.kr

# Rate Limiting (Relaxed for testing)
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# PDF Generation
PDF_GENERATION_TIMEOUT=30
PDF_MAX_CONCURRENT=5

# Performance
REQUEST_TIMEOUT=60
MAX_UPLOAD_SIZE_MB=50

# Feature Flags
ENABLE_DEBUG_ENDPOINTS=True
ENABLE_PERFORMANCE_LOGGING=True
EOF
```

### 1.2 Start Staging Server

**Option A: Direct Python (Development/Testing)**
```bash
# Load staging environment
export $(cat .env.staging | xargs)

# Start server
cd /home/user/webapp
python app/main.py
```

**Option B: Using Uvicorn (Recommended for Staging)**
```bash
# Start with staging config
cd /home/user/webapp
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --reload \
  --log-level debug \
  --env-file .env.staging
```

**Option C: Using PM2 (Production-like)**
```bash
# Create PM2 ecosystem file
cat > ecosystem.staging.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'zerosite-staging',
    script: 'uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8001 --reload',
    cwd: '/home/user/webapp',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env_file: '.env.staging',
    env: {
      NODE_ENV: 'staging',
      PYTHONUNBUFFERED: '1'
    },
    error_file: './logs/staging-error.log',
    out_file: './logs/staging-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.staging.config.js
pm2 logs zerosite-staging
```

### 1.3 Verify Server is Running

```bash
# 1. Check if server is listening
curl http://localhost:8001/health
# Expected: {"status": "ok", "version": "4.0.0"}

# 2. Check OpenAPI docs
open http://localhost:8001/docs
# Should see Swagger UI

# 3. Check logs
tail -f logs/staging-out.log  # if using PM2
# or
# Check terminal output if using direct Python/Uvicorn
```

---

## 🧪 STEP 2: Automated Smoke Tests

Run automated tests against staging:

```bash
# 1. Export staging URL
export STAGING_URL="http://localhost:8001"

# 2. Run Phase 3.5 tests (should all pass)
cd /home/user/webapp
pytest tests/test_phase35c_data_restoration.py -v --base-url=$STAGING_URL
pytest tests/test_data_propagation.py -v --base-url=$STAGING_URL

# Expected: 13/13 PASSED

# 3. Run E2E validation
pytest tests/test_phase3_e2e_validation.py -v --base-url=$STAGING_URL
# Expected: 7/7 PASSED
```

---

## 👁️ STEP 3: Visual QA - Manual Verification

### 3.1 Test Data Preparation

Create a test context with known values:

```bash
# Option 1: Use existing test context
CONTEXT_ID="test-001"

# Option 2: Create new test context via API
curl -X POST http://localhost:8001/api/v4/context/create \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "area_pyeong": 300,
    "user_id": "qa-tester-001"
  }'
# Save the returned context_id
```

### 3.2 Visual QA Checklist

#### ✅ Module M2: 토지감정평가 보고서

**HTML Preview**:
```bash
open "http://localhost:8001/api/v4/reports/M2/html?context_id=${CONTEXT_ID}"
```

**Expected Values** (Check visually):
- [ ] 토지 가치: **60.82억원** (not N/A)
- [ ] 평당 단가: **5,000만원** (not N/A)
- [ ] 신뢰도: **85.0%** (not N/A)
- [ ] M6 판단 표시: **CONDITIONAL** or **GO** or **NOGO**
- [ ] M6 점수 표시: **75.0/100** (not 0.0/100)

**PDF Download**:
```bash
curl -o "M2_토지감정평가_staging.pdf" \
  "http://localhost:8001/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}"

# Open the PDF
open M2_토지감정평가_staging.pdf
```

**PDF Visual Checklist**:
- [ ] Header: "M2 토지감정평가 보고서"
- [ ] Date: Current date (2025-12-27)
- [ ] Land value: 60.82억원 (formatted with commas)
- [ ] Unit price: 5,000만원/평
- [ ] Confidence: 85.0%
- [ ] No "N/A" values
- [ ] No "판단 정보를 불러올 수 없습니다"
- [ ] ZeroSite watermark present
- [ ] Page numbers present
- [ ] Korean text renders correctly (no garbled characters)

---

#### ✅ Module M3: LH 선호유형 보고서

**HTML Preview**:
```bash
open "http://localhost:8001/api/v4/reports/M3/html?context_id=${CONTEXT_ID}"
```

**Expected Values**:
- [ ] 추천 유형: **youth** or **newlywed** or **general** (not N/A)
- [ ] 총점: **85.5** (not 0.0)
- [ ] 수요 지수: **90.0** (not N/A)
- [ ] M6 판단 연동 확인

**PDF Download**:
```bash
curl -o "M3_LH선호유형_staging.pdf" \
  "http://localhost:8001/api/v4/reports/M3/pdf?context_id=${CONTEXT_ID}"

open M3_LH선호유형_staging.pdf
```

**PDF Visual Checklist**:
- [ ] Header: "M3 LH 선호유형 분석 보고서"
- [ ] Recommended type displayed (not N/A)
- [ ] Scores displayed with proper formatting
- [ ] Charts/graphs render correctly (if present)
- [ ] Korean text clear and readable

---

#### ✅ Module M4: 건축규모 분석 보고서

**HTML Preview**:
```bash
open "http://localhost:8001/api/v4/reports/M4/html?context_id=${CONTEXT_ID}"
```

**Expected Values**:
- [ ] 총 세대수: **20세대** (not N/A, not 0)
- [ ] 인센티브 세대수: **26세대** (not N/A)
- [ ] 연면적: **1,500㎡** (not N/A)
- [ ] 증가율 표시 확인

**PDF Download**:
```bash
curl -o "M4_건축규모_staging.pdf" \
  "http://localhost:8001/api/v4/reports/M4/pdf?context_id=${CONTEXT_ID}"

open M4_건축규모_staging.pdf
```

**PDF Visual Checklist**:
- [ ] Header: "M4 건축규모 분석 보고서"
- [ ] Total units: 20세대
- [ ] Incentive units: 26세대
- [ ] Area calculations correct
- [ ] Bar charts display correctly
- [ ] No 0 or N/A values

---

#### ✅ Module M5: 사업성 분석 보고서

**HTML Preview**:
```bash
open "http://localhost:8001/api/v4/reports/M5/html?context_id=${CONTEXT_ID}"
```

**Expected Values**:
- [ ] NPV (순현재가치): **7.93억원** (not N/A, not 0)
- [ ] IRR (내부수익률): **12.5%** (not N/A, not 0%)
- [ ] ROI (투자수익률): **15.2%** (not N/A)
- [ ] 재무 등급: **B** (not N/A)

**PDF Download**:
```bash
curl -o "M5_사업성분석_staging.pdf" \
  "http://localhost:8001/api/v4/reports/M5/pdf?context_id=${CONTEXT_ID}"

open M5_사업성분석_staging.pdf
```

**PDF Visual Checklist**:
- [ ] Header: "M5 사업성 분석 보고서"
- [ ] NPV: 7.93억원 (positive value, formatted)
- [ ] IRR: 12.5% (decimal displayed)
- [ ] ROI: 15.2% (decimal displayed)
- [ ] Financial grade: B
- [ ] Tables formatted correctly
- [ ] Currency values have commas

---

#### ✅ Module M6: LH 심사예측 보고서

**HTML Preview**:
```bash
open "http://localhost:8001/api/v4/reports/M6/html?context_id=${CONTEXT_ID}"
```

**Expected Values**:
- [ ] 판단 (Judgement): **CONDITIONAL** or **GO** or **NOGO** (not N/A)
- [ ] 총점: **75.0/100** (not 0.0/100, not N/A)
- [ ] 등급: **B** (not N/A)
- [ ] 감점 사유 리스트 표시
- [ ] 개선 제안 리스트 표시

**PDF Download**:
```bash
curl -o "M6_LH심사예측_staging.pdf" \
  "http://localhost:8001/api/v4/reports/M6/pdf?context_id=${CONTEXT_ID}"

open M6_LH심사예측_staging.pdf
```

**PDF Visual Checklist**:
- [ ] Header: "M6 LH 심사예측 보고서"
- [ ] Judgement displayed clearly (GO/CONDITIONAL/NOGO)
- [ ] Score: 75.0/100 (not 0.0)
- [ ] Grade: B (color-coded if possible)
- [ ] Section scores breakdown present
- [ ] Deduction reasons listed
- [ ] Improvement points listed
- [ ] **CRITICAL**: No "판단 정보를 불러올 수 없습니다"

---

#### ✅ Final Reports: 최종보고서 6종

Test all 6 final report types:

**1. All-in-One Report (종합 보고서)**
```bash
# HTML
open "http://localhost:8001/api/v4/reports/final/all_in_one/html?context_id=${CONTEXT_ID}"

# PDF
curl -o "Final_AllInOne_staging.pdf" \
  "http://localhost:8001/api/v4/reports/final/all_in_one/pdf?context_id=${CONTEXT_ID}"
open Final_AllInOne_staging.pdf
```

**Checklist**:
- [ ] M6 판단 표시 (CONDITIONAL/GO/NOGO)
- [ ] M2 토지 가치: 60.82억원
- [ ] M3 추천 유형 표시
- [ ] M4 세대수: 20세대
- [ ] M5 NPV: 7.93억원
- [ ] M5 IRR: 12.5%
- [ ] All sections present
- [ ] Executive summary clear

**2. Landowner Summary Report (토지주 요약 보고서)**
```bash
open "http://localhost:8001/api/v4/reports/final/landowner_summary/html?context_id=${CONTEXT_ID}"
```

**Checklist**:
- [ ] 현재 땅 가치: 60.82억원
- [ ] 예상 세대수: 20세대
- [ ] 사업 수익성 (NPV): 7.93억원
- [ ] Simplified language (non-technical)
- [ ] Key recommendations clear

**3. LH Technical Report (LH 기술검토 보고서)**
```bash
open "http://localhost:8001/api/v4/reports/final/lh_technical/html?context_id=${CONTEXT_ID}"
```

**Checklist**:
- [ ] Technical details comprehensive
- [ ] M6 score breakdown detailed
- [ ] All modules referenced
- [ ] Professional formatting

**4-6. Test remaining report types**:
```bash
# Financial Feasibility
open "http://localhost:8001/api/v4/reports/final/financial_feasibility/html?context_id=${CONTEXT_ID}"

# Quick Check
open "http://localhost:8001/api/v4/reports/final/quick_check/html?context_id=${CONTEXT_ID}"

# Internal Review
open "http://localhost:8001/api/v4/reports/final/internal_review/html?context_id=${CONTEXT_ID}"
```

---

### 3.3 Cross-Report Consistency Verification

**CRITICAL: All reports MUST show identical values**

Create a comparison spreadsheet:

| Value | M2 PDF | M3 PDF | M4 PDF | M5 PDF | M6 PDF | All-in-One | Landowner | Match? |
|-------|--------|--------|--------|--------|--------|------------|-----------|--------|
| 토지 가치 | 60.82억 | - | - | - | - | 60.82억 | 60.82억 | ✅ |
| 세대수 | - | - | 20세대 | - | - | 20세대 | 20세대 | ✅ |
| NPV | - | - | - | 7.93억 | - | 7.93억 | 7.93억 | ✅ |
| IRR | - | - | - | 12.5% | - | 12.5% | 12.5% | ✅ |
| M6 판단 | COND | COND | COND | COND | COND | COND | COND | ✅ |
| M6 점수 | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 | ✅ |

**❌ FAIL CRITERIA**: If ANY value doesn't match across reports → STOP, DO NOT DEPLOY

---

## 🐛 STEP 4: Error Scenario Testing

### 4.1 Missing Data Scenarios

**Test 1: Missing M2 Data**
```bash
# Create context without M2
curl -X POST http://localhost:8001/api/v4/context/create \
  -H "Content-Type: application/json" \
  -d '{"address": "Test", "area_pyeong": 100}'

# Try to generate M2 PDF (should FAIL FAST)
curl "http://localhost:8001/api/v4/reports/M2/pdf?context_id=${NEW_CONTEXT_ID}"
```

**Expected**:
- [ ] HTTP 400 Bad Request
- [ ] Error message: "필수 분석 데이터가 누락되었습니다: M2"
- [ ] Clear guidance: "M2 파이프라인을 먼저 실행하세요"
- [ ] NO generic "Internal Server Error"

**Test 2: Invalid Context ID**
```bash
curl "http://localhost:8001/api/v4/reports/M2/pdf?context_id=invalid-id-12345"
```

**Expected**:
- [ ] HTTP 404 Not Found
- [ ] Error message: "분석 데이터를 찾을 수 없습니다"
- [ ] Clear guidance included

---

## 📊 STEP 5: Performance Testing

### 5.1 Response Time Verification

```bash
# Test M2 PDF generation time
time curl -o /dev/null -s -w "%{time_total}\n" \
  "http://localhost:8001/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}"

# Expected: < 2 seconds
```

**Performance Targets**:
- [ ] HTML Preview: < 500ms
- [ ] PDF Generation: < 2s
- [ ] Final Report (All-in-One) PDF: < 3s

### 5.2 Concurrent Request Testing

```bash
# Generate 10 PDFs concurrently
for i in {1..10}; do
  curl -o "test_${i}.pdf" \
    "http://localhost:8001/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}" &
done
wait

# Verify all PDFs generated correctly
ls -lh test_*.pdf
```

**Expected**:
- [ ] All 10 PDFs generated
- [ ] No errors or timeouts
- [ ] File sizes consistent
- [ ] No corrupted PDFs

---

## ✅ STEP 6: Final Staging Approval

### 6.1 Sign-Off Checklist

**Code Quality**:
- [ ] All tests pass (13/13)
- [ ] No console errors in logs
- [ ] No deprecation warnings
- [ ] Type safety verified

**Data Integrity**:
- [ ] M2 values match across all reports
- [ ] M3 values match across all reports
- [ ] M4 values match across all reports
- [ ] M5 values match across all reports
- [ ] M6 values match across all reports
- [ ] No N/A values in production scenarios
- [ ] No 0.0/100 scores

**Visual Quality**:
- [ ] All PDFs render correctly
- [ ] Korean text displays properly
- [ ] Charts/graphs clear
- [ ] Professional formatting
- [ ] Consistent branding

**Error Handling**:
- [ ] FAIL FAST works (missing data)
- [ ] Clear error messages
- [ ] No stack traces exposed to users
- [ ] Proper HTTP status codes

**Performance**:
- [ ] HTML < 500ms
- [ ] PDF < 2s
- [ ] Concurrent requests OK
- [ ] No memory leaks

---

## 🚀 STEP 7: Production Deployment Approval

### 7.1 Staging Summary Report

Create a summary report for stakeholders:

```markdown
# Staging Validation Report - ZeroSite 4.0

**Date**: 2025-12-27
**Tester**: [Your Name]
**Environment**: Staging (localhost:8001)
**Commit**: 83d30e7

## Test Results

### Automated Tests
- Phase 3.5C Data Restoration: ✅ 8/8 PASSED
- Phase 3.5F Data Propagation: ✅ 5/5 PASSED
- Phase 3 E2E Validation: ✅ 7/7 PASSED
- **Total**: ✅ 20/20 PASSED

### Visual QA
- M2 토지감정평가 PDF: ✅ PASSED
- M3 선호유형 PDF: ✅ PASSED
- M4 건축규모 PDF: ✅ PASSED
- M5 사업성분석 PDF: ✅ PASSED
- M6 심사예측 PDF: ✅ PASSED
- Final Reports (6종): ✅ PASSED

### Data Consistency
- Cross-report values match: ✅ VERIFIED
- No N/A values: ✅ VERIFIED
- M6 SSOT enforced: ✅ VERIFIED

### Performance
- HTML response time: ✅ < 500ms
- PDF generation time: ✅ < 2s
- Concurrent requests: ✅ PASSED

### Error Handling
- FAIL FAST mechanism: ✅ WORKING
- User-friendly errors: ✅ VERIFIED
- No stack traces: ✅ VERIFIED

## Recommendation

✅ **APPROVED FOR PRODUCTION DEPLOYMENT**

Staging validation complete. All critical systems working as expected.
Emergency fix (Commit 83d30e7) successfully resolves PDF N/A issue.

**Next Step**: Schedule production deployment window.
```

### 7.2 Production Deployment Readiness

If all checks pass:

```bash
# Tag this version for production
cd /home/user/webapp
git tag -a v4.0.0-prod -m "Production release: Post emergency fix

- All module PDFs show real data
- 20/20 tests passing
- Staging validation complete
- FAIL FAST verified
- Cross-report consistency verified"

git push origin v4.0.0-prod
```

---

## 🔄 STEP 8: Production Deployment

### 8.1 Create Production Environment

```bash
# Copy staging config to production
cp .env.staging .env.production

# Update production-specific values
nano .env.production
```

**Production `.env` changes**:
```bash
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
PORT=8000

# Use production database
DATABASE_URL=postgresql://zerosite_prod:prod_pass@prod-db:5432/zerosite_prod

# Use production Redis
REDIS_URL=redis://prod-redis:6379/0

# Production API keys
GOOGLE_MAPS_API_KEY=<production-key>
KAKAO_API_KEY=<production-key>

# Production monitoring
SENTRY_ENVIRONMENT=production

# Strict rate limits
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=300
```

### 8.2 Production Deployment

**Option 1: Docker**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Option 2: PM2**
```bash
pm2 start ecosystem.production.config.js
pm2 save
```

### 8.3 Post-Deployment Verification

```bash
# 1. Health check
curl https://zerosite.kr/health

# 2. Generate test PDF
curl -o prod_test.pdf \
  "https://zerosite.kr/api/v4/reports/M2/pdf?context_id=${TEST_CONTEXT}"

# 3. Visual inspection
open prod_test.pdf

# 4. Monitor logs
pm2 logs zerosite-production
```

---

## 🎯 Success Criteria

### Staging Must Pass
- ✅ All 20 automated tests pass
- ✅ All module PDFs show real data (no N/A)
- ✅ All final reports show consistent values
- ✅ FAIL FAST works for missing data
- ✅ Error messages are user-friendly
- ✅ Performance meets targets (< 2s)
- ✅ Korean text renders correctly
- ✅ No console errors or warnings

### Production Must Pass
- ✅ Health endpoint returns 200
- ✅ First production PDF generates successfully
- ✅ Values match staging
- ✅ Monitoring shows no errors
- ✅ Database connection stable
- ✅ Redis connection stable

---

## 📞 Support & Rollback

### If Issues Found in Staging
```bash
# Rollback code
git revert 83d30e7

# Or checkout previous stable version
git checkout v3.5.0

# Restart server
pm2 restart zerosite-staging
```

### If Issues Found in Production
```bash
# Immediate rollback
pm2 stop zerosite-production
git checkout v3.5.0-stable
pm2 start ecosystem.production.config.js

# Alert team
# Document issue
# Plan hotfix
```

---

## 📝 Notes

- **Estimated Time**: 2-4 hours for full staging validation
- **Required**: 1 QA tester, 1 developer on standby
- **Best Time**: Low-traffic period (early morning or weekend)
- **Backup**: Always backup database before production deployment

---

**Prepared by**: AI Assistant (Claude)  
**Last Updated**: 2025-12-27  
**Version**: 1.0
