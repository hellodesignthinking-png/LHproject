"""
LH 매입가 시뮬레이션 모듈

LH(한국토지주택공사)의 공공주택 매입 기준에 따른 매입가 산정
- 토지비 + 건축비 + 적정이윤
- 사업 유형별 이윤율 차등 적용
- LH 매입 기준 검증
"""

from datetime import datetime
from typing import List
from .models import (
    UnitType,
    PurchaseSimulationRequest,
    PurchaseSimulationResponse
)


class LHPurchaseCalculator:
    """LH 매입가 산정 계산기"""
    
    # LH 매입 기준 (2025년 기준)
    # 출처: LH 공공주택 매입약정 가이드라인
    
    # 사업 유형별 적정이윤율
    PROFIT_RATES = {
        UnitType.YOUTH: 0.08,  # 청년주택: 8%
        UnitType.NEWLYWED: 0.09,  # 신혼희망: 9%
        UnitType.PUBLIC_RENTAL: 0.07,  # 공공임대: 7%
    }
    
    # LH 매입 조건
    PURCHASE_CRITERIA = {
        UnitType.YOUTH: {
            "max_area_per_unit": 60,  # 전용 60㎡ 이하
            "min_units": 10,  # 최소 10세대
            "location": ["서울", "경기", "인천", "세종"],  # 수도권 및 세종
        },
        UnitType.NEWLYWED: {
            "max_area_per_unit": 85,  # 전용 85㎡ 이하
            "min_units": 20,  # 최소 20세대
            "location": [],  # 전국 (제한 없음)
        },
        UnitType.PUBLIC_RENTAL: {
            "max_area_per_unit": 60,  # 전용 60㎡ 이하
            "min_units": 30,  # 최소 30세대
            "location": [],  # 전국 (제한 없음)
        },
    }
    
    def __init__(self):
        """초기화"""
        pass
    
    def calculate(self, request: PurchaseSimulationRequest) -> PurchaseSimulationResponse:
        """
        LH 매입가 계산
        
        매입가 = 토지비 + 건축비 + 적정이윤
        적정이윤 = (토지비 + 건축비) × 이윤율
        
        Args:
            request: 매입가 시뮬레이션 요청
            
        Returns:
            PurchaseSimulationResponse: 계산 결과
        """
        # 1. 이윤율 결정 (사용자 지정 또는 자동)
        profit_rate = request.custom_profit_rate if request.custom_profit_rate else self.PROFIT_RATES[request.unit_type]
        
        # 2. 적정이윤 계산
        total_cost = request.land_value + request.construction_cost
        profit_amount = total_cost * profit_rate
        
        # 3. LH 총 매입가
        total_purchase_price = total_cost + profit_amount
        
        # 4. 단가 계산
        price_per_unit = total_purchase_price / request.num_units
        total_pyeong = request.gross_area / 3.3
        price_per_pyeong = total_purchase_price / total_pyeong
        price_per_sqm = total_purchase_price / request.gross_area
        
        # 5. ROI 계산
        total_investment = total_cost
        expected_profit = profit_amount
        roi_percentage = (expected_profit / total_investment) * 100
        
        # 6. LH 매입 기준 검증
        is_eligible, eligibility_notes = self._check_eligibility(request)
        
        return PurchaseSimulationResponse(
            land_value=request.land_value,
            construction_cost=request.construction_cost,
            profit_rate=profit_rate * 100,  # 퍼센트로 변환
            profit_amount=round(profit_amount),
            total_purchase_price=round(total_purchase_price),
            price_per_unit=round(price_per_unit),
            price_per_pyeong=round(price_per_pyeong),
            price_per_sqm=round(price_per_sqm),
            total_investment=round(total_investment),
            expected_profit=round(expected_profit),
            roi_percentage=round(roi_percentage, 2),
            is_eligible=is_eligible,
            eligibility_notes=eligibility_notes,
            calculated_at=datetime.now()
        )
    
    def _check_eligibility(self, request: PurchaseSimulationRequest) -> tuple[bool, List[str]]:
        """
        LH 매입 기준 충족 여부 검증
        
        Args:
            request: 요청 데이터
            
        Returns:
            (충족 여부, 검토 메모 리스트)
        """
        criteria = self.PURCHASE_CRITERIA[request.unit_type]
        notes = []
        is_eligible = True
        
        # 1. 세대당 면적 체크
        avg_area_per_unit = request.gross_area / request.num_units
        max_area = criteria["max_area_per_unit"]
        
        if avg_area_per_unit > max_area:
            is_eligible = False
            notes.append(f"❌ 세대당 면적 초과: {avg_area_per_unit:.1f}㎡ > {max_area}㎡")
        else:
            notes.append(f"✅ 세대당 면적 적합: {avg_area_per_unit:.1f}㎡ ≤ {max_area}㎡")
        
        # 2. 최소 세대수 체크
        min_units = criteria["min_units"]
        
        if request.num_units < min_units:
            is_eligible = False
            notes.append(f"❌ 최소 세대수 미달: {request.num_units}세대 < {min_units}세대")
        else:
            notes.append(f"✅ 세대수 충족: {request.num_units}세대 ≥ {min_units}세대")
        
        # 3. 지역 조건 체크
        allowed_locations = criteria["location"]
        
        if allowed_locations:  # 지역 제한이 있는 경우
            region_key = request.region.split()[0].replace("특별시", "").replace("광역시", "").replace("도", "")
            
            if region_key in allowed_locations:
                notes.append(f"✅ 지역 조건 충족: {request.region}")
            else:
                is_eligible = False
                notes.append(f"❌ 지역 조건 불충족: {request.region} (허용 지역: {', '.join(allowed_locations)})")
        else:
            notes.append("✅ 지역 제한 없음 (전국 가능)")
        
        # 4. 종합 평가
        if is_eligible:
            notes.insert(0, "🎉 LH 매입 기준 충족 - 매입 가능성 높음")
        else:
            notes.insert(0, "⚠️ LH 매입 기준 일부 미충족 - 추가 검토 필요")
        
        return is_eligible, notes
    
    def calculate_with_market_comparison(
        self,
        request: PurchaseSimulationRequest,
        market_price_per_sqm: float
    ) -> dict:
        """
        시장가 대비 LH 매입가 비교 분석
        
        Args:
            request: 매입가 시뮬레이션 요청
            market_price_per_sqm: 시장 분양가 (㎡당 원)
            
        Returns:
            dict: 비교 분석 결과
        """
        # LH 매입가 계산
        lh_result = self.calculate(request)
        
        # 시장 분양가 총액
        market_total_price = market_price_per_sqm * request.gross_area
        
        # 차이 계산
        price_difference = market_total_price - lh_result.total_purchase_price
        price_difference_rate = (price_difference / market_total_price) * 100
        
        return {
            "lh_purchase": lh_result,
            "market_total_price": round(market_total_price),
            "market_price_per_sqm": market_price_per_sqm,
            "price_difference": round(price_difference),
            "price_difference_rate": round(price_difference_rate, 2),
            "is_lh_cheaper": price_difference > 0,
            "recommendation": self._generate_recommendation(price_difference_rate)
        }
    
    def _generate_recommendation(self, price_difference_rate: float) -> str:
        """
        가격 차이에 따른 권장사항 생성
        
        Args:
            price_difference_rate: 가격 차이율 (%)
            
        Returns:
            str: 권장사항
        """
        if price_difference_rate > 30:
            return "✅ 시장가 대비 매우 유리 - LH 매입 적극 추천"
        elif price_difference_rate > 15:
            return "✅ 시장가 대비 유리 - LH 매입 권장"
        elif price_difference_rate > 5:
            return "⚠️ 시장가와 유사 - LH 매입 검토 필요"
        elif price_difference_rate > -5:
            return "⚠️ 시장가와 거의 동일 - 신중한 검토 필요"
        else:
            return "❌ 시장가 대비 불리 - LH 매입 재검토 권장"


# 편의 함수
def calculate_lh_purchase(request: PurchaseSimulationRequest) -> PurchaseSimulationResponse:
    """
    LH 매입가 계산 편의 함수
    
    Args:
        request: 계산 요청
        
    Returns:
        PurchaseSimulationResponse: 계산 결과
    """
    calculator = LHPurchaseCalculator()
    return calculator.calculate(request)
