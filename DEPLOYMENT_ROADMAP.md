# 🚀 ZeroSite 4.0 Deployment Roadmap

**Date**: 2025-12-27  
**Current Status**: Phase 3.5F Complete (100% Production Ready)  
**Repository**: https://github.com/hellodesignthinking-png/LHproject  
**Final Commit**: bb1f364

---

## 📋 DEPLOYMENT PHASES

### Phase 1: Pre-Deployment Verification ✅
**Status**: COMPLETE  
**Duration**: Completed

- [x] All tests passing (20/20)
- [x] Data propagation verified
- [x] HTML/PDF/Report consistency verified
- [x] FAIL FAST enforcement active
- [x] Type safety verified
- [x] Git history clean
- [x] Documentation complete

---

### Phase 2: Staging Deployment 🟡
**Status**: READY TO START  
**Duration**: 2-4 hours  
**Owner**: DevOps Team

#### 2.1 Environment Setup

**Create Staging Environment**:
```bash
# 1. Clone production environment configuration
cp .env.production .env.staging

# 2. Update staging-specific variables
# - Database: staging database
# - API keys: staging keys
# - Debug: Enable detailed logging
# - Rate limits: Relaxed for testing

# 3. Deploy to staging server
git checkout main
git pull origin main
docker-compose -f docker-compose.staging.yml up -d
```

**Environment Variables** (`.env.staging`):
```bash
# Application
APP_ENV=staging
DEBUG=True
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://user:pass@staging-db:5432/zerosite_staging

# Redis
REDIS_URL=redis://staging-redis:6379/0

# External APIs (use staging keys)
GOOGLE_MAPS_API_KEY=<staging-key>
KAKAO_API_KEY=<staging-key>

# Monitoring
SENTRY_DSN=<staging-sentry-dsn>
SENTRY_ENVIRONMENT=staging

# Performance
MAX_WORKERS=4
TIMEOUT=60
```

#### 2.2 Database Migration

```bash
# 1. Backup current staging database
pg_dump -U user -d zerosite_staging > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
alembic upgrade head

# 3. Verify migration
psql -U user -d zerosite_staging -c "SELECT version_num FROM alembic_version;"
```

#### 2.3 Deployment Verification

**Health Checks**:
```bash
# 1. Application health
curl https://staging.zerosite.kr/health
# Expected: {"status": "healthy", "version": "4.0.0"}

# 2. Database connection
curl https://staging.zerosite.kr/api/health/db
# Expected: {"status": "connected"}

# 3. Redis connection
curl https://staging.zerosite.kr/api/health/redis
# Expected: {"status": "connected"}

# 4. External APIs
curl https://staging.zerosite.kr/api/health/external
# Expected: {"google_maps": "ok", "kakao": "ok"}
```

**Smoke Tests**:
```bash
# Run smoke test suite
pytest tests/smoke/ -v

# Expected: All critical paths working
# - User authentication
# - M2-M6 pipeline execution
# - HTML report generation
# - PDF generation
# - API endpoints
```

---

### Phase 3: Visual QA 🟡
**Status**: PENDING STAGING  
**Duration**: 4-8 hours  
**Owner**: QA Team + Product Manager

#### 3.1 Test Scenarios

**Scenario 1: Complete Pipeline E2E**
1. Login as test user
2. Enter land address: "서울특별시 강남구 테헤란로 123"
3. Run M2-M6 pipeline
4. Verify HTML report displays:
   - M6 judgment (CONDITIONAL/GO/NOGO)
   - M2 land value (formatted: "60.82억원")
   - M3 recommended type ("youth")
   - M4 unit count ("20세대")
   - M5 NPV ("7.93억원")
5. Download PDF (all 6 modules)
6. Verify PDF M6 header on all module PDFs

**Scenario 2: Data Change Propagation**
1. Modify M2 land value in system
2. Re-generate report
3. Verify HTML shows updated value immediately
4. Download PDF
5. Verify PDF shows same updated value

