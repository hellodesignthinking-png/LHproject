"""
통합 사업성 분석 서비스

모든 분석 기능을 통합하여 원스톱 사업성 분석 제공
"""

from typing import List

from .models import (
    ComprehensiveAnalysisRequest,
    ComprehensiveAnalysisResponse,
    CostCalculationRequest,
    PurchaseSimulationRequest,
    ROIAnalysisRequest,
    UnitType
)
from .construction_cost import calculate_construction_cost
from .purchase_price import calculate_lh_purchase
from .roi_calculator import calculate_roi_irr


class ComprehensiveAnalysisService:
    """종합 사업성 분석 서비스"""
    
    # 평가 기준
    RATING_CRITERIA = {
        "excellent": {"roi_min": 12, "irr_min": 10},  # 우수
        "good": {"roi_min": 8, "irr_min": 7},          # 양호
        "fair": {"roi_min": 5, "irr_min": 5},          # 보통
        "poor": {"roi_min": 0, "irr_min": 0}           # 미흡
    }
    
    def analyze(self, request: ComprehensiveAnalysisRequest) -> ComprehensiveAnalysisResponse:
        """
        종합 사업성 분석 수행
        
        Args:
            request: 종합 분석 요청
            
        Returns:
            ComprehensiveAnalysisResponse: 분석 결과
        """
        # 1. 건축비 분석
        construction_analysis = self._analyze_construction_cost(request)
        
        # 2. LH 매입가 분석
        purchase_analysis = self._analyze_lh_purchase(request, construction_analysis)
        
        # 3. ROI/IRR 분석
        roi_analysis = self._analyze_roi_irr(request, purchase_analysis)
        
        # 4. 종합 평가
        overall_rating = self._evaluate_overall(roi_analysis, purchase_analysis)
        
        # 5. 권장 사항 생성
        recommendations = self._generate_recommendations(
            construction_analysis,
            purchase_analysis,
            roi_analysis
        )
        
        # 6. 리스크 요인 분석
        risk_factors = self._identify_risk_factors(
            construction_analysis,
            purchase_analysis,
            roi_analysis
        )
        
        return ComprehensiveAnalysisResponse(
            project_name=request.project_name,
            address=request.address,
            construction_analysis=construction_analysis,
            purchase_analysis=purchase_analysis,
            roi_analysis=roi_analysis,
            overall_rating=overall_rating,
            recommendations=recommendations,
            risk_factors=risk_factors
        )
    
    def _analyze_construction_cost(
        self, 
        request: ComprehensiveAnalysisRequest
    ):
        """건축비 분석"""
        cost_request = CostCalculationRequest(
            unit_type=request.unit_type,
            gross_area=request.gross_area,
            region=request.region,
            num_units=request.num_units
        )
        return calculate_construction_cost(cost_request)
    
    def _analyze_lh_purchase(
        self, 
        request: ComprehensiveAnalysisRequest,
        construction_analysis
    ):
        """LH 매입가 분석"""
        # 토지 비용 계산
        land_value = request.land_area * request.land_price_per_sqm
        
        purchase_request = PurchaseSimulationRequest(
            unit_type=request.unit_type,
            land_value=land_value,
            construction_cost=construction_analysis.grand_total,
            gross_area=request.gross_area,
            num_units=request.num_units,
            region=request.region
        )
        return calculate_lh_purchase(purchase_request)
    
    def _analyze_roi_irr(
        self,
        request: ComprehensiveAnalysisRequest,
        purchase_analysis
    ):
        """ROI/IRR 분석"""
        # 토지 비용 계산
        land_cost = request.land_area * request.land_price_per_sqm
        
        roi_request = ROIAnalysisRequest(
            project_name=request.project_name,
            land_acquisition_cost=land_cost,
            construction_cost=purchase_analysis.construction_cost,
            other_costs=0,  # 기타 비용은 포함되어 있음
            lh_purchase_price=purchase_analysis.total_purchase_price,
            land_acquisition_year=0,
            construction_start_year=0,
            construction_duration_years=request.construction_duration_years,
            lh_purchase_year=request.construction_duration_years
        )
        return calculate_roi_irr(roi_request)
    
    def _evaluate_overall(self, roi_analysis, purchase_analysis) -> str:
        """
        종합 평가 등급 결정
        
        Args:
            roi_analysis: ROI/IRR 분석 결과
            purchase_analysis: LH 매입가 분석 결과
            
        Returns:
            str: 평가 등급 (우수/양호/보통/미흡)
        """
        roi = roi_analysis.roi_percentage
        irr = roi_analysis.irr_percentage if roi_analysis.irr_percentage else 0
        is_eligible = purchase_analysis.is_eligible
        
        # LH 매입 자격 미달이면 미흡
        if not is_eligible:
            return "미흡"
        
        # ROI와 IRR 기준으로 평가
        if (roi >= self.RATING_CRITERIA["excellent"]["roi_min"] and 
            irr >= self.RATING_CRITERIA["excellent"]["irr_min"]):
            return "우수"
        elif (roi >= self.RATING_CRITERIA["good"]["roi_min"] and 
              irr >= self.RATING_CRITERIA["good"]["irr_min"]):
            return "양호"
        elif (roi >= self.RATING_CRITERIA["fair"]["roi_min"] and 
              irr >= self.RATING_CRITERIA["fair"]["irr_min"]):
            return "보통"
        else:
            return "미흡"
    
    def _generate_recommendations(
        self,
        construction_analysis,
        purchase_analysis,
        roi_analysis
    ) -> List[str]:
        """
        권장 사항 생성
        
        Args:
            construction_analysis: 건축비 분석 결과
            purchase_analysis: LH 매입가 분석 결과
            roi_analysis: ROI/IRR 분석 결과
            
        Returns:
            List[str]: 권장 사항 목록
        """
        recommendations = []
        
        # ROI 기반 권장 사항
        if roi_analysis.roi_percentage >= 12:
            recommendations.append("✅ 우수한 투자수익률로 사업 추진 강력 권장")
        elif roi_analysis.roi_percentage >= 8:
            recommendations.append("✅ 양호한 수익성, 사업 추진 권장")
        elif roi_analysis.roi_percentage >= 5:
            recommendations.append("⚠️ 보통 수준의 수익성, 신중한 검토 필요")
        else:
            recommendations.append("❌ 낮은 수익성, 사업 재검토 권장")
        
        # 회수 기간 기반 권장 사항
        if roi_analysis.payback_period_years <= 2:
            recommendations.append("✅ 빠른 투자 회수 기간 (2년 이내)")
        elif roi_analysis.payback_period_years <= 3:
            recommendations.append("✅ 적정한 투자 회수 기간 (3년 이내)")
        else:
            recommendations.append("⚠️ 긴 투자 회수 기간, 현금흐름 관리 필요")
        
        # LH 매입 자격 기반 권장 사항
        if purchase_analysis.is_eligible:
            recommendations.append("✅ LH 매입 기준 충족, 안정적인 매각 가능")
        else:
            recommendations.append("❌ LH 매입 기준 미달, 조건 재검토 필요")
            # 구체적인 미달 사항 추가
            for note in purchase_analysis.eligibility_notes:
                if "❌" in note:
                    recommendations.append(f"   - {note}")
        
        # 건축비 할증률 기반 권장 사항
        if construction_analysis.regional_multiplier > 1.1:
            recommendations.append(f"⚠️ 높은 지역 할증률({construction_analysis.regional_multiplier}배), 건축비 상승 고려")
        
        # IRR 기반 권장 사항
        if roi_analysis.irr_percentage and roi_analysis.irr_percentage >= 10:
            recommendations.append("✅ 우수한 내부수익률(IRR), 자금 조달 용이")
        
        return recommendations
    
    def _identify_risk_factors(
        self,
        construction_analysis,
        purchase_analysis,
        roi_analysis
    ) -> List[str]:
        """
        리스크 요인 식별
        
        Args:
            construction_analysis: 건축비 분석 결과
            purchase_analysis: LH 매입가 분석 결과
            roi_analysis: ROI/IRR 분석 결과
            
        Returns:
            List[str]: 리스크 요인 목록
        """
        risk_factors = []
        
        # 낮은 수익성 리스크
        if roi_analysis.roi_percentage < 5:
            risk_factors.append("⚠️ 낮은 ROI로 인한 수익성 리스크")
        
        # 긴 회수 기간 리스크
        if roi_analysis.payback_period_years > 3:
            risk_factors.append("⚠️ 긴 투자 회수 기간으로 인한 유동성 리스크")
        
        # LH 매입 불가 리스크
        if not purchase_analysis.is_eligible:
            risk_factors.append("⚠️ LH 매입 기준 미달로 인한 매각 리스크")
        
        # 높은 건축비 리스크
        if construction_analysis.cost_per_pyeong > 1500000:  # 평당 150만원 이상
            risk_factors.append("⚠️ 높은 건축비로 인한 원가 상승 리스크")
        
        # 지역 할증 리스크
        if construction_analysis.regional_multiplier > 1.15:
            risk_factors.append("⚠️ 높은 지역 할증률로 인한 비용 증가 리스크")
        
        # NPV 음수 리스크
        if roi_analysis.npv and roi_analysis.npv < 0:
            risk_factors.append("⚠️ 음수 NPV로 인한 투자 가치 하락 리스크")
        
        # 낮은 IRR 리스크
        if roi_analysis.irr_percentage and roi_analysis.irr_percentage < 5:
            risk_factors.append("⚠️ 낮은 IRR로 인한 자금 조달 어려움")
        
        # 리스크가 없으면 긍정 메시지
        if not risk_factors:
            risk_factors.append("✅ 주요 리스크 요인 없음, 안정적인 사업")
        
        return risk_factors


# 편의 함수
def analyze_comprehensive(
    request: ComprehensiveAnalysisRequest
) -> ComprehensiveAnalysisResponse:
    """
    종합 사업성 분석 편의 함수
    
    Args:
        request: 종합 분석 요청
        
    Returns:
        ComprehensiveAnalysisResponse: 분석 결과
    """
    service = ComprehensiveAnalysisService()
    return service.analyze(request)
