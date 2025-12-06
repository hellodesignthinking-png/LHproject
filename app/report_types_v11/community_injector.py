"""
ZeroSite Phase 10: Community Injector

Automatically selects and injects community facility modules
based on Phase 6.7 recommended_type output.

Architecture:
    Phase 6.7 (recommended_type) → Community Selector → Community Module → Decision Object
    
Key Features:
    - Automatic selection based on housing type
    - Multiple community modules per type
    - Cost estimation included
    - Narrative generation
    - Benefits listing
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from pydantic import BaseModel

from app.report_types_v11.base_report_engine import CommunityModule


class CommunityDatabase:
    """
    Community facility module database
    
    In production, this would be a real database.
    For Phase 10, we use a JSON-based mock database.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize community database"""
        self.data_dir = data_dir or Path("./app/data/community_modules")
        self.modules: Dict[str, List[CommunityModule]] = {}
        self._load_modules()
    
    def _load_modules(self):
        """Load community modules from JSON files"""
        # If data directory doesn't exist, create it with default modules
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_modules()
        
        # Load all JSON files
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    module = CommunityModule(**data)
                    
                    if module.target_type not in self.modules:
                        self.modules[module.target_type] = []
                    
                    self.modules[module.target_type].append(module)
            except Exception as e:
                print(f"Error loading community module {json_file}: {e}")
    
    def _create_default_modules(self):
        """Create default community modules"""
        default_modules = [
            # Youth modules
            {
                "module_id": "YOUTH_001",
                "module_name": "Youth Innovation Hub",
                "target_type": "Youth",
                "facilities": [
                    "공유 오피스 (Shared Office)",
                    "스터디 라운지 (Study Lounge)",
                    "24시간 헬스장 (24hr Gym)",
                    "게임 & 미디어룸 (Game & Media Room)",
                    "루프탑 카페 (Rooftop Cafe)"
                ],
                "estimated_cost": 150000000,
                "space_requirement_m2": 200,
                "narrative": "청년층을 위한 혁신적인 커뮤니티 공간으로, 창업과 자기개발을 지원하는 시설들로 구성됩니다. 공유 오피스와 스터디 라운지는 재택근무와 학습을 위한 최적의 환경을 제공하며, 24시간 운영되는 헬스장은 바쁜 일정 속에서도 건강을 관리할 수 있도록 돕습니다.",
                "benefits": [
                    "창업 지원 및 네트워킹 공간",
                    "자기개발 인프라 제공",
                    "건강한 라이프스타일 지원",
                    "커뮤니티 형성 촉진"
                ]
            },
            {
                "module_id": "YOUTH_002",
                "module_name": "Urban Lifestyle Center",
                "target_type": "Youth",
                "facilities": [
                    "코워킹 스페이스 (Co-working Space)",
                    "프리미엄 피트니스 (Premium Fitness)",
                    "무인 카페테리아 (Unmanned Cafeteria)",
                    "VR 체험존 (VR Experience Zone)",
                    "패키지룸 (Package Room)"
                ],
                "estimated_cost": 180000000,
                "space_requirement_m2": 250,
                "narrative": "도심 라이프스타일을 선도하는 프리미엄 커뮤니티 공간입니다. 최신 트렌드를 반영한 시설들로 구성되어 있으며, 특히 1인 가구 증가 추세에 맞춘 무인 서비스와 스마트 시설이 특징입니다.",
                "benefits": [
                    "프리미엄 라이프스타일 제공",
                    "스마트 생활 인프라",
                    "1인 가구 최적화 서비스",
                    "안전한 택배 보관 시스템"
                ]
            },
            
            # Newlyweds Type I modules
            {
                "module_id": "NEWLYWED1_001",
                "module_name": "Family Start Package",
                "target_type": "Newlyweds_TypeI",
                "facilities": [
                    "키즈 플레이룸 (Kids Playroom)",
                    "육아 상담실 (Parenting Counseling)",
                    "공동 육아방 (Community Childcare)",
                    "맘카페 (Mom's Cafe)",
                    "유아용품 대여소 (Baby Gear Library)"
                ],
                "estimated_cost": 120000000,
                "space_requirement_m2": 180,
                "narrative": "신혼부부와 영유아 가정을 위한 육아 지원 커뮤니티입니다. 전문 보육교사가 상주하는 공동 육아방과 육아 상담 서비스를 제공하며, 고가의 유아용품을 대여할 수 있는 서비스가 경제적 부담을 덜어줍니다.",
                "benefits": [
                    "전문적인 육아 지원",
                    "경제적 부담 경감",
                    "육아 정보 공유 네트워크",
                    "안전한 놀이 공간 제공"
                ]
            },
            
            # Newlyweds Type II modules
            {
                "module_id": "NEWLYWED2_001",
                "module_name": "Growing Family Center",
                "target_type": "Newlyweds_TypeII",
                "facilities": [
                    "어린이 도서관 (Children's Library)",
                    "실내 놀이터 (Indoor Playground)",
                    "가족 요리교실 (Family Cooking Class)",
                    "미술 공작실 (Arts & Crafts Studio)",
                    "가족 영화관 (Family Theater)"
                ],
                "estimated_cost": 200000000,
                "space_requirement_m2": 300,
                "narrative": "성장하는 가족을 위한 다목적 커뮤니티 공간입니다. 아이들의 교육과 창의력 발달을 지원하는 시설들이 갖춰져 있으며, 가족 단위 활동을 통해 이웃 간 유대감을 형성할 수 있습니다.",
                "benefits": [
                    "아동 교육 프로그램 제공",
                    "창의력 발달 지원",
                    "가족 단위 커뮤니티 형성",
                    "안전한 실내 활동 공간"
                ]
            },
            
            # Multi-Child modules
            {
                "module_id": "MULTICHILD_001",
                "module_name": "Big Family Support Hub",
                "target_type": "MultiChild",
                "facilities": [
                    "대형 키즈카페 (Large Kids Cafe)",
                    "학습 지원센터 (Learning Support Center)",
                    "체육 활동실 (Sports Activity Room)",
                    "공동 식당 (Community Kitchen)",
                    "세탁 & 청소 서비스 (Laundry & Cleaning)"
                ],
                "estimated_cost": 250000000,
                "space_requirement_m2": 350,
                "narrative": "다자녀 가구를 위한 실질적인 생활 지원 커뮤니티입니다. 여러 자녀를 키우는 데 필요한 공간과 서비스를 제공하며, 특히 공동 식당과 세탁 서비스는 가사 부담을 크게 줄여줍니다.",
                "benefits": [
                    "다자녀 가구 특화 서비스",
                    "가사 부담 경감",
                    "형제자매 함께 활동 공간",
                    "이웃 간 상호 지원 네트워크"
                ]
            },
            
            # Senior modules
            {
                "module_id": "SENIOR_001",
                "module_name": "Silver Care & Wellness",
                "target_type": "Senior",
                "facilities": [
                    "건강관리실 (Health Care Room)",
                    "실버 체육관 (Silver Gym)",
                    "취미 문화교실 (Hobby & Culture Class)",
                    "독서실 & 바둑실 (Library & Baduk Room)",
                    "건강 상담실 (Health Consulting)"
                ],
                "estimated_cost": 160000000,
                "space_requirement_m2": 220,
                "narrative": "고령자를 위한 건강과 여가 중심의 커뮤니티 공간입니다. 전문 간호사가 상주하여 건강 상담을 제공하며, 연령대에 맞춘 운동 프로그램과 문화 활동을 통해 활기찬 노후 생활을 지원합니다.",
                "benefits": [
                    "전문 건강 관리 서비스",
                    "연령 맞춤형 운동 프로그램",
                    "사회적 교류 촉진",
                    "정서적 안정 지원"
                ]
            }
        ]
        
        # Save default modules
        for module_data in default_modules:
            file_name = f"{module_data['module_id']}.json"
            file_path = self.data_dir / file_name
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(module_data, f, indent=2, ensure_ascii=False)
    
    def get_modules_by_type(self, target_type: str) -> List[CommunityModule]:
        """Get all community modules for a specific housing type"""
        return self.modules.get(target_type, [])
    
    def get_module_by_id(self, module_id: str) -> Optional[CommunityModule]:
        """Get specific community module by ID"""
        for modules_list in self.modules.values():
            for module in modules_list:
                if module.module_id == module_id:
                    return module
        return None


class CommunitySelector:
    """
    Selects appropriate community module based on housing type
    
    Selection Logic:
        1. Get all modules for the housing type
        2. Select default (first) or best match
        3. Return selected module
    
    Usage:
        selector = CommunitySelector()
        module = selector.select("Youth")
        engine.inject_community(module)
    """
    
    def __init__(self, database: CommunityDatabase = None):
        """Initialize community selector"""
        self.database = database or CommunityDatabase()
    
    def select(
        self,
        recommended_type: str,
        preference: Optional[str] = None
    ) -> Optional[CommunityModule]:
        """
        Select community module based on housing type
        
        Args:
            recommended_type: Housing type from Phase 6.7 (e.g., "Youth", "Newlyweds_TypeI")
            preference: Optional preference (e.g., "premium", "basic", "family")
        
        Returns:
            Selected community module, or None if not found
        """
        # Get all modules for this type
        modules = self.database.get_modules_by_type(recommended_type)
        
        if not modules:
            print(f"Warning: No community modules found for type '{recommended_type}'")
            return None
        
        # If preference specified, try to match
        if preference:
            for module in modules:
                if preference.lower() in module.module_name.lower():
                    return module
        
        # Otherwise, return first (default) module
        return modules[0]
    
    def select_by_id(self, module_id: str) -> Optional[CommunityModule]:
        """Select specific community module by ID"""
        return self.database.get_module_by_id(module_id)
    
    def list_available_modules(self, target_type: str = None) -> Dict[str, List[str]]:
        """
        List all available community modules
        
        Args:
            target_type: Optional filter by housing type
        
        Returns:
            Dictionary of {housing_type: [module_names]}
        """
        result = {}
        
        if target_type:
            modules = self.database.get_modules_by_type(target_type)
            result[target_type] = [m.module_name for m in modules]
        else:
            for htype, modules in self.database.modules.items():
                result[htype] = [m.module_name for m in modules]
        
        return result


# Convenience functions
def inject_community_auto(
    decision,
    selector: CommunitySelector = None,
    preference: Optional[str] = None
):
    """
    Automatically inject community module into decision
    
    This is the main function to use in Phase 10 workflow.
    
    Usage:
        from app.report_types_v11.community_injector import inject_community_auto
        
        decision = ZeroSiteDecision(...)
        inject_community_auto(decision)
        # decision.community is now populated
    
    Args:
        decision: ZeroSiteDecision object
        selector: Optional custom selector
        preference: Optional preference string
    """
    if selector is None:
        selector = CommunitySelector()
    
    module = selector.select(
        recommended_type=decision.recommended_type,
        preference=preference
    )
    
    if module:
        decision.community = module
        print(f"✓ Community module injected: {module.module_name}")
    else:
        print(f"✗ No community module found for type: {decision.recommended_type}")


def get_community_cost_summary(module: CommunityModule) -> Dict[str, any]:
    """
    Get cost summary for community module
    
    Returns breakdown of costs per unit
    """
    return {
        "module_name": module.module_name,
        "total_cost": module.estimated_cost,
        "space_m2": module.space_requirement_m2,
        "cost_per_m2": module.estimated_cost / module.space_requirement_m2 if module.space_requirement_m2 > 0 else 0,
        "facilities_count": len(module.facilities),
        "benefits_count": len(module.benefits)
    }