**Scenario 3: Error Handling**
1. Enter invalid address
2. Verify user-friendly error message (not stack trace)
3. Verify error message in Korean
4. Verify system doesn't crash

**Scenario 4: Multi-User Concurrent Access**
1. Open 5 browser tabs
2. Run pipeline in each tab simultaneously
3. Verify all complete without errors
4. Verify no cross-contamination of data

**Scenario 5: 6 Report Types**
1. Generate all 6 report types:
   - All-in-One
   - Landowner Summary
   - Quick Check
   - LH Technical
   - Financial Feasibility
   - Presentation
2. Verify M6 judgment identical across all
3. Verify key numbers (land value, units, NPV) identical

#### 3.2 Visual Regression Testing

**Screenshot Comparison**:
```bash
# 1. Generate baseline screenshots (first time only)
npm run test:visual:baseline

# 2. Run visual regression tests
npm run test:visual

# 3. Review differences
npm run test:visual:review
```

**Manual Visual Checks**:
- [ ] Font rendering correct (Korean characters)
- [ ] Colors match design (GO: green, CONDITIONAL: orange, NOGO: red)
- [ ] Spacing/padding consistent
- [ ] Mobile responsive (iPhone, Galaxy)
- [ ] Tablet responsive (iPad)
- [ ] Desktop (1920x1080, 2560x1440)
- [ ] Print preview (PDF generation)

#### 3.3 Cross-Browser Testing

**Desktop Browsers**:
- [ ] Chrome 120+ (Windows, macOS)
- [ ] Firefox 120+ (Windows, macOS)
- [ ] Safari 17+ (macOS)
- [ ] Edge 120+ (Windows)

**Mobile Browsers**:
- [ ] Chrome Mobile (Android 13+)
- [ ] Safari Mobile (iOS 16+)
- [ ] Samsung Internet (Android)

**Expected**: All features work identically across browsers.

---

### Phase 4: Performance Testing 🟡
**Status**: PENDING STAGING  
**Duration**: 4-6 hours  
**Owner**: DevOps + Backend Team

#### 4.1 Load Testing

**Test 1: Baseline Load**
```bash
# Use Locust or k6
locust -f tests/performance/load_test.py --host=https://staging.zerosite.kr

# Configuration:
# - Users: 50 concurrent
# - Spawn rate: 5 users/sec
# - Duration: 10 minutes
```

**Metrics to Monitor**:
- Response time (p50, p95, p99)
  - Expected p50: < 500ms
  - Expected p95: < 2000ms
  - Expected p99: < 5000ms
- Throughput (requests/sec)
  - Expected: > 100 req/s
- Error rate
  - Expected: < 0.1%
- CPU usage
  - Expected: < 70%
- Memory usage
  - Expected: < 80%

**Test 2: Stress Test**
```bash
# Gradual ramp-up to find breaking point
locust -f tests/performance/stress_test.py

# Ramp: 50 → 100 → 200 → 500 → 1000 users
# Duration: 30 minutes
```

**Test 3: Spike Test**
```bash
# Sudden traffic spike
locust -f tests/performance/spike_test.py

# Pattern: 10 users → 500 users (instant) → 10 users
# Duration: 5 minutes
```

#### 4.2 PDF Generation Performance

**Batch PDF Test**:
```python
import time
from app.api.endpoints.pdf_reports import generate_module_pdf

# Generate 100 PDFs sequentially
start = time.time()
for i in range(100):
    pdf = generate_module_pdf("M2", assembled_data)
end = time.time()

avg_time = (end - start) / 100
print(f"Average PDF generation time: {avg_time:.2f}s")

# Expected: < 3 seconds per PDF
```

**Concurrent PDF Test**:
```python
import asyncio

async def generate_pdfs_concurrent():
    tasks = [generate_module_pdf_async("M2", assembled_data) for _ in range(50)]
    results = await asyncio.gather(*tasks)
    return results

# Expected: All complete within 10 seconds
```

#### 4.3 Database Performance

