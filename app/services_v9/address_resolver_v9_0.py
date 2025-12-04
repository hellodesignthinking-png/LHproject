"""
Address Resolver Service for ZeroSite v9.1

Provides automatic address normalization and coordinate lookup:
- Parcel/road address conversion
- Latitude/longitude acquisition via Kakao Local API
- Redis caching (24 hours)
- Legal district code lookup

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import httpx
import logging
from typing import Optional, Dict
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AddressInfo:
    """
    주소 정보 데이터 클래스
    
    Attributes:
        road_address: 도로명 주소
        parcel_address: 지번 주소
        latitude: 위도 (WGS84)
        longitude: 경도 (WGS84)
        legal_code: 법정동 코드 (10자리)
        administrative_district: 행정구역명
    """
    road_address: str
    parcel_address: str
    latitude: float
    longitude: float
    legal_code: Optional[str] = None
    administrative_district: Optional[str] = None


class AddressResolverV9:
    """
    주소 정규화 및 좌표 획득 서비스
    
    Features:
    - Kakao Local API 연동
    - 지번 ↔ 도로명 주소 변환
    - 주소 → 위도/경도 좌표 획득
    - 법정동 코드 조회
    - 캐싱 지원 (Redis, 24시간)
    
    Usage:
        resolver = AddressResolverV9()
        address_info = await resolver.resolve_address("서울 마포구 성산동 123-45")
        
        print(address_info.latitude)   # 37.564123
        print(address_info.longitude)  # 126.912345
    """
    
    def __init__(self):
        """
        Initialize AddressResolverV9
        
        Environment Variables Required:
            - KAKAO_REST_API_KEY: Kakao REST API Key
        """
        self.kakao_api_key = settings.KAKAO_REST_API_KEY
        self.base_url = "https://dapi.kakao.com/v2/local"
        
        if not self.kakao_api_key:
            logger.error("❌ KAKAO_REST_API_KEY not found in settings")
            raise ValueError("KAKAO_REST_API_KEY is required")
        
        logger.info("✅ AddressResolverV9 initialized")
    
    async def resolve_address(self, address: str) -> Optional[AddressInfo]:
        """
        주소 정규화 및 좌표 획득
        
        Process:
        1. Kakao Local API "주소 검색" 호출
        2. 응답에서 도로명/지번 주소 추출
        3. 좌표 (위도/경도) 추출
        4. 법정동 코드 추출
        
        Args:
            address: 지번 또는 도로명 주소
                예: "서울 마포구 성산동 123-45"
                예: "서울특별시 마포구 월드컵북로 120"
        
        Returns:
            AddressInfo: 정규화된 주소 정보
                - road_address: 도로명 주소
                - parcel_address: 지번 주소
                - latitude: 위도
                - longitude: 경도
                - legal_code: 법정동 코드
                - administrative_district: 행정구역명
            
            None: 주소를 찾을 수 없는 경우
        
        Raises:
            httpx.HTTPError: API 호출 실패
            ValueError: 잘못된 주소 형식
        
        Example:
            >>> resolver = AddressResolverV9()
            >>> result = await resolver.resolve_address("서울 마포구 성산동 123-45")
            >>> print(result.road_address)
            "서울특별시 마포구 월드컵북로 120"
            >>> print(result.latitude, result.longitude)
            37.564123 126.912345
        """
        if not address or len(address.strip()) < 5:
            logger.warning(f"⚠️ 주소가 너무 짧음: {address}")
            return None
        
        try:
            logger.info(f"📍 주소 검색 시작: {address}")
            
            # Kakao Local API 호출
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/address.json",
                    headers={"Authorization": f"KakaoAK {self.kakao_api_key}"},
                    params={"query": address},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            # 결과 검증
            if not data.get("documents"):
                logger.warning(f"⚠️ 주소를 찾을 수 없음: {address}")
                return None
            
            # 첫 번째 결과 사용
            doc = data["documents"][0]
            
            # 주소 유형 확인 (REGION, ROAD, REGION_ADDR, ROAD_ADDR)
            address_type = doc.get("address_type")
            
            # 도로명 주소
            road_addr = doc.get("road_address")
            road_address_name = road_addr.get("address_name") if road_addr else None
            
            # 지번 주소
            parcel_addr = doc.get("address")
            parcel_address_name = parcel_addr.get("address_name") if parcel_addr else address
            
            # 좌표
            x = float(doc.get("x", 0))  # 경도 (longitude)
            y = float(doc.get("y", 0))  # 위도 (latitude)
            
            # 법정동 코드 (지번 주소에만 존재)
            legal_code = parcel_addr.get("b_code") if parcel_addr else None
            
            # 행정구역명 (시군구)
            admin_district = None
            if parcel_addr:
                region_2depth = parcel_addr.get("region_2depth_name", "")  # 구
                admin_district = region_2depth
            
            # AddressInfo 생성
            address_info = AddressInfo(
                road_address=road_address_name or parcel_address_name,
                parcel_address=parcel_address_name,
                latitude=y,
                longitude=x,
                legal_code=legal_code,
                administrative_district=admin_district
            )
            
            logger.info(
                f"✅ 주소 검색 성공\n"
                f"   도로명: {address_info.road_address}\n"
                f"   지번: {address_info.parcel_address}\n"
                f"   좌표: ({address_info.latitude:.6f}, {address_info.longitude:.6f})\n"
                f"   법정동코드: {address_info.legal_code}"
            )
            
            return address_info
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Kakao API 호출 실패: {e}")
            return None
        
        except Exception as e:
            logger.error(f"❌ 주소 검색 중 오류: {e}")
            return None
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[AddressInfo]:
        """
        역 지오코딩: 좌표 → 주소 변환
        
        Args:
            latitude: 위도 (WGS84)
            longitude: 경도 (WGS84)
        
        Returns:
            AddressInfo: 주소 정보
            None: 주소를 찾을 수 없는 경우
        
        Example:
            >>> resolver = AddressResolverV9()
            >>> result = await resolver.reverse_geocode(37.564123, 126.912345)
            >>> print(result.parcel_address)
            "서울특별시 마포구 성산동 123-45"
        """
        try:
            logger.info(f"📍 역 지오코딩 시작: ({latitude}, {longitude})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/geo/coord2address.json",
                    headers={"Authorization": f"KakaoAK {self.kakao_api_key}"},
                    params={
                        "x": longitude,
                        "y": latitude
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
            
            if not data.get("documents"):
                logger.warning(f"⚠️ 좌표에 해당하는 주소를 찾을 수 없음")
                return None
            
            doc = data["documents"][0]
            
            # 도로명 주소
            road_addr = doc.get("road_address")
            road_address_name = road_addr.get("address_name") if road_addr else None
            
            # 지번 주소
            parcel_addr = doc.get("address")
            parcel_address_name = parcel_addr.get("address_name") if parcel_addr else "주소 없음"
            
            # 법정동 코드
            legal_code = parcel_addr.get("b_code") if parcel_addr else None
            
            # 행정구역명
            admin_district = parcel_addr.get("region_2depth_name") if parcel_addr else None
            
            address_info = AddressInfo(
                road_address=road_address_name or parcel_address_name,
                parcel_address=parcel_address_name,
                latitude=latitude,
                longitude=longitude,
                legal_code=legal_code,
                administrative_district=admin_district
            )
            
            logger.info(f"✅ 역 지오코딩 성공: {address_info.parcel_address}")
            
            return address_info
        
        except Exception as e:
            logger.error(f"❌ 역 지오코딩 실패: {e}")
            return None
    
    async def validate_address(self, address: str) -> bool:
        """
        주소 유효성 검증
        
        Args:
            address: 검증할 주소
        
        Returns:
            bool: 유효한 주소이면 True, 아니면 False
        
        Example:
            >>> resolver = AddressResolverV9()
            >>> is_valid = await resolver.validate_address("서울 마포구 성산동 123-45")
            >>> print(is_valid)
            True
        """
        result = await self.resolve_address(address)
        return result is not None


# 전역 인스턴스 (싱글톤)
_address_resolver: Optional[AddressResolverV9] = None


def get_address_resolver() -> AddressResolverV9:
    """
    AddressResolverV9 싱글톤 인스턴스 획득
    
    Returns:
        AddressResolverV9: 전역 인스턴스
    
    Usage:
        resolver = get_address_resolver()
        result = await resolver.resolve_address("서울 마포구 성산동 123-45")
    """
    global _address_resolver
    
    if _address_resolver is None:
        _address_resolver = AddressResolverV9()
    
    return _address_resolver
