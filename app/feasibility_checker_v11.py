"""
ZeroSite v11.0 - Feasibility Check Layer
=========================================
세대유형 추천의 현실성을 검증하는 레이어

검증 항목:
1. 토지 면적 vs 세대유형 적합성
2. 용적률/건폐율 vs 필요 세대수
3. 건물 유형 제약 (단독/다가구/다세대/연립/아파트)
4. 법적 제약 (용도지역별 허용 세대수)
5. 경제성 검증 (소형/중형/대형 세대 비율)
"""

from typing import Dict, Any, List, Tuple
from enum import Enum


class UnitTypeFeasibility(Enum):
    """세대유형별 최소 요구사항"""
    YOUTH = {
        "min_land_area": 300,  # ㎡
        "min_units": 10,
        "optimal_unit_size": 36,  # ㎡ (전용면적)
        "min_far": 150,
        "preferred_building_types": ["다세대", "연립", "아파트"]
    }
    NEWLYWED = {
        "min_land_area": 400,
        "min_units": 15,
        "optimal_unit_size": 46,
        "min_far": 180,
        "preferred_building_types": ["다세대", "연립", "아파트"]
    }
    SENIOR = {
        "min_land_area": 500,
        "min_units": 20,
        "optimal_unit_size": 46,
        "min_far": 200,
        "preferred_building_types": ["아파트", "실버타운"],
        "special_requirements": {
            "elevator": True,
            "barrier_free": True,
            "medical_accessibility": True
        }
    }
    GENERAL = {
        "min_land_area": 300,
        "min_units": 8,
        "optimal_unit_size": 59,
        "min_far": 150,
        "preferred_building_types": ["다세대", "연립", "아파트"]
    }
    VULNERABLE = {
        "min_land_area": 250,
        "min_units": 10,
        "optimal_unit_size": 36,
        "min_far": 150,
        "preferred_building_types": ["다세대", "연립", "아파트"],
        "special_requirements": {
            "accessibility": True,
            "public_transport": True
        }
    }