**Query Analysis**:
```sql
-- Enable query logging
ALTER DATABASE zerosite_staging SET log_statement = 'all';
ALTER DATABASE zerosite_staging SET log_duration = on;

-- Run typical workload, then analyze slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 100  -- queries taking > 100ms
ORDER BY mean_time DESC
LIMIT 20;
```

**Expected**: No queries > 500ms average.

#### 4.4 Caching Performance

**Redis Cache Hit Rate**:
```bash
redis-cli --stat

# Expected cache hit rate: > 80%
```

**Test Cache Effectiveness**:
```python
import time

# First request (cache miss)
start = time.time()
response1 = client.get("/api/land-info/서울특별시강남구테헤란로123")
time1 = time.time() - start

# Second request (cache hit)
start = time.time()
response2 = client.get("/api/land-info/서울특별시강남구테헤란로123")
time2 = time.time() - start

speedup = time1 / time2
print(f"Cache speedup: {speedup:.1f}x")

# Expected: > 10x speedup
```

---

### Phase 5: Security Audit 🟡
**Status**: PENDING STAGING  
**Duration**: 2-4 hours  
**Owner**: Security Team

#### 5.1 Vulnerability Scanning

**Dependencies**:
```bash
# Python dependencies
pip install safety
safety check

# JavaScript dependencies (if any)
npm audit

# Expected: No high/critical vulnerabilities
```

**OWASP Top 10 Checks**:
- [ ] SQL Injection (parameterized queries)
- [ ] XSS (input sanitization)
- [ ] CSRF (token validation)
- [ ] Authentication (JWT validation)
- [ ] Authorization (role-based access)
- [ ] Sensitive data exposure (encrypted storage)
- [ ] Security misconfiguration (headers, CORS)
- [ ] Known vulnerabilities (dependency scan)
- [ ] Insufficient logging (audit trail)
- [ ] Deserialization attacks (input validation)

#### 5.2 API Security

**Rate Limiting**:
```bash
# Test rate limit enforcement
for i in {1..150}; do
  curl -w "%{http_code}\n" -o /dev/null -s https://staging.zerosite.kr/api/land-info/test
done

# Expected: First 100 succeed (200), remaining fail (429)
```

**Authentication**:
```bash
# Test without token
curl https://staging.zerosite.kr/api/reports
# Expected: 401 Unauthorized

# Test with invalid token
curl -H "Authorization: Bearer invalid" https://staging.zerosite.kr/api/reports
# Expected: 401 Unauthorized

# Test with valid token
curl -H "Authorization: Bearer $VALID_TOKEN" https://staging.zerosite.kr/api/reports
# Expected: 200 OK
```

#### 5.3 Data Privacy

**PII Protection**:
- [ ] User passwords hashed (bcrypt/argon2)
- [ ] API keys not logged
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS enforced (no HTTP)
- [ ] Secure cookies (HttpOnly, Secure, SameSite)

**GDPR Compliance** (if applicable):
- [ ] User data export API
- [ ] User data deletion API
- [ ] Privacy policy accessible
- [ ] Cookie consent banner

---

### Phase 6: Monitoring Setup 🟡
**Status**: PENDING STAGING  
**Duration**: 2-3 hours  
**Owner**: DevOps Team

#### 6.1 Application Monitoring (Sentry)

**Configuration**:
```python
# app/core/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.APP_ENV,
    traces_sample_rate=0.1,  # 10% performance monitoring
    integrations=[FastApiIntegration()],
)
```

**Alerts**:
- Error rate > 1% (5 min window) → Slack alert
- Response time p95 > 5s (5 min window) → Slack alert
- Memory usage > 90% → PagerDuty alert

#### 6.2 Infrastructure Monitoring (Prometheus + Grafana)

**Metrics to Track**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'zerosite-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Key Metrics**:
- Request rate (requests/sec)
- Error rate (errors/sec)
- Response time (p50, p95, p99)
- Active connections
- Database connections
- Redis connections
- CPU/Memory/Disk usage

