"""
민감도 분석 모듈

주요 변수 변동에 따른 사업성 영향도 분석
"""

from typing import List, Dict
import copy

from .models import (
    SensitivityAnalysisRequest,
    SensitivityAnalysisResponse,
    SensitivityScenario,
    SensitivityVariable,
    ROIAnalysisRequest
)
from .roi_calculator import calculate_roi_irr


class SensitivityAnalyzer:
    """민감도 분석기"""
    
    def analyze(self, request: SensitivityAnalysisRequest) -> SensitivityAnalysisResponse:
        """
        민감도 분석 수행
        
        Args:
            request: 민감도 분석 요청
            
        Returns:
            SensitivityAnalysisResponse: 분석 결과
        """
        # 1. 기본 시나리오 계산
        base_result = calculate_roi_irr(request.base_scenario)
        
        # 2. 각 변수별로 민감도 분석
        scenarios = []
        
        for variable in request.variables:
            for change_pct in request.variation_percentages:
                scenario = self._create_scenario(
                    request.base_scenario,
                    variable,
                    change_pct
                )
                scenarios.append(scenario)
        
        # 3. 가장 민감한 변수 찾기
        most_sensitive = self._find_most_sensitive_variable(scenarios)
        
        # 4. ROI 범위 계산
        roi_range = self._calculate_roi_range(scenarios)
        
        return SensitivityAnalysisResponse(
            base_roi=base_result.roi_percentage,
            base_irr=base_result.irr_percentage,
            scenarios=scenarios,
            most_sensitive_variable=most_sensitive,
            roi_range=roi_range
        )
    
    def _create_scenario(
        self,
        base_request: ROIAnalysisRequest,
        variable: SensitivityVariable,
        change_percentage: float
    ) -> SensitivityScenario:
        """
        시나리오 생성 및 계산
        
        Args:
            base_request: 기본 요청
            variable: 변경할 변수
            change_percentage: 변동 비율 (%)
            
        Returns:
            SensitivityScenario: 시나리오 결과
        """
        # 요청 복사
        modified_request = copy.deepcopy(base_request)
        
        # 변수에 따라 값 변경
        multiplier = 1 + (change_percentage / 100)
        
        if variable == SensitivityVariable.LAND_PRICE:
            modified_request.land_acquisition_cost *= multiplier
        elif variable == SensitivityVariable.CONSTRUCTION_COST:
            modified_request.construction_cost *= multiplier
        elif variable == SensitivityVariable.PROFIT_RATE:
            # 이윤율 변경 시 LH 매입가 재계산 필요
            # 기존 이윤 추출
            total_cost = (
                modified_request.land_acquisition_cost +
                modified_request.construction_cost +
                modified_request.other_costs
            )
            current_profit = modified_request.lh_purchase_price - total_cost
            current_profit_rate = current_profit / total_cost
            
            # 새로운 이윤율 적용
            new_profit_rate = current_profit_rate * multiplier
            new_profit = total_cost * new_profit_rate
            modified_request.lh_purchase_price = total_cost + new_profit
        elif variable == SensitivityVariable.INTEREST_RATE:
            # 금리 변동은 기타 비용에 반영 (이자 비용)
            modified_request.other_costs *= multiplier
        
        # ROI/IRR 계산
        result = calculate_roi_irr(modified_request)
        
        return SensitivityScenario(
            variable=variable,
            change_percentage=change_percentage,
            roi=result.roi_percentage,
            irr=result.irr_percentage,
            net_profit=result.net_profit
        )
    
    def _find_most_sensitive_variable(
        self, 
        scenarios: List[SensitivityScenario]
    ) -> SensitivityVariable:
        """
        가장 민감한 변수 찾기 (ROI 변동폭이 가장 큰 변수)
        
        Args:
            scenarios: 시나리오 목록
            
        Returns:
            SensitivityVariable: 가장 민감한 변수
        """
        # 변수별로 ROI 변동폭 계산
        sensitivity_scores = {}
        
        for variable in SensitivityVariable:
            variable_scenarios = [s for s in scenarios if s.variable == variable]
            if variable_scenarios:
                roi_values = [s.roi for s in variable_scenarios]
                # 표준편차로 변동폭 측정
                roi_range = max(roi_values) - min(roi_values)
                sensitivity_scores[variable] = roi_range
        
        # 가장 큰 변동폭을 가진 변수 반환
        if sensitivity_scores:
            return max(sensitivity_scores, key=sensitivity_scores.get)
        else:
            return SensitivityVariable.LAND_PRICE
    
    def _calculate_roi_range(
        self, 
        scenarios: List[SensitivityScenario]
    ) -> Dict[str, float]:
        """
        ROI 범위 계산
        
        Args:
            scenarios: 시나리오 목록
            
        Returns:
            Dict[str, float]: min, max ROI
        """
        if not scenarios:
            return {"min": 0.0, "max": 0.0}
        
        roi_values = [s.roi for s in scenarios]
        return {
            "min": round(min(roi_values), 2),
            "max": round(max(roi_values), 2)
        }


# 편의 함수
def analyze_sensitivity(request: SensitivityAnalysisRequest) -> SensitivityAnalysisResponse:
    """
    민감도 분석 편의 함수
    
    Args:
        request: 민감도 분석 요청
        
    Returns:
        SensitivityAnalysisResponse: 분석 결과
    """
    analyzer = SensitivityAnalyzer()
    return analyzer.analyze(request)
