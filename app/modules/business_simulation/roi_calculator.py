"""
ROI/IRR 계산기 모듈

현금흐름 분석, 투자수익률(ROI), 내부수익률(IRR), 순현재가치(NPV) 계산
"""

from typing import List, Optional
import numpy as np
from numpy_financial import irr, npv

from .models import (
    ROIAnalysisRequest,
    ROIAnalysisResponse,
    CashFlowItem
)


class ROIIRRCalculator:
    """ROI/IRR 계산기"""
    
    # 기본 할인율 (NPV 계산용)
    DEFAULT_DISCOUNT_RATE = 0.10  # 10%
    
    def calculate(self, request: ROIAnalysisRequest) -> ROIAnalysisResponse:
        """
        ROI/IRR 종합 분석
        
        Args:
            request: ROI 분석 요청
            
        Returns:
            ROIAnalysisResponse: 분석 결과
        """
        # 1. 총 투자액 계산
        total_investment = (
            request.land_acquisition_cost +
            request.construction_cost +
            request.other_costs
        )
        
        # 2. 순이익 계산
        total_revenue = request.lh_purchase_price
        net_profit = total_revenue - total_investment
        
        # 3. ROI 계산
        roi_percentage = (net_profit / total_investment) * 100
        
        # 4. 현금흐름 생성
        cash_flows = self._generate_cash_flows(request)
        
        # 5. IRR 계산
        irr_percentage = self._calculate_irr(cash_flows)
        
        # 6. 투자 회수 기간 계산
        payback_period = self._calculate_payback_period(cash_flows)
        
        # 7. NPV 계산
        npv_value = self._calculate_npv(cash_flows, self.DEFAULT_DISCOUNT_RATE)
        
        return ROIAnalysisResponse(
            project_name=request.project_name,
            total_investment=total_investment,
            total_revenue=total_revenue,
            net_profit=net_profit,
            roi_percentage=round(roi_percentage, 2),
            irr_percentage=round(irr_percentage, 2) if irr_percentage else None,
            payback_period_years=round(payback_period, 2),
            cash_flows=cash_flows,
            npv=round(npv_value, 2) if npv_value else None
        )
    
    def _generate_cash_flows(self, request: ROIAnalysisRequest) -> List[CashFlowItem]:
        """
        연도별 현금흐름 생성
        
        Args:
            request: ROI 분석 요청
            
        Returns:
            List[CashFlowItem]: 현금흐름 목록
        """
        cash_flows = []
        
        # 토지 매입 (Year 0 또는 지정된 시점)
        cash_flows.append(CashFlowItem(
            year=request.land_acquisition_year,
            amount=-request.land_acquisition_cost,
            description="토지 매입"
        ))
        
        # 건축비 분할 지출 (건축 기간 동안)
        construction_years = request.construction_duration_years
        construction_per_year = request.construction_cost / construction_years
        
        for i in range(construction_years):
            year = request.construction_start_year + i
            cash_flows.append(CashFlowItem(
                year=year,
                amount=-construction_per_year,
                description=f"건축비 ({i+1}차)"
            ))
        
        # 기타 비용 (건축 마지막 해에 일괄 지출)
        if request.other_costs > 0:
            last_construction_year = request.construction_start_year + construction_years - 1
            cash_flows.append(CashFlowItem(
                year=last_construction_year,
                amount=-request.other_costs,
                description="기타 비용 (설계비, 인허가비 등)"
            ))
        
        # LH 매입 (수익 발생)
        cash_flows.append(CashFlowItem(
            year=request.lh_purchase_year,
            amount=request.lh_purchase_price,
            description="LH 매입 대금 수령"
        ))
        
        # 연도순으로 정렬
        cash_flows.sort(key=lambda x: x.year)
        
        return cash_flows
    
    def _calculate_irr(self, cash_flows: List[CashFlowItem]) -> Optional[float]:
        """
        내부수익률(IRR) 계산
        
        Args:
            cash_flows: 현금흐름 목록
            
        Returns:
            Optional[float]: IRR (%), 계산 불가시 None
        """
        try:
            # 연도별로 그룹화하여 합산
            max_year = max(cf.year for cf in cash_flows)
            yearly_flows = [0.0] * (max_year + 1)
            
            for cf in cash_flows:
                yearly_flows[cf.year] += cf.amount
            
            # numpy_financial의 irr 함수 사용
            irr_value = irr(yearly_flows)
            
            # irr은 소수로 반환되므로 퍼센트로 변환
            if not np.isnan(irr_value) and np.isfinite(irr_value):
                return irr_value * 100
            else:
                return None
                
        except Exception:
            return None
    
    def _calculate_npv(
        self, 
        cash_flows: List[CashFlowItem], 
        discount_rate: float
    ) -> Optional[float]:
        """
        순현재가치(NPV) 계산
        
        Args:
            cash_flows: 현금흐름 목록
            discount_rate: 할인율 (소수)
            
        Returns:
            Optional[float]: NPV (원), 계산 불가시 None
        """
        try:
            # 연도별로 그룹화하여 합산
            max_year = max(cf.year for cf in cash_flows)
            yearly_flows = [0.0] * (max_year + 1)
            
            for cf in cash_flows:
                yearly_flows[cf.year] += cf.amount
            
            # numpy_financial의 npv 함수 사용
            # 첫 번째 현금흐름은 Year 0이므로 별도 처리
            npv_value = yearly_flows[0] + npv(discount_rate, yearly_flows[1:])
            
            if np.isfinite(npv_value):
                return npv_value
            else:
                return None
                
        except Exception:
            return None
    
    def _calculate_payback_period(self, cash_flows: List[CashFlowItem]) -> float:
        """
        투자 회수 기간 계산 (단순 회수 기간)
        
        Args:
            cash_flows: 현금흐름 목록
            
        Returns:
            float: 회수 기간 (년)
        """
        # 연도별로 그룹화하여 누적 현금흐름 계산
        max_year = max(cf.year for cf in cash_flows)
        yearly_flows = [0.0] * (max_year + 1)
        
        for cf in cash_flows:
            yearly_flows[cf.year] += cf.amount
        
        # 누적 현금흐름 계산
        cumulative_flow = 0.0
        for year, flow in enumerate(yearly_flows):
            cumulative_flow += flow
            
            # 누적 현금흐름이 0을 넘으면 회수 완료
            if cumulative_flow >= 0:
                # 이전 연도의 누적 현금흐름
                prev_cumulative = cumulative_flow - flow
                
                # 회수 기간 = 이전 연도 + (남은 금액 / 현재 연도 현금흐름)
                if flow > 0:
                    fraction = abs(prev_cumulative) / flow
                    return year + fraction
                else:
                    return float(year)
        
        # 회수되지 않으면 전체 기간 반환
        return float(max_year)


# 편의 함수
def calculate_roi_irr(request: ROIAnalysisRequest) -> ROIAnalysisResponse:
    """
    ROI/IRR 분석 편의 함수
    
    Args:
        request: ROI 분석 요청
        
    Returns:
        ROIAnalysisResponse: 분석 결과
    """
    calculator = ROIIRRCalculator()
    return calculator.calculate(request)