**Dashboards**:
1. **Overview Dashboard**
   - Request rate (last 24h)
   - Error rate (last 24h)
   - Response time (last 24h)
   - Active users

2. **Performance Dashboard**
   - API endpoint latencies
   - Database query times
   - Cache hit rates
   - PDF generation times

3. **Infrastructure Dashboard**
   - CPU usage per service
   - Memory usage per service
   - Disk I/O
   - Network I/O

#### 6.3 Log Aggregation (ELK Stack or CloudWatch)

**Log Format** (JSON):
```json
{
  "timestamp": "2025-12-27T12:34:56.789Z",
  "level": "INFO",
  "service": "zerosite-api",
  "request_id": "abc-123-def",
  "user_id": "user-456",
  "endpoint": "/api/reports",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 345,
  "message": "Report generated successfully"
}
```

**Log Retention**:
- Staging: 7 days
- Production: 90 days

---

### Phase 7: Canary Deployment 🔴
**Status**: PENDING STAGING VALIDATION  
**Duration**: 24-48 hours  
**Owner**: DevOps + Product Team

#### 7.1 Canary Strategy

**Deployment Plan**:
```
Stage 1: 1% of traffic → New version
         99% of traffic → Old version
         Duration: 2 hours
         Monitor: Error rate, latency

Stage 2: 10% of traffic → New version
         90% of traffic → Old version
         Duration: 6 hours
         Monitor: Error rate, latency, user feedback

Stage 3: 50% of traffic → New version
         50% of traffic → Old version
         Duration: 12 hours
         Monitor: Error rate, latency, user feedback

Stage 4: 100% of traffic → New version
         Old version: Standby (ready for rollback)
         Duration: 24 hours
         Monitor: All metrics

Stage 5: Decommission old version
```

#### 7.2 Rollback Criteria

**Auto-Rollback Triggers**:
- Error rate > 5% (compared to baseline)
- Response time p95 > 3x baseline
- Critical errors (500) > 10 in 5 minutes
- User complaints > threshold

**Manual Rollback Command**:
```bash
# Instant rollback to previous version
kubectl rollout undo deployment/zerosite-api

# Or with specific revision
kubectl rollout undo deployment/zerosite-api --to-revision=2
```

#### 7.3 Success Criteria

**Canary Passes If**:
- [ ] Error rate < baseline + 0.5%
- [ ] Response time p95 < baseline + 20%
- [ ] Zero critical errors
- [ ] User feedback positive
- [ ] No data loss
- [ ] No data corruption

---

### Phase 8: Production Deployment 🔴
**Status**: PENDING CANARY SUCCESS  
**Duration**: 1-2 hours  
**Owner**: DevOps Team

#### 8.1 Pre-Deployment Checklist

**Code**:
- [ ] All tests passing (20/20)
- [ ] Code review approved (2+ reviewers)
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Documentation updated

**Infrastructure**:
- [ ] Production database backed up
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Incident response team on standby

**Communication**:
- [ ] Stakeholders notified (email)
- [ ] Maintenance window scheduled (if needed)
- [ ] Support team briefed
- [ ] Documentation published

#### 8.2 Deployment Steps

**1. Database Migration** (if needed):
```bash
# 1. Enable maintenance mode (optional)
redis-cli SET maintenance_mode true

# 2. Backup production database
pg_dump -U user -d zerosite_prod > backup_production_$(date +%Y%m%d_%H%M%S).sql

# 3. Run migrations
alembic -c alembic.production.ini upgrade head

# 4. Verify migration
psql -U user -d zerosite_prod -c "SELECT version_num FROM alembic_version;"

# 5. Disable maintenance mode
redis-cli DEL maintenance_mode
```

**2. Application Deployment**:
```bash
# Blue-Green Deployment (recommended)

# 1. Deploy to "green" environment
kubectl apply -f k8s/deployment-green.yml

# 2. Wait for green to be healthy
kubectl wait --for=condition=ready pod -l app=zerosite-green --timeout=300s

# 3. Run smoke tests on green
pytest tests/smoke/ --host=green.zerosite.kr

# 4. Switch traffic to green
kubectl apply -f k8s/service-green.yml

# 5. Monitor for 10 minutes
# If issues: kubectl apply -f k8s/service-blue.yml (rollback)
# If success: kubectl delete -f k8s/deployment-blue.yml (cleanup)
```

