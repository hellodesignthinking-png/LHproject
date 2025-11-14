"""
통합 테스트: 모든 사업성 시뮬레이션 기능 테스트
"""

import pytest
from app.modules.business_simulation.models import (
    UnitType,
    CostCalculationRequest,
    PurchaseSimulationRequest,
    ROIAnalysisRequest,
    ComprehensiveAnalysisRequest
)
from app.modules.business_simulation import (
    calculate_construction_cost,
    calculate_lh_purchase,
    calculate_roi_irr,
    analyze_comprehensive
)


class TestConstructionCost:
    """건축비 계산 테스트"""
    
    def test_seoul_youth_housing(self):
        """서울 청년주택 건축비 계산"""
        request = CostCalculationRequest(
            unit_type=UnitType.YOUTH,
            gross_area=1000,
            region="서울",
            num_units=20
        )
        result = calculate_construction_cost(request)
        
        assert result.total_cost > 0
        assert result.cost_per_pyeong == 1440000  # 120만원 * 1.2 (서울)
        assert result.regional_multiplier == 1.2
        assert result.grand_total > result.total_cost  # 부가비용 포함
    
    def test_gyeonggi_newlywed_housing(self):
        """경기 신혼희망타운 건축비 계산"""
        request = CostCalculationRequest(
            unit_type=UnitType.NEWLYWED,
            gross_area=2000,
            region="경기",
            num_units=30
        )
        result = calculate_construction_cost(request)
        
        assert result.total_cost > 0
        assert result.cost_per_pyeong == 1430000  # 130만원 * 1.1 (경기)
        assert result.regional_multiplier == 1.1


class TestLHPurchase:
    """LH 매입가 시뮬레이션 테스트"""
    
    def test_eligible_youth_housing(self):
        """자격 충족하는 청년주택"""
        request = PurchaseSimulationRequest(
            unit_type=UnitType.YOUTH,
            land_value=3000000000,
            construction_cost=2000000000,
            gross_area=1000,
            num_units=20,
            region="서울특별시"
        )
        result = calculate_lh_purchase(request)
        
        assert result.is_eligible is True
        assert result.total_purchase_price == 5400000000  # (30억+20억) * 1.08
        assert result.profit_rate == 8.0
        assert result.roi_percentage == 8.0
    
    def test_ineligible_large_unit(self):
        """면적 초과로 자격 미달"""
        request = PurchaseSimulationRequest(
            unit_type=UnitType.YOUTH,
            land_value=2000000000,
            construction_cost=1500000000,
            gross_area=1400,  # 70㎡/세대 (초과)
            num_units=20,
            region="서울특별시"
        )
        result = calculate_lh_purchase(request)
        
        assert result.is_eligible is False
        assert any("면적" in note or "초과" in note for note in result.eligibility_notes)


class TestROIIRR:
    """ROI/IRR 분석 테스트"""
    
    def test_profitable_project(self):
        """수익성 있는 프로젝트"""
        request = ROIAnalysisRequest(
            project_name="서울 강남 청년주택",
            land_acquisition_cost=3000000000,
            construction_cost=2000000000,
            other_costs=200000000,
            lh_purchase_price=5800000000,
            construction_duration_years=2,
            lh_purchase_year=2
        )
        result = calculate_roi_irr(request)
        
        assert result.total_investment == 5200000000
        assert result.total_revenue == 5800000000
        assert result.net_profit == 600000000
        assert result.roi_percentage > 0
        assert result.irr_percentage is not None
        assert result.payback_period_years > 0
        assert len(result.cash_flows) > 0
    
    def test_cash_flow_generation(self):
        """현금흐름 생성 검증"""
        request = ROIAnalysisRequest(
            project_name="테스트 프로젝트",
            land_acquisition_cost=1000000000,
            construction_cost=500000000,
            other_costs=0,
            lh_purchase_price=1800000000,
            construction_duration_years=2,
            lh_purchase_year=2
        )
        result = calculate_roi_irr(request)
        
        # 토지 매입 현금흐름 확인
        land_flow = [cf for cf in result.cash_flows if "토지" in cf.description]
        assert len(land_flow) > 0
        assert land_flow[0].amount == -1000000000
        
        # LH 매입 현금흐름 확인
        lh_flow = [cf for cf in result.cash_flows if "LH" in cf.description]
        assert len(lh_flow) > 0
        assert lh_flow[0].amount == 1800000000


