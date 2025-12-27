"""
ZeroSite v4.0 - Business Metrics
비즈니스 메트릭 추가 (Prometheus + Grafana)
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Business Performance Metrics
# ============================================================================

# 사업 타당성 판정 분포
verdict_distribution = Counter(
    'zerosite_business_verdict_distribution',
    'Distribution of business verdicts',
    ['verdict', 'zone', 'month']
)

# LH 점수 분포
lh_score_distribution = Histogram(
    'zerosite_lh_score_distribution',
    'Distribution of LH scores',
    ['zone'],
    buckets=(60, 65, 70, 75, 80, 85, 90, 95, 100)
)

# 수익률 분포
roi_distribution = Histogram(
    'zerosite_roi_distribution',
    'Distribution of ROI percentages',
    ['verdict'],
    buckets=(5, 10, 15, 20, 25, 30, 40, 50)
)

# 사업비 규모 분포
project_cost_distribution = Histogram(
    'zerosite_project_cost_distribution_million',
    'Distribution of project costs (million won)',
    buckets=(5000, 10000, 20000, 30000, 50000, 100000, 200000)
)

# 호수 규모 분포
unit_count_distribution = Histogram(
    'zerosite_unit_count_distribution',
    'Distribution of buildable units',
    ['zone'],
    buckets=(10, 20, 30, 50, 100, 150, 200, 300)
)


# ============================================================================
# Customer Metrics
# ============================================================================

# 조직별 분석 요청 수
org_analysis_requests = Counter(
    'zerosite_org_analysis_requests_total',
    'Total analysis requests by organization',
    ['org_id', 'org_name']
)

# 조직별 월간 분석 사용량
org_monthly_usage = Gauge(
    'zerosite_org_monthly_usage',
    'Monthly analysis usage by organization',
    ['org_id', 'org_name', 'month']
)

# 사용자별 분석 성공률
user_success_rate = Gauge(
    'zerosite_user_success_rate',
    'User analysis success rate',
    ['user_id', 'username']
)

# API 키별 사용 패턴
api_key_request_pattern = Counter(
    'zerosite_api_key_request_pattern',
    'API key usage pattern',
    ['key_name', 'endpoint', 'hour_of_day']
)


# ============================================================================
# Data Quality Metrics
# ============================================================================

# 입력 데이터 완전성
data_completeness = Gauge(
    'zerosite_data_completeness_percent',
    'Input data completeness percentage',
    ['field_name']
)

# 데이터 검증 실패율
validation_failure_rate = Counter(
    'zerosite_validation_failures_total',
    'Total validation failures',
    ['field_name', 'error_type']
)

# 이상치 탐지
outlier_detection = Counter(
    'zerosite_outliers_detected_total',
    'Total outliers detected',
    ['field_name', 'outlier_type']
)


# ============================================================================
# Financial Metrics
# ============================================================================

# 예상 수익 총합
total_expected_revenue = Gauge(
    'zerosite_total_expected_revenue_million',
    'Total expected revenue from all analyses (million won)'
)

# 예상 순이익 총합
total_expected_profit = Gauge(
    'zerosite_total_expected_profit_million',
    'Total expected profit from all analyses (million won)'
)

# 평균 ROI
average_roi = Summary(
    'zerosite_average_roi_percent',
    'Average ROI percentage'
)

# 평균 회수 기간
average_payback_period = Summary(
    'zerosite_average_payback_period_years',
    'Average payback period (years)'
)


# ============================================================================
# Geographic Metrics
# ============================================================================

# 지역별 분석 수
regional_analysis_count = Counter(
    'zerosite_regional_analysis_count',
    'Analysis count by region',
    ['city', 'district']
)

# 용도지역별 분석 수
zone_analysis_count = Counter(
    'zerosite_zone_analysis_count',
    'Analysis count by zoning',
    ['zone_type']
)

# 지역별 평균 LH 점수
regional_average_lh_score = Gauge(
    'zerosite_regional_average_lh_score',
    'Average LH score by region',
    ['city', 'district']
)


# ============================================================================
# Time-based Metrics
# ============================================================================

# 시간대별 분석 요청
hourly_analysis_pattern = Counter(
    'zerosite_hourly_analysis_pattern',
    'Analysis requests by hour',
    ['hour']
)

# 요일별 분석 요청
daily_analysis_pattern = Counter(
    'zerosite_daily_analysis_pattern',
    'Analysis requests by day of week',
    ['day_of_week']
)

# 월별 분석 트렌드
monthly_analysis_trend = Gauge(
    'zerosite_monthly_analysis_trend',
    'Monthly analysis trend',
    ['year', 'month']
)


# ============================================================================
# Helper Functions
# ============================================================================

def record_business_verdict(verdict: str, zone: str):
    """사업 타당성 판정 기록"""
    month = datetime.now().strftime('%Y-%m')
    verdict_distribution.labels(verdict=verdict, zone=zone, month=month).inc()


def record_lh_score(score: float, zone: str):
    """LH 점수 기록"""
    lh_score_distribution.labels(zone=zone).observe(score)


def record_roi(roi_percent: float, verdict: str):
    """ROI 기록"""
    roi_distribution.labels(verdict=verdict).observe(roi_percent)
    average_roi.observe(roi_percent)


def record_project_cost(cost_million: float):
    """사업비 기록"""
    project_cost_distribution.observe(cost_million)


def record_unit_count(count: int, zone: str):
    """호수 기록"""
    unit_count_distribution.labels(zone=zone).observe(count)


def record_org_analysis(org_id: int, org_name: str):
    """조직별 분석 기록"""
    org_analysis_requests.labels(org_id=str(org_id), org_name=org_name).inc()


def update_org_monthly_usage(org_id: int, org_name: str, count: int):
    """조직 월간 사용량 업데이트"""
    month = datetime.now().strftime('%Y-%m')
    org_monthly_usage.labels(
        org_id=str(org_id),
        org_name=org_name,
        month=month
    ).set(count)


def record_regional_analysis(city: str, district: str, lh_score: float):
    """지역별 분석 기록"""
    regional_analysis_count.labels(city=city, district=district).inc()
    
    # 평균 점수 업데이트 (간단한 방식)
    regional_average_lh_score.labels(city=city, district=district).set(lh_score)


def record_analysis_time_pattern():
    """분석 시간 패턴 기록"""
    now = datetime.now()
    hour = now.strftime('%H')
    day_of_week = now.strftime('%A')
    
    hourly_analysis_pattern.labels(hour=hour).inc()
    daily_analysis_pattern.labels(day_of_week=day_of_week).inc()


def update_financial_totals(expected_revenue: float, expected_profit: float):
    """재무 총합 업데이트"""
    total_expected_revenue.set(expected_revenue)
    total_expected_profit.set(expected_profit)


def record_data_quality(field_name: str, completeness_percent: float):
    """데이터 품질 기록"""
    data_completeness.labels(field_name=field_name).set(completeness_percent)


# ============================================================================
# Comprehensive Recording Function
# ============================================================================

def record_analysis_business_metrics(analysis_result: Dict):
    """
    분석 결과에서 모든 비즈니스 메트릭 추출 및 기록
    
    Args:
        analysis_result: 분석 결과 딕셔너리
    """
    try:
        # 기본 정보
        land_info = analysis_result.get('land_info', {})
        lh_review = analysis_result.get('lh_review', {})
        feasibility = analysis_result.get('feasibility', {})
        capacity = analysis_result.get('capacity', {})
        
        # 1. 사업 타당성 판정
        verdict = lh_review.get('final_verdict')
        zone = land_info.get('zone', 'Unknown')
        if verdict:
            record_business_verdict(verdict, zone)
        
        # 2. LH 점수
        lh_score = lh_review.get('lh_score')
        if lh_score:
            record_lh_score(lh_score, zone)
        
        # 3. ROI
        roi_percent = feasibility.get('roi_percent')
        if roi_percent and verdict:
            record_roi(roi_percent, verdict)
        
        # 4. 사업비
        project_cost = analysis_result.get('appraisal', {}).get('total_project_cost_million')
        if project_cost:
            record_project_cost(project_cost)
        
        # 5. 호수
        unit_count = capacity.get('buildable_units')
        if unit_count:
            record_unit_count(unit_count, zone)
        
        # 6. 지역 정보
        address = land_info.get('address', '')
        if address:
            # 주소에서 시/구 추출 (간단한 파싱)
            parts = address.split()
            if len(parts) >= 2:
                city = parts[0]
                district = parts[1]
                if lh_score:
                    record_regional_analysis(city, district, lh_score)
        
        # 7. 시간 패턴
        record_analysis_time_pattern()
        
        logger.info("Business metrics recorded successfully")
        
    except Exception as e:
        logger.error(f"Failed to record business metrics: {e}")


# ============================================================================
# Dashboard Query Helpers
# ============================================================================

def get_business_metrics_summary() -> Dict:
    """비즈니스 메트릭 요약 반환"""
    return {
        "verdict_distribution": "zerosite_business_verdict_distribution",
        "lh_score_distribution": "zerosite_lh_score_distribution",
        "roi_distribution": "zerosite_roi_distribution",
        "regional_analysis": "zerosite_regional_analysis_count",
        "time_patterns": {
            "hourly": "zerosite_hourly_analysis_pattern",
            "daily": "zerosite_daily_analysis_pattern"
        },
        "financial": {
            "total_revenue": "zerosite_total_expected_revenue_million",
            "total_profit": "zerosite_total_expected_profit_million",
            "average_roi": "zerosite_average_roi_percent"
        }
    }
