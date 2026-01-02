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
        # Kakao API가 없으면 지능형 폴백 사용
        if not self.is_available:
            logger.warning("⚠️ Kakao API not available, using intelligent fallback")
            return self._intelligent_geocode_fallback(address)
        
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
    
    def _intelligent_geocode_fallback(self, address: str) -> Dict[str, Any]:
        """
        지능형 주소 파싱 폴백 (Kakao API 없을 때)
        
        실제 주소 패턴을 분석하여 가능한 정확하게 좌표를 추정
        """
        import re
        
        # 주소 파싱
        parts = address.split()
        
        # 시/도 추출
        sido = ""
        for part in parts:
            if "특별시" in part or "광역시" in part or "도" in part:
                sido = part
                break
        if not sido:
            sido = parts[0] if parts else "서울특별시"
        
        # 시/군/구 추출
        sigungu = ""
        for part in parts:
            if ("시" in part or "군" in part or "구" in part) and part != sido:
                sigungu = part
                break
        if not sigungu:
            sigungu = parts[1] if len(parts) > 1 else "강남구"
        
        # 읍/면/동 추출
        dong = ""
        for part in parts:
            if "읍" in part or "면" in part or "동" in part or "리" in part:
                dong = part
                break
        if not dong:
            dong = parts[2] if len(parts) > 2 else "역삼동"
        
        # 지역별 대표 좌표 (주요 시/구청 위치)
        region_coords = {
            # 서울
            "서울특별시": {
                "강남구": (37.5172, 127.0473),
                "서초구": (37.4837, 127.0324),
                "송파구": (37.5145, 127.1059),
                "강동구": (37.5301, 127.1238),
                "마포구": (37.5663, 126.9019),
                "용산구": (37.5326, 126.9900),
                "종로구": (37.5735, 126.9788),
                "중구": (37.5641, 126.9979),
                "default": (37.5665, 126.9780)
            },
            # 경기도
            "경기도": {
                "수원시": (37.2636, 127.0286),
                "성남시": (37.4201, 127.1262),
                "용인시": (37.2410, 127.1776),
                "default": (37.4138, 127.5183)
            },
            # 인천
            "인천광역시": {
                "남동구": (37.4475, 126.7313),
                "연수구": (37.4105, 126.6780),
                "default": (37.4563, 126.7052)
            },
            # 대전
            "대전광역시": {
                "유성구": (36.3621, 127.3567),
                "default": (36.3504, 127.3845)
            }
        }
        
        # 좌표 결정
        lat, lon = 37.5665, 126.9780  # 기본값: 서울시청
        
        if sido in region_coords:
            region_map = region_coords[sido]
            if sigungu in region_map:
                lat, lon = region_map[sigungu]
            else:
                lat, lon = region_map["default"]
        
        # B-Code 생성 (법정동 코드)
        sido_code = {
            "서울특별시": "11",
            "경기도": "41",
            "인천광역시": "28",
            "대전광역시": "30",
            "부산광역시": "26",
            "대구광역시": "27",
            "광주광역시": "29",
            "울산광역시": "31"
        }.get(sido, "11")
        
        sigungu_code = {
            "강남구": "680",
            "서초구": "650",
            "송파구": "710",
            "강동구": "740",
            "마포구": "440",
            "용산구": "170",
            "종로구": "110",
            "중구": "140"
        }.get(sigungu.replace("시", "").replace("군", ""), "000")
        
        b_code = f"{sido_code}{sigungu_code}00000"
        
        result = {
            "address": address,
            "lat": lat,
            "lon": lon,
            "region_1depth": sido,
            "region_2depth": sigungu,
            "region_3depth": dong,
            "b_code": b_code,
            "h_code": b_code,
            "road_address": address,
            "jibun_address": address,
            "main_address_no": "1",
            "sub_address_no": "0",
            "mountain_yn": "N",
            "is_fallback": True  # 폴백 모드임을 표시
        }
        
        logger.info(f"✅ Fallback geocoding: {result['address']} ({result['lat']}, {result['lon']})")
        logger.info(f"📍 Region: {result['region_1depth']} {result['region_2depth']} {result['region_3depth']}")
        
        return result
    
    def geocode_address_sync(self, address: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for geocode_address
        동기 컨텍스트에서 사용 가능한 주소 변환
        """
        import asyncio
        
        try:
            # asyncio loop 가져오기 (또는 생성)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # async 함수 실행
            return loop.run_until_complete(self.geocode_address(address))
        except Exception as e:
            logger.error(f"Sync geocode error: {e}")
            raise


# Global service instance
kakao_geocoding_service = KakaoGeocodingService()