class FeasibilityChecker:
    """세대유형 추천의 현실성 검증 엔진"""
    
    def __init__(self, 
                 land_area: float,
                 bcr: float,
                 far: float,
                 zone_type: str,
                 max_floors: int,
                 unit_count: int,
                 total_gfa: float):
        self.land_area = land_area
        self.bcr = bcr
        self.far = far
        self.zone_type = zone_type
        self.max_floors = max_floors
        self.unit_count = unit_count
        self.total_gfa = total_gfa
        self.avg_unit_size = total_gfa / unit_count if unit_count > 0 else 0
    
    def check_unit_type_feasibility(self, recommended_type: str) -> Dict[str, Any]:
        """추천된 세대유형의 현실성 검증"""
        
        # 세대유형 매핑
        type_map = {
            "youth": UnitTypeFeasibility.YOUTH.value,
            "청년형": UnitTypeFeasibility.YOUTH.value,
            "newlywed": UnitTypeFeasibility.NEWLYWED.value,
            "신혼형": UnitTypeFeasibility.NEWLYWED.value,
            "senior": UnitTypeFeasibility.SENIOR.value,
            "고령자형": UnitTypeFeasibility.SENIOR.value,
            "general": UnitTypeFeasibility.GENERAL.value,
            "일반형": UnitTypeFeasibility.GENERAL.value,
            "vulnerable": UnitTypeFeasibility.VULNERABLE.value,
            "취약계층형": UnitTypeFeasibility.VULNERABLE.value
        }
        
        requirements = type_map.get(recommended_type.lower(), UnitTypeFeasibility.GENERAL.value)
        
        # 검증 항목별 체크
        checks = {
            "land_area_check": self._check_land_area(requirements),
            "unit_count_check": self._check_unit_count(requirements),
            "far_check": self._check_far(requirements),
            "building_type_check": self._check_building_type(requirements),
            "zone_compatibility_check": self._check_zone_compatibility(recommended_type),
            "economic_feasibility_check": self._check_economic_feasibility(recommended_type)
        }
        
        # 종합 판정
        all_passed = all(check["status"] == "PASS" for check in checks.values())
        critical_failures = [
            check_name for check_name, check in checks.items() 
            if check["status"] == "FAIL" and check.get("critical", False)
        ]
        
        # 대안 제시
        alternative_types = []
        if not all_passed:
            alternative_types = self._suggest_alternatives(recommended_type, checks)
        
        return {
            "recommended_type": recommended_type,
            "feasibility_status": "PASS" if all_passed else "FAIL" if critical_failures else "WARNING",
            "overall_score": self._calculate_feasibility_score(checks),
            "detailed_checks": checks,
            "critical_failures": critical_failures,
            "alternative_types": alternative_types,
            "final_recommendation": self._generate_final_recommendation(
                recommended_type, all_passed, alternative_types
            )
        }
    
    def _check_land_area(self, requirements: Dict) -> Dict[str, Any]:
        """토지 면적 검증"""
        min_area = requirements["min_land_area"]
        
        if self.land_area >= min_area * 1.2:
            status = "PASS"
            message = f"토지면적 {self.land_area:.0f}㎡는 최소 요구면적 {min_area}㎡ 대비 충분합니다."
        elif self.land_area >= min_area:
            status = "PASS"
            message = f"토지면적 {self.land_area:.0f}㎡는 최소 요구면적 {min_area}㎡를 충족합니다."
        else:
            status = "FAIL"
            message = f"토지면적 {self.land_area:.0f}㎡는 최소 요구면적 {min_area}㎡에 미달합니다."
        
        return {
            "status": status,
            "message": message,
            "current_value": self.land_area,
            "required_value": min_area,
            "critical": True
        }
    
    def _check_unit_count(self, requirements: Dict) -> Dict[str, Any]:
        """세대수 검증"""
        min_units = requirements["min_units"]
        
        if self.unit_count >= min_units * 1.5:
            status = "PASS"
            message = f"계획세대수 {self.unit_count}세대는 최소 요구세대수 {min_units}세대 대비 충분합니다."
        elif self.unit_count >= min_units:
            status = "PASS"
            message = f"계획세대수 {self.unit_count}세대는 최소 요구세대수 {min_units}세대를 충족합니다."
        else:
            status = "WARNING"
            message = f"계획세대수 {self.unit_count}세대는 최소 요구세대수 {min_units}세대에 다소 부족합니다."
        
        return {
            "status": status,
            "message": message,
            "current_value": self.unit_count,
            "required_value": min_units,
            "critical": False
        }
    
    def _check_far(self, requirements: Dict) -> Dict[str, Any]:
        """용적률 검증"""
        min_far = requirements["min_far"]
        
        if self.far >= min_far * 1.2:
            status = "PASS"
            message = f"용적률 {self.far}%는 최소 요구 용적률 {min_far}% 대비 충분합니다."
        elif self.far >= min_far:
            status = "PASS"
            message = f"용적률 {self.far}%는 최소 요구 용적률 {min_far}%를 충족합니다."
        else:
            status = "FAIL"
            message = f"용적률 {self.far}%는 최소 요구 용적률 {min_far}%에 미달합니다."
        
        return {
            "status": status,
            "message": message,
            "current_value": self.far,
            "required_value": min_far,
            "critical": True
        }
    
    def _check_building_type(self, requirements: Dict) -> Dict[str, Any]:
        """건물 유형 검증"""
        preferred_types = requirements.get("preferred_building_types", [])
        
        # 층수로 건물 유형 추정
        if self.max_floors >= 15:
            estimated_type = "아파트"
        elif self.max_floors >= 5:
            estimated_type = "연립"
        elif self.max_floors >= 3:
            estimated_type = "다세대"
        else:
            estimated_type = "단독/다가구"
        
        if estimated_type in preferred_types:
            status = "PASS"
            message = f"추정 건물유형 '{estimated_type}'는 해당 세대유형에 적합합니다."
        else:
            status = "WARNING"
            message = f"추정 건물유형 '{estimated_type}'는 해당 세대유형에 비추천입니다. 권장: {', '.join(preferred_types)}"
        
        return {
            "status": status,
            "message": message,
            "estimated_type": estimated_type,
            "preferred_types": preferred_types,
            "critical": False
        }
    
    def _check_zone_compatibility(self, recommended_type: str) -> Dict[str, Any]:
        """용도지역 적합성 검증"""
        # 용도지역별 세대유형 적합성
        zone_suitability = {
            "제1종전용주거지역": ["일반형"],
            "제2종전용주거지역": ["일반형", "청년형"],
            "제1종일반주거지역": ["일반형", "청년형", "신혼형"],
            "제2종일반주거지역": ["일반형", "청년형", "신혼형", "취약계층형"],
            "제3종일반주거지역": ["청년형", "신혼형", "일반형", "고령자형", "취약계층형"],
            "준주거지역": ["청년형", "신혼형", "일반형"]
        }
        
        suitable_types = []
        for zone, types in zone_suitability.items():
            if zone in self.zone_type:
                suitable_types = types
                break
        
        # 한글 타입명 매핑
        type_name_map = {
            "youth": "청년형", "newlywed": "신혼형", "senior": "고령자형",
            "general": "일반형", "vulnerable": "취약계층형"
        }
        recommended_type_kr = type_name_map.get(recommended_type.lower(), recommended_type)
        
        if recommended_type_kr in suitable_types or not suitable_types:
            status = "PASS"
            message = f"'{self.zone_type}'에서 '{recommended_type_kr}' 유형 개발이 가능합니다."
        else:
            status = "WARNING"
            message = f"'{self.zone_type}'에서 '{recommended_type_kr}' 유형은 비추천입니다. 적합 유형: {', '.join(suitable_types)}"
        
        return {
            "status": status,
            "message": message,
            "zone_type": self.zone_type,
            "suitable_types": suitable_types,
            "critical": False
        }
    
    def _check_economic_feasibility(self, recommended_type: str) -> Dict[str, Any]:
        """경제성 검증"""
        # 평균 전용면적 기준 경제성 평가
        type_size_range = {
            "youth": (30, 40),
            "청년형": (30, 40),
            "newlywed": (40, 55),
            "신혼형": (40, 55),
            "senior": (40, 60),
            "고령자형": (40, 60),
            "general": (50, 85),
            "일반형": (50, 85),
            "vulnerable": (30, 50),
            "취약계층형": (30, 50)
        }
        
        size_range = type_size_range.get(recommended_type.lower(), (40, 60))
        min_size, max_size = size_range
        
        if min_size <= self.avg_unit_size <= max_size:
            status = "PASS"
            message = f"평균 전용면적 {self.avg_unit_size:.1f}㎡는 해당 유형의 적정 범위({min_size}-{max_size}㎡) 내에 있습니다."
        elif self.avg_unit_size < min_size:
            status = "WARNING"
            message = f"평균 전용면적 {self.avg_unit_size:.1f}㎡는 해당 유형 기준({min_size}-{max_size}㎡)보다 작습니다."
        else:
            status = "WARNING"
            message = f"평균 전용면적 {self.avg_unit_size:.1f}㎡는 해당 유형 기준({min_size}-{max_size}㎡)보다 큽니다."
        
        return {
            "status": status,
            "message": message,
            "avg_unit_size": self.avg_unit_size,
            "optimal_range": size_range,
            "critical": False
        }
    
    def _calculate_feasibility_score(self, checks: Dict[str, Dict]) -> int:
        """현실성 종합 점수 계산"""
        total_score = 0
        max_score = 0
        
        for check in checks.values():
            if check["status"] == "PASS":
                score = 20 if check.get("critical", False) else 10
            elif check["status"] == "WARNING":
                score = 15 if check.get("critical", False) else 7
            else:  # FAIL
                score = 0
            
            total_score += score
            max_score += (20 if check.get("critical", False) else 10)
        
        return int((total_score / max_score) * 100) if max_score > 0 else 0
    
    def _suggest_alternatives(self, original_type: str, checks: Dict) -> List[Dict[str, Any]]:
        """대안 세대유형 제안"""
        alternatives = []
        
        # 토지면적/용적률 기준 대안 제시
        if checks["land_area_check"]["status"] == "FAIL" or checks["far_check"]["status"] == "FAIL":
            # 소규모 개발에 적합한 유형
            if self.land_area < 400:
                alternatives.append({
                    "type": "청년형",
                    "reason": "소규모 토지에 적합하며, 소형 세대 중심 개발로 경제성 확보 가능"
                })
                alternatives.append({
                    "type": "취약계층형",
                    "reason": "최소 토지면적 요구사항이 낮으며, 정책 지원 혜택 활용 가능"
                })
            elif self.land_area < 600:
                alternatives.append({
                    "type": "신혼형",
                    "reason": "중규모 토지에 적합하며, 안정적인 수요 기반 확보"
                })
                alternatives.append({
                    "type": "일반형",
                    "reason": "다양한 가구 수요 대응 가능, 분양/임대 전환 유연성 확보"
                })
        
        # 용적률 기준 대안
        if self.far < 180:
            alternatives.append({
                "type": "일반형",
                "reason": "낮은 용적률에서도 경제성 확보 가능, 중대형 세대 구성"
            })
        
        # 중복 제거
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt["type"] not in seen and alt["type"] != original_type:
                seen.add(alt["type"])
                unique_alternatives.append(alt)
        
        return unique_alternatives[:3]  # 최대 3개
    
    def _generate_final_recommendation(self, 
                                       recommended_type: str, 
                                       is_feasible: bool, 
                                       alternatives: List[Dict]) -> str:
        """최종 권고사항 생성"""
        if is_feasible:
            return f"✅ '{recommended_type}' 유형은 현재 부지 조건에서 실현 가능하며, 사업 추진을 권장합니다."
        elif alternatives:
            alt_types = ", ".join([f"'{alt['type']}'" for alt in alternatives])
            return f"⚠️ '{recommended_type}' 유형은 일부 제약이 있습니다. 대안으로 {alt_types} 유형을 검토하시기 바랍니다."
        else:
            return f"⚠️ '{recommended_type}' 유형은 현재 부지 조건에서 일부 제약이 있으나, 설계 조정을 통해 실현 가능합니다."


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    # 테스트 케이스 1: 소규모 부지에 고령자형 추천 (불가능)
    checker1 = FeasibilityChecker(
        land_area=200,  # 너무 작음
        bcr=60,
        far=150,  # 너무 낮음
        zone_type="제2종일반주거지역",
        max_floors=4,
        unit_count=8,
        total_gfa=600
    )
    
    result1 = checker1.check_unit_type_feasibility("고령자형")
    print("=" * 60)
    print("테스트 1: 소규모 부지에 고령자형 추천")
    print(f"현실성 상태: {result1['feasibility_status']}")
    print(f"종합 점수: {result1['overall_score']}/100")
    print(f"최종 권고: {result1['final_recommendation']}")
    if result1['alternative_types']:
        print("\n대안 유형:")
        for alt in result1['alternative_types']:
            print(f"  - {alt['type']}: {alt['reason']}")
    
    # 테스트 케이스 2: 적정 규모에 청년형 추천 (가능)
    checker2 = FeasibilityChecker(
        land_area=500,
        bcr=60,
        far=250,
        zone_type="제3종일반주거지역",
        max_floors=10,
        unit_count=30,
        total_gfa=1200
    )
    
    result2 = checker2.check_unit_type_feasibility("청년형")
    print("\n" + "=" * 60)
    print("테스트 2: 적정 규모에 청년형 추천")
    print(f"현실성 상태: {result2['feasibility_status']}")
    print(f"종합 점수: {result2['overall_score']}/100")
    print(f"최종 권고: {result2['final_recommendation']}")
