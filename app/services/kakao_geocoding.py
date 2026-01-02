"""
Kakao Maps API Service for Real Address Geocoding
==================================================

실제 카카오 지도 API를 사용한 주소 → 좌표 변환

Author: ZeroSite Development Team
Date: 2026-01-01
Version: 1.7.0
"""

from typing import Dict, Any, Optional, List
import httpx
import logging
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KakaoGeocodingError(Exception):
    """Kakao API 관련 에러"""
    pass


class AddressNotFoundError(KakaoGeocodingError):
    """주소를 찾을 수 없는 경우"""
    pass


class KakaoGeocodingService:
    """
    카카오 지도 API 기반 주소 검색 및 좌표 변환 서비스
    
    Features:
    - 실제 주소 → 좌표 변환
    - 행정구역 정보 추출
    - 법정동 코드 획득
    - PNU 생성 지원
    """
    
    def __init__(self):
        self.base_url = "https://dapi.kakao.com"
        self.api_key = settings.kakao_rest_api_key
        
        if not self.api_key or self.api_key.startswith('mock_'):
            logger.warning("⚠️ Kakao API key not configured or is mock")
            self.is_available = False
        else:
            self.is_available = True
            logger.info(f"✅ Kakao Geocoding Service initialized")
    
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        주소를 좌표로 변환 (카카오 지도 API 실제 호출)
        
        Args:
            address: 도로명 주소 또는 지번 주소
        
        Returns:
            {
                "address": "정확한 주소",
                "lat": 위도,
                "lon": 경도,
                "region_1depth": "시/도",
                "region_2depth": "시/군/구",
                "region_3depth": "읍/면/동",
                "b_code": "법정동 코드",
                "road_address": "도로명 주소",
                "jibun_address": "지번 주소"
            }
        
        Raises:
            AddressNotFoundError: 주소를 찾을 수 없는 경우
            KakaoGeocodingError: API 호출 실패
        """
        if not self.is_available:
            raise KakaoGeocodingError("Kakao API key not configured")
        
        logger.info(f"🔍 Geocoding address: {address}")
        
        try:
            url = f"{self.base_url}/v2/local/search/address.json"
            headers = {
                "Authorization": f"KakaoAK {self.api_key}"
            }
            params = {
                "query": address,
                "analyze_type": "similar"  # 유사 주소도 찾기
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                documents = data.get("documents", [])
                
                if not documents:
                    logger.warning(f"❌ Address not found: {address}")
                    raise AddressNotFoundError(f"주소를 찾을 수 없습니다: {address}")
                
                # 가장 정확한 결과 선택
                doc = documents[0]
                
                # 주소 정보 추출
                address_info = doc.get("address", {})
                road_address_info = doc.get("road_address", {})
                
                result = {
                    "address": doc.get("address_name", address),
                    "lat": float(doc.get("y", 0)),
                    "lon": float(doc.get("x", 0)),
                    "region_1depth": address_info.get("region_1depth_name", ""),
                    "region_2depth": address_info.get("region_2depth_name", ""),
                    "region_3depth": address_info.get("region_3depth_name", ""),
                    "b_code": address_info.get("b_code", ""),
                    "h_code": address_info.get("h_code", ""),  # 행정동 코드
                    "road_address": road_address_info.get("address_name", "") if road_address_info else "",
                    "jibun_address": address_info.get("address_name", ""),
                    "main_address_no": address_info.get("main_address_no", ""),
                    "sub_address_no": address_info.get("sub_address_no", ""),
                    "mountain_yn": address_info.get("mountain_yn", "N"),
                }
                
                logger.info(f"✅ Geocoding success: {result['address']} ({result['lat']}, {result['lon']})")
                logger.info(f"📍 Region: {result['region_1depth']} {result['region_2depth']} {result['region_3depth']}")
                logger.info(f"🏷️ B-Code: {result['b_code']}")
                
                return result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Kakao API HTTP error: {e.response.status_code}")
            if e.response.status_code == 401:
                raise KakaoGeocodingError("Kakao API 인증 실패 (API 키 확인 필요)")
            elif e.response.status_code == 429:
                raise KakaoGeocodingError("Kakao API 호출 한도 초과")
            else:
                raise KakaoGeocodingError(f"Kakao API 호출 실패: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"❌ Kakao API request error: {str(e)}")
            raise KakaoGeocodingError(f"네트워크 오류: {str(e)}")
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise KakaoGeocodingError(f"예상치 못한 오류: {str(e)}")
    
    async def search_address(self, query: str, page: int = 1, size: int = 10) -> List[Dict[str, Any]]:
        """
        주소 검색 (자동완성용)
        
        Args:
            query: 검색어
            page: 페이지 번호
            size: 결과 개수
        
        Returns:
            주소 목록
        """
        if not self.is_available:
            return []
        
        try:
            url = f"{self.base_url}/v2/local/search/address.json"
            headers = {
                "Authorization": f"KakaoAK {self.api_key}"
            }
            params = {
                "query": query,
                "page": page,
                "size": min(size, 30)  # Max 30
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                documents = data.get("documents", [])
                
                results = []
                for doc in documents:
                    address_info = doc.get("address", {})
                    road_address_info = doc.get("road_address", {})
                    
                    results.append({
                        "address": doc.get("address_name"),
                        "road_address": road_address_info.get("address_name", "") if road_address_info else "",
                        "lat": float(doc.get("y", 0)),
                        "lon": float(doc.get("x", 0)),
                        "region": f"{address_info.get('region_1depth_name', '')} {address_info.get('region_2depth_name', '')} {address_info.get('region_3depth_name', '')}".strip()
                    })
                
                return results
        
        except Exception as e:
            logger.error(f"❌ Address search error: {str(e)}")
            return []
    
    def generate_pnu(
        self, 
        b_code: str, 
        main_no: str = "0001", 
        sub_no: str = "0000",
        is_mountain: bool = False
    ) -> str:
        """
        법정동 코드로부터 PNU 생성
        
        Args:
            b_code: 법정동 코드 (10자리)
            main_no: 본번 (4자리)
            sub_no: 부번 (4자리)
            is_mountain: 산 여부
        
        Returns:
            PNU (19자리)
        
        Format:
            시도(2) + 시군구(3) + 읍면동(3) + 리(2) + 산(1) + 본번(4) + 부번(4) = 19자리
        """
        # B-Code는 10자리 법정동 코드
        if len(b_code) < 10:
            b_code = b_code.ljust(10, '0')
        
        # 산 코드
        mountain_code = "2" if is_mountain else "1"
        
        # Main/Sub 번호 포맷팅
        try:
            main_formatted = f"{int(main_no):04d}"
            sub_formatted = f"{int(sub_no):04d}"
        except (ValueError, TypeError):
            main_formatted = "0001"
            sub_formatted = "0000"
        
        pnu = f"{b_code}{mountain_code}{main_formatted}{sub_formatted}"
        
        logger.info(f"🏷️ Generated PNU: {pnu} (B-Code: {b_code}, Mountain: {is_mountain})")
        
        return pnu
    
    def is_mock_mode(self) -> bool:
        """Mock 모드 여부 확인"""
        return not self.is_available


# Global service instance
kakao_geocoding_service = KakaoGeocodingService()
