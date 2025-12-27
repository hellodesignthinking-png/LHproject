# 🚀 ZeroSite 4.0 프로덕션 릴리즈 체크리스트

**Version**: 4.0  
**Release Date**: 2025-12-27  
**Status**: Phase 3.5B

---

## ✅ 배포 전 필수 체크리스트

### 🔒 코드 품질 & 검증

- [x] **Kill-Switch 검증**
  ```bash
  cd /home/user/webapp
  python scripts/kill_switch_checker.py
  # Expected: ✅ PASSED (0 CRITICAL, 0 WARNING)
  ```
  - Status: ✅ PASSED
  - Last Check: 2025-12-27

- [x] **E2E 테스트**
  ```bash
  pytest tests/test_phase3_e2e_validation.py -v
  # Expected: 7/7 PASSED
  ```
  - Status: ✅ 7/7 PASSED
  - Last Check: 2025-12-27

- [x] **6종 보고서 일관성**
  - AllInOneReport: ✅
  - LandownerSummaryReport: ✅
  - LHTechnicalReport: ✅
  - FinancialFeasibilityReport: ✅
  - QuickCheckReport: ✅
  - PresentationReport: ✅

- [x] **M6 중심성 검증**
  - M6SingleSourceOfTruth 구조: ✅
  - ReportConsistencyError 구현: ✅
  - get_conclusion_sentence() 통일: ✅

---

### 📊 성능 & 안정성

- [ ] **부하 테스트**
  ```bash
  # 동시 요청 100개 처리 테스트
  locust -f tests/load_test.py --headless -u 100 -r 10
  ```
  - Target: 평균 응답시간 < 3초
  - Status: ⏳ TODO

- [ ] **메모리 누수 체크**
  ```bash
  # 장시간 실행 후 메모리 모니터링
  python -m memory_profiler app/main.py
  ```
  - Status: ⏳ TODO

- [ ] **에러 핸들링 검증**
  - M6 결과 없을 때: ✅ ValueError 발생
  - 일관성 검증 실패: ✅ ReportConsistencyError 발생
  - 네트워크 오류: ⏳ TODO

---

### 🔐 보안 & 권한

- [ ] **API 키 관리**
  - 환경 변수로 분리: ⏳ TODO
  - .env 파일 .gitignore 추가: ⏳ TODO
  
- [ ] **입력 검증**
  - SQL Injection 방어: ⏳ TODO
  - XSS 방어: ⏳ TODO
  - CSRF 토큰: ⏳ TODO

- [ ] **접근 제어**
  - 관리자 전용 엔드포인트: ⏳ TODO
  - API Rate Limiting: ⏳ TODO

---

### 📝 문서화

- [x] **기술 문서**
  - PHASE_3_5A_OUTPUT_LOCK_COMPLETE.md: ✅
  - PHASE_3_PLUS_SYSTEM_HARDENING_COMPLETE.md: ✅
  - PHASE_3_FINAL_COMPLETE_REPORT.md: ✅

- [x] **API 문서**
  - Swagger/OpenAPI 스펙: ⏳ 자동 생성 (FastAPI)

- [ ] **사용자 가이드**
  - LH 담당자용 매뉴얼: ⏳ TODO
  - 토지주용 간편 가이드: ⏳ TODO

- [ ] **운영 가이드**
  - 배포 절차: ⏳ (이 문서)
  - 장애 대응: ⏳ TODO
  - Kill-Switch 모니터링: ✅ (scripts/kill_switch_checker.py)

---

### 🌐 배포 환경

- [ ] **환경 설정**
  - 개발(DEV): ⏳ localhost
  - 스테이징(STAGING): ⏳ TODO
  - 프로덕션(PROD): ⏳ TODO

- [ ] **데이터베이스**
  - Migration 스크립트: ⏳ TODO
  - 백업 전략: ⏳ TODO

- [ ] **모니터링**
  - 로그 수집: ⏳ TODO
  - 에러 추적 (Sentry 등): ⏳ TODO
  - 성능 모니터링: ⏳ TODO

---

## 🚦 배포 단계별 절차

### Stage 1: 사전 준비 (Pre-deployment)

```bash
# 1. 최신 코드 동기화
git pull origin main

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Kill-Switch 검증
python scripts/kill_switch_checker.py

# 4. E2E 테스트
pytest tests/test_phase3_e2e_validation.py -v

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (API 키, DB 연결 등)
```

**✅ Pass Criteria**: Kill-Switch PASSED, E2E 7/7 PASSED

---

### Stage 2: 스테이징 배포 (Staging)

```bash
# 1. 스테이징 서버에 배포
git push staging main

# 2. 스테이징 환경에서 검증
curl https://staging.zerosite.com/health
# Expected: {"status": "healthy"}

# 3. 통합 테스트 실행
pytest tests/integration/ -v --staging

# 4. 사용자 시나리오 테스트
# - LH 담당자 시나리오
# - 토지주 시나리오
# - 관리자 시나리오
```

