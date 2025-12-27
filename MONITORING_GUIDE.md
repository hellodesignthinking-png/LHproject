# ZeroSite v4.0 Monitoring Setup Guide
# Prometheus + Grafana 모니터링 시스템 구축 가이드

## 목차
1. [시스템 개요](#시스템-개요)
2. [빠른 시작](#빠른-시작)
3. [구성 요소](#구성-요소)
4. [설치 및 설정](#설치-및-설정)
5. [대시보드 사용법](#대시보드-사용법)
6. [알림 설정](#알림-설정)
7. [문제 해결](#문제-해결)

---

## 시스템 개요

ZeroSite v4.0 모니터링 스택은 다음 구성 요소로 이루어져 있습니다:

### 메트릭 수집
- **Prometheus**: 시계열 메트릭 데이터베이스
- **Node Exporter**: 시스템 메트릭 (CPU, 메모리, 디스크)
- **Redis Exporter**: Redis 캐시 메트릭
- **Postgres Exporter**: PostgreSQL 데이터베이스 메트릭

### 시각화 및 알림
- **Grafana**: 대시보드 및 시각화
- **Alertmanager**: 알림 라우팅 및 발송

### 커스텀 메트릭
- API 요청/응답 메트릭
- 분석 작업 메트릭
- 인증 및 보안 메트릭
- 캐시 성능 메트릭

---

## 빠른 시작

### 1. 모니터링 스택 실행

```bash
# 모니터링 서비스 시작
docker-compose -f docker-compose.monitoring.yml up -d

# 로그 확인
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 2. 접속 URL

| 서비스 | URL | 기본 로그인 |
|--------|-----|------------|
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |

### 3. Grafana 대시보드 접속

1. http://localhost:3000 접속
2. `admin` / `admin123` 로그인
3. Dashboards → ZeroSite v4.0 - API Performance Dashboard 선택

---

## 구성 요소

### Prometheus 메트릭

#### 표준 HTTP 메트릭
```promql
# 요청 속도 (req/s)
rate(zerosite_requests_total[5m])

# 응답 시간 (P95)
histogram_quantile(0.95, rate(zerosite_request_duration_seconds_bucket[5m]))

# 에러율
rate(zerosite_requests_total{status=~"5.."}[5m]) / rate(zerosite_requests_total[5m])
```

#### 커스텀 애플리케이션 메트릭
```promql
# 분석 요청 현황
zerosite_analysis_requests_total

# 활성 작업 수
zerosite_active_jobs

# 캐시 히트율
rate(zerosite_cache_hit_total[5m]) / (rate(zerosite_cache_hit_total[5m]) + rate(zerosite_cache_miss_total[5m]))

# 데이터베이스 연결 풀
zerosite_db_pool_connections{status="active"}
```

---

## 설치 및 설정

### FastAPI 앱에 메트릭 추가

```python
from fastapi import FastAPI
from app.core.metrics import setup_metrics, MetricsMiddleware

app = FastAPI()

# Prometheus 메트릭 설정
instrumentator = setup_metrics(app)

# 미들웨어 추가
app.add_middleware(MetricsMiddleware)

# /metrics 엔드포인트 노출
instrumentator.expose(app, endpoint="/metrics")
```

### 메트릭 기록 예시

```python
from app.core.metrics import (
    record_analysis_request,
    record_analysis_duration,
    update_active_jobs,
    record_cache_hit
)

# 분석 요청 기록
record_analysis_request(status="completed", verdict="GO")

# 분석 시간 기록
import time
start_time = time.time()
# ... 분석 작업 ...
duration = time.time() - start_time
record_analysis_duration(stage="appraisal", duration=duration)

# 활성 작업 수 업데이트
update_active_jobs(len(active_jobs))

# 캐시 히트 기록
if cache_result:
    record_cache_hit()
else:
    record_cache_miss()
```

---

## 대시보드 사용법

### Grafana 대시보드 구성

#### 패널 1: API Request Rate
- **메트릭**: `rate(zerosite_requests_total[5m])`
- **설명**: 초당 API 요청 수
- **목표**: > 100 RPS

#### 패널 2: API Response Time (P95)
- **메트릭**: `histogram_quantile(0.95, rate(zerosite_request_duration_seconds_bucket[5m]))`
- **설명**: 95 백분위수 응답 시간
- **목표**: < 1초

#### 패널 3: Analysis Requests by Status
- **메트릭**: `sum by (status, verdict) (rate(zerosite_analysis_requests_total[5m]))`
- **설명**: 상태별 분석 요청 추이

#### 패널 4: Active Analysis Jobs
- **메트릭**: `zerosite_active_jobs`
- **설명**: 현재 진행 중인 분석 작업 수
- **임계값**: 경고(50), 위험(100)

#### 패널 5: Cache Hit Rate
- **메트릭**: `rate(zerosite_cache_hit_total[5m]) / (rate(zerosite_cache_hit_total[5m]) + rate(zerosite_cache_miss_total[5m]))`
- **설명**: 캐시 히트율
- **목표**: > 70%

---

## 알림 설정

### 알림 규칙 (Prometheus Alert Rules)

#### 1. High API Latency (높은 응답 시간)
```yaml
- alert: HighAPILatency
  expr: histogram_quantile(0.95, rate(zerosite_request_duration_seconds_bucket[5m])) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "API 응답 시간이 높습니다"
    description: "P95 응답 시간: {{ $value }}초"
```

#### 2. High Error Rate (높은 에러율)
```yaml
- alert: HighErrorRate
  expr: rate(zerosite_requests_total{status=~"5.."}[5m]) / rate(zerosite_requests_total[5m]) > 0.05
  for: 3m
  labels:
    severity: warning
  annotations:
    summary: "높은 에러율 감지"
    description: "에러율: {{ $value | humanizePercentage }}"
```

#### 3. Low Cache Hit Rate (낮은 캐시 히트율)
```yaml
- alert: LowCacheHitRate
  expr: rate(zerosite_cache_hit_total[5m]) / (rate(zerosite_cache_hit_total[5m]) + rate(zerosite_cache_miss_total[5m])) < 0.7
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "낮은 캐시 히트율"
    description: "캐시 히트율: {{ $value | humanizePercentage }}"
```

### Alertmanager 알림 라우팅

```yaml
route:
  receiver: 'default'
  routes:
    # Critical 알림 - 즉시 발송
    - match:
        severity: critical
      receiver: 'critical-team'
      repeat_interval: 5m
    
    # Warning 알림 - 5분 대기
    - match:
        severity: warning
      receiver: 'warning-team'
      repeat_interval: 1h
```

### 이메일 알림 설정

```yaml
receivers:
  - name: 'critical-team'
    email_configs:
      - to: 'critical-team@example.com'
        headers:
          Subject: '[ZeroSite] 🚨 Critical Alert'
```

---

## 모니터링 체크리스트

### 일일 점검 항목
- [ ] 대시보드 정상 작동 확인
- [ ] 활성 알림 확인
- [ ] 에러율 < 1%
- [ ] API 응답 시간 (P95) < 1초
- [ ] 캐시 히트율 > 70%

### 주간 점검 항목
- [ ] 메트릭 저장소 디스크 사용량
- [ ] 알림 규칙 정확도 검증
- [ ] 대시보드 패널 정렬
- [ ] Prometheus 타겟 상태 확인

### 월간 점검 항목
- [ ] 알림 임계값 조정
- [ ] 대시보드 개선
- [ ] 메트릭 보존 정책 검토
- [ ] 성능 트렌드 분석

---

## 문제 해결

### Prometheus가 메트릭을 수집하지 못할 때

```bash
# Prometheus 타겟 상태 확인
http://localhost:9090/targets

# API 서버 /metrics 엔드포인트 확인
curl http://localhost:8000/metrics

# Prometheus 로그 확인
docker logs zerosite-prometheus
```

### Grafana 대시보드가 표시되지 않을 때

```bash
# Grafana 로그 확인
docker logs zerosite-grafana

# Prometheus 데이터소스 연결 확인
# Grafana UI: Configuration → Data Sources → Prometheus
```

### 알림이 발송되지 않을 때

```bash
# Alertmanager 상태 확인
http://localhost:9093/#/alerts

# Alertmanager 로그 확인
docker logs zerosite-alertmanager

# 알림 규칙 검증
promtool check rules monitoring/prometheus/alert_rules.yml
```

---

## 고급 설정

### 커스텀 메트릭 추가

```python
from prometheus_client import Counter

# 새로운 메트릭 정의
custom_metric = Counter(
    'zerosite_custom_metric',
    'Description of custom metric',
    ['label1', 'label2']
)

# 메트릭 기록
custom_metric.labels(label1='value1', label2='value2').inc()
```

### 대시보드 JSON 내보내기/가져오기

```bash
# 대시보드 내보내기
# Grafana UI: Dashboard → Settings → JSON Model

# 대시보드 파일 위치
monitoring/grafana/dashboards/zerosite_api_dashboard.json
```

### Prometheus 데이터 보존 기간 설정

```yaml
# docker-compose.monitoring.yml
command:
  - '--storage.tsdb.retention.time=30d'  # 30일 보존
  - '--storage.tsdb.retention.size=10GB' # 최대 10GB
```

---

## 참고 자료

- [Prometheus 공식 문서](https://prometheus.io/docs/)
- [Grafana 공식 문서](https://grafana.com/docs/)
- [PromQL 쿼리 가이드](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)

---

**ZeroSite v4.0 Monitoring System**  
Version: 1.0.0  
Last Updated: 2025-12-27