class TestComprehensiveAnalysis:
    """종합 사업성 분석 테스트"""
    
    def test_full_analysis(self):
        """전체 통합 분석"""
        request = ComprehensiveAnalysisRequest(
            project_name="서울 강남 청년주택",
            address="서울특별시 강남구",
            unit_type=UnitType.YOUTH,
            land_area=1000,
            land_price_per_sqm=3000000,
            gross_area=1000,
            num_units=20,
            num_floors=5,
            region="서울",
            construction_duration_years=2
        )
        result = analyze_comprehensive(request)
        
        # 건축비 분석 확인
        assert result.construction_analysis.total_cost > 0
        
        # LH 매입가 분석 확인
        assert result.purchase_analysis.total_purchase_price > 0
        
        # ROI/IRR 분석 확인
        assert result.roi_analysis.roi_percentage > 0
        
        # 종합 평가 확인
        assert result.overall_rating in ["우수", "양호", "보통", "미흡"]
        
        # 권장 사항 확인
        assert len(result.recommendations) > 0
        
        # 리스크 요인 확인
        assert len(result.risk_factors) > 0
    
    def test_excellent_rating(self):
        """우수 등급 프로젝트"""
        request = ComprehensiveAnalysisRequest(
            project_name="우수 프로젝트",
            address="서울특별시",
            unit_type=UnitType.YOUTH,
            land_area=1000,
            land_price_per_sqm=2000000,  # 낮은 토지비
            gross_area=1000,
            num_units=20,
            num_floors=5,
            region="충청",  # 낮은 건축비
            construction_duration_years=2
        )
        result = analyze_comprehensive(request)
        
        # 낮은 비용으로 높은 ROI 기대
        assert result.roi_analysis.roi_percentage >= 8


class TestEdgeCases:
    """경계 조건 테스트"""
    
    def test_minimum_units(self):
        """최소 세대수"""
        request = PurchaseSimulationRequest(
            unit_type=UnitType.YOUTH,
            land_value=1000000000,
            construction_cost=500000000,
            gross_area=500,
            num_units=10,  # 최소
            region="서울특별시"
        )
        result = calculate_lh_purchase(request)
        
        assert result.is_eligible is True
    
    def test_maximum_area_per_unit(self):
        """최대 세대당 면적"""
        request = PurchaseSimulationRequest(
            unit_type=UnitType.YOUTH,
            land_value=1000000000,
            construction_cost=500000000,
            gross_area=600,  # 60㎡/세대 (경계값)
            num_units=10,
            region="서울특별시"
        )
        result = calculate_lh_purchase(request)
        
        assert result.is_eligible is True


class TestIntegration:
    """통합 시나리오 테스트"""
    
    def test_complete_workflow(self):
        """전체 워크플로우: 건축비 → LH 매입가 → ROI/IRR"""
        # 1단계: 건축비 계산
        cost_request = CostCalculationRequest(
            unit_type=UnitType.YOUTH,
            gross_area=1000,
            region="서울",
            num_units=20
        )
        cost_result = calculate_construction_cost(cost_request)
        
        # 2단계: LH 매입가 시뮬레이션
        purchase_request = PurchaseSimulationRequest(
            unit_type=UnitType.YOUTH,
            land_value=3000000000,
            construction_cost=cost_result.grand_total,
            gross_area=1000,
            num_units=20,
            region="서울특별시"
        )
        purchase_result = calculate_lh_purchase(purchase_request)
        
        # 3단계: ROI/IRR 분석
        roi_request = ROIAnalysisRequest(
            project_name="통합 테스트 프로젝트",
            land_acquisition_cost=3000000000,
            construction_cost=purchase_result.construction_cost,
            other_costs=0,
            lh_purchase_price=purchase_result.total_purchase_price,
            construction_duration_years=2,
            lh_purchase_year=2
        )
        roi_result = calculate_roi_irr(roi_request)
        
        # 검증
        assert cost_result.grand_total > 0
        assert purchase_result.is_eligible is True
        assert roi_result.roi_percentage > 0
        assert roi_result.net_profit > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
