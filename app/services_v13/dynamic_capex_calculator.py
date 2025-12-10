"""
ZeroSite v23 - Dynamic CAPEX Calculator
========================================

시장가 기반 CAPEX 토지비 동적 계산 + LH 인정 건축비 검증

Author: ZeroSite AI Analysis System
Date: 2025-12-10
Version: v23
"""

from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DynamicCapexCalculator:
    """
    동적 CAPEX 계산기
    
    기능:
    1. 시장가 기반 CAPEX 토지비 동적 계산
    2. LH 인정 건축비 검증
    3. CAPEX 재조정 권장사항
    """
    
    # Default ratios
    DEFAULT_LAND_RATIO = 0.25  # 25% (기존 고정 비율)
    MIN_LAND_RATIO = 0.15      # 15% (최소)
    MAX_LAND_RATIO = 0.50      # 50% (최대)
    
    # LH Standards
    LH_STANDARD_CONSTRUCTION_COST = 3500000  # 350만원/㎡
    LH_TOLERANCE_RATIO = 1.20  # LH 표준 +20% 이내 권장
    
    def __init__(self):
        """Initialize Dynamic CAPEX Calculator"""
        logger.info("💰 Dynamic CAPEX Calculator v23 초기화")
    
    def calculate_dynamic_land_cost(
        self,
        market_land_value: float,
        capex_total: float,
        negotiation_discount: float = 0.05,
        use_dynamic: bool = True
    ) -> Dict:
        """
        시장가 기반 CAPEX 토지비 동적 계산
        
        Args:
            market_land_value: 시장 토지가 (원)
            capex_total: 총 CAPEX (원)
            negotiation_discount: 협상 할인율 (기본 5%)
            use_dynamic: 동적 비율 사용 여부
        
        Returns:
            {
                'estimated_land_cost': 협상 후 예상 토지비,
                'land_cost_ratio': CAPEX 대비 비율,
                'land_cost_won': 최종 CAPEX 토지비,
                'adjustment_needed': 조정 필요 여부,
                'recommendation': 권장사항
            }
        """
        if not use_dynamic:
            # Use fixed ratio (기존 방식)
            land_cost_won = capex_total * self.DEFAULT_LAND_RATIO
            
            return {
                'method': 'Fixed Ratio',
                'estimated_land_cost_won': market_land_value * (1 - negotiation_discount),
                'estimated_land_cost_eok': market_land_value * (1 - negotiation_discount) / 1e8,
                'land_cost_ratio': self.DEFAULT_LAND_RATIO,
                'land_cost_ratio_pct': self.DEFAULT_LAND_RATIO * 100,
                'land_cost_won': land_cost_won,
                'land_cost_eok': land_cost_won / 1e8,
                'adjustment_needed': False,
                'recommendation': f'고정 비율 {self.DEFAULT_LAND_RATIO*100:.0f}% 적용',
                'discrepancy_eok': (market_land_value - land_cost_won) / 1e8,
                'discrepancy_pct': ((market_land_value - land_cost_won) / market_land_value * 100) if market_land_value > 0 else 0
            }
        
        # STEP 1: 협상 후 예상 토지비
        estimated_land_cost = market_land_value * (1 - negotiation_discount)
        
        # STEP 2: CAPEX 대비 비율 계산
        raw_ratio = estimated_land_cost / capex_total if capex_total > 0 else 0
        
        # STEP 3: 비율 제한 (15% ~ 50%)
        capped_ratio = max(self.MIN_LAND_RATIO, min(self.MAX_LAND_RATIO, raw_ratio))
        
        # STEP 4: 최종 CAPEX 토지비
        land_cost_won = capex_total * capped_ratio
        
        # STEP 5: 조정 로직
        adjustment_needed = False
        recommendation = ""
        recommended_capex = capex_total
        
        if raw_ratio > self.MAX_LAND_RATIO:
            # 토지비가 CAPEX의 50% 초과 → CAPEX 증액 필요
            adjustment_needed = True
            recommended_capex = estimated_land_cost / self.MAX_LAND_RATIO
            recommendation = (
                f"⚠️ CAPEX 증액 필요: 토지비 비율 {raw_ratio*100:.1f}% → "
                f"{self.MAX_LAND_RATIO*100:.0f}%로 제한\n"
                f"   현재 CAPEX: {capex_total/1e8:.0f}억원\n"
                f"   권장 CAPEX: {recommended_capex/1e8:.0f}억원 "
                f"(+{(recommended_capex-capex_total)/1e8:.0f}억원)"
            )
        elif raw_ratio < self.MIN_LAND_RATIO:
            # 토지비가 CAPEX의 15% 미만 → 토지비 비율 상향
            adjustment_needed = True
            recommendation = (
                f"✅ 토지비 비율 조정: {raw_ratio*100:.1f}% → "
                f"{self.MIN_LAND_RATIO*100:.0f}%로 상향\n"
                f"   시장가 대비 저평가된 토지 확보 가능"
            )
        else:
            # 정상 범위 (15% ~ 50%)
            recommendation = (
                f"✅ 정상 범위 ({capped_ratio*100:.1f}%): "
                f"시장가 기반 토지비 산정 완료"
            )
        
        logger.info(f"💰 Dynamic Land Cost: {land_cost_won/1e8:.2f}억원 ({capped_ratio*100:.1f}%)")
        
        return {
            'method': 'Market-based Dynamic',
            'estimated_land_cost_won': estimated_land_cost,
            'estimated_land_cost_eok': round(estimated_land_cost / 1e8, 2),
            'land_cost_ratio': capped_ratio,
            'land_cost_ratio_pct': round(capped_ratio * 100, 1),
            'land_cost_won': land_cost_won,
            'land_cost_eok': round(land_cost_won / 1e8, 2),
            'adjustment_needed': adjustment_needed,
            'recommended_capex_won': recommended_capex,
            'recommended_capex_eok': round(recommended_capex / 1e8, 2),
            'recommendation': recommendation,
            'raw_ratio': raw_ratio,
            'raw_ratio_pct': round(raw_ratio * 100, 1),
            'negotiation_discount_pct': negotiation_discount * 100,
            'discrepancy_eok': round((market_land_value - land_cost_won) / 1e8, 2),
            'discrepancy_pct': round((market_land_value - land_cost_won) / market_land_value * 100, 1) if market_land_value > 0 else 0
        }
    
    def validate_construction_cost(
        self,
        capex_building_cost: float,
        gross_floor_area: float,
        lh_standard: float = None
    ) -> Dict:
        """
        LH 인정 건축비 검증
        
        Args:
            capex_building_cost: CAPEX 건축비 (원)
            gross_floor_area: 연면적 (㎡)
            lh_standard: LH 표준건축비 (원/㎡, 기본 350만원)
        
        Returns:
            {
                'status': 'OK' | 'WARNING' | 'ERROR',
                'capex_cost_per_sqm': CAPEX 건축비/㎡,
                'lh_standard': LH 표준건축비/㎡,
                'excess': 초과액,
                'message': 검증 메시지
            }
        """
        if lh_standard is None:
            lh_standard = self.LH_STANDARD_CONSTRUCTION_COST
        
        if gross_floor_area <= 0:
            return {
                'status': 'ERROR',
                'message': '연면적이 0 이하입니다.'
            }
        
        # Calculate per-sqm cost
        capex_cost_per_sqm = capex_building_cost / gross_floor_area
        
        # LH tolerance threshold
        lh_max_acceptable = lh_standard * self.LH_TOLERANCE_RATIO
        
        # Excess calculation
        excess_won = capex_cost_per_sqm - lh_standard
        excess_pct = (excess_won / lh_standard * 100) if lh_standard > 0 else 0
        
        # Status determination
        if capex_cost_per_sqm <= lh_standard:
            status = 'OK'
            message = (
                f"✅ 건축비 적정: {capex_cost_per_sqm/10000:.0f}만원/㎡ "
                f"≤ LH 표준 {lh_standard/10000:.0f}만원/㎡"
            )
        elif capex_cost_per_sqm <= lh_max_acceptable:
            status = 'WARNING'
            message = (
                f"⚠️ 건축비 주의: {capex_cost_per_sqm/10000:.0f}만원/㎡가 "
                f"LH 표준 {lh_standard/10000:.0f}만원/㎡를 {excess_pct:.0f}% 초과\n"
                f"   (LH 인정 한도: +{self.LH_TOLERANCE_RATIO*100-100:.0f}% 이내)"
            )
        else:
            status = 'ERROR'
            message = (
                f"❌ 건축비 과다: {capex_cost_per_sqm/10000:.0f}만원/㎡가 "
                f"LH 표준 {lh_standard/10000:.0f}만원/㎡를 {excess_pct:.0f}% 초과\n"
                f"   → LH 매입가 < CAPEX 위험 (사업성 없음)\n"
                f"   권장: 건축비를 {lh_max_acceptable/10000:.0f}만원/㎡ 이하로 조정"
            )
        
        logger.info(f"🔍 Construction Cost Validation: {status} - {capex_cost_per_sqm/10000:.0f}만원/㎡")
        
        return {
            'status': status,
            'capex_cost_per_sqm': capex_cost_per_sqm,
            'capex_cost_per_sqm_man': round(capex_cost_per_sqm / 10000, 0),
            'lh_standard': lh_standard,
            'lh_standard_man': round(lh_standard / 10000, 0),
            'lh_max_acceptable': lh_max_acceptable,
            'lh_max_acceptable_man': round(lh_max_acceptable / 10000, 0),
            'excess_won': excess_won,
            'excess_man': round(excess_won / 10000, 0),
            'excess_pct': round(excess_pct, 1),
            'message': message
        }
    
    def adjust_capex_breakdown(
        self,
        capex_total: float,
        land_cost: float,
        gross_floor_area: float
    ) -> Dict:
        """
        CAPEX 세부 항목 동적 조정
        
        토지비가 확정되면, 나머지 항목 비율을 조정
        
        Args:
            capex_total: 총 CAPEX (원)
            land_cost: 확정된 토지비 (원)
            gross_floor_area: 연면적 (㎡)
        
        Returns:
            {
                'land_cost': 토지비,
                'construction': 건축비,
                'indirect': 간접비,
                'design': 설계비,
                'other': 기타비용,
                'validation': 건축비 검증 결과
            }
        """
        remaining_budget = capex_total - land_cost
        
        # 기본 비율 (토지비 제외)
        # 기존: 건축비 55%, 간접비 10%, 설계비 5%, 기타 5% = 75%
        # 토지비 제외 후 정규화
        base_ratios = {
            'construction': 0.55,
            'indirect': 0.10,
            'design': 0.05,
            'other': 0.05
        }
        
        total_ratio = sum(base_ratios.values())
        
        # 비율 정규화
        adjusted = {}
        for key, ratio in base_ratios.items():
            amount = remaining_budget * (ratio / total_ratio)
            adjusted[key] = {
                'amount_won': amount,
                'amount_eok': round(amount / 1e8, 2),
                'ratio_pct': round((ratio / total_ratio) * 100, 1)
            }
        
        # 건축비 검증
        construction_validation = self.validate_construction_cost(
            capex_building_cost=adjusted['construction']['amount_won'],
            gross_floor_area=gross_floor_area
        )
        
        return {
            'land_cost_won': land_cost,
            'land_cost_eok': round(land_cost / 1e8, 2),
            'land_cost_ratio_pct': round(land_cost / capex_total * 100, 1),
            'construction': adjusted['construction'],
            'indirect': adjusted['indirect'],
            'design': adjusted['design'],
            'other': adjusted['other'],
            'remaining_budget_won': remaining_budget,
            'remaining_budget_eok': round(remaining_budget / 1e8, 2),
            'validation': construction_validation
        }


