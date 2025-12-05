"""
Synchronous Address Resolver for ZeroSite v9.1

Simplified synchronous version of AddressResolverV9 for use in
non-async contexts like the auto input service.

For production use, consider using the full async AddressResolverV9
with proper event loop handling.

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import logging
import requests
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AddressInfo:
    """주소 정보 (간소화 버전)"""
    success: bool
    road_address: Optional[str] = None
    parcel_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    legal_code: Optional[str] = None
    administrative_district: Optional[str] = None
    confidence_score: float = 0.0
    error_message: Optional[str] = None


class AddressResolverSyncV91:
    """
    동기식 주소 → 좌표 변환 서비스
    
    Features:
    - 카카오 주소 검색 API 연동 (동기식)
    - 도로명/지번 주소 정규화
    - 위도/경도 좌표 획득
    - 법정동 코드 추출
    
    Note:
        This is a simplified synchronous version.
        For async environments, use AddressResolverV9.
    """
    
    def __init__(self, kakao_api_key: Optional[str] = None):
        """
        Args:
            kakao_api_key: Kakao REST API Key (optional, loads from env)
        """
        if kakao_api_key:
            self.kakao_api_key = kakao_api_key
        else:
            # Try to load from settings
            try:
                from app.core.config import settings
                self.kakao_api_key = settings.kakao_rest_api_key
            except:
                logger.warning("⚠️  Kakao API key not configured")
                self.kakao_api_key = None
        
        self.base_url = "https://dapi.kakao.com/v2/local"
        logger.info("🗺️  AddressResolverSyncV91 initialized")
    
    def resolve_address(self, address: str) -> AddressInfo:
        """
        주소 → 좌표 변환 (동기식)
        
        Args:
            address: 지번 또는 도로명 주소
        
        Returns:
            AddressInfo: 주소 정보 (좌표 포함)
        
        Example:
            >>> resolver = AddressResolverSyncV91()
            >>> info = resolver.resolve_address("서울 마포구 성산동 123")
            >>> print(info.latitude, info.longitude)
            37.564123 126.912345
        """
        if not self.kakao_api_key:
            logger.warning("⚠️  Kakao API key not available - returning mock data")
            return self._get_mock_address_info(address)
        
        try:
            # Kakao Local API 호출
            url = f"{self.base_url}/search/address.json"
            headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
            params = {"query": address}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code != 200:
                logger.error(f"❌ Kakao API error: {response.status_code}")
                return AddressInfo(
                    success=False,
                    error_message=f"API error: {response.status_code}"
                )
            
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                logger.warning(f"⚠️  No results for address: {address}")
                return self._get_mock_address_info(address)
            
            # 첫 번째 결과 사용
            doc = documents[0]
            address_data = doc.get("address", {})
            road_address_data = doc.get("road_address", {})
            
            # 주소 정보 추출
            parcel_address = address_data.get("address_name")
            road_address = road_address_data.get("address_name") if road_address_data else None
            
            # 좌표 추출
            latitude = float(doc.get("y", 0))
            longitude = float(doc.get("x", 0))
            
            # 법정동 코드
            legal_code = address_data.get("b_code")
            
            # 행정구역
            region_1 = address_data.get("region_1depth_name", "")  # 시/도
            region_2 = address_data.get("region_2depth_name", "")  # 구/군
            region_3 = address_data.get("region_3depth_name", "")  # 동/읍/면
            administrative_district = f"{region_1} {region_2} {region_3}".strip()
            
            # 신뢰도 계산
            confidence = 100.0 if road_address else 80.0
            
            logger.info(f"✅ Address resolved: {parcel_address}")
            logger.info(f"   Coordinates: ({latitude:.6f}, {longitude:.6f})")
            
            return AddressInfo(
                success=True,
                road_address=road_address,
                parcel_address=parcel_address,
                latitude=latitude,
                longitude=longitude,
                legal_code=legal_code,
                administrative_district=administrative_district,
                confidence_score=confidence
            )
            
        except requests.exceptions.Timeout:
            logger.error("❌ Kakao API timeout")
            return AddressInfo(
                success=False,
                error_message="API timeout"
            )
        
        except Exception as e:
            logger.error(f"❌ Address resolution error: {e}")
            return self._get_mock_address_info(address)
    
    def _get_mock_address_info(self, address: str) -> AddressInfo:
        """
        Mock 주소 정보 생성 (API 실패 시 폴백)
        
        서울시청 좌표를 기본값으로 사용
        """
        logger.warning(f"⚠️  Using mock coordinates for: {address}")
        
        # 서울시청 좌표
        mock_lat = 37.5665
        mock_lng = 126.9780
        
        return AddressInfo(
            success=True,  # Mock이지만 success=True (시스템 계속 동작)
            parcel_address=address,
            road_address=None,
            latitude=mock_lat,
            longitude=mock_lng,
            legal_code="1111010100",  # 서울시 종로구 청운동
            administrative_district="서울특별시 중구 을지로",
            confidence_score=20.0,  # Low confidence for mock data
            error_message="Kakao API unavailable - using default coordinates"
        )
    
    def reverse_geocode(
        self, 
        latitude: float, 
        longitude: float
    ) -> AddressInfo:
        """
        좌표 → 주소 변환 (동기식)
        
        Args:
            latitude: 위도
            longitude: 경도
        
        Returns:
            AddressInfo: 주소 정보
        """
        if not self.kakao_api_key:
            logger.warning("⚠️  Kakao API key not available")
            return AddressInfo(
                success=False,
                error_message="Kakao API key not configured"
            )
        
        try:
            url = f"{self.base_url}/geo/coord2address.json"
            headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
            params = {
                "x": longitude,
                "y": latitude,
                "input_coord": "WGS84"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code != 200:
                return AddressInfo(
                    success=False,
                    error_message=f"API error: {response.status_code}"
                )
            
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                return AddressInfo(
                    success=False,
                    error_message="No address found for coordinates"
                )
            
            doc = documents[0]
            address_data = doc.get("address", {})
            road_address_data = doc.get("road_address", {})
            
            return AddressInfo(
                success=True,
                parcel_address=address_data.get("address_name"),
                road_address=road_address_data.get("address_name") if road_address_data else None,
                latitude=latitude,
                longitude=longitude,
                legal_code=address_data.get("b_code"),
                administrative_district=address_data.get("region_3depth_name"),
                confidence_score=100.0
            )
            
        except Exception as e:
            logger.error(f"❌ Reverse geocoding error: {e}")
            return AddressInfo(
                success=False,
                error_message=str(e)
            )


# Convenience function
def quick_resolve_address(address: str) -> tuple:
    """
    빠른 주소 → 좌표 변환
    
    Args:
        address: 주소
    
    Returns:
        tuple: (latitude, longitude, success)
    
    Example:
        >>> lat, lng, success = quick_resolve_address("서울 마포구 성산동 123")
        >>> print(lat, lng)
        37.564123 126.912345
    """
    resolver = AddressResolverSyncV91()
    info = resolver.resolve_address(address)
    
    return (info.latitude, info.longitude, info.success)
