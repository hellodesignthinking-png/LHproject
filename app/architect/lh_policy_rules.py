"""
ZeroSite Phase 11: LH Policy Rules Database

LH 신축매입임대 정책 기준을 데이터베이스화한 모듈

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.2
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LHSupplyType(str, Enum):
    """LH 공급 유형"""
    YOUTH = "youth"          # 청년형
    NEWLYWED = "newlywed"    # 신혼부부형
    SENIOR = "senior"        # 고령자형
    GENERAL = "general"      # 일반형
    MIXED = "mixed"          # 혼합형


@dataclass
class UnitSizeRule:
    """평형(전용면적) 규칙"""
    unit_type: str
    size_min: float  # 최소 면적 (㎡)
    size_max: float  # 최대 면적 (㎡)
    size_avg: float  # 평균 면적 (㎡)
    default_ratio: float  # 기본 배분 비율


@dataclass
class DesignRule:
    """설계 규칙"""
    rule_name: str
    rule_value: float
    description: str


class LHPolicyRules:
    """
    LH 신축매입임대 정책 규칙 관리
    
    Features:
    - LH 공급유형별 평형 규칙
    - 공용공간 비율 규칙
    - 주차 기준
    - 설계 제약 조건
    """
    
    def __init__(self):
        """Initialize LH policy rules database"""
        self._load_unit_size_rules()
        self._load_design_rules()
    
    def _load_unit_size_rules(self):
        """Load LH unit size rules"""
        
        # LH 공급유형별 평형 규칙
        self.unit_size_rules = {
            LHSupplyType.YOUTH: [
                UnitSizeRule(
                    unit_type="youth_14",
                    size_min=14.0,
                    size_max=14.0,
                    size_avg=14.0,
                    default_ratio=1.0
                )
            ],
            LHSupplyType.NEWLYWED: [
                UnitSizeRule(
                    unit_type="newlywed_18",
                    size_min=18.0,
                    size_max=22.0,
                    size_avg=20.0,
                    default_ratio=0.5
                ),
                UnitSizeRule(
                    unit_type="newlywed_24",
                    size_min=22.0,
                    size_max=26.0,
                    size_avg=24.0,
                    default_ratio=0.5
                )
            ],
            LHSupplyType.SENIOR: [
                UnitSizeRule(
                    unit_type="senior_24",
                    size_min=24.0,
                    size_max=28.0,
                    size_avg=26.0,
                    default_ratio=0.6
                ),
                UnitSizeRule(
                    unit_type="senior_32",
                    size_min=28.0,
                    size_max=32.0,
                    size_avg=30.0,
                    default_ratio=0.4
                )
            ],
            LHSupplyType.MIXED: [
                UnitSizeRule(
                    unit_type="youth_14",
                    size_min=14.0,
                    size_max=14.0,
                    size_avg=14.0,
                    default_ratio=0.7
                ),
                UnitSizeRule(
                    unit_type="newlywed_20",
                    size_min=18.0,
                    size_max=22.0,
                    size_avg=20.0,
                    default_ratio=0.2
                ),
                UnitSizeRule(
                    unit_type="senior_26",
                    size_min=24.0,
                    size_max=28.0,
                    size_avg=26.0,
                    default_ratio=0.1
                )
            ]
        }
    
    def _load_design_rules(self):
        """Load design constraint rules"""
        
        self.design_rules = {
            "common_area_ratio": DesignRule(
                rule_name="common_area_ratio",
                rule_value=0.15,
                description="공용공간 최소 비율 (15% 이상)"
            ),
            "parking_per_unit": DesignRule(
                rule_name="parking_per_unit",
                rule_value=0.2,
                description="도시형생활주택 주차 기준 (0.2대/세대)"
            ),
            "parking_per_unit_seoul": DesignRule(
                rule_name="parking_per_unit_seoul",
                rule_value=0.3,
                description="서울시 주차 기준 (0.3대/세대)"
            ),
            "corridor_width": DesignRule(
                rule_name="corridor_width",
                rule_value=1.8,
                description="복도 최소 폭 (1.8m)"
            ),
            "ceiling_height": DesignRule(
                rule_name="ceiling_height",
                rule_value=2.3,
                description="천장 최소 높이 (2.3m)"
            ),
            "efficiency_ratio": DesignRule(
                rule_name="efficiency_ratio",
                rule_value=0.75,
                description="전용률 목표 (75% 이상)"
            )
        }
    
    def get_unit_rules(self, supply_type: LHSupplyType) -> List[UnitSizeRule]:
        """
        공급유형별 평형 규칙 조회
        
        Args:
            supply_type: LH 공급유형
        
        Returns:
            List of UnitSizeRule
        """
        return self.unit_size_rules.get(supply_type, [])
    
    def get_design_rule(self, rule_name: str) -> Optional[DesignRule]:
        """
        설계 규칙 조회
        
        Args:
            rule_name: 규칙 이름
        
        Returns:
            DesignRule or None
        """
        return self.design_rules.get(rule_name)
    
    def get_common_area_ratio(self) -> float:
        """공용공간 최소 비율"""
        return self.design_rules["common_area_ratio"].rule_value
    
    def get_parking_ratio(self, region: str = "general") -> float:
        """
        주차 기준 조회
        
        Args:
            region: 지역 ("seoul" or "general")
        
        Returns:
            주차대수/세대 비율
        """
        if region.lower() in ["서울", "seoul"]:
            return self.design_rules["parking_per_unit_seoul"].rule_value
        else:
            return self.design_rules["parking_per_unit"].rule_value
    
    def calculate_total_units(
        self,
        total_gfa: float,
        supply_type: LHSupplyType,
        common_area_ratio: Optional[float] = None
    ) -> Dict[str, int]:
        """
        총 세대수 및 유형별 배분 계산
        
        Args:
            total_gfa: 총 연면적 (㎡)
            supply_type: LH 공급유형
            common_area_ratio: 공용공간 비율 (기본: 15%)
        
        Returns:
            Dict with unit counts by type
        """
        if common_area_ratio is None:
            common_area_ratio = self.get_common_area_ratio()
        
        # 공용공간 제외한 순수 주거면적
        net_residential_area = total_gfa * (1 - common_area_ratio)
        
        # 평형 규칙 가져오기
        unit_rules = self.get_unit_rules(supply_type)
        
        if not unit_rules:
            return {}
        
        # 유형별 세대수 계산
        unit_distribution = {}
        remaining_area = net_residential_area
        
        for rule in unit_rules:
            allocated_area = net_residential_area * rule.default_ratio
            unit_count = int(allocated_area / rule.size_avg)
            
            if unit_count > 0:
                unit_distribution[rule.unit_type] = {
                    "count": unit_count,
                    "size_avg": rule.size_avg,
                    "total_area": unit_count * rule.size_avg
                }
        
        return unit_distribution
    
    def get_design_philosophy(self, supply_type: LHSupplyType) -> str:
        """
        공급유형별 설계 철학 텍스트
        
        Args:
            supply_type: LH 공급유형
        
        Returns:
            설계 철학 서술
        """
        philosophies = {
            LHSupplyType.YOUTH: """