**3. Post-Deployment Verification**:
```bash
# 1. Health check
curl https://api.zerosite.kr/health

# 2. Version check
curl https://api.zerosite.kr/version
# Expected: {"version": "4.0.0", "commit": "bb1f364"}

# 3. Smoke tests
pytest tests/smoke/ --host=api.zerosite.kr -v

# 4. Monitor logs (first 5 minutes)
kubectl logs -f deployment/zerosite-api --tail=100

# 5. Check error rate in Sentry
# Expected: < 0.1%
```

---

### Phase 9: Post-Deployment Monitoring 🔴
**Status**: PENDING PRODUCTION DEPLOYMENT  
**Duration**: 7 days  
**Owner**: Entire Team

#### 9.1 Day 1-3: Intensive Monitoring

**Hourly Checks**:
- [ ] Error rate < 0.1%
- [ ] Response time p95 < 2s
- [ ] CPU usage < 70%
- [ ] Memory usage < 80%
- [ ] Zero critical errors
- [ ] User feedback positive

**Daily Metrics Review**:
- Total requests
- Total errors
- Slowest endpoints
- Most active users
- PDF generations
- Cache hit rate

#### 9.2 Day 4-7: Standard Monitoring

**Daily Checks**:
- [ ] Error rate < 0.5%
- [ ] Response time stable
- [ ] Infrastructure stable
- [ ] User feedback reviewed

**Weekly Team Sync**:
- Review key metrics
- Discuss user feedback
- Identify improvements
- Plan next iteration

#### 9.3 Incident Response Plan

**Severity Levels**:

**P0 (Critical) - Service Down**:
- Response time: 15 minutes
- Team: All hands on deck
- Action: Immediate rollback + investigation
- Communication: Status page + email

**P1 (Major) - Degraded Performance**:
- Response time: 1 hour
- Team: On-call engineer + backend lead
- Action: Investigate + fix or rollback
- Communication: Status page

**P2 (Minor) - Non-Critical Issue**:
- Response time: 4 hours
- Team: On-call engineer
- Action: Create ticket + fix in next release
- Communication: Internal only

**P3 (Trivial) - Enhancement Request**:
- Response time: Next sprint
- Team: Product manager
- Action: Add to backlog
- Communication: None

---

## 📊 SUCCESS METRICS

### Technical Metrics

| Metric | Baseline | Target | Threshold |
|--------|----------|--------|-----------|
| Response Time (p95) | 800ms | < 2s | < 5s |
| Error Rate | 0.05% | < 0.1% | < 1% |
| Availability | 99.5% | > 99.9% | > 99.5% |
| PDF Generation | 2.5s | < 3s | < 10s |
| Cache Hit Rate | 75% | > 80% | > 70% |
| Database Query Time | 50ms | < 100ms | < 500ms |

### Business Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| User Satisfaction | N/A | > 4.5/5 | User survey |
| Report Completions | N/A | > 90% | Analytics |
| Time to Report | N/A | < 5 min | User flow |
| PDF Downloads | N/A | > 80% | Analytics |
| Repeat Users | N/A | > 60% | Weekly actives |

---

## 🚨 ROLLBACK PROCEDURES

### Scenario 1: High Error Rate

**Trigger**: Error rate > 5% for 5 minutes

**Action**:
```bash
# 1. Immediate rollback
kubectl rollout undo deployment/zerosite-api

# 2. Verify rollback success
kubectl rollout status deployment/zerosite-api

# 3. Check error rate returns to normal
# Monitor Sentry dashboard

# 4. Investigate root cause
kubectl logs deployment/zerosite-api --previous

# 5. Create incident report
```

### Scenario 2: Database Issue

**Trigger**: Database connection failures

