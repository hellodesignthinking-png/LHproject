"""
ZeroSite v4.0 M8 Comparison Models
==================================

다중 부지 비교 분석을 위한 데이터 모델

Author: ZeroSite M8 Team
Date: 2025-12-26
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RecommendationTier(Enum):
    """추천 등급"""
    TIER_1_BEST = "TIER_1_최우선"      # 85점 이상, GO
    TIER_2_STRONG = "TIER_2_적극검토"  # 70-84점, CONDITIONAL
    TIER_3_CONSIDER = "TIER_3_조건부"  # 60-69점, 개선 가능
    TIER_4_WEAK = "TIER_4_미흡"        # 50-59점, 보완 필요
    TIER_5_REJECT = "TIER_5_제외"      # 50점 미만 또는 Fatal Reject


@dataclass
class SiteComparisonResult:
    """개별 부지 분석 결과"""
    
    # 기본 정보
    site_id: str
    site_name: str
    address: str
    parcel_id: str
    
    # M6 결과
    lh_score_total: float
    judgement: str
    grade: str
    fatal_reject: bool
    region_weight: str
    
    # 핵심 지표
    land_value: int
    land_area_sqm: float
    price_per_sqm: float
    price_per_py: float
    
    total_units: int
    cost_per_unit: int
    
    npv_public: int
    irr_public: float
    profitability_grade: str
    
    # 섹션별 점수
    section_scores: Dict[str, float]  # {"A": 21.0, "B": 20.0, ...}
    
    # 추천 등급
    recommendation_tier: RecommendationTier
    
    # 강점/약점
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # 개선 포인트
    improvement_points: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'site_id': self.site_id,
            'site_name': self.site_name,
            'address': self.address,
            'parcel_id': self.parcel_id,
            'lh_score_total': round(self.lh_score_total, 1),
            'judgement': self.judgement,
            'grade': self.grade,
            'fatal_reject': self.fatal_reject,
            'region_weight': self.region_weight,
            'land_value': self.land_value,
            'land_area_sqm': round(self.land_area_sqm, 2),
            'price_per_sqm': round(self.price_per_sqm, 2),
            'price_per_py': round(self.price_per_py, 2),
            'total_units': self.total_units,
            'cost_per_unit': self.cost_per_unit,
            'npv_public': self.npv_public,
            'irr_public': round(self.irr_public, 2),
            'profitability_grade': self.profitability_grade,
            'section_scores': self.section_scores,
            'recommendation_tier': self.recommendation_tier.value,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'improvement_points': self.improvement_points
        }


@dataclass
class ComparisonMatrix:
    """부지 비교 매트릭스"""
    
    # 비교 대상 부지들
    sites: List[SiteComparisonResult]
    
    # 순위 (LH 점수 기준)
    ranking: List[str]  # site_id 리스트
    
    # 카테고리별 최고 부지
    best_by_category: Dict[str, str]  # {"location": "site_1", "price": "site_2", ...}
    
    # 종합 분석
    total_sites: int
    go_sites: int
    conditional_sites: int
    no_go_sites: int
    
    # 평균값
    avg_lh_score: float
    avg_npv: int
    avg_irr: float
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'sites': [site.to_dict() for site in self.sites],
            'ranking': self.ranking,
            'best_by_category': self.best_by_category,
            'total_sites': self.total_sites,
            'go_sites': self.go_sites,
            'conditional_sites': self.conditional_sites,
            'no_go_sites': self.no_go_sites,
            'avg_lh_score': round(self.avg_lh_score, 1),
            'avg_npv': self.avg_npv,
            'avg_irr': round(self.avg_irr, 2)
        }


@dataclass
class ComparisonReport:
    """다중 부지 비교 보고서"""
    
    # 메타데이터
    report_id: str
    report_title: str
    generated_date: str
    
    # 비교 매트릭스
    comparison_matrix: ComparisonMatrix
    
    # 추천 요약
    tier_1_sites: List[SiteComparisonResult]  # 최우선 추천
    tier_2_sites: List[SiteComparisonResult]  # 적극 검토
    tier_3_sites: List[SiteComparisonResult]  # 조건부
    tier_4_sites: List[SiteComparisonResult]  # 미흡
    tier_5_sites: List[SiteComparisonResult]  # 제외
    
    # 종합 추천
    top_recommendation: Optional[SiteComparisonResult]
    alternative_recommendations: List[SiteComparisonResult]
    
    # 전략적 인사이트
    strategic_insights: List[str] = field(default_factory=list)
    regional_analysis: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'report_id': self.report_id,
            'report_title': self.report_title,
            'generated_date': self.generated_date,
            'comparison_matrix': self.comparison_matrix.to_dict(),
            'tier_1_sites': [s.to_dict() for s in self.tier_1_sites],
            'tier_2_sites': [s.to_dict() for s in self.tier_2_sites],
            'tier_3_sites': [s.to_dict() for s in self.tier_3_sites],
            'tier_4_sites': [s.to_dict() for s in self.tier_4_sites],
            'tier_5_sites': [s.to_dict() for s in self.tier_5_sites],
            'top_recommendation': self.top_recommendation.to_dict() if self.top_recommendation else None,
            'alternative_recommendations': [s.to_dict() for s in self.alternative_recommendations],
            'strategic_insights': self.strategic_insights,
            'regional_analysis': self.regional_analysis
        }


__all__ = [
    'RecommendationTier',
    'SiteComparisonResult',
    'ComparisonMatrix',
    'ComparisonReport'
]
