"""
ZeroSite v17 - Private Rental Financial Engine
민간형 30년 임대운영 사업성 평가 엔진 (참고용)

핵심 개념:
- 30년 장기 임대운영 모델
- 운영 수익 기반 평가 (NOI, Cap Rate, IRR)
- 민간 개발사업자 관점 분석
- LH 신축매입임대와는 다른 모델 (비교 참고용으로만 사용)

주의사항:
- 이 엔진은 **참고용**입니다
- 실제 LH 신축매입임대 사업 평가는 PolicyTransactionFinancialEngine을 사용하세요
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PrivateRentalResult:
    """민간형 임대운영 평가 결과"""
    # CAPEX
    capex_total: float
    land_cost: float
    construction_cost: float
    
    # 30년 운영 수익
    annual_revenue: float
    annual_opex: float
    noi: float  # Net Operating Income
    
    # 수익성 지표
    cap_rate: float  # NOI / CAPEX
    npv_30yr: float  # 30년 NPV (2.87% 할인율)
    irr_30yr: float  # 30년 IRR
    payback_years: float  # 회수기간
    
    # 30년 현금흐름
    cash_flow_30yr: List[Dict[str, float]]
    
    # 판단
    decision: str  # GO / NO_GO / REVISE
    decision_reason: str


class PrivateRentalFinancialEngine:
    """
    민간형 임대운영 재무 평가 엔진
    
    전통적인 부동산 개발 프로젝트 평가 방법:
    1. 30년 임대운영 수익 모델
    2. NOI 기반 수익성 평가
    3. Cap Rate, IRR, NPV 계산
    4. 민간 시장 할인율 적용 (5.5%)
    
    **중요**: 이 모델은 LH 신축매입임대 사업에는 적합하지 않습니다.
             LH 사업은 "매입 거래"가 핵심이므로 PolicyTransactionFinancialEngine을 사용하세요.
    """
    
    def __init__(self):
        self.public_discount_rate = 0.0287  # 공공 할인율 2.87%
        self.private_discount_rate = 0.055  # 민간 할인율 5.5%
        self.operating_period_years = 30  # 30년 운영
        
    def calculate_30yr_cash_flow(
        self,
        capex_total: float,
        annual_revenue: float,
        annual_opex: float,
        growth_rate: float = 0.02
    ) -> List[Dict[str, float]]:
        """
        30년 현금흐름 계산
        
        Args:
            capex_total: 초기 투자비
            annual_revenue: 연간 수익
            annual_opex: 연간 운영비
            growth_rate: 연간 성장률 (기본 2%)
            
        Returns:
            30년 현금흐름 리스트
        """
        cash_flow = []
        cumulative_cash = -capex_total
        
        for year in range(1, 31):
            # 첫 5년은 램프업 기간
            if year <= 5:
                occupancy_rate = 0.5 + (year - 1) * 0.1  # 50% -> 90%
            else:
                occupancy_rate = 0.90  # 90% 안정화
            
            # 6년차부터 2% 성장
            if year >= 6:
                revenue = annual_revenue * occupancy_rate * ((1 + growth_rate) ** (year - 6))
                opex = annual_opex * occupancy_rate * ((1 + growth_rate) ** (year - 6))
            else:
                revenue = annual_revenue * occupancy_rate
                opex = annual_opex * occupancy_rate
            
            net_cash = revenue - opex
            cumulative_cash += net_cash
            
            cash_flow.append({
                'year': year,
                'revenue': revenue,
                'opex': opex,
                'net_cash_flow': net_cash,
                'cumulative_cash_flow': cumulative_cash,
                'occupancy_rate': occupancy_rate
            })
        
        return cash_flow
    
    def calculate_npv(
        self,
        cash_flow: List[Dict[str, float]],
        discount_rate: float
    ) -> float:
        """
        NPV 계산
        
        Args:
            cash_flow: 현금흐름 리스트
            discount_rate: 할인율
            
        Returns:
            NPV 값
        """
        npv = -cash_flow[0]['cumulative_cash_flow'] if cash_flow else 0  # Initial investment
        
        for cf in cash_flow:
            year = cf['year']
            net_cash = cf['net_cash_flow']
            npv += net_cash / ((1 + discount_rate) ** year)
        
        return npv
    
    def calculate_irr(
        self,
        capex_total: float,
        cash_flow: List[Dict[str, float]]
    ) -> float:
        """
        IRR 계산 (Newton-Raphson method)
        
        Args:
            capex_total: 초기 투자비
            cash_flow: 현금흐름 리스트
            
        Returns:
            IRR 값
        """
        # Try numpy first
        try:
            import numpy as np
            cash_flows = [-capex_total] + [cf['net_cash_flow'] for cf in cash_flow]
            irr = np.irr(cash_flows)
            return irr if not np.isnan(irr) else -999.0
        except Exception:
            # Fallback: simple approximation
            total_profit = sum(cf['net_cash_flow'] for cf in cash_flow)
            return (total_profit / capex_total) / len(cash_flow) if capex_total > 0 else -999.0
    
    def calculate_payback_period(
        self,
        cash_flow: List[Dict[str, float]]
    ) -> float:
        """
        회수기간 계산
        
        Args:
            cash_flow: 현금흐름 리스트
            
        Returns:
            회수기간 (년)
        """
        for cf in cash_flow:
            if cf['cumulative_cash_flow'] >= 0:
                return cf['year']
        
        return 999.0  # Never payback
    
    def evaluate(
        self,
        capex_data: Dict[str, Any],
        revenue_data: Dict[str, Any],
        opex_data: Dict[str, Any]
    ) -> PrivateRentalResult:
        """
        민간형 임대운영 사업성 종합 평가
        
        Args:
            capex_data: CAPEX 데이터 (land, construction, total)
            revenue_data: 수익 데이터 (annual_revenue)
            opex_data: 운영비 데이터 (annual_opex)
            
        Returns:
            PrivateRentalResult 객체
        """
        logger.info("=" * 60)
        logger.info("🏢 민간형 임대운영 재무 평가 시작 (30년 모델)")
        logger.info("⚠️  참고: 이 모델은 LH 신축매입임대 사업에는 적합하지 않습니다")
        logger.info("=" * 60)
        
        # 1. CAPEX 추출
        land_cost = capex_data.get('land', 0)
        construction_cost = capex_data.get('construction', 0)
        capex_total = capex_data.get('total', land_cost + construction_cost)
        
        # 2. 수익/비용 추출
        annual_revenue = revenue_data.get('annual', 0)
        annual_opex = opex_data.get('annual', 0)
        noi = annual_revenue - annual_opex
        
        logger.info(f"📊 CAPEX: {capex_total/1e8:.1f}억")
        logger.info(f"💰 연간 수익: {annual_revenue/1e8:.1f}억")
        logger.info(f"💸 연간 운영비: {annual_opex/1e8:.1f}억")
        logger.info(f"✅ NOI: {noi/1e8:.1f}억")
        
        # 3. 30년 현금흐름 생성
        cash_flow_30yr = self.calculate_30yr_cash_flow(
            capex_total=capex_total,
            annual_revenue=annual_revenue,
            annual_opex=annual_opex,
            growth_rate=0.02
        )
        
        # 4. 수익성 지표 계산
        cap_rate = (noi / capex_total) if capex_total > 0 else 0
        npv_public = self.calculate_npv(cash_flow_30yr, self.public_discount_rate)
        npv_private = self.calculate_npv(cash_flow_30yr, self.private_discount_rate)
        irr = self.calculate_irr(capex_total, cash_flow_30yr)
        payback = self.calculate_payback_period(cash_flow_30yr)
        
        logger.info(f"📈 Cap Rate: {cap_rate*100:.2f}%")
        logger.info(f"💵 NPV (Public 2.87%): {npv_public/1e8:.1f}억")
        logger.info(f"💵 NPV (Private 5.5%): {npv_private/1e8:.1f}억")
        logger.info(f"📊 IRR: {irr*100:.2f}%")
        logger.info(f"⏱️  Payback: {payback:.1f}년")
        
        # 5. 의사결정
        decision, reason = self._make_decision(
            npv_public=npv_public,
            irr=irr,
            payback=payback
        )
        
        logger.info(f"🎯 판단: {decision}")
        logger.info(f"📝 근거: {reason}")
        logger.info("=" * 60)
        
        return PrivateRentalResult(
            capex_total=capex_total,
            land_cost=land_cost,
            construction_cost=construction_cost,
            annual_revenue=annual_revenue,
            annual_opex=annual_opex,
            noi=noi,
            cap_rate=cap_rate,
            npv_30yr=npv_public,  # Use public discount rate for LH context
            irr_30yr=irr,
            payback_years=payback,
            cash_flow_30yr=cash_flow_30yr,
            decision=decision,
            decision_reason=reason
        )
    
    def _make_decision(
        self,
        npv_public: float,
        irr: float,
        payback: float
    ) -> Tuple[str, str]:
        """
        의사결정 판단
        
        Returns:
            (decision, reason) 튜플
        """
        if npv_public >= 0 and irr >= 0.02 and payback <= 20:
            decision = "GO"
            reason = f"민간형 수익성 양호 (NPV {npv_public/1e8:.1f}억, IRR {irr*100:.1f}%, 회수 {payback:.0f}년). 단, LH 신축매입임대는 거래형 모델이므로 정책형 평가를 참고하세요."
        
        elif npv_public >= -50e8:
            decision = "REVISE"
            reason = f"민간형 수익성 부족 (NPV {npv_public/1e8:.1f}억). 임대운영 모델로는 어려움. LH 신축매입임대는 정책형 평가(매입가 기반)를 참고하세요."
        
        else:
            decision = "NO_GO"
            reason = f"민간형 수익성 매우 부족 (NPV {npv_public/1e8:.1f}억, IRR {irr*100:.1f}%). 임대운영 사업으로는 NO-GO. 단, LH 신축매입임대는 거래형 모델이므로 정책형 평가를 우선 참고하세요."
        
        return decision, reason
