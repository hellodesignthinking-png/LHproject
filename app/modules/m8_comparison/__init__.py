"""
ZeroSite v4.0 M8 Multi-Site Comparison Engine
============================================

M8 다중 부지 비교 분석 모듈

Author: ZeroSite M8 Team
Date: 2025-12-26
Version: 1.0 (Initial Release)

Purpose:
    여러 후보 부지를 동시에 분석하고 비교하여 최적의 부지를 선정

Features:
    - 다중 부지 자동 분석 (M1→M6 파이프라인)
    - 상대적 순위 평가
    - 비교 매트릭스 생성
    - 최적 부지 추천
    - 비교 보고서 생성
"""

from .comparison_engine import MultiSiteComparisonEngine
from .comparison_models import (
    SiteComparisonResult,
    ComparisonMatrix,
    RecommendationTier,
    ComparisonReport
)

__all__ = [
    'MultiSiteComparisonEngine',
    'SiteComparisonResult',
    'ComparisonMatrix',
    'RecommendationTier',
    'ComparisonReport'
]
