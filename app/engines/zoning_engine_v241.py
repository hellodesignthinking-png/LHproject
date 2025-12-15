"""
ZeroSite v24.1 - Zoning Engine (용도지역 엔진)
Korean Land Use Zoning Analysis System

Provides comprehensive zoning analysis including:
- 23 Korean zone types classification
- FAR/BCR limits by zone
- Allowed/prohibited uses
- Development restrictions
- Policy compliance checks

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    from .base_engine import BaseEngine
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class ZoneCategory(Enum):
    """Major zoning categories"""
    RESIDENTIAL = "주거지역"
    COMMERCIAL = "상업지역"
    INDUSTRIAL = "공업지역"
    GREEN = "녹지지역"


@dataclass
class ZoneRegulation:
    """Zone-specific regulations"""
    zone_name: str
    category: ZoneCategory
    legal_far_min: float
    legal_far_max: float
    legal_bcr_max: float
    height_limit: Optional[float]
    floor_limit: Optional[int]
    allowed_uses: List[str]
    prohibited_uses: List[str]
    special_restrictions: List[str]


@dataclass
class ZoningAnalysisResult:
    """Complete zoning analysis result"""
    zone_name: str
    zone_code: str
    category: str
    legal_far_range: Tuple[float, float]
    legal_bcr: float
    height_limit: Optional[float]
    floor_limit: Optional[int]
    
    # Use analysis
    allowed_uses: List[str]
    prohibited_uses: List[str]
    lh_housing_allowed: bool
    
    # Restrictions
    restrictions: List[str]
    relaxation_eligible: bool
    relaxation_types: List[str]
    
    # Compliance
    compliance_notes: List[str]
    development_difficulty: str  # EASY, MODERATE, DIFFICULT


class ZoningEngineV241(BaseEngine):
    """
    Comprehensive Korean Zoning Analysis Engine
    
    Features:
    - 23 Korean zone types database
    - FAR/BCR limits by zone
    - Use permissions analysis
    - LH housing compatibility check
    - Relaxation eligibility assessment
    - Development difficulty rating
    
    Input:
        zone_type: str (Korean zone name)
        address: Optional[str] (for API lookup - future)
        proposed_use: Optional[str] (for compatibility check)
    
    Output:
        ZoningAnalysisResult with complete regulations
    """
    
    # Korean Zoning Database (23 types)
    ZONE_DATABASE = {
        # Residential Zones (주거지역)
        "제1종전용주거지역": ZoneRegulation(
            zone_name="제1종전용주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=50.0,
            legal_far_max=100.0,
            legal_bcr_max=50.0,
            height_limit=None,
            floor_limit=4,
            allowed_uses=["단독주택", "공동주택", "제1종근린생활시설"],
            prohibited_uses=["상업시설", "공업시설", "위락시설"],
            special_restrictions=["저층 주거 환경 보호", "조용한 주거 환경 유지"]
        ),
        "제2종전용주거지역": ZoneRegulation(
            zone_name="제2종전용주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=100.0,
            legal_far_max=150.0,
            legal_bcr_max=50.0,
            height_limit=None,
            floor_limit=7,
            allowed_uses=["단독주택", "공동주택", "제1종근린생활시설", "제2종근린생활시설"],
            prohibited_uses=["상업시설", "공업시설", "위락시설"],
            special_restrictions=["중층 주거 환경 보호"]
        ),
        "제1종일반주거지역": ZoneRegulation(
            zone_name="제1종일반주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=100.0,
            legal_far_max=200.0,
            legal_bcr_max=60.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["단독주택", "공동주택", "제1종근린생활시설", "제2종근린생활시설", "문화시설"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["저층주택 중심"]
        ),
        "제2종일반주거지역": ZoneRegulation(
            zone_name="제2종일반주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=150.0,
            legal_far_max=250.0,
            legal_bcr_max=60.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["단독주택", "공동주택", "제1,2종근린생활시설", "문화시설", "종교시설"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["중층주택 중심", "편의시설 허용"]
        ),
        "제3종일반주거지역": ZoneRegulation(
            zone_name="제3종일반주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=200.0,
            legal_far_max=300.0,
            legal_bcr_max=50.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["공동주택", "제1,2종근린생활시설", "문화시설", "종교시설", "판매시설"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["고층주택 중심", "복합용도 가능"]
        ),
        "준주거지역": ZoneRegulation(
            zone_name="준주거지역",
            category=ZoneCategory.RESIDENTIAL,
            legal_far_min=200.0,
            legal_far_max=500.0,
            legal_bcr_max=70.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["공동주택", "근린생활시설", "문화시설", "판매시설", "업무시설"],
            prohibited_uses=["중공업시설", "위험물저장시설"],
            special_restrictions=["주거·상업 복합 가능", "고밀도 개발 허용"]
        ),
        
        # Commercial Zones (상업지역)
        "중심상업지역": ZoneRegulation(
            zone_name="중심상업지역",
            category=ZoneCategory.COMMERCIAL,
            legal_far_min=400.0,
            legal_far_max=1500.0,
            legal_bcr_max=90.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["판매시설", "업무시설", "숙박시설", "위락시설", "공동주택"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["도심 핵심기능", "초고층 가능"]
        ),
        "일반상업지역": ZoneRegulation(
            zone_name="일반상업지역",
            category=ZoneCategory.COMMERCIAL,
            legal_far_min=300.0,
            legal_far_max=1300.0,
            legal_bcr_max=80.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["판매시설", "업무시설", "숙박시설", "공동주택", "문화시설"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["일반 상업기능"]
        ),
        "근린상업지역": ZoneRegulation(
            zone_name="근린상업지역",
            category=ZoneCategory.COMMERCIAL,
            legal_far_min=200.0,
            legal_far_max=900.0,
            legal_bcr_max=70.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["근린생활시설", "판매시설", "업무시설", "공동주택"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["근린 편의시설 중심"]
        ),
        "유통상업지역": ZoneRegulation(
            zone_name="유통상업지역",
            category=ZoneCategory.COMMERCIAL,
            legal_far_min=200.0,
            legal_far_max=1100.0,
            legal_bcr_max=80.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["도매시장", "창고시설", "운수시설", "공동주택"],
            prohibited_uses=["위험물저장시설"],
            special_restrictions=["유통·물류 중심"]
        ),
        
        # Industrial Zones (공업지역)
        "전용공업지역": ZoneRegulation(
            zone_name="전용공업지역",
            category=ZoneCategory.INDUSTRIAL,
            legal_far_min=150.0,
            legal_far_max=300.0,
            legal_bcr_max=70.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["공장", "창고시설", "위험물저장시설"],
            prohibited_uses=["주거시설", "교육시설", "의료시설"],
            special_restrictions=["중화학공업 중심", "주거 불가"]
        ),
        "일반공업지역": ZoneRegulation(
            zone_name="일반공업지역",
            category=ZoneCategory.INDUSTRIAL,
            legal_far_min=200.0,
            legal_far_max=350.0,
            legal_bcr_max=70.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["공장", "창고시설", "근린생활시설"],
            prohibited_uses=["주거시설", "교육시설"],
            special_restrictions=["경공업 가능"]
        ),
        "준공업지역": ZoneRegulation(
            zone_name="준공업지역",
            category=ZoneCategory.INDUSTRIAL,
            legal_far_min=200.0,
            legal_far_max=400.0,
            legal_bcr_max=70.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["공장", "창고시설", "주거시설", "근린생활시설", "업무시설"],
            prohibited_uses=["위험물저장시설"],
            special_restrictions=["주거·공업 혼재 가능", "LH 신축매입임대 가능"]
        ),
        
        # Green Zones (녹지지역)
        "보전녹지지역": ZoneRegulation(
            zone_name="보전녹지지역",
            category=ZoneCategory.GREEN,
            legal_far_min=50.0,
            legal_far_max=80.0,
            legal_bcr_max=20.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["단독주택", "근린생활시설", "농림어업시설"],
            prohibited_uses=["공동주택", "상업시설", "공업시설"],
            special_restrictions=["자연환경 보전", "개발 엄격 제한"]
        ),
        "생산녹지지역": ZoneRegulation(
            zone_name="생산녹지지역",
            category=ZoneCategory.GREEN,
            legal_far_min=50.0,
            legal_far_max=100.0,
            legal_bcr_max=20.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["단독주택", "근린생활시설", "농림어업시설"],
            prohibited_uses=["공동주택", "상업시설", "공업시설"],
            special_restrictions=["농업생산 보호"]
        ),
        "자연녹지지역": ZoneRegulation(
            zone_name="자연녹지지역",
            category=ZoneCategory.GREEN,
            legal_far_min=50.0,
            legal_far_max=100.0,
            legal_bcr_max=20.0,
            height_limit=None,
            floor_limit=None,
            allowed_uses=["단독주택", "공동주택", "근린생활시설", "농림어업시설"],
            prohibited_uses=["공업시설", "위험물저장시설"],
            special_restrictions=["제한적 개발 허용"]
        ),
    }
    
    # LH Housing Compatible Zones
    LH_COMPATIBLE_ZONES = [
        "제1종일반주거지역",
        "제2종일반주거지역",
        "제3종일반주거지역",
        "준주거지역",
        "준공업지역",
        "자연녹지지역"
    ]
    
    def __init__(self):
        super().__init__(engine_name="ZoningEngine", version="24.1.0")
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Args:
            input_data: {
                'zone_type': str (Korean zone name),
                'address': Optional[str] (for API lookup - future),
                'proposed_use': Optional[str] (e.g., 'LH신축매입임대')
            }
        
        Returns:
            Complete zoning analysis
        """
        self.validate_input(input_data, ['zone_type'])
        
        zone_type = input_data['zone_type']
        proposed_use = input_data.get('proposed_use', 'LH신축매입임대')
        
        # Get zone regulations
        zone_reg = self.ZONE_DATABASE.get(zone_type)
        
        if not zone_reg:
            # Try to find similar zone
            zone_reg = self._find_similar_zone(zone_type)
            if not zone_reg:
                raise ValueError(f"Unknown zone type: {zone_type}")
        
        # Analyze zone
        result = self._analyze_zone(zone_reg, proposed_use)
        
        self.logger.info(f"Zoning analysis complete: {zone_type} - LH Housing: {result.lh_housing_allowed}")
        
        return self._result_to_dict(result)
    
    def _find_similar_zone(self, zone_type: str) -> Optional[ZoneRegulation]:
        """Find similar zone if exact match not found"""
        # Simple fuzzy matching
        for key, reg in self.ZONE_DATABASE.items():
            if zone_type in key or key in zone_type:
                logger.warning(f"Using similar zone: {key} for {zone_type}")
                return reg
        return None
    
    def _analyze_zone(self, zone_reg: ZoneRegulation, proposed_use: str) -> ZoningAnalysisResult:
        """Perform comprehensive zoning analysis"""
        
        # Check LH housing compatibility
        lh_housing_allowed = zone_reg.zone_name in self.LH_COMPATIBLE_ZONES
        
        # Determine relaxation eligibility
        relaxation_eligible = zone_reg.category in [ZoneCategory.RESIDENTIAL, ZoneCategory.INDUSTRIAL]
        relaxation_types = self._get_relaxation_types(zone_reg)
        
        # Assess development difficulty
        difficulty = self._assess_difficulty(zone_reg, lh_housing_allowed)
        
        # Generate compliance notes
        compliance_notes = self._generate_compliance_notes(zone_reg, proposed_use, lh_housing_allowed)
        
        # Generate zone code (simplified)
        zone_code = self._generate_zone_code(zone_reg)
        
        return ZoningAnalysisResult(
            zone_name=zone_reg.zone_name,
            zone_code=zone_code,
            category=zone_reg.category.value,
            legal_far_range=(zone_reg.legal_far_min, zone_reg.legal_far_max),
            legal_bcr=zone_reg.legal_bcr_max,
            height_limit=zone_reg.height_limit,
            floor_limit=zone_reg.floor_limit,
            allowed_uses=zone_reg.allowed_uses,
            prohibited_uses=zone_reg.prohibited_uses,
            lh_housing_allowed=lh_housing_allowed,
            restrictions=zone_reg.special_restrictions,
            relaxation_eligible=relaxation_eligible,
            relaxation_types=relaxation_types,
            compliance_notes=compliance_notes,
            development_difficulty=difficulty
        )
    
    def _get_relaxation_types(self, zone_reg: ZoneRegulation) -> List[str]:
        """Determine available relaxation bonuses"""
        relaxations = []
        
        if zone_reg.category == ZoneCategory.RESIDENTIAL:
            relaxations.extend([
                "녹색건축물 인증 (+15%)",
                "공공시설 제공 (+10%)",
                "지하주차장 (+5%)",
                "소형주택 (+5%)",
                "에너지효율 (+10%)"
            ])
        
        if zone_reg.category == ZoneCategory.INDUSTRIAL:
            if "준공업" in zone_reg.zone_name:
                relaxations.extend([
                    "주거복합 개발 (+10%)",
                    "공공기여 (+15%)"
                ])
        
        return relaxations
    
    def _assess_difficulty(self, zone_reg: ZoneRegulation, lh_allowed: bool) -> str:
        """Assess development difficulty level"""
        
        if not lh_allowed:
            return "DIFFICULT"
        
        if zone_reg.category == ZoneCategory.GREEN:
            return "DIFFICULT"
        
        if zone_reg.legal_far_max >= 200 and zone_reg.legal_bcr_max >= 60:
            return "EASY"
        elif zone_reg.legal_far_max >= 150:
            return "MODERATE"
        else:
            return "DIFFICULT"
    
    def _generate_compliance_notes(self, zone_reg: ZoneRegulation, 
                                   proposed_use: str, lh_allowed: bool) -> List[str]:
        """Generate compliance and recommendation notes"""
        notes = []
        
        if lh_allowed:
            notes.append("✅ LH 신축매입임대 개발 가능")
        else:
            notes.append("❌ LH 신축매입임대 개발 불가 - 용도지역 제한")
        
        if zone_reg.legal_far_max >= 200:
            notes.append(f"✅ 고밀도 개발 가능 (최대 용적률 {zone_reg.legal_far_max}%)")
        else:
            notes.append(f"⚠️ 저밀도 지역 (최대 용적률 {zone_reg.legal_far_max}%)")
        
        if zone_reg.floor_limit:
            notes.append(f"⚠️ 층수 제한: {zone_reg.floor_limit}층 이하")
        
        if "공동주택" in zone_reg.allowed_uses:
            notes.append("✅ 공동주택 건설 허용")
        
        return notes
    
    def _generate_zone_code(self, zone_reg: ZoneRegulation) -> str:
        """Generate zone code (simplified for demo)"""
        category_codes = {
            ZoneCategory.RESIDENTIAL: "R",
            ZoneCategory.COMMERCIAL: "C",
            ZoneCategory.INDUSTRIAL: "I",
            ZoneCategory.GREEN: "G"
        }
        
        category_code = category_codes.get(zone_reg.category, "X")
        far_code = f"F{int(zone_reg.legal_far_max)}"
        
        return f"{category_code}-{far_code}"
    
    def _result_to_dict(self, result: ZoningAnalysisResult) -> Dict:
        """Convert result to dictionary"""
        return {
            'zone_name': result.zone_name,
            'zone_code': result.zone_code,
            'category': result.category,
            'regulations': {
                'legal_far_min': result.legal_far_range[0],
                'legal_far_max': result.legal_far_range[1],
                'legal_bcr': result.legal_bcr,
                'height_limit': result.height_limit,
                'floor_limit': result.floor_limit
            },
            'uses': {
                'allowed': result.allowed_uses,
                'prohibited': result.prohibited_uses,
                'lh_housing_allowed': result.lh_housing_allowed
            },
            'development': {
                'restrictions': result.restrictions,
                'relaxation_eligible': result.relaxation_eligible,
                'relaxation_types': result.relaxation_types,
                'difficulty': result.development_difficulty
            },
            'compliance': {
                'notes': result.compliance_notes
            }
        }
    
    def get_zone_list(self) -> List[str]:
        """Get list of all supported zones"""
        return list(self.ZONE_DATABASE.keys())
    
    def check_lh_compatibility(self, zone_type: str) -> bool:
        """Quick check if zone is LH-compatible"""
        return zone_type in self.LH_COMPATIBLE_ZONES


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ZONING ENGINE v24.1 - CLI TEST")
    print("=" * 80)
    
    engine = ZoningEngineV241()
    
    # Test case 1: 제3종일반주거지역 (High-rise residential)
    print("\n[TEST 1] 제3종일반주거지역")
    print("-" * 80)
    test_input_1 = {
        'zone_type': '제3종일반주거지역',
        'proposed_use': 'LH신축매입임대'
    }
    result_1 = engine.process(test_input_1)
    
    print(f"Zone: {result_1['zone_name']} ({result_1['zone_code']})")
    print(f"Category: {result_1['category']}")
    print(f"FAR Range: {result_1['regulations']['legal_far_min']}% - {result_1['regulations']['legal_far_max']}%")
    print(f"BCR Limit: {result_1['regulations']['legal_bcr']}%")
    print(f"LH Housing Allowed: {result_1['uses']['lh_housing_allowed']}")
    print(f"Development Difficulty: {result_1['development']['difficulty']}")
    print(f"\nCompliance Notes:")
    for note in result_1['compliance']['notes']:
        print(f"  {note}")
    
    # Test case 2: 준공업지역 (Semi-industrial)
    print("\n[TEST 2] 준공업지역")
    print("-" * 80)
    test_input_2 = {
        'zone_type': '준공업지역',
        'proposed_use': 'LH신축매입임대'
    }
    result_2 = engine.process(test_input_2)
    
    print(f"Zone: {result_2['zone_name']} ({result_2['zone_code']})")
    print(f"LH Housing Allowed: {result_2['uses']['lh_housing_allowed']}")
    print(f"Relaxation Types: {len(result_2['development']['relaxation_types'])}")
    for relax in result_2['development']['relaxation_types']:
        print(f"  - {relax}")
    
    print("\n" + "=" * 80)
    print(f"Total zones in database: {len(engine.get_zone_list())}")
    print("=" * 80)