def format_dynamic_capex_report(
    land_cost_result: Dict,
    validation_result: Dict,
    breakdown_result: Optional[Dict] = None
) -> str:
    """
    Dynamic CAPEX 분석 리포트 포맷팅
    """
    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZeroSite v23 - Dynamic CAPEX 분석 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 시장가 기반 CAPEX 토지비 동적 계산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

계산 방법: {land_cost_result['method']}

예상 토지비 (협상 후):
  • {land_cost_result['estimated_land_cost_eok']:.2f}억원
  • (협상 할인율: {land_cost_result.get('negotiation_discount_pct', 5.0):.0f}%)

CAPEX 토지비:
  • {land_cost_result['land_cost_eok']:.2f}억원
  • 비율: {land_cost_result['land_cost_ratio_pct']:.1f}%
  • (원래 비율: {land_cost_result.get('raw_ratio_pct', 0):.1f}%)

{land_cost_result['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. LH 인정 건축비 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

상태: {validation_result['status']}

CAPEX 건축비: {validation_result['capex_cost_per_sqm_man']}만원/㎡
LH 표준건축비: {validation_result['lh_standard_man']}만원/㎡
LH 인정 한도: {validation_result['lh_max_acceptable_man']}만원/㎡ (표준 +20%)

초과액: {validation_result['excess_man']}만원/㎡ ({validation_result['excess_pct']:.1f}%)

{validation_result['message']}
"""
    
    if breakdown_result:
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. CAPEX 세부 항목 (조정 후)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────┬────────┬───────────┬──────────────┐
│   항목       │  비율  │   금액    │     상태     │
├──────────────┼────────┼───────────┼──────────────┤
│ 토지비       │ {breakdown_result['land_cost_ratio_pct']:>5.1f}% │ {breakdown_result['land_cost_eok']:>8.2f}억│ ✅ 시장가 기반│
│ 직접 건축비  │ {breakdown_result['construction']['ratio_pct']:>5.1f}% │ {breakdown_result['construction']['amount_eok']:>8.2f}억│ {_get_status_icon(breakdown_result['validation']['status'])} {breakdown_result['validation']['status']:<12}│
│ 간접비       │ {breakdown_result['indirect']['ratio_pct']:>5.1f}% │ {breakdown_result['indirect']['amount_eok']:>8.2f}억│              │
│ 설계비       │ {breakdown_result['design']['ratio_pct']:>5.1f}% │ {breakdown_result['design']['amount_eok']:>8.2f}억│              │
│ 기타비용     │ {breakdown_result['other']['ratio_pct']:>5.1f}% │ {breakdown_result['other']['amount_eok']:>8.2f}억│              │
└──────────────┴────────┴───────────┴──────────────┘
"""
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report


def _get_status_icon(status: str) -> str:
    """Get status icon"""
    if status == 'OK':
        return '✅'
    elif status == 'WARNING':
        return '⚠️'
    else:
        return '❌'


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    calculator = DynamicCapexCalculator()
    
    # Test 1: Dynamic land cost
    land_result = calculator.calculate_dynamic_land_cost(
        market_land_value=24200000000,  # 242억
        capex_total=30000000000,  # 300억
        use_dynamic=True
    )
    
    # Test 2: Construction cost validation
    validation_result = calculator.validate_construction_cost(
        capex_building_cost=16500000000,  # 165억 (55%)
        gross_floor_area=2200
    )
    
    # Test 3: CAPEX breakdown adjustment
    breakdown_result = calculator.adjust_capex_breakdown(
        capex_total=30000000000,
        land_cost=land_result['land_cost_won'],
        gross_floor_area=2200
    )
    
    print(format_dynamic_capex_report(land_result, validation_result, breakdown_result))
