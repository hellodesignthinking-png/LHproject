"""
ZeroSite v24.1 - Development & Regulation Analysis Engine
Analyzes development potential and regulatory constraints

Features:
- Zone type analysis
- Development opportunities
- Regulatory constraints
- Generates narrative-style analysis

Author: ZeroSite Development Team
Version: 24.1.0 (Genspark v4.0)
Created: 2025-12-13
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DevelopmentScore:
    """Development analysis result"""
    regulation_score: int
    opportunity_factors: List[str]
    constraint_factors: List[str]
    narrative: List[str]
    details: Dict[str, Any]


class DevelopmentRegulationEngine:
    """
    Development & Regulation Analysis Engine
    
    Analyzes development potential and regulatory environment
    """
    
    def __init__(self):
        """Initialize engine"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Zone type characteristics
        self.zone_characteristics = {
            "제1종전용주거지역": {
                "description": "저층 단독주택 중심 지역",
                "typical_far": 100,
                "typical_bcr": 50,
                "typical_height": "4층 이하",
                "development_type": "단독주택, 다세대주택",
                "score_base": 50
            },
            "제2종일반주거지역": {
                "description": "중층 공동주택 중심 지역",
                "typical_far": 150,
                "typical_bcr": 60,
                "typical_height": "7층 이하",
                "development_type": "아파트, 연립주택, 근린생활시설",
                "score_base": 65
            },
            "제3종일반주거지역": {
                "description": "중고층 공동주택 중심 지역",
                "typical_far": 200,
                "typical_bcr": 50,
                "typical_height": "7~15층",
                "development_type": "아파트, 오피스텔, 근린생활시설",
                "score_base": 75
            },
            "준주거지역": {
                "description": "주거·상업 복합 지역",
                "typical_far": 400,
                "typical_bcr": 70,
                "typical_height": "15층 이상",
                "development_type": "주상복합, 업무시설, 판매시설",
                "score_base": 85
            },
            "일반상업지역": {
                "description": "상업·업무 중심 지역",
                "typical_far": 800,
                "typical_bcr": 70,
                "typical_height": "제한 없음",
                "development_type": "업무시설, 판매시설, 숙박시설",
                "score_base": 90
            },
            "중심상업지역": {
                "description": "도심 핵심 상업 지역",
                "typical_far": 1000,
                "typical_bcr": 60,
                "typical_height": "제한 없음",
                "development_type": "초고층 복합개발",
                "score_base": 95
            },
            "default": {
                "description": "일반 지역",
                "typical_far": 150,
                "typical_bcr": 60,
                "typical_height": "중층",
                "development_type": "일반 개발",
                "score_base": 60
            }
        }
    
    def analyze(
        self,
        zone_type: str,
        bcr_legal: float,
        far_legal: float,
        address: str,
        overlays: Optional[List[str]] = None
    ) -> DevelopmentScore:
        """
        Analyze development potential and regulations
        
        Args:
            zone_type: Zoning type
            bcr_legal: Legal building coverage ratio (%)
            far_legal: Legal floor area ratio (%)
            address: Property address
            overlays: Overlay zones (district plan, height district, etc.)
            
        Returns:
            DevelopmentScore object with analysis
        """
        try:
            self.logger.info(f"🏗️ Analyzing development for: {zone_type}")
            
            # Get zone characteristics
            zone_char = self.zone_characteristics.get(
                zone_type, 
                self.zone_characteristics["default"]
            )
            
            # Base score from zone type
            score = zone_char["score_base"]
            
            # Adjust based on FAR
            far_ratio = far_legal / zone_char["typical_far"]
            if far_ratio > 1.2:
                score += 10
            elif far_ratio < 0.8:
                score -= 10
            
            # Check for overlays
            overlays = overlays or []
            has_district_plan = any("지구단위" in o for o in overlays)
            has_height_district = any("고도지구" in o for o in overlays)
            
            # Identify opportunities
            opportunities = self._identify_opportunities(
                zone_type, zone_char, far_legal, address
            )
            
            # Identify constraints
            constraints = self._identify_constraints(
                zone_type, overlays, has_district_plan, has_height_district
            )
            
            # Adjust score based on constraints
            score -= len(constraints) * 5
            score = max(0, min(100, score))
            
            # Generate narratives
            narratives = self._generate_narratives(
                zone_type, zone_char, opportunities, constraints, score
            )
            
            result = DevelopmentScore(
                regulation_score=score,
                opportunity_factors=opportunities,
                constraint_factors=constraints,
                narrative=narratives,
                details={
                    "zone_type": zone_type,
                    "zone_description": zone_char["description"],
                    "development_type": zone_char["development_type"],
                    "typical_height": zone_char["typical_height"],
                    "overlays": overlays,
                    "has_district_plan": has_district_plan,
                    "has_height_district": has_height_district
                }
            )
            
            self.logger.info(f"✅ Development analysis complete: Score = {score}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Development analysis failed: {e}")
            # Return fallback
            return DevelopmentScore(
                regulation_score=70,
                opportunity_factors=["일반적인 개발 가능"],
                constraint_factors=["상세 검토 필요"],
                narrative=["대상지는 일반적인 개발 여건을 갖추고 있습니다."],
                details={}
            )
    
    def _identify_opportunities(
        self, 
        zone_type: str, 
        zone_char: Dict[str, Any], 
        far_legal: float,
        address: str
    ) -> List[str]:
        """Identify development opportunities"""
        opportunities = []
        
        # Zone-specific opportunities
        if "주거" in zone_type:
            if "제3종" in zone_type:
                opportunities.append("제3종일반주거지역으로 중고층 공동주택 개발에 적합")
            elif "제2종" in zone_type:
                opportunities.append("제2종일반주거지역으로 중층 주거 개발 가능")
            opportunities.append("주거 수요가 안정적인 주거지역")
        
        if "준주거" in zone_type:
            opportunities.append("주거·상업 복합개발 가능으로 수익성 제고 가능")
            opportunities.append("업무시설 및 판매시설 허용으로 다양한 개발 유형 선택 가능")
        
        if "상업" in zone_type:
            opportunities.append("상업지역으로 높은 용적률 활용 가능")
            opportunities.append("업무·상업·숙박시설 등 다양한 용도 개발 가능")
        
        # Location-based opportunities
        if "강남" in address or "서초" in address:
            opportunities.append("강남권 입지로 중장기적인 토지가치 상승 기대")
        if "역삼" in address or "선릉" in address or "삼성" in address:
            opportunities.append("역세권 인접으로 개발 시 수요 확보 유리")
        
        # FAR-based opportunities
        if far_legal >= 200:
            opportunities.append(f"법정 용적률 {far_legal}%로 충분한 개발 용적 확보 가능")
        
        return opportunities
    
    def _identify_constraints(
        self, 
        zone_type: str, 
        overlays: List[str],
        has_district_plan: bool,
        has_height_district: bool
    ) -> List[str]:
        """Identify regulatory constraints"""
        constraints = []
        
        # Overlay-based constraints
        if has_district_plan:
            constraints.append("지구단위계획구역으로 세부계획에 따라 건폐율·용적률이 조정될 수 있음")
            constraints.append("건축물 용도·형태·높이 등에 대한 추가 제한 가능")
        
        if has_height_district:
            constraints.append("고도지구 지정으로 건축물 높이 제한 적용")
        
        # Check for green belt
        if any("개발제한" in o for o in overlays):
            constraints.append("개발제한구역(그린벨트) 지정으로 개발 행위 제한")
        
        # Check for cultural heritage
        if any("문화재" in o or "보호구역" in o for o in overlays):
            constraints.append("문화재보호구역으로 건축 행위 제한 및 심의 필요")
        
        # Zone-specific constraints
        if "주거" in zone_type:
            constraints.append("주거지역 특성상 일부 상업시설 용도 제한 가능")
        
        return constraints
    
    def _generate_narratives(
        self, 
        zone_type: str, 
        zone_char: Dict[str, Any],
        opportunities: List[str],
        constraints: List[str],
        score: int
    ) -> List[str]:
        """Generate narrative descriptions"""
        narratives = []
        
        # Zone description
        narratives.append(
            f"대상지는 {zone_type}으로 {zone_char['description']}에 해당하며, "
            f"{zone_char['development_type']} 개발에 적합합니다."
        )
        
        # Height/FAR description
        narratives.append(
            f"법정 건폐율·용적률 범위 내에서 {zone_char['typical_height']} 규모의 "
            "건축이 가능합니다."
        )
        
        # Opportunities summary
        if len(opportunities) >= 3:
            narratives.append(
                "입지 여건 및 개발 잠재력이 우수하여 다양한 개발 방안 검토가 가능합니다."
            )
        elif len(opportunities) >= 1:
            narratives.append(
                "적정 수준의 개발 여건을 갖추고 있습니다."
            )
        
        # Constraints summary
        if len(constraints) >= 2:
            narratives.append(
                "다만 지구단위계획 등 추가적인 규제 사항이 있어 상세 검토가 필요합니다."
            )
        elif len(constraints) == 1:
            narratives.append(
                "일부 규제 사항이 있으나 개발에 큰 제약은 없을 것으로 판단됩니다."
            )
        
        # Overall assessment
        if score >= 80:
            narratives.append(
                "종합적으로 개발 여건 및 규제 환경이 양호하여 개발 사업 추진이 적합한 것으로 평가됩니다."
            )
        elif score >= 60:
            narratives.append(
                "종합적으로 일반적인 수준의 개발 여건을 갖추고 있습니다."
            )
        else:
            narratives.append(
                "종합적으로 규제 사항이 다소 많아 신중한 검토가 필요합니다."
            )
        
        return narratives


# Singleton instance
_development_engine = None

def get_development_engine() -> DevelopmentRegulationEngine:
    """Get singleton instance of DevelopmentRegulationEngine"""
    global _development_engine
    if _development_engine is None:
        _development_engine = DevelopmentRegulationEngine()
    return _development_engine
