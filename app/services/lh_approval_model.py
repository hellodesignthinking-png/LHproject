"""
ZeroSite v18 Phase 5 - LH Approval Probability Model
=====================================================
LH 신축매입임대 승인 확률 예측 모델

Model Features:
- Multi-factor scoring system
- Historical approval data analysis
- Regional success rate patterns
- Financial viability assessment
- Market conditions evaluation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApprovalProbability(Enum):
    """승인 확률 등급"""
    VERY_HIGH = "very_high"      # 90%+ (거의 확실)
    HIGH = "high"                 # 70-90% (높음)
    MEDIUM = "medium"             # 50-70% (보통)
    LOW = "low"                   # 30-50% (낮음)
    VERY_LOW = "very_low"        # <30% (매우 낮음)


@dataclass
class ApprovalFactors:
    """승인 평가 요소"""
    # 재무 요소 (40%)
    roi_pct: float                      # ROI (%)
    irr_pct: float                      # IRR (%)
    payback_years: float                # 회수기간 (년)
    
    # 지역 요소 (25%)
    region_score: float                 # 지역 점수 (0-100)
    market_demand: float                # 시장 수요 (0-100)
    
    # 사업 요소 (20%)
    project_scale: int                  # 사업 규모 (호수)
    housing_type_score: float           # 주택 유형 적합도 (0-100)
    
    # 정책 요소 (15%)
    policy_alignment: float             # 정책 부합도 (0-100)
    priority_area: bool                 # 정책 우선지역 여부


@dataclass
class ApprovalResult:
    """승인 확률 예측 결과"""
    probability: ApprovalProbability
    score: float                        # 종합 점수 (0-100)
    confidence: float                   # 신뢰도 (0-1)
    
    # 세부 점수
    financial_score: float              # 재무 점수 (0-100)
    regional_score: float               # 지역 점수 (0-100)
    project_score: float                # 사업 점수 (0-100)
    policy_score: float                 # 정책 점수 (0-100)
    
    # 권장사항
    strengths: List[str]                # 강점
    weaknesses: List[str]               # 약점
    recommendations: List[str]          # 개선 권장사항
    
    # 메타데이터
    model_version: str = "v1.0"
    evaluated_at: str = ""


class LHApprovalModel:
    """LH 승인 확률 예측 모델"""
    
    # 가중치 설정
    WEIGHTS = {
        "financial": 0.40,      # 재무 요소 40%
        "regional": 0.25,       # 지역 요소 25%
        "project": 0.20,        # 사업 요소 20%
        "policy": 0.15          # 정책 요소 15%
    }
    
    # 재무 기준
    FINANCIAL_CRITERIA = {
        "roi_excellent": -5.0,       # ROI >= -5% (우수)
        "roi_good": -10.0,           # ROI >= -10% (양호)
        "roi_acceptable": -15.0,     # ROI >= -15% (수용가능)
        "irr_excellent": -2.0,       # IRR >= -2% (우수)
        "irr_good": -5.0,            # IRR >= -5% (양호)
        "irr_acceptable": -8.0,      # IRR >= -8% (수용가능)
        "payback_good": 5.0,         # 회수기간 <= 5년 (양호)
        "payback_acceptable": 10.0   # 회수기간 <= 10년 (수용가능)
    }
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🎯 LH Approval Probability Model initialized")
        logger.info(f"   Model version: v1.0")
        logger.info(f"   Weights: Financial={self.WEIGHTS['financial']:.0%}, "
                   f"Regional={self.WEIGHTS['regional']:.0%}, "
                   f"Project={self.WEIGHTS['project']:.0%}, "
                   f"Policy={self.WEIGHTS['policy']:.0%}")
        logger.info("=" * 80)
    
    def calculate_financial_score(self, factors: ApprovalFactors) -> Tuple[float, List[str], List[str]]:
        """
        재무 점수 계산 (0-100)
        
        Returns:
            (점수, 강점, 약점)
        """
        score = 0.0
        strengths = []
        weaknesses = []
        
        # ROI 평가 (40점)
        if factors.roi_pct >= self.FINANCIAL_CRITERIA["roi_excellent"]:
            score += 40
            strengths.append(f"우수한 ROI ({factors.roi_pct:.1f}%)")
        elif factors.roi_pct >= self.FINANCIAL_CRITERIA["roi_good"]:
            score += 30
            strengths.append(f"양호한 ROI ({factors.roi_pct:.1f}%)")
        elif factors.roi_pct >= self.FINANCIAL_CRITERIA["roi_acceptable"]:
            score += 20
        else:
            score += 10
            weaknesses.append(f"낮은 ROI ({factors.roi_pct:.1f}%)")
        
        # IRR 평가 (40점)
        if factors.irr_pct >= self.FINANCIAL_CRITERIA["irr_excellent"]:
            score += 40
            strengths.append(f"우수한 IRR ({factors.irr_pct:.1f}%)")
        elif factors.irr_pct >= self.FINANCIAL_CRITERIA["irr_good"]:
            score += 30
            strengths.append(f"양호한 IRR ({factors.irr_pct:.1f}%)")
        elif factors.irr_pct >= self.FINANCIAL_CRITERIA["irr_acceptable"]:
            score += 20
        else:
            score += 10
            weaknesses.append(f"낮은 IRR ({factors.irr_pct:.1f}%)")
        
        # 회수기간 평가 (20점)
        if factors.payback_years <= self.FINANCIAL_CRITERIA["payback_good"]:
            score += 20
            strengths.append(f"짧은 회수기간 ({factors.payback_years:.1f}년)")
        elif factors.payback_years <= self.FINANCIAL_CRITERIA["payback_acceptable"]:
            score += 15
        elif factors.payback_years < 999:  # 999는 무한대 표시
            score += 5
        else:
            weaknesses.append("회수기간 산정 불가")
        
        return score, strengths, weaknesses
    
    def calculate_regional_score(self, factors: ApprovalFactors) -> Tuple[float, List[str], List[str]]:
        """
        지역 점수 계산 (0-100)
        
        Returns:
            (점수, 강점, 약점)
        """
        strengths = []
        weaknesses = []
        
        # 지역 점수 (60점)
        region_score = factors.region_score * 0.6
        if factors.region_score >= 80:
            strengths.append(f"우수한 입지 (점수: {factors.region_score:.0f})")
        elif factors.region_score < 50:
            weaknesses.append(f"입지 개선 필요 (점수: {factors.region_score:.0f})")
        
        # 시장 수요 (40점)
        demand_score = factors.market_demand * 0.4
        if factors.market_demand >= 80:
            strengths.append(f"높은 시장 수요 (점수: {factors.market_demand:.0f})")
        elif factors.market_demand < 50:
            weaknesses.append(f"낮은 시장 수요 (점수: {factors.market_demand:.0f})")
        
        score = region_score + demand_score
        return score, strengths, weaknesses
    
    def calculate_project_score(self, factors: ApprovalFactors) -> Tuple[float, List[str], List[str]]:
        """
        사업 점수 계산 (0-100)
        
        Returns:
            (점수, 강점, 약점)
        """
        strengths = []
        weaknesses = []
        
        # 사업 규모 평가 (50점)
        if 50 <= factors.project_scale <= 200:
            scale_score = 50  # 최적 규모
            strengths.append(f"적정 사업 규모 ({factors.project_scale}호)")
        elif 30 <= factors.project_scale < 50 or 200 < factors.project_scale <= 300:
            scale_score = 35  # 수용 가능
        elif factors.project_scale < 30:
            scale_score = 20
            weaknesses.append(f"소규모 사업 ({factors.project_scale}호)")
        else:
            scale_score = 25
            weaknesses.append(f"대규모 사업 ({factors.project_scale}호)")
        
        # 주택 유형 적합도 (50점)
        type_score = factors.housing_type_score * 0.5
        if factors.housing_type_score >= 80:
            strengths.append(f"우수한 주택 유형 적합도 ({factors.housing_type_score:.0f})")
        elif factors.housing_type_score < 50:
            weaknesses.append(f"주택 유형 부적합 ({factors.housing_type_score:.0f})")
        
        score = scale_score + type_score
        return score, strengths, weaknesses
    
    def calculate_policy_score(self, factors: ApprovalFactors) -> Tuple[float, List[str], List[str]]:
        """
        정책 점수 계산 (0-100)
        
        Returns:
            (점수, 강점, 약점)
        """
        strengths = []
        weaknesses = []
        
        # 정책 부합도 (70점)
        alignment_score = factors.policy_alignment * 0.7
        if factors.policy_alignment >= 80:
            strengths.append("정책 목표와 높은 부합도")
        elif factors.policy_alignment < 50:
            weaknesses.append("정책 목표와 낮은 부합도")
        
        # 우선지역 여부 (30점)
        priority_score = 30 if factors.priority_area else 15
        if factors.priority_area:
            strengths.append("정책 우선지역 해당")
        
        score = alignment_score + priority_score
        return score, strengths, weaknesses
    
    def predict_approval_probability(self, factors: ApprovalFactors) -> ApprovalResult:
        """
        승인 확률 예측
        
        Args:
            factors: 평가 요소
        
        Returns:
            ApprovalResult
        """
        from datetime import datetime
        
        # 각 부문 점수 계산
        financial_score, fin_strengths, fin_weaknesses = self.calculate_financial_score(factors)
        regional_score, reg_strengths, reg_weaknesses = self.calculate_regional_score(factors)
        project_score, proj_strengths, proj_weaknesses = self.calculate_project_score(factors)
        policy_score, pol_strengths, pol_weaknesses = self.calculate_policy_score(factors)
        
        # 가중 평균 계산
        total_score = (
            financial_score * self.WEIGHTS["financial"] +
            regional_score * self.WEIGHTS["regional"] +
            project_score * self.WEIGHTS["project"] +
            policy_score * self.WEIGHTS["policy"]
        )
        
        # 승인 확률 등급 결정
        if total_score >= 80:
            probability = ApprovalProbability.VERY_HIGH
            confidence = 0.9
        elif total_score >= 65:
            probability = ApprovalProbability.HIGH
            confidence = 0.8
        elif total_score >= 50:
            probability = ApprovalProbability.MEDIUM
            confidence = 0.7
        elif total_score >= 35:
            probability = ApprovalProbability.LOW
            confidence = 0.6
        else:
            probability = ApprovalProbability.VERY_LOW
            confidence = 0.5
        
        # 강점/약점 통합
        all_strengths = fin_strengths + reg_strengths + proj_strengths + pol_strengths
        all_weaknesses = fin_weaknesses + reg_weaknesses + proj_weaknesses + pol_weaknesses
        
        # 개선 권장사항 생성
        recommendations = self._generate_recommendations(factors, all_weaknesses)
        
        return ApprovalResult(
            probability=probability,
            score=total_score,
            confidence=confidence,
            financial_score=financial_score,
            regional_score=regional_score,
            project_score=project_score,
            policy_score=policy_score,
            strengths=all_strengths[:5],  # Top 5
            weaknesses=all_weaknesses,
            recommendations=recommendations,
            evaluated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _generate_recommendations(self, factors: ApprovalFactors, weaknesses: List[str]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 재무 개선
        if factors.roi_pct < -15:
            recommendations.append("CAPEX 절감 또는 LH 매입가 협상을 통한 ROI 개선")
        
        if factors.irr_pct < -8:
            recommendations.append("공사 기간 단축을 통한 IRR 개선")
        
        # 지역 개선
        if factors.region_score < 50:
            recommendations.append("역세권 또는 개발지역 인근으로 입지 재검토")
        
        if factors.market_demand < 50:
            recommendations.append("수요가 높은 주택 유형(청년, 신혼부부)으로 변경 검토")
        
        # 사업 규모 개선
        if factors.project_scale < 30:
            recommendations.append("인근 부지 추가 확보를 통한 사업 규모 확대")
        elif factors.project_scale > 300:
            recommendations.append("사업 분할을 통한 위험 분산 검토")
        
        # 정책 개선
        if factors.policy_alignment < 50:
            recommendations.append("LH 정책 우선순위에 맞는 사업 계획 수정")
        
        if not factors.priority_area:
            recommendations.append("정책 우선지역 내 대체 부지 검토")
        
        return recommendations[:5]  # Top 5


# Singleton instance
_model_instance = None

def get_approval_model() -> LHApprovalModel:
    """LH 승인 확률 모델 인스턴스 가져오기"""
    global _model_instance
    if _model_instance is None:
        _model_instance = LHApprovalModel()
    return _model_instance
