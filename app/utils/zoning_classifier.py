"""
Zoning Classifier for ZeroSite v22
===================================

Automatic zoning classification and regulation application.

Key Features:
- Automatic BCR/FAR classification by zone type
- Relaxation rule auto-application
- Station-zone, youth housing, happy housing bonuses
- Policy-based calculation

Author: ZeroSite Development Team
Date: 2025-12-10
Version: v22.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ZoningRule:
    """Zoning regulation rule"""
    zone_type: str
    bcr: int  # Building Coverage Ratio (%)
    far: int  # Floor Area Ratio (%)
    description: str


@dataclass
class RelaxationRule:
    """FAR relaxation rule"""
    name: str
    far_bonus: int  # Bonus percentage points
    condition: str
    description: str


class ZoningClassifier:
    """
    Automatic zoning classification and regulation application
    
    Applies Korean urban planning regulations automatically.
    """
    
    # Base zoning rules (법정 기준)
    ZONING_RULES = {
        "제1종전용주거지역": ZoningRule(
            zone_type="제1종전용주거지역",
            bcr=50,
            far=100,
            description="단독주택 중심의 양호한 주거환경 보호"
        ),
        "제2종전용주거지역": ZoningRule(
            zone_type="제2종전용주거지역",
            bcr=50,
            far=150,
            description="공동주택 중심의 양호한 주거환경 보호"
        ),
        "제1종일반주거지역": ZoningRule(
            zone_type="제1종일반주거지역",
            bcr=60,
            far=150,
            description="저층주택 중심의 편리한 주거환경 조성"
        ),
        "제2종일반주거지역": ZoningRule(
            zone_type="제2종일반주거지역",
            bcr=60,
            far=200,
            description="중층주택 중심의 편리한 주거환경 조성"
        ),
        "제3종일반주거지역": ZoningRule(
            zone_type="제3종일반주거지역",
            bcr=50,
            far=250,
            description="중고층주택 중심의 편리한 주거환경 조성"
        ),
        "준주거지역": ZoningRule(
            zone_type="준주거지역",
            bcr=70,
            far=400,
            description="주거기능 위주 + 상업/업무 혼재 허용"
        ),
        "일반상업지역": ZoningRule(
            zone_type="일반상업지역",
            bcr=80,
            far=800,
            description="일반적인 상업/업무 기능 유도"
        ),
        "근린상업지역": ZoningRule(
            zone_type="근린상업지역",
            bcr=70,
            far=600,
            description="근린생활 지원 상업/업무 기능 유도"
        )
    }
    
    # Relaxation rules (완화 규정)
    RELAXATION_RULES = {
        "역세권": RelaxationRule(
            name="역세권 특례",
            far_bonus=20,
            condition="지하철역 500m 이내",
            description="대중교통 활성화를 위한 역세권 용적률 완화"
        ),
        "준주거특례": RelaxationRule(
            name="준주거지역 특례",
            far_bonus=50,
            condition="준주거지역 내 공공주택",
            description="준주거지역 내 공공주택 공급 확대"
        ),
        "청년주택": RelaxationRule(
            name="청년주택 특례",
            far_bonus=20,
            condition="청년주택 공급 사업",
            description="청년주택 공급 활성화를 위한 용적률 완화"
        ),
        "신혼부부": RelaxationRule(
            name="신혼부부 특례",
            far_bonus=15,
            condition="신혼부부 주택 공급",
            description="신혼부부 주거 안정 지원"
        ),
        "행복주택": RelaxationRule(
            name="행복주택 특례",
            far_bonus=30,
            condition="행복주택 사업",
            description="행복주택 공급 확대를 위한 용적률 완화"
        ),
        "공공기여": RelaxationRule(
            name="공공기여 특례",
            far_bonus=10,
            condition="공공시설 기부채납",
            description="공공시설 기부채납 시 용적률 인센티브"
        )
    }
    
    # Default zone type (most common in Seoul)
    DEFAULT_ZONE = "제2종일반주거지역"
    
    @classmethod
    def classify(
        cls,
        address: str,
        context: Dict,
        zone_type: Optional[str] = None
    ) -> Dict:
        """
        Classify zoning and apply regulations automatically
        
        Args:
            address: Target address
            context: Context dict with additional info
            zone_type: Optional explicit zone type
            
        Returns:
            Dictionary with zoning classification results
        """
        # Determine zone type
        if not zone_type:
            zone_type = cls._detect_zone_type(address, context)
        
        # Get base rules
        base_rule = cls.ZONING_RULES.get(zone_type, cls.ZONING_RULES[cls.DEFAULT_ZONE])
        
        # Apply relaxations
        relaxations = cls._apply_relaxations(context)
        
        # Calculate final FAR
        total_far_bonus = sum(r["far_bonus"] for r in relaxations)
        far_final = base_rule.far + total_far_bonus
        
        # Calculate buildable area
        land_area_sqm = context.get("land_area_sqm", 0)
        buildable_area_legal = land_area_sqm * (base_rule.far / 100)
        buildable_area_final = land_area_sqm * (far_final / 100)
        
        return {
            # Zone information
            "zone_type": base_rule.zone_type,
            "zone_description": base_rule.description,
            
            # Legal standards (법정 기준)
            "bcr_legal": base_rule.bcr,
            "far_legal": base_rule.far,
            
            # Relaxations applied
            "bcr_relaxation": 0,  # BCR은 일반적으로 완화 없음
            "far_relaxation": total_far_bonus,
            "relaxations_applied": [r["name"] for r in relaxations],
            "relaxation_details": relaxations,
            
            # Final values (최종 적용)
            "bcr_final": base_rule.bcr,
            "far_final": far_final,
            
            # Calculated areas
            "buildable_area_legal": round(buildable_area_legal, 2),
            "buildable_area_final": round(buildable_area_final, 2),
            "buildable_area_increase": round(buildable_area_final - buildable_area_legal, 2),
            
            # Percentage increase
            "far_increase_pct": round((total_far_bonus / base_rule.far * 100), 1) if base_rule.far > 0 else 0,
            
            # Policy basis
            "policy_basis": cls._generate_policy_basis(relaxations),
            
            # Compliance check
            "compliance": cls._check_compliance(far_final, base_rule.zone_type)
        }
    
    @classmethod
    def _detect_zone_type(cls, address: str, context: Dict) -> str:
        """
        Detect zone type from address and context
        
        Auto-detection logic:
        1. Check explicit zone_type in context
        2. Detect from address keywords
        3. Default to 제2종일반주거지역
        """
        # Check context first
        if "zoning_type" in context:
            return context["zoning_type"]
        
        # Detect from address
        if any(keyword in address for keyword in ["준주거", "상업", "업무"]):
            return "준주거지역"
        
        if any(keyword in address for keyword in ["강남", "서초", "송파"]):
            # Premium areas often 제2종 or 제3종
            return "제2종일반주거지역"
        
        # Default
        return cls.DEFAULT_ZONE
    
    @classmethod
    def _apply_relaxations(cls, context: Dict) -> List[Dict]:
        """
        Apply relaxation rules based on context
        
        Returns:
            List of applied relaxation dicts
        """
        relaxations = []
        
        # Check 역세권 (station zone)
        near_subway = context.get("near_subway", False)
        subway_distance = context.get("subway_distance_m", 999)
        
        if near_subway and subway_distance <= 500:
            rule = cls.RELAXATION_RULES["역세권"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": f"지하철역까지 {subway_distance}m"
            })
        
        # Check supply type
        supply_type = context.get("supply_type", "")
        
        if supply_type == "청년":
            rule = cls.RELAXATION_RULES["청년주택"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": "청년주택 공급 사업"
            })
        
        elif supply_type == "신혼부부":
            rule = cls.RELAXATION_RULES["신혼부부"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": "신혼부부 주택 공급 사업"
            })
        
        elif supply_type == "행복주택":
            rule = cls.RELAXATION_RULES["행복주택"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": "행복주택 공급 사업"
            })
        
        # Check 준주거지역 특례
        if context.get("zoning_type") == "준주거지역":
            rule = cls.RELAXATION_RULES["준주거특례"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": "준주거지역 내 공공주택"
            })
        
        # Check 공공기여 (if school zone or public facility)
        if context.get("school_zone", False):
            rule = cls.RELAXATION_RULES["공공기여"]
            relaxations.append({
                "name": rule.name,
                "far_bonus": rule.far_bonus,
                "condition": rule.condition,
                "description": rule.description,
                "evidence": "학교용지 인접 + 공공기여"
            })
        
        return relaxations
    
    @classmethod
    def _generate_policy_basis(cls, relaxations: List[Dict]) -> List[str]:
        """Generate policy basis citations for relaxations"""
        policy_basis = []
        
        for r in relaxations:
            if "역세권" in r["name"]:
                policy_basis.append("국토교통부, 『역세권 공공주택 용적률 완화 기준』, 2023.8")
            elif "청년" in r["name"]:
                policy_basis.append("국토교통부, 『청년주택 공급 활성화 방안』, 2024.3")
            elif "신혼부부" in r["name"]:
                policy_basis.append("국토교통부, 『신혼부부 주거 지원 강화 대책』, 2024.1")
            elif "행복주택" in r["name"]:
                policy_basis.append("국토교통부, 『행복주택 건설기준 및 운영기준』, 2023.12")
            elif "준주거" in r["name"]:
                policy_basis.append("서울시, 『준주거지역 공공주택 용적률 특례 기준』, 2024.2")
            elif "공공기여" in r["name"]:
                policy_basis.append("서울시, 『공공기여 용적률 인센티브 운영 기준』, 2023.6")
        
        return policy_basis
    
    @classmethod
    def _check_compliance(cls, far_final: int, zone_type: str) -> Dict:
        """
        Check compliance with max limits
        
        Returns:
            Compliance check result
        """
        # Maximum FAR limits by zone (서울시 기준)
        max_limits = {
            "제1종전용주거지역": 150,
            "제2종전용주거지역": 200,
            "제1종일반주거지역": 250,
            "제2종일반주거지역": 300,
            "제3종일반주거지역": 400,
            "준주거지역": 500,
            "일반상업지역": 1000,
            "근린상업지역": 800
        }
        
        max_far = max_limits.get(zone_type, 300)
        is_compliant = far_final <= max_far
        
        return {
            "is_compliant": is_compliant,
            "max_far_limit": max_far,
            "current_far": far_final,
            "headroom": max_far - far_final if is_compliant else 0,
            "status": "적정" if is_compliant else "초과"
        }


# Convenience functions
def classify_zoning(address: str, context: Dict, zone_type: Optional[str] = None) -> Dict:
    """Classify zoning and apply regulations"""
    return ZoningClassifier.classify(address, context, zone_type)


def get_base_far(zone_type: str) -> int:
    """Get base FAR for zone type"""
    rule = ZoningClassifier.ZONING_RULES.get(zone_type)
    return rule.far if rule else 200
