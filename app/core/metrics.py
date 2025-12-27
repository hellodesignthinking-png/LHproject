"""
ZeroSite v4.0 - Prometheus Metrics Exporter
FastAPI 애플리케이션 메트릭 수집 및 노출
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# ============================================================================
# Custom Metrics Definitions
# ============================================================================

# 분석 요청 카운터
analysis_requests_total = Counter(
    'zerosite_analysis_requests_total',
    'Total number of analysis requests',
    ['status', 'verdict']
)

# 분석 처리 시간 히스토그램
analysis_duration_seconds = Histogram(
    'zerosite_analysis_duration_seconds',
    'Time spent processing analysis',
    ['stage'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

# 활성 작업 수 게이지
active_jobs_gauge = Gauge(
    'zerosite_active_jobs',
    'Number of currently active analysis jobs'
)

# API 키 사용 카운터
api_key_usage_total = Counter(
    'zerosite_api_key_usage_total',
    'Total API key usage',
    ['key_name', 'endpoint']
)

# JWT 토큰 발급 카운터
jwt_tokens_issued_total = Counter(
    'zerosite_jwt_tokens_issued_total',
    'Total JWT tokens issued',
    ['token_type']  # access, refresh
)

# 차트 생성 카운터
chart_generation_total = Counter(
    'zerosite_chart_generation_total',
    'Total charts generated',
    ['chart_type']
)

# 데이터베이스 연결 풀 게이지
db_pool_connections = Gauge(
    'zerosite_db_pool_connections',
    'Database connection pool status',
    ['status']  # active, idle, total
)

# Redis 캐시 히트율
cache_hit_total = Counter(
    'zerosite_cache_hit_total',
    'Total cache hits'
)

cache_miss_total = Counter(
    'zerosite_cache_miss_total',
    'Total cache misses'
)

# 애플리케이션 정보
app_info = Info(
    'zerosite_app',
    'ZeroSite application information'
)
app_info.info({
    'version': '4.0.0',
    'environment': 'production',
    'platform': 'fastapi'
})


# ============================================================================
# Custom Instrumentator Setup
# ============================================================================

def setup_metrics(app: FastAPI) -> Instrumentator:
    """
    Prometheus 메트릭 설정 및 FastAPI 앱에 적용
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    
    Returns:
        Instrumentator 인스턴스
    """
    
    # Instrumentator 생성
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="zerosite_requests_inprogress",
        inprogress_labels=True
    )
    
    # 기본 메트릭 추가
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_name="zerosite_request_size_bytes",
            metric_doc="Size of requests in bytes"
        )
    )
    
    instrumentator.add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_name="zerosite_response_size_bytes",
            metric_doc="Size of responses in bytes"
        )
    )
    
    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_name="zerosite_request_duration_seconds",
            metric_doc="Duration of HTTP requests in seconds"
        )
    )
    
    instrumentator.add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_name="zerosite_requests_total",
            metric_doc="Total number of requests by method and path"
        )
    )
    
    # FastAPI 앱에 적용
    instrumentator.instrument(app)
    
    return instrumentator


# ============================================================================
# Metrics Helper Functions
# ============================================================================

def record_analysis_request(status: str, verdict: str):
    """분석 요청 기록"""
    analysis_requests_total.labels(status=status, verdict=verdict).inc()


def record_analysis_duration(stage: str, duration: float):
    """분석 단계별 처리 시간 기록"""
    analysis_duration_seconds.labels(stage=stage).observe(duration)


def update_active_jobs(count: int):
    """활성 작업 수 업데이트"""
    active_jobs_gauge.set(count)


def record_api_key_usage(key_name: str, endpoint: str):
    """API 키 사용 기록"""
    api_key_usage_total.labels(key_name=key_name, endpoint=endpoint).inc()


def record_jwt_token_issued(token_type: str):
    """JWT 토큰 발급 기록"""
    jwt_tokens_issued_total.labels(token_type=token_type).inc()


def record_chart_generation(chart_type: str):
    """차트 생성 기록"""
    chart_generation_total.labels(chart_type=chart_type).inc()


def update_db_pool_connections(active: int, idle: int, total: int):
    """데이터베이스 연결 풀 상태 업데이트"""
    db_pool_connections.labels(status='active').set(active)
    db_pool_connections.labels(status='idle').set(idle)
    db_pool_connections.labels(status='total').set(total)


def record_cache_hit():
    """캐시 히트 기록"""
    cache_hit_total.inc()


def record_cache_miss():
    """캐시 미스 기록"""
    cache_miss_total.inc()


# ============================================================================
# Metrics Collection Middleware
# ============================================================================

class MetricsMiddleware(BaseHTTPMiddleware):
    """커스텀 메트릭 수집 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # 요청 시작 시간
        start_time = time.time()
        
        # 요청 처리
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 메트릭 기록 (특정 엔드포인트에 대해)
        if request.url.path.startswith("/api/v1/analyze"):
            analysis_duration_seconds.labels(stage="total").observe(process_time)
        
        return response


# ============================================================================
# Health Check with Metrics
# ============================================================================

def get_metrics_summary() -> dict:
    """메트릭 요약 정보 반환"""
    return {
        "metrics_enabled": True,
        "metrics_endpoint": "/metrics",
        "custom_metrics": [
            "zerosite_analysis_requests_total",
            "zerosite_analysis_duration_seconds",
            "zerosite_active_jobs",
            "zerosite_api_key_usage_total",
            "zerosite_jwt_tokens_issued_total",
            "zerosite_chart_generation_total",
            "zerosite_cache_hit_total",
            "zerosite_cache_miss_total"
        ]
    }
