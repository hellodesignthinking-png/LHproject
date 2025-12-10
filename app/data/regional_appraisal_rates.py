"""
ZeroSite v18 Phase 5 - Regional Appraisal Rate Database
========================================================
LH 신축매입임대 지역별 감정평가율 데이터베이스

Data Sources:
- LH 공식 매입 가이드라인
- 과거 사업 실적 분석
- 지역별 시장 특성

Appraisal Rate Components:
- Land: 토지 감정평가 인정률 (85-100%)
- Building: 건물 공사비 인정률 (80-95%)
- Safety Factor: 안전계수 (95-100%)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Region(Enum):
    """지역 분류"""
    SEOUL = "seoul"                      # 서울특별시
    GYEONGGI = "gyeonggi"               # 경기도
    INCHEON = "incheon"                 # 인천광역시
    BUSAN = "busan"                     # 부산광역시
    DAEGU = "daegu"                     # 대구광역시
    GWANGJU = "gwangju"                 # 광주광역시
    DAEJEON = "daejeon"                 # 대전광역시
    ULSAN = "ulsan"                     # 울산광역시
    SEJONG = "sejong"                   # 세종특별자치시
    GANGWON = "gangwon"                 # 강원도
    CHUNGBUK = "chungbuk"               # 충청북도
    CHUNGNAM = "chungnam"               # 충청남도
    JEONBUK = "jeonbuk"                 # 전라북도
    JEONNAM = "jeonnam"                 # 전라남도
    GYEONGBUK = "gyeongbuk"             # 경상북도
    GYEONGNAM = "gyeongnam"             # 경상남도
    JEJU = "jeju"                       # 제주특별자치도


class HousingType(Enum):
    """주택 유형"""
    YOUTH = "youth"                     # 청년 주택
    NEWLYWED = "newlywed"              # 신혼부부 주택
    SENIOR = "senior"                   # 고령자 주택
    GENERAL = "general"                 # 일반 주택
    WELFARE = "welfare"                 # 복지시설 연계


class ProjectScale(Enum):
    """사업 규모"""
    SMALL = "small"                     # 소형 (50호 미만)
    MEDIUM = "medium"                   # 중형 (50-100호)
    LARGE = "large"                     # 대형 (100호 이상)


@dataclass
class AppraisalRate:
    """감정평가율 데이터"""
    region: Region
    housing_type: HousingType
    project_scale: ProjectScale
    
    # 토지 감정평가 인정률
    land_appraisal_rate: float          # 0.85 - 1.00
    
    # 건물 공사비 인정률
    building_ack_rate: float            # 0.80 - 0.95
    
    # 안전계수 (최종 조정)
    safety_factor: float                # 0.95 - 1.00
    
    # 메모
    notes: str = ""
    
    # 데이터 출처
    source: str = "LH 내부 가이드라인 기반"
    
    # 최종 업데이트
    last_updated: str = "2025-12"


# ==========================================
# 지역별 감정평가율 데이터베이스
# ==========================================

APPRAISAL_RATE_DATABASE: List[AppraisalRate] = [
    
    # ========== 서울특별시 ==========
    AppraisalRate(
        region=Region.SEOUL,
        housing_type=HousingType.YOUTH,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.98,
        building_ack_rate=0.92,
        safety_factor=0.98,
        notes="서울 청년주택 우대 (수요 높음)",
        source="LH 2024 서울 청년주택 사업 기준"
    ),
    AppraisalRate(
        region=Region.SEOUL,
        housing_type=HousingType.NEWLYWED,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.97,
        building_ack_rate=0.91,
        safety_factor=0.98,
        notes="서울 신혼부부 주택 우대",
        source="LH 2024 서울 신혼부부 사업 기준"
    ),
    AppraisalRate(
        region=Region.SEOUL,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.95,
        building_ack_rate=0.90,
        safety_factor=0.98,
        notes="서울 일반 기준 (높은 시장성)",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 경기도 ==========
    AppraisalRate(
        region=Region.GYEONGGI,
        housing_type=HousingType.YOUTH,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.96,
        building_ack_rate=0.91,
        safety_factor=0.98,
        notes="경기 수도권 청년주택 (분당, 판교 등 우대)",
        source="LH 2024 경기 북부/남부 차등 적용"
    ),
    AppraisalRate(
        region=Region.GYEONGGI,
        housing_type=HousingType.NEWLYWED,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.95,
        building_ack_rate=0.90,
        safety_factor=0.98,
        notes="경기 신혼부부 표준",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.GYEONGGI,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.93,
        building_ack_rate=0.89,
        safety_factor=0.97,
        notes="경기 일반 기준 (GTX 노선 추가 우대 가능)",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 인천광역시 ==========
    AppraisalRate(
        region=Region.INCHEON,
        housing_type=HousingType.YOUTH,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.94,
        building_ack_rate=0.90,
        safety_factor=0.97,
        notes="인천 청년주택 (송도, 영종 우대)",
        source="LH 2024 인천 사업 기준"
    ),
    AppraisalRate(
        region=Region.INCHEON,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.92,
        building_ack_rate=0.88,
        safety_factor=0.97,
        notes="인천 일반 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 부산광역시 ==========
    AppraisalRate(
        region=Region.BUSAN,
        housing_type=HousingType.YOUTH,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.93,
        building_ack_rate=0.89,
        safety_factor=0.97,
        notes="부산 청년주택 (해운대, 센텀 우대)",
        source="LH 2024 부산 사업 기준"
    ),
    AppraisalRate(
        region=Region.BUSAN,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.91,
        building_ack_rate=0.88,
        safety_factor=0.97,
        notes="부산 일반 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 대구광역시 ==========
    AppraisalRate(
        region=Region.DAEGU,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.90,
        building_ack_rate=0.87,
        safety_factor=0.97,
        notes="대구 표준 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 광주광역시 ==========
    AppraisalRate(
        region=Region.GWANGJU,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.89,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="광주 표준 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 대전광역시 ==========
    AppraisalRate(
        region=Region.DAEJEON,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.90,
        building_ack_rate=0.87,
        safety_factor=0.97,
        notes="대전 표준 기준 (과학단지 인근 우대 가능)",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 울산광역시 ==========
    AppraisalRate(
        region=Region.ULSAN,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.89,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="울산 표준 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 세종특별자치시 ==========
    AppraisalRate(
        region=Region.SEJONG,
        housing_type=HousingType.YOUTH,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.94,
        building_ack_rate=0.90,
        safety_factor=0.98,
        notes="세종 청년주택 (행복도시 정책 우대)",
        source="LH 2024 세종 사업 기준"
    ),
    AppraisalRate(
        region=Region.SEJONG,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.92,
        building_ack_rate=0.88,
        safety_factor=0.97,
        notes="세종 일반 기준",
        source="LH 표준 가이드라인"
    ),
    
    # ========== 지방 (기타 도) ==========
    AppraisalRate(
        region=Region.GANGWON,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.SMALL,
        land_appraisal_rate=0.87,
        building_ack_rate=0.85,
        safety_factor=0.96,
        notes="강원도 소규모 사업 기준",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.CHUNGBUK,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.88,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="충북 표준 기준",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.CHUNGNAM,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.88,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="충남 표준 기준 (천안 아산 우대 가능)",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.JEONBUK,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.87,
        building_ack_rate=0.85,
        safety_factor=0.96,
        notes="전북 표준 기준",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.JEONNAM,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.86,
        building_ack_rate=0.84,
        safety_factor=0.95,
        notes="전남 표준 기준",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.GYEONGBUK,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.87,
        building_ack_rate=0.85,
        safety_factor=0.96,
        notes="경북 표준 기준 (포항 경주 우대 가능)",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.GYEONGNAM,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.MEDIUM,
        land_appraisal_rate=0.88,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="경남 표준 기준 (창원 김해 우대 가능)",
        source="LH 표준 가이드라인"
    ),
    AppraisalRate(
        region=Region.JEJU,
        housing_type=HousingType.GENERAL,
        project_scale=ProjectScale.SMALL,
        land_appraisal_rate=0.89,
        building_ack_rate=0.86,
        safety_factor=0.96,
        notes="제주 특별 기준 (관광지역 고려)",
        source="LH 표준 가이드라인"
    ),
]


class RegionalAppraisalRateDB:
    """지역별 감정평가율 데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.database = APPRAISAL_RATE_DATABASE
    
    def get_rate(
        self,
        region: Region,
        housing_type: Optional[HousingType] = None,
        project_scale: Optional[ProjectScale] = None
    ) -> AppraisalRate:
        """
        지역별 감정평가율 조회
        
        Args:
            region: 지역
            housing_type: 주택 유형 (Optional)
            project_scale: 사업 규모 (Optional)
        
        Returns:
            AppraisalRate 객체 (매칭되지 않으면 기본값)
        """
        # 정확한 매치 찾기
        for rate in self.database:
            if rate.region == region:
                if housing_type and rate.housing_type != housing_type:
                    continue
                if project_scale and rate.project_scale != project_scale:
                    continue
                return rate
        
        # 지역만 매칭
        for rate in self.database:
            if rate.region == region:
                return rate
        
        # 기본값 (경기도 일반)
        return AppraisalRate(
            region=Region.GYEONGGI,
            housing_type=HousingType.GENERAL,
            project_scale=ProjectScale.MEDIUM,
            land_appraisal_rate=0.93,
            building_ack_rate=0.89,
            safety_factor=0.97,
            notes="기본값 (매칭 데이터 없음)",
            source="기본값"
        )
    
    def get_rate_by_address(self, address: str) -> AppraisalRate:
        """
        주소 기반 감정평가율 조회
        
        Args:
            address: 한국 주소 (예: "서울특별시 마포구...")
        
        Returns:
            AppraisalRate 객체
        """
        address_lower = address.lower()
        
        # 지역 매핑
        region_map = {
            "서울": Region.SEOUL,
            "경기": Region.GYEONGGI,
            "인천": Region.INCHEON,
            "부산": Region.BUSAN,
            "대구": Region.DAEGU,
            "광주": Region.GWANGJU,
            "대전": Region.DAEJEON,
            "울산": Region.ULSAN,
            "세종": Region.SEJONG,
            "강원": Region.GANGWON,
            "충북": Region.CHUNGBUK,
            "충남": Region.CHUNGNAM,
            "전북": Region.JEONBUK,
            "전남": Region.JEONNAM,
            "경북": Region.GYEONGBUK,
            "경남": Region.GYEONGNAM,
            "제주": Region.JEJU,
        }
        
        for key, region in region_map.items():
            if key in address:
                return self.get_rate(region)
        
        # 기본값
        return self.get_rate(Region.GYEONGGI)
    
    def get_all_rates_by_region(self, region: Region) -> List[AppraisalRate]:
        """특정 지역의 모든 감정평가율 조회"""
        return [rate for rate in self.database if rate.region == region]
    
    def get_statistics(self) -> Dict[str, any]:
        """데이터베이스 통계"""
        return {
            "total_entries": len(self.database),
            "regions": len(set(rate.region for rate in self.database)),
            "housing_types": len(set(rate.housing_type for rate in self.database)),
            "avg_land_rate": sum(r.land_appraisal_rate for r in self.database) / len(self.database),
            "avg_building_rate": sum(r.building_ack_rate for r in self.database) / len(self.database),
            "avg_safety_factor": sum(r.safety_factor for r in self.database) / len(self.database),
        }


# Singleton instance
_db_instance = None

def get_appraisal_db() -> RegionalAppraisalRateDB:
    """감정평가율 DB 인스턴스 가져오기"""
    global _db_instance
    if _db_instance is None:
        _db_instance = RegionalAppraisalRateDB()
    return _db_instance
