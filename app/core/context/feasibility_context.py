"""
M5: Feasibility Context
========================

사업성 검토 모듈(M5) 출력 Context

이 모듈은 재무 타당성을 분석합니다:
- 감정가 vs LH 매입가
- 총 사업비 (토지비 + 건축비)
- ROI, IRR, NPV
- Payback Period

🔒 필수 규칙:
- 감정가는 M2.AppraisalContext에서 READ-ONLY로 참조
- 감정가 재계산 절대 금지
- 감정가 보정 절대 금지

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CostBreakdown:
    """비용 구조"""
    land_acquisition_cost: float        # 토지 매입비
    construction_cost: float            # 건축비
    design_cost: float                  # 설계비
    indirect_cost: float                # 간접비
    financing_cost: float               # 금융비용
    contingency: float                  # 예비비
    total_cost: float                   # 총 사업비


@dataclass(frozen=True)
class RevenueProjection:
    """수익 예측"""
    lh_purchase_price: float            # LH 매입가
    private_sale_revenue: float         # 민간 분양 수익 (있는 경우)
    rental_income_annual: float         # 연간 임대 수익
    total_revenue: float                # 총 수익


@dataclass(frozen=True)
class FinancialMetrics:
    """재무 지표"""
    npv_public: float                   # NPV (공공 할인율 2%)
    npv_market: float                   # NPV (시장 할인율 5.5%)
    irr_public: float                   # IRR (공공)
    irr_market: float                   # IRR (시장)
    roi: float                          # ROI (%)
    payback_years: float                # 회수 기간 (년)
    profitability_index: float          # 수익성 지수


@dataclass(frozen=True)
class FeasibilityContext:
    """
    사업성 Context (M5 출력)
    
    frozen=True: 생성 후 수정 불가
    
    🔒 중요: 감정가는 M2 결과를 READ-ONLY로 참조만
    """
    
    # === 감정평가 참조 (M2 결과, READ-ONLY) ===
    appraised_value: float              # M2.land_value 참조만 (재계산 금지!)
    appraised_unit_price: float         # M2.unit_price_sqm 참조만
    
    # === LH 매입가 ===
    lh_purchase_price: float            # LH 매입 예상가
    lh_unit_price: float                # LH 단가 (㎡당)
    purchase_premium_rate: float        # 매입 프리미엄률 (%)
    
    # === 비용 구조 ===
    cost_breakdown: CostBreakdown       # 상세 비용 분석
    
    # === 수익 예측 ===
    revenue_projection: RevenueProjection  # 수익 구조
    
    # === 재무 지표 ===
    financial_metrics: FinancialMetrics  # 재무 지표
    
    # === 사업성 판단 ===
    is_profitable: bool                 # 수익성 여부
    profitability_grade: str            # 사업성 등급 (A/B/C/D/F)
    profitability_score: float          # 사업성 점수 (40점 만점)
    
    # === 메타데이터 ===
    analysis_date: str                  # 분석 일시
    construction_cost_base_year: int = 2025  # 공사비 기준년도 (default: current year)
    
    # === 리스크 ===
    financial_risks: List[str] = field(default_factory=list)  # 재무 리스크
    risk_mitigation: List[str] = field(default_factory=list)  # 리스크 완화 방안
    
    # === 시나리오 분석 ===
    best_case_npv: Optional[float] = None     # 최선 시나리오 NPV
    worst_case_npv: Optional[float] = None    # 최악 시나리오 NPV
    assumptions: Dict[str, any] = field(default_factory=dict)  # 가정 사항
    
    def __post_init__(self):
        """유효성 검증"""
        assert self.appraised_value > 0, "감정가는 0보다 커야 합니다"
        assert self.lh_purchase_price > 0, "LH 매입가는 0보다 커야 합니다"
        assert self.cost_breakdown.total_cost > 0, "총 사업비는 0보다 커야 합니다"
        assert self.profitability_grade in ["A", "B", "C", "D", "F"], \
            "사업성 등급은 A/B/C/D/F 중 하나"
    
    @property
    def price_gap_pct(self) -> float:
        """감정가 vs LH 매입가 차이 (%)"""
        return ((self.lh_purchase_price - self.appraised_value) / 
                self.appraised_value * 100)
    
    @property
    def is_underpriced(self) -> bool:
        """LH 매입가가 감정가보다 낮은지"""
        return self.lh_purchase_price < self.appraised_value
    
    @property
    def is_high_profitability(self) -> bool:
        """높은 수익성 여부"""
        return self.profitability_grade in ["A", "B"]
    
    @property
    def feasibility_summary(self) -> str:
        """사업성 요약"""
        return (
            f"사업성 등급: {self.profitability_grade}\n"
            f"ROI: {self.financial_metrics.roi:.1f}%\n"
            f"IRR (공공): {self.financial_metrics.irr_public:.1f}%\n"
            f"회수 기간: {self.financial_metrics.payback_years:.1f}년"
        )
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "appraisal": {
                "value": self.appraised_value,
                "unit_price": self.appraised_unit_price,
                "source": "M2.AppraisalContext (READ-ONLY)"
            },
            "lh_purchase": {
                "price": self.lh_purchase_price,
                "unit_price": self.lh_unit_price,
                "premium_rate": self.purchase_premium_rate,
                "price_gap_pct": self.price_gap_pct
            },
            "costs": {
                "land": self.cost_breakdown.land_acquisition_cost,
                "construction": self.cost_breakdown.construction_cost,
                "total": self.cost_breakdown.total_cost
            },
            "revenue": {
                "lh_purchase": self.revenue_projection.lh_purchase_price,
                "rental_annual": self.revenue_projection.rental_income_annual,
                "total": self.revenue_projection.total_revenue
            },
            "financials": {
                "npv_public": self.financial_metrics.npv_public,
                "npv_market": self.financial_metrics.npv_market,
                "irr_public": self.financial_metrics.irr_public,
                "irr_market": self.financial_metrics.irr_market,
                "roi": self.financial_metrics.roi,
                "payback_years": self.financial_metrics.payback_years
            },
            "profitability": {
                "is_profitable": self.is_profitable,
                "grade": self.profitability_grade,
                "score": self.profitability_score
            },
            "risks": {
                "financial": self.financial_risks,
                "mitigation": self.risk_mitigation
            },
            "meta": {
                "analysis_date": self.analysis_date,
                "construction_cost_base_year": self.construction_cost_base_year,
                "base_year_note": f"공사비는 {self.construction_cost_base_year}년 기준입니다"
            }
        }