본 설계는 LH 청년형 매입임대 정책의 핵심 목표인 '도심 내 청년 주거 안정'과 
'1인 가구 커뮤니티 기반 구축'을 중심으로 계획되었습니다.

14㎡ 전용면적 기준으로 효율적인 공간 활용과 함께, 
공용공간(15% 이상)을 통한 Sharing Economy 모델을 적용하여
개인 공간의 한계를 극복하고 거주자 간 상호작용을 촉진합니다.

커뮤니티 라운지, 공유 주방, 세탁실, 스터디룸 등의 공용시설을 통해
'함께 사는 1인 가구'의 새로운 주거 모델을 제시합니다.
            """,
            
            LHSupplyType.NEWLYWED: """
본 설계는 LH 신혼부부형 매입임대의 정책 목표인 '신혼가구 주거 안정'과
'출산·양육 친화 환경 조성'을 핵심 가치로 합니다.

18~24㎡의 적정 규모 평형 구성으로 신혼 초기부터 자녀 양육까지 
단계별 주거 수요를 충족하며, 공용공간에는 키즈카페, 놀이터, 육아지원시설을
배치하여 육아 부담을 경감합니다.

'함께 키우는 아이들'이라는 커뮤니티 철학으로 
신혼부부의 사회적 연대와 육아 네트워크를 지원합니다.
            """,
            
            LHSupplyType.SENIOR: """
본 설계는 LH 고령자형 매입임대의 '고령자 주거 복지 향상'과
'안전하고 편리한 생활환경 조성'을 목표로 합니다.

