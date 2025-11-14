"""
건축비 자동 산정 모듈

2025년 기준 건축비를 자동으로 계산합니다.
- 주택 유형별 기본 평당 단가
- 지역별 할증률 적용
- 공사 항목별 비용 산출
- 부대비용 (설계/감리/인허가 등) 포함
"""

from datetime import datetime
from .models import (
    UnitType,
    CostCalculationRequest,
    CostCalculationResponse,
    CostBreakdown
)


class ConstructionCostCalculator:
    """건축비 자동 산정 계산기"""
    
    # 2025년 기준 표준 건축비 (평당, 원)
    # 출처: 한국감정원, LH 표준 건축비 기준
    BASE_COSTS = {
        UnitType.YOUTH: 1_200_000,  # 청년주택: 평당 120만원
        UnitType.NEWLYWED: 1_300_000,  # 신혼희망: 평당 130만원
        UnitType.PUBLIC_RENTAL: 1_100_000,  # 공공임대: 평당 110만원
    }
    
    # 지역별 할증률
    # 서울/수도권 등 지가 및 인건비 차이 반영
    REGIONAL_MULTIPLIERS = {
        "서울": 1.20,  # 서울 20% 할증
        "경기": 1.10,  # 경기 10% 할증
        "인천": 1.05,  # 인천 5% 할증
        "세종": 1.08,  # 세종 8% 할증
        "대전": 1.03,  # 대전 3% 할증
        "대구": 1.03,  # 대구 3% 할증
        "부산": 1.05,  # 부산 5% 할증
        "광주": 1.02,  # 광주 2% 할증
        "울산": 1.03,  # 울산 3% 할증
        "강원": 0.95,  # 강원 5% 할인
        "충북": 0.95,  # 충북 5% 할인
        "충남": 0.98,  # 충남 2% 할인
        "전북": 0.93,  # 전북 7% 할인
        "전남": 0.92,  # 전남 8% 할인
        "경북": 0.94,  # 경북 6% 할인
        "경남": 0.96,  # 경남 4% 할인
        "제주": 1.08,  # 제주 8% 할증
    }
    
    # 공사 항목별 비용 배분율
    # 표준 건축비 산정 기준
    COST_RATIOS = {
        "civil": 0.15,  # 토목공사: 15%
        "architecture": 0.50,  # 건축공사: 50%
        "mechanical": 0.15,  # 기계설비: 15%
        "electrical": 0.10,  # 전기공사: 10%
        "landscaping": 0.05,  # 조경공사: 5%
        "others": 0.05,  # 기타: 5%
    }
    
    # 부대비용 비율 (총 건축비의 비율)
    ADDITIONAL_COST_RATE = 0.10  # 10% (설계비, 감리비, 인허가 등)
    
    def __init__(self):
        """초기화"""
        pass
    
    def calculate(self, request: CostCalculationRequest) -> CostCalculationResponse:
        """
        건축비 계산
        
        Args:
            request: 건축비 계산 요청 데이터
            
        Returns:
            CostCalculationResponse: 계산 결과
        """
        # 1. 기본 평당 단가
        base_cost = self.BASE_COSTS[request.unit_type]
        
        # 2. 지역 할증률 적용
        regional_multiplier = self._get_regional_multiplier(request.region)
        
        # 3. 실제 평당 단가 계산
        actual_cost_per_pyeong = base_cost * regional_multiplier
        
        # 4. 연면적을 평으로 변환 (1평 = 3.3㎡)
        total_pyeong = request.gross_area / 3.3
        
        # 5. 총 건축비 계산
        total_cost = actual_cost_per_pyeong * total_pyeong
        
        # 6. 공사 항목별 비용 산출
        breakdown = self._calculate_cost_breakdown(total_cost)
        
        # 7. 부대비용 계산 (설계비, 감리비, 인허가 등)
        additional_costs = total_cost * self.ADDITIONAL_COST_RATE
        
        # 8. 총 사업비 (건축비 + 부대비용)
        grand_total = total_cost + additional_costs
        
        # 9. ㎡당 건축비 계산
        cost_per_sqm = grand_total / request.gross_area
        
        return CostCalculationResponse(
            total_cost=round(total_cost),
            cost_per_pyeong=round(actual_cost_per_pyeong),
            cost_per_sqm=round(cost_per_sqm),
            cost_breakdown=breakdown,
            additional_costs=round(additional_costs),
            grand_total=round(grand_total),
            base_cost_per_pyeong=base_cost,
            regional_multiplier=regional_multiplier,
            total_pyeong=round(total_pyeong, 2),
            calculated_at=datetime.now()
        )
    
    def _get_regional_multiplier(self, region: str) -> float:
        """
        지역별 할증률 조회
        
        Args:
            region: 지역명 (예: "서울특별시", "경기도 수원시")
            
        Returns:
            float: 할증률 (기본값 1.0)
        """
        # 지역명에서 첫 단어 추출 (예: "서울특별시" -> "서울")
        region_key = region.split()[0] if region else ""
        
        # 특별시/광역시 접미사 제거
        region_key = region_key.replace("특별시", "").replace("광역시", "").replace("특별자치시", "").replace("도", "")
        
        # 할증률 조회 (기본값 1.0)
        return self.REGIONAL_MULTIPLIERS.get(region_key, 1.0)
    
    def _calculate_cost_breakdown(self, total_cost: float) -> CostBreakdown:
        """
        공사 항목별 비용 산출
        
        Args:
            total_cost: 총 건축비
            
        Returns:
            CostBreakdown: 항목별 비용
        """
        return CostBreakdown(
            civil=round(total_cost * self.COST_RATIOS["civil"]),
            architecture=round(total_cost * self.COST_RATIOS["architecture"]),
            mechanical=round(total_cost * self.COST_RATIOS["mechanical"]),
            electrical=round(total_cost * self.COST_RATIOS["electrical"]),
            landscaping=round(total_cost * self.COST_RATIOS["landscaping"]),
            others=round(total_cost * self.COST_RATIOS["others"]),
        )
    
    def estimate_by_unit_count(
        self,
        unit_type: UnitType,
        num_units: int,
        avg_unit_area: float,
        region: str
    ) -> CostCalculationResponse:
        """
        세대수 기반 간편 견적
        
        Args:
            unit_type: 주택 유형
            num_units: 세대수
            avg_unit_area: 세대당 평균 면적 (㎡)
            region: 지역명
            
        Returns:
            CostCalculationResponse: 계산 결과
        """
        gross_area = num_units * avg_unit_area * 1.3  # 공용면적 30% 추가
        
        request = CostCalculationRequest(
            unit_type=unit_type,
            gross_area=gross_area,
            region=region,
            num_units=num_units
        )
        
        return self.calculate(request)


# 편의 함수
def calculate_construction_cost(request: CostCalculationRequest) -> CostCalculationResponse:
    """
    건축비 계산 편의 함수
    
    Args:
        request: 계산 요청
        
    Returns:
        CostCalculationResponse: 계산 결과
    """
    calculator = ConstructionCostCalculator()
    return calculator.calculate(request)
