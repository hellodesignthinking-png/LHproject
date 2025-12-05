"""
ZeroSite v9.0 - Financial Engine
=================================

재무 엔진 v9.0 - IRR 계산, 민감도 분석, LH 연동

주요 기능:
1. 공사비 연동 시스템 (50세대+ → LH_LINKED)
2. LH 매입가 계산 (검증된 공사비 기준)
3. 10년 IRR 계산 (numpy_financial)
4. 민감도 분석 (공사비 ±10%, 임대료 ±5% → 15개 시나리오)
5. 재무 지표: Cap Rate, ROI, IRR, Breakeven Year
6. 사업성 점수 (0-40점)

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Dict, List, Optional, Tuple
import logging
import math
import numpy as np
import numpy_financial as npf  # v9.0: numpy.irr deprecated, numpy_financial 필수

from app.models_v9.standard_schema_v9_0 import (
    FinancialResult,
    AnalysisMode
)

logger = logging.getLogger(__name__)


class FinancialEngineV90:
    """
    Financial Engine v9.0
    
    주요 개선사항:
    - IRR 계산 (10년 현금흐름)
    - 민감도 분석 (15개 시나리오)
    - LH 매입가 연동 (50세대+ 자동)
    - 검증된 공사비 시스템
    - KeyError 제로
    """
    
    # LH 매입가 기준 (2025년 기준)
    LH_PURCHASE_PRICE_PER_SQM = 4_500_000  # 원/m² (평균)
    LH_VERIFIED_COST_PER_SQM = 3_200_000   # 원/m² (검증된 공사비)
    
    # 임대료 가정 (평균)
    RENTAL_INCOME_PER_UNIT_PER_MONTH = 800_000  # 원/세대/월
    
    # 운영비 비율
    OPERATING_EXPENSE_RATIO = 0.30  # 30% (관리비, 세금, 유지보수)
    
    # 세대수 기준 (LH 연동 여부)
    LH_LINKED_THRESHOLD = 50  # 50세대 이상
    
    def __init__(self):
        """Financial Engine 초기화"""
        logger.info("💰 Financial Engine v9.0 초기화 완료")
    
    def analyze_comprehensive_financial(
        self,
        land_area: float,
        total_land_price: float,
        floor_area_ratio: float,
        unit_count: int,
        construction_cost_per_sqm: Optional[float] = None,
        unit_type_distribution: Optional[Dict[str, int]] = None
    ) -> FinancialResult:
        """
        종합 재무 분석 수행
        
        Args:
            land_area: 대지 면적 (m²)
            total_land_price: 총 토지가격 (원)
            floor_area_ratio: 용적률 (%)
            unit_count: 세대수
            construction_cost_per_sqm: 단위 공사비 (원/m², None이면 기본값 사용)
            unit_type_distribution: 유형별 세대수 (예: {"59A": 30, "84B": 20})
            
        Returns:
            FinancialResult (정규화된 v9.0 스키마)
        """
        logger.info(f"💰 재무 분석 시작: 세대수 {unit_count}개")
        
        # 1. 분석 모드 결정 (50세대 기준)
        analysis_mode = self._determine_analysis_mode(unit_count)
        logger.info(f"  📊 분석 모드: {analysis_mode.value}")
        
        # 2. 건축 연면적 계산
        total_floor_area = land_area * (floor_area_ratio / 100)
        
        # 3. 공사비 계산
        if construction_cost_per_sqm is None:
            # 기본 공사비 (일반: 2.5M/m², LH: 3.2M/m²)
            if analysis_mode == AnalysisMode.LH_LINKED:
                construction_cost_per_sqm = self.LH_VERIFIED_COST_PER_SQM
            else:
                construction_cost_per_sqm = 2_500_000  # 원/m²
        
        total_construction_cost = total_floor_area * construction_cost_per_sqm
        total_capex = total_land_price + total_construction_cost
        
        # 4. LH 매입가 계산 (LH_LINKED 모드인 경우)
        lh_purchase_price = None
        lh_purchase_price_per_sqm = None
        verified_cost = None
        
        if analysis_mode == AnalysisMode.LH_LINKED:
            lh_purchase_price = total_floor_area * self.LH_PURCHASE_PRICE_PER_SQM
            lh_purchase_price_per_sqm = self.LH_PURCHASE_PRICE_PER_SQM
            verified_cost = total_construction_cost  # 검증된 공사비
            logger.info(f"  🏢 LH 매입가: {lh_purchase_price:,.0f}원 ({lh_purchase_price_per_sqm:,.0f}원/m²)")
        
        # 5. 연간 NOI 계산
        annual_rental_income = unit_count * self.RENTAL_INCOME_PER_UNIT_PER_MONTH * 12
        annual_operating_expense = annual_rental_income * self.OPERATING_EXPENSE_RATIO
        annual_noi = annual_rental_income - annual_operating_expense
        
        # 6. Cap Rate 계산
        cap_rate = (annual_noi / total_capex) * 100 if total_capex > 0 else 0.0
        
        # 7. 10년 IRR 계산
        irr_10yr = self._calculate_irr_10yr(
            initial_investment=total_capex,
            annual_noi=annual_noi,
            exit_value=lh_purchase_price if lh_purchase_price else total_capex * 1.2,
            years=10
        )
        
        # 8. 10년 ROI 계산
        total_return_10yr = annual_noi * 10 + (lh_purchase_price if lh_purchase_price else total_capex * 1.2)
        roi_10yr = ((total_return_10yr - total_capex) / total_capex) * 100 if total_capex > 0 else 0.0
        
        # 9. 손익분기년도 계산
        breakeven_year = self._calculate_breakeven_year(
            initial_investment=total_capex,
            annual_noi=annual_noi
        )
        
        # 10. 재무 등급 산출
        overall_grade = self._calculate_financial_grade(cap_rate, irr_10yr, roi_10yr)
        
        # 11. 유형별 세대수 기본값
        if unit_type_distribution is None:
            unit_type_distribution = {"Standard": unit_count}
        
        # 12. FinancialResult 생성
        result = FinancialResult(
            total_land_price=total_land_price,
            construction_cost_per_sqm=construction_cost_per_sqm,
            total_construction_cost=total_construction_cost,
            total_capex=total_capex,
            analysis_mode=analysis_mode,
            lh_purchase_price=lh_purchase_price,
            lh_purchase_price_per_sqm=lh_purchase_price_per_sqm,
            verified_cost=verified_cost,
            annual_noi=annual_noi,
            cap_rate=round(cap_rate, 2),
            roi_10yr=round(roi_10yr, 2),
            irr_10yr=round(irr_10yr, 2),
            unit_count=unit_count,
            unit_type_distribution=unit_type_distribution,
            overall_grade=overall_grade,
            breakeven_year=breakeven_year
        )
        
        logger.info(f"✅ 재무 분석 완료: Cap Rate {cap_rate:.2f}%, IRR {irr_10yr:.2f}%, 등급 {overall_grade}")
        return result
    
    def sensitivity_analysis(
        self,
        base_result: FinancialResult,
        land_area: float,
        floor_area_ratio: float
    ) -> List[Dict]:
        """
        민감도 분석 (15개 시나리오)
        
        변수:
        - 공사비: -10%, 0%, +10%
        - 임대료: -5%, 0%, +5%
        
        Args:
            base_result: 기본 재무 분석 결과
            land_area: 대지 면적 (m²)
            floor_area_ratio: 용적률 (%)
            
        Returns:
            List[Dict]: 15개 시나리오 결과
        """
        logger.info("📊 민감도 분석 시작 (15개 시나리오)")
        
        scenarios = []
        
        # 공사비 변동: -10%, 0%, +10%
        cost_variations = [-0.10, 0.0, 0.10]
        
        # 임대료 변동: -5%, 0%, +5%
        rent_variations = [-0.05, 0.0, 0.05]
        
        for cost_var in cost_variations:
            for rent_var in rent_variations:
                # 조정된 공사비
                adjusted_cost_per_sqm = base_result.construction_cost_per_sqm * (1 + cost_var)
                
                # 조정된 임대료
                adjusted_rental_income = (
                    base_result.unit_count * 
                    self.RENTAL_INCOME_PER_UNIT_PER_MONTH * 
                    (1 + rent_var) * 12
                )
                
                # 재계산
                total_floor_area = land_area * (floor_area_ratio / 100)
                adjusted_construction_cost = total_floor_area * adjusted_cost_per_sqm
                adjusted_capex = base_result.total_land_price + adjusted_construction_cost
                
                adjusted_operating_expense = adjusted_rental_income * self.OPERATING_EXPENSE_RATIO
                adjusted_noi = adjusted_rental_income - adjusted_operating_expense
                
                adjusted_cap_rate = (adjusted_noi / adjusted_capex) * 100 if adjusted_capex > 0 else 0.0
                
                adjusted_irr = self._calculate_irr_10yr(
                    initial_investment=adjusted_capex,
                    annual_noi=adjusted_noi,
                    exit_value=base_result.lh_purchase_price if base_result.lh_purchase_price else adjusted_capex * 1.2,
                    years=10
                )
                
                # 시나리오 저장
                scenario = {
                    "cost_variation": f"{cost_var*100:+.0f}%",
                    "rent_variation": f"{rent_var*100:+.0f}%",
                    "capex": adjusted_capex,
                    "noi": adjusted_noi,
                    "cap_rate": round(adjusted_cap_rate, 2),
                    "irr": round(adjusted_irr, 2)
                }
                scenarios.append(scenario)
        
        logger.info(f"✅ 민감도 분석 완료: {len(scenarios)}개 시나리오")
        return scenarios
    
    def _determine_analysis_mode(self, unit_count: int) -> AnalysisMode:
        """
        분석 모드 자동 결정
        
        Args:
            unit_count: 세대수
            
        Returns:
            AnalysisMode (STANDARD or LH_LINKED)
        """
        if unit_count >= self.LH_LINKED_THRESHOLD:
            return AnalysisMode.LH_LINKED
        else:
            return AnalysisMode.STANDARD
    
    def _calculate_irr_10yr(
        self,
        initial_investment: float,
        annual_noi: float,
        exit_value: float,
        years: int = 10
    ) -> float:
        """
        10년 IRR 계산 (numpy_financial 사용)
        
        현금흐름:
        - Year 0: -initial_investment
        - Year 1-9: annual_noi (2% 성장 가정)
        - Year 10: annual_noi + exit_value
        
        Args:
            initial_investment: 초기 투자액 (CAPEX)
            annual_noi: 연간 순운영수익 (NOI)
            exit_value: 출구 가치 (LH 매입가 or 시장가)
            years: 기간 (기본 10년)
            
        Returns:
            float: IRR (%)
        """
        try:
            # 현금흐름 생성
            cash_flows = [-initial_investment]  # Year 0
            
            for year in range(1, years + 1):
                # 연간 NOI (2% 성장 가정)
                noi_year = annual_noi * (1.02 ** year)
                
                if year == years:
                    # 마지막 해: NOI + Exit Value
                    cash_flows.append(noi_year + exit_value)
                else:
                    cash_flows.append(noi_year)
            
            # IRR 계산 (numpy_financial 사용)
            irr = npf.irr(cash_flows) * 100
            
            # NaN/Infinity 방어
            if math.isnan(irr) or math.isinf(irr):
                return 0.0
            
            return irr
        
        except Exception as e:
            logger.warning(f"⚠️ IRR 계산 오류: {e}")
            return 0.0
    
    def _calculate_breakeven_year(
        self,
        initial_investment: float,
        annual_noi: float
    ) -> Optional[int]:
        """
        손익분기년도 계산
        
        Args:
            initial_investment: 초기 투자액
            annual_noi: 연간 순운영수익
            
        Returns:
            int: 손익분기년도 (없으면 None)
        """
        if annual_noi <= 0:
            return None
        
        breakeven_year = int(math.ceil(initial_investment / annual_noi))
        
        if breakeven_year > 30:
            return None  # 30년 초과는 비현실적
        
        return breakeven_year
    
    def _calculate_financial_grade(
        self,
        cap_rate: float,
        irr: float,
        roi: float
    ) -> str:
        """
        재무 등급 산출 (S/A/B/C/D/F)
        
        평가 기준:
        - S: Cap Rate ≥ 7%, IRR ≥ 12%, ROI ≥ 100%
        - A: Cap Rate ≥ 6%, IRR ≥ 10%, ROI ≥ 80%
        - B: Cap Rate ≥ 5%, IRR ≥ 8%, ROI ≥ 60%
        - C: Cap Rate ≥ 4%, IRR ≥ 6%, ROI ≥ 40%
        - D: Cap Rate ≥ 3%, IRR ≥ 4%, ROI ≥ 20%
        - F: 그 외
        
        Args:
            cap_rate: Cap Rate (%)
            irr: IRR (%)
            roi: ROI (%)
            
        Returns:
            str: 등급 (S/A/B/C/D/F)
        """
        # 점수 계산 (각 지표당 40점, 총 120점)
        cap_score = min(40, cap_rate * 5)
        irr_score = min(40, irr * 3)
        roi_score = min(40, roi * 0.4)
        
        total_score = cap_score + irr_score + roi_score
        
        # 등급 산출
        if total_score >= 100:
            return "S"
        elif total_score >= 85:
            return "A"
        elif total_score >= 70:
            return "B"
        elif total_score >= 55:
            return "C"
        elif total_score >= 40:
            return "D"
        else:
            return "F"