24~32㎡의 여유 있는 공간 구성과 함께 무장애(Barrier-Free) 설계를 적용하여
고령자의 안전한 일상생활을 지원합니다.

공용공간에는 건강관리실, 커뮤니티 센터, 돌봄 서비스 공간을 배치하여
고령자의 사회적 고립을 방지하고 건강한 노후 생활을 지원합니다.
            """,
            
            LHSupplyType.MIXED: """
본 설계는 LH 혼합형 매입임대의 '다양한 계층 통합 거주'와
'세대 간 상호 이해 증진'을 핵심 가치로 합니다.

청년(70%), 신혼부부(20%), 고령자(10%)의 균형 있는 구성으로
세대 간 자연스러운 교류와 상호 돌봄 네트워크를 형성합니다.

공용공간은 모든 연령대가 함께 이용할 수 있는 커뮤니티 공간으로 계획되어
'함께 사는 마을(Co-living Village)'의 새로운 주거 모델을 제시합니다.
            """
        }
        
        return philosophies.get(supply_type, "")
    
    def get_policy_fit_narrative(self) -> str:
        """
        LH 정책 적합성 서술
        
        Returns:
            정책 부합성 텍스트
        """
        return """
본 설계안은 국토교통부 「LH 신축매입임대 운영지침(2024)」에 따른
평형 구성, 공용공간 확보 기준, 주차 기준을 충족합니다.

주요 정책 부합 사항:
1. LH 표준 평형 체계 준수 (청년 14㎡, 신혼 18~24㎡, 고령자 24~32㎡)
2. 공용공간 15% 이상 확보로 커뮤니티 기능 강화
3. 도시형생활주택 특례 적용 (주차 0.2~0.3대/세대)
4. 무장애 설계 기준 적용 (BF 인증 예정)
5. 에너지 효율 1등급 달성 목표

이를 통해 LH 매입 심사에서 높은 평가를 받을 수 있으며,
정책 목표인 '공공주택 공급 확대'와 '주거 복지 향상'에 기여합니다.
        """
    
    def to_dict(self) -> Dict:
        """규칙을 딕셔너리로 변환"""
        return {
            "unit_size_rules": {
                str(k): [
                    {
                        "unit_type": r.unit_type,
                        "size_min": r.size_min,
                        "size_max": r.size_max,
                        "size_avg": r.size_avg,
                        "default_ratio": r.default_ratio
                    }
                    for r in v
                ]
                for k, v in self.unit_size_rules.items()
            },
            "design_rules": {
                k: {
                    "rule_name": v.rule_name,
                    "rule_value": v.rule_value,
                    "description": v.description
                }
                for k, v in self.design_rules.items()
            }
        }


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Initialize policy rules
    rules = LHPolicyRules()
    
    print("="*80)
    print("LH Policy Rules Database")
    print("="*80)
    
    # Test 1: Unit size rules
    print("\n📏 청년형 평형 규칙:")
    youth_rules = rules.get_unit_rules(LHSupplyType.YOUTH)
    for rule in youth_rules:
        print(f"  - {rule.unit_type}: {rule.size_avg}㎡ (비율: {rule.default_ratio*100:.0f}%)")
    
    # Test 2: Design rules
    print("\n📐 설계 규칙:")
    common_ratio = rules.get_common_area_ratio()
    print(f"  - 공용공간 비율: {common_ratio*100:.0f}%")
    
    parking_general = rules.get_parking_ratio("general")
    parking_seoul = rules.get_parking_ratio("seoul")
    print(f"  - 주차 기준 (일반): {parking_general}대/세대")
    print(f"  - 주차 기준 (서울): {parking_seoul}대/세대")
    
    # Test 3: Calculate units
    print("\n🏠 세대수 계산 (연면적 1000㎡, 청년형):")
    distribution = rules.calculate_total_units(1000.0, LHSupplyType.YOUTH)
    for unit_type, info in distribution.items():
        print(f"  - {unit_type}: {info['count']}세대 ({info['size_avg']}㎡)")
    
    # Test 4: Design philosophy
    print("\n💡 설계 철학 (청년형):")
    philosophy = rules.get_design_philosophy(LHSupplyType.YOUTH)
    print(philosophy.strip())
    
    print("\n" + "="*80)
    print("✅ LH Policy Rules Database 정상 작동")