**Action**:
```bash
# 1. Restore database from backup
pg_restore -U user -d zerosite_prod backup_production_TIMESTAMP.sql

# 2. Rollback application
kubectl rollout undo deployment/zerosite-api

# 3. Verify database integrity
psql -U user -d zerosite_prod -c "SELECT COUNT(*) FROM reports;"

# 4. Run data consistency checks
python scripts/verify_data_integrity.py
```

### Scenario 3: Performance Degradation

**Trigger**: Response time p95 > 10s

**Action**:
```bash
# 1. Scale up immediately (buy time)
kubectl scale deployment/zerosite-api --replicas=10

# 2. Investigate bottleneck
# - Check database slow queries
# - Check external API latencies
# - Check memory leaks

# 3. If no quick fix, rollback
kubectl rollout undo deployment/zerosite-api

# 4. Scale down
kubectl scale deployment/zerosite-api --replicas=4
```

---

## 📝 DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] All tests passing (20/20)
- [ ] Code review approved
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Staging validation complete
- [ ] Database backup created
- [ ] Rollback plan documented
- [ ] Stakeholders notified
- [ ] Support team briefed

### Deployment
- [ ] Maintenance mode enabled (if needed)
- [ ] Database migration successful
- [ ] Application deployed
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Monitoring alerts active
- [ ] Maintenance mode disabled

### Post-Deployment
- [ ] Error rate < 0.1%
- [ ] Response time < 2s
- [ ] Zero critical errors
- [ ] User feedback positive
- [ ] Monitoring stable
- [ ] Documentation updated
- [ ] Team debriefed

---

## 👥 TEAM RESPONSIBILITIES

### DevOps Team
- Environment setup
- Deployment execution
- Monitoring configuration
- Incident response (technical)

### Backend Team
- Code quality
- Performance optimization
- Database migrations
- API stability

### QA Team
- Test execution
- Bug reporting
- Visual QA
- User acceptance testing

### Product Team
- Business metrics tracking
- User feedback collection
- Feature validation
- Stakeholder communication

### Support Team
- User issue triage
- Documentation updates
- User training
- Feedback escalation

---

## 📞 CONTACT LIST

### On-Call Schedule
- **Week 1**: DevOps Lead + Backend Senior
- **Week 2**: DevOps Engineer + Backend Developer
- **Week 3**: Rotation continues...

### Escalation Path
1. On-call Engineer (15 min response)
2. Team Lead (30 min response)
3. Engineering Manager (1 hour response)
4. CTO (Critical only)

### Communication Channels
- **Slack**: #zerosite-alerts (auto alerts)
- **Slack**: #zerosite-ops (team discussion)
- **PagerDuty**: Critical alerts
- **Email**: deployment-team@company.com
- **Status Page**: status.zerosite.kr

---

## 🎯 TIMELINE SUMMARY

| Phase | Duration | Start After |
|-------|----------|-------------|
| 1. Pre-Deployment Verification | ✅ Done | - |
| 2. Staging Deployment | 2-4 hours | Phase 1 |
| 3. Visual QA | 4-8 hours | Phase 2 |
| 4. Performance Testing | 4-6 hours | Phase 3 |
| 5. Security Audit | 2-4 hours | Phase 3 |
| 6. Monitoring Setup | 2-3 hours | Phase 2 |
| 7. Canary Deployment | 24-48 hours | Phase 3,4,5 |
| 8. Production Deployment | 1-2 hours | Phase 7 |
| 9. Post-Deployment Monitoring | 7 days | Phase 8 |

**Total Estimated Time**: 2-3 weeks (with buffer)

**Fastest Path** (if all phases green-lit): 3-5 days

---

## 📖 LESSONS LEARNED (TO BE UPDATED)

_This section will be updated after production deployment._

### What Went Well
- TBD

### What Could Be Improved
- TBD

### Action Items for Next Release
- TBD

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-27  
**Next Review**: After Production Deployment  
**Owner**: DevOps Team

---

**Ready to Deploy?** ✅  
Let's go to production! 🚀