**✅ Pass Criteria**: 모든 시나리오 정상 동작

---

### Stage 3: 프로덕션 배포 (Production)

```bash
# 1. 배포 태그 생성
git tag -a v4.0.0 -m "ZeroSite 4.0 - Phase 3.5B Production Release"
git push origin v4.0.0

# 2. 프로덕션 배포
git push production main

# 3. 배포 후 즉시 검증
curl https://api.zerosite.com/health
# Expected: {"status": "healthy"}

# 4. Kill-Switch 즉시 실행
ssh production-server
cd /app
python scripts/kill_switch_checker.py
# Expected: ✅ PASSED

# 5. 모니터링 대시보드 확인
# - 에러율 < 1%
# - 평균 응답시간 < 3초
# - CPU/메모리 정상 범위
```

**✅ Pass Criteria**: 
- Health check 성공
- Kill-Switch PASSED
- 모니터링 정상

---

### Stage 4: 배포 후 모니터링 (Post-deployment)

```bash
# 1시간 집중 모니터링
watch -n 60 'curl -s https://api.zerosite.com/metrics'

# 주요 모니터링 지표:
# - 요청 처리량 (RPS)
# - 에러율 (%)
# - P95 응답시간 (ms)
# - M6 판단 일관성 (자동 검증)
```

**모니터링 기간**: 
- 1시간: 집중 모니터링
- 24시간: 주기적 확인
- 7일: 안정화 확인

---

## 🔄 롤백 절차

### 긴급 롤백 (Critical Issues)

**롤백 트리거:**
- Kill-Switch FAILED
- E2E 테스트 실패
- 에러율 > 5%
- M6 일관성 깨짐

```bash
# 1. 즉시 이전 버전으로 롤백
git revert HEAD
git push production main

# 2. 또는 태그 기반 롤백
git checkout v3.5.0
git push production main --force

# 3. 롤백 후 검증
python scripts/kill_switch_checker.py
pytest tests/test_phase3_e2e_validation.py -v

# 4. 사후 분석
# - 로그 수집
# - 원인 파악
# - 수정 계획 수립
```

---

## 📊 배포 성공 기준

### 필수 조건 (MUST)

- ✅ Kill-Switch: PASSED (0 CRITICAL, 0 WARNING)
- ✅ E2E Tests: 7/7 PASSED
- ✅ 6종 보고서 일관성: 100%
- ✅ M6 중심성: 검증 완료
- ⏳ 에러율: < 1%
- ⏳ 평균 응답시간: < 3초

### 권장 조건 (SHOULD)

- ⏳ 부하 테스트: 100 동시 사용자 처리
- ⏳ 메모리 사용: < 2GB
- ⏳ CPU 사용: < 70%
- ⏳ 로그 수집: 실시간
- ⏳ 모니터링 대시보드: 구축

---

## 🎯 Phase 3.5B 완료 기준

### 기술적 완성도
- [x] Kill-Switch: 0 위반
- [x] E2E Tests: 100% 통과
- [x] 코드베이스 정화: 완료

### 운영 준비도
- [x] 릴리즈 체크리스트: ✅ (이 문서)
- [ ] 배포 스크립트: ⏳ TODO
- [ ] 모니터링 시스템: ⏳ TODO
- [x] Kill-Switch 자동화: ✅ (scripts/kill_switch_checker.py)

### 문서화
- [x] 기술 문서: ✅ (Phase 3 시리즈)
- [ ] 사용자 가이드: ⏳ TODO
- [x] 운영 가이드: ✅ (이 문서)

---

## 📝 배포 로그 템플릿

```markdown
## 배포 기록

**Date**: YYYY-MM-DD HH:MM
**Version**: v4.0.0
**Environment**: Production
**Deployed By**: [이름]

### Pre-deployment Checks
- [ ] Kill-Switch: PASSED
- [ ] E2E Tests: 7/7 PASSED
- [ ] Code Review: Approved
- [ ] Staging Test: PASSED

### Deployment Steps
- [ ] 1. Git tag created
- [ ] 2. Production push
- [ ] 3. Health check
- [ ] 4. Kill-Switch verification
- [ ] 5. Monitoring check

### Post-deployment Status
- Error Rate: __%
- Avg Response Time: __ms
- Active Users: __
- M6 Consistency: __/__ PASSED

### Issues
- None / [이슈 설명]

### Rollback
- Not Required / Executed at [시각]
```

---

**릴리즈 체크리스트 버전**: 1.0  
**최종 업데이트**: 2025-12-27  
**관리자**: ZeroSite 4.0 Team
