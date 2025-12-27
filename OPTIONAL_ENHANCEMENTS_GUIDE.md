# ZeroSite v4.0 - Optional Enhancements Complete Guide
# 선택적 고도화 기능 완전 가이드

## 📋 목차
1. [개요](#개요)
2. [Phase A: 즉시 실행 가능 기능](#phase-a-즉시-실행-가능-기능)
3. [Phase B: 중장기 개선 계획](#phase-b-중장기-개선-계획)
4. [구현 상태](#구현-상태)
5. [사용 가이드](#사용-가이드)

---

## 개요

이 문서는 ZeroSite v4.0 플랫폼의 선택적 고도화 기능에 대한 완전한 가이드입니다.

### 구현 완료 항목 (Phase A)
✅ **Load Testing** - Locust 성능 테스트  
✅ **Security Audit** - OWASP 보안 점검  
✅ **Monitoring** - Prometheus + Grafana

### 설계 완료 항목 (Phase B)
✅ **GraphQL API** - Strawberry 스키마  
📋 **Multi-tenancy** - 조직별 데이터 격리 (설계 문서)  
📋 **Machine Learning** - 타당성 예측 (설계 문서)  
📋 **Mobile App** - React Native (설계 문서)

---

## Phase A: 즉시 실행 가능 기능

### 1️⃣ Load Testing with Locust

#### 📁 구현 파일
```
tests/
├── locustfile.py              # Locust 테스트 시나리오
└── load_test_scenarios.sh     # 자동화 스크립트
```

#### 🚀 실행 방법

**기본 테스트 (웹 UI)**
```bash
cd /home/user/webapp
locust -f tests/locustfile.py --host=http://localhost:8000
# 브라우저에서 http://localhost:8089 접속
```

**자동화 테스트 (CLI)**
```bash
cd /home/user/webapp
./tests/load_test_scenarios.sh
```

#### 📊 테스트 시나리오

| 시나리오 | 사용자 수 | 지속 시간 | 목적 |
|---------|----------|----------|------|
| **Baseline** | 10 | 2분 | 기본 성능 측정 |
| **Load** | 50 | 5분 | 일반 부하 테스트 |
| **Stress** | 200 | 3분 | 시스템 한계 테스트 |
| **Spike** | 100 (50/s) | 1분 | 급격한 트래픽 증가 |
| **Endurance** | 30 | 10분 | 장시간 안정성 |

#### 📈 성능 목표

| 메트릭 | 목표 |
|--------|------|
| API 응답 시간 (P95) | < 200ms |
| 분석 처리 시간 | < 5s |
| 대시보드 로드 시간 | < 500ms |
| 성공률 | > 99.5% |
| 처리량 (RPS) | > 100 |

#### 📂 결과 파일
```
tests/load_test_results/
├── baseline_report.html      # HTML 리포트
├── load_report.html
├── stress_report.html
├── spike_report.html
├── endurance_report.html
├── baseline_stats.csv        # CSV 원시 데이터
├── load_stats.csv
├── stress_stats.csv
├── spike_stats.csv
├── endurance_stats.csv
└── summary.md                # 요약 리포트
```

---

### 2️⃣ Security Audit with OWASP

#### 📁 구현 파일
```
tests/
├── security_audit.py                      # 보안 점검 스크립트
└── security_audit_results/
    ├── security_checklist.json            # 체크리스트 (JSON)
    └── security_audit_report.md           # 감사 보고서
```

#### 🚀 실행 방법

```bash
cd /home/user/webapp
python tests/security_audit.py
```

#### 🔐 보안 점검 카테고리

**1. 인증 및 세션 관리**
- JWT 토큰 만료 검증
- Refresh 토큰 보안
- 비밀번호 복잡도 정책
- 브루트 포스 방어 (Rate Limiting)
- 세션 고정 공격 방어

**2. 권한 관리**
- API 키 권한 검증
- RBAC (Role-Based Access Control)
- 수평적 권한 상승 방어
- 수직적 권한 상승 방어

**3. 입력 검증**
- SQL Injection 방어
- XSS (Cross-Site Scripting) 방어
- CSRF (Cross-Site Request Forgery) 방어
- 파일 업로드 검증
- JSON 입력 검증 (Pydantic)

**4. 암호화**
- 비밀번호 해싱 (bcrypt)
- JWT 서명 검증
- API 키 해싱 (SHA256)
- HTTPS 강제 사용
- 민감 데이터 암호화

**5. 보안 헤더**
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security
- X-XSS-Protection

**6. API 보안**
- Rate Limiting (IP/API Key)
- CORS 설정
- API 버전 관리
- 에러 메시지 정보 노출 방지
- 로깅 및 모니터링

#### 📋 수동 검토 가이드

**1. 인증 플로우 검토**
1. 로그인 페이지에서 SQL Injection 시도
2. JWT 토큰 만료 후 요청 시도
3. 잘못된 Refresh 토큰으로 갱신 시도
4. 동시 다중 로그인 테스트
5. 로그아웃 후 토큰 재사용 시도

**2. API 권한 검증**
1. API 키 없이 보호된 엔드포인트 접근
2. 다른 사용자의 데이터 조회 시도 (IDOR)
3. 만료된 API 키 사용 시도
4. Rate Limit 초과 테스트
5. 관리자 전용 API 일반 사용자로 접근

**3. 입력 검증 테스트**
1. 특수문자 포함 입력값 테스트
2. 매우 긴 문자열 입력 (Buffer Overflow)
3. 잘못된 JSON 형식 전송
4. 파일 업로드 시 악성 파일 차단 확인
5. XSS 페이로드 테스트: `<script>alert('XSS')</script>`

**4. 보안 헤더 확인**
```bash
curl -I http://localhost:8000/health
```
- Content-Security-Policy 헤더 존재 확인
- X-Frame-Options: DENY 확인
- Strict-Transport-Security 확인
- X-Content-Type-Options: nosniff 확인

#### 🔗 OWASP ZAP 통합 (선택사항)

**설치**
```bash
pip install python-owasp-zap-v2.4
```

**ZAP Daemon 실행**
```bash
zap.sh -daemon -port 8080
```

---

### 3️⃣ Monitoring with Prometheus + Grafana

#### 📁 구현 파일
```
monitoring/
├── prometheus/
│   ├── prometheus.yml         # Prometheus 설정
│   └── alert_rules.yml        # 알림 규칙 (15+ 규칙)
├── grafana/
│   └── dashboards/
│       └── zerosite_api_dashboard.json  # Grafana 대시보드
├── alertmanager/
│   └── alertmanager.yml       # 알림 관리 설정
app/core/
└── metrics.py                 # 커스텀 메트릭 (8+ 메트릭)
docker-compose.monitoring.yml  # 모니터링 스택
MONITORING_GUIDE.md            # 상세 가이드
```

#### 🚀 실행 방법

**Docker Compose로 전체 스택 실행**
```bash
cd /home/user/webapp
docker-compose -f docker-compose.monitoring.yml up -d
```

**개별 서비스 확인**
```bash
docker-compose -f docker-compose.monitoring.yml ps
docker-compose -f docker-compose.monitoring.yml logs -f grafana
```

#### 🌐 접속 URL

| 서비스 | URL | 로그인 |
|--------|-----|--------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **Alertmanager** | http://localhost:9093 | - |
| **Node Exporter** | http://localhost:9100 | - |

#### 📊 Grafana 대시보드 패널

**패널 1: API Request Rate**
- 메트릭: `rate(zerosite_requests_total[5m])`
- 설명: 초당 API 요청 수

**패널 2: API Response Time (P95)**
- 메트릭: `histogram_quantile(0.95, rate(zerosite_request_duration_seconds_bucket[5m]))`
- 목표: < 1초

**패널 3: Analysis Requests by Status**
- 메트릭: `sum by (status, verdict) (rate(zerosite_analysis_requests_total[5m]))`
- 설명: 상태별 분석 요청 추이

**패널 4: Active Analysis Jobs**
- 메트릭: `zerosite_active_jobs`
- 임계값: 경고(50), 위험(100)

**패널 5: Analysis Duration by Stage**
- 메트릭: `histogram_quantile(0.95, rate(zerosite_analysis_duration_seconds_bucket[5m]))`
- 설명: 단계별 처리 시간

**패널 6: Cache Hit Rate**
- 메트릭: `rate(zerosite_cache_hit_total[5m]) / (rate(zerosite_cache_hit_total[5m]) + rate(zerosite_cache_miss_total[5m]))`
- 목표: > 70%

**패널 7: Database Connection Pool**
- 메트릭: `zerosite_db_pool_connections{status="active"}`
- 설명: DB 연결 풀 상태

**패널 8: Chart Generation Rate**
- 메트릭: `sum by (chart_type) (rate(zerosite_chart_generation_total[5m]))`
- 설명: 차트 타입별 생성 빈도

#### 🚨 알림 규칙 (15+ 규칙)

**성능 알림**
- HighAPILatency (P95 > 1초, 5분)
- CriticalAPILatency (P95 > 5초, 2분)
- HighErrorRate (에러율 > 5%, 3분)
- CriticalErrorRate (에러율 > 20%, 1분)

**분석 작업 알림**
- HighAnalysisFailureRate (실패율 > 10%, 5분)
- SlowAnalysisProcessing (처리 시간 > 10초, 5분)
- TooManyActiveJobs (활성 작업 > 100, 5분)

**보안 알림**
- SuspiciousTokenIssuance (토큰 발급 > 100/s, 2분)
- UnusualAPIKeyUsage (API 키 사용 > 500/s, 2분)

**데이터베이스 알림**
- LowDatabaseConnections (유휴 연결 < 2, 2분)
- DatabaseConnectionSaturation (사용률 > 90%, 3분)

**캐시 알림**
- LowCacheHitRate (히트율 < 70%, 5분)

**시스템 리소스 알림**
- HighCPUUsage (CPU > 80%, 5분)
- HighMemoryUsage (메모리 > 85%, 5분)
- LowDiskSpace (디스크 > 85%, 5분)

**가용성 알림**
- ServiceDown (서비스 다운, 1분)
- HighInProgressRequests (처리 중 요청 > 50, 3분)

#### 📧 알림 발송 설정

**Alertmanager 설정 (`monitoring/alertmanager/alertmanager.yml`)**
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'zerosite-alerts@example.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

receivers:
  - name: 'critical-team'
    email_configs:
      - to: 'critical-team@example.com'
```

---

## Phase B: 중장기 개선 계획

### 4️⃣ GraphQL API with Strawberry

#### 📁 구현 파일
```
app/graphql/
├── schema.py                  # GraphQL 스키마 (10.7KB)
└── router.py                  # FastAPI 라우터
```

#### 🌟 주요 기능

**Types (8개)**
- LandInfo, AppraisalResult, CapacityResult
- FeasibilityResult, LHReview, AnalysisResult
- User, APIKey, Chart

**Queries (8개)**
```graphql
query {
  hello
  analysisResult(jobId: "xxx")
  analysisResults(status: COMPLETED, limit: 10)
  user(id: 1)
  users(role: ADMIN)
  apiKeys(userId: 1)
  charts(jobId: "xxx")
}
```

**Mutations (6개)**
```graphql
mutation {
  createAnalysis(landInfo: {...})
  deleteAnalysis(jobId: "xxx")
  createUser(userInput: {...})
  createApiKey(apiKeyInput: {...})
  revokeApiKey(apiKeyId: 1)
}
```

**Subscriptions (실시간 업데이트)**
```graphql
subscription {
  analysisProgress(jobId: "xxx") {
    jobId
    status
    progress
  }
}
```

#### 🚀 사용 예시

**FastAPI에 GraphQL 추가**
```python
from fastapi import FastAPI
from app.graphql.router import get_graphql_router

app = FastAPI()

# GraphQL 라우터 추가
graphql_router = get_graphql_router()
app.include_router(graphql_router, prefix="/graphql")
```

**GraphiQL IDE 접속**
```
http://localhost:8000/graphql
```

**cURL 예시**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { hello }"
  }'
```

---

### 5️⃣ Multi-tenancy Architecture (설계 문서)

#### 🏗️ 아키텍처 설계

**1. Row-Level Security (RLS) 방식**
```sql
-- 모든 테이블에 organization_id 추가
ALTER TABLE analysis_jobs ADD COLUMN organization_id INTEGER;
ALTER TABLE users ADD COLUMN organization_id INTEGER;

-- RLS 정책 적용
CREATE POLICY org_isolation ON analysis_jobs
  USING (organization_id = current_setting('app.current_org_id')::int);
```

**2. Database-per-Tenant 방식**
```python
# 조직별 데이터베이스 연결
def get_org_database(org_id: int):
    return create_engine(f"postgresql://host/zerosite_org_{org_id}")
```

**3. Schema-per-Tenant 방식**
```python
# 조직별 스키마 분리
def get_org_schema(org_id: int):
    return f"org_{org_id}"
```

#### 📋 구현 체크리스트
- [ ] Organization 모델 생성
- [ ] 모든 테이블에 organization_id 추가
- [ ] RLS 정책 또는 필터 미들웨어 구현
- [ ] 조직 관리 API 엔드포인트
- [ ] 조직별 데이터 격리 테스트
- [ ] 조직 간 데이터 누출 방지 검증

---

### 6️⃣ Machine Learning - 타당성 예측 (설계 문서)

#### 🤖 ML 파이프라인 설계

**1. 데이터 수집 및 전처리**
```python
# 과거 분석 데이터 수집
features = [
    'area_sqm', 'zone', 'far_percent', 'bcr_percent',
    'asking_price_million', 'location_score', 'development_score'
]
target = 'final_verdict'  # GO, CONDITIONAL_GO, NO_GO
```

**2. 모델 학습**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 모델 학습
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 모델 평가
accuracy = model.score(X_test, y_test)
```

**3. 모델 배포**
```python
# FastAPI 엔드포인트
@app.post("/api/v1/predict")
async def predict_feasibility(land_info: LandInfoInput):
    features = extract_features(land_info)
    prediction = model.predict([features])
    confidence = model.predict_proba([features])
    
    return {
        "prediction": prediction[0],
        "confidence": confidence[0],
        "recommendation": generate_recommendation(prediction, confidence)
    }
```

#### 📊 모델 성능 목표
- 정확도 (Accuracy): > 85%
- 정밀도 (Precision): > 80%
- 재현율 (Recall): > 80%
- F1 Score: > 80%

---

### 7️⃣ Mobile App - React Native (설계 문서)

#### 📱 앱 구조 설계

**기술 스택**
- React Native (Expo)
- TypeScript
- React Navigation
- Axios (API 통신)
- AsyncStorage (로컬 저장소)
- React Query (상태 관리)

**화면 구성**
1. **로그인/회원가입**
2. **대시보드** (분석 목록)
3. **분석 입력** (부지 정보 입력)
4. **분석 진행** (실시간 프로그레스)
5. **결과 상세** (차트, 지도, 리포트)
6. **비교 분석**
7. **설정**

#### 🚀 초기 설정

```bash
# Expo 프로젝트 생성
npx create-expo-app zerosite-mobile
cd zerosite-mobile

# 의존성 설치
npm install @react-navigation/native @react-navigation/stack
npm install axios react-query
npm install @react-native-async-storage/async-storage
```

#### 📂 프로젝트 구조
```
zerosite-mobile/
├── src/
│   ├── components/        # 공통 컴포넌트
│   ├── screens/           # 화면
│   ├── navigation/        # 내비게이션
│   ├── services/          # API 서비스
│   ├── hooks/             # 커스텀 훅
│   ├── utils/             # 유틸리티
│   └── types/             # TypeScript 타입
├── App.tsx
└── package.json
```

---

## 구현 상태

### ✅ 완료 항목

| 기능 | 상태 | 파일 수 | LOC |
|------|------|---------|-----|
| **Load Testing** | ✅ 완료 | 2 | 9.5K |
| **Security Audit** | ✅ 완료 | 3 | 10.0K |
| **Monitoring** | ✅ 완료 | 7 | 40.0K |
| **GraphQL API** | ✅ 완료 | 2 | 11.5K |

### 📋 설계 완료 항목

| 기능 | 상태 | 우선순위 |
|------|------|----------|
| **Multi-tenancy** | 📋 설계 | Medium |
| **Machine Learning** | 📋 설계 | Low |
| **Mobile App** | 📋 설계 | Low |

---

## 사용 가이드

### 빠른 시작 (Quick Start)

#### 1. Load Testing
```bash
cd /home/user/webapp
./tests/load_test_scenarios.sh
```

#### 2. Security Audit
```bash
cd /home/user/webapp
python tests/security_audit.py
```

#### 3. Monitoring Stack
```bash
cd /home/user/webapp
docker-compose -f docker-compose.monitoring.yml up -d

# Grafana 접속: http://localhost:3000 (admin / admin123)
```

#### 4. GraphQL IDE
```bash
# API 서버 실행 후
# 브라우저에서 http://localhost:8000/graphql 접속
```

---

## 문서 링크

- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - 모니터링 상세 가이드
- [FINAL_IMPLEMENTATION_REPORT.md](./FINAL_IMPLEMENTATION_REPORT.md) - 최종 구현 리포트
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 배포 가이드
- [ENTERPRISE_UPGRADE_GUIDE.md](./ENTERPRISE_UPGRADE_GUIDE.md) - 엔터프라이즈 업그레이드

---

## GitHub Repository

**Repository**: https://github.com/hellodesignthinking-png/LHproject

**Latest Commit**: d06b025 - "feat: Optional Enhancements - Load Testing, Security Audit, Monitoring, GraphQL"

**Total Files**: 65+  
**Total LOC**: 18,000+

---

## 다음 단계

### 즉시 실행 가능
1. ✅ Load Testing 실행 → 성능 벤치마크 확립
2. ✅ Security Audit 실행 → 취약점 파악 및 수정
3. ✅ Monitoring 대시보드 구축 → 실시간 모니터링 시작

### 중장기 개선
4. 📋 Multi-tenancy 구현 → 조직별 데이터 격리
5. 📋 Machine Learning 모델 개발 → 자동 타당성 예측
6. 📋 Mobile App 개발 → 모바일 클라이언트

---

**ZeroSite v4.0 - Optional Enhancements Complete!**  
**Version**: 1.0.0  
**Last Updated**: 2025-12-27  
**Status**: Production Ready 🚀
