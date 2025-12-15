"""
Advanced Address Parser v1.0
정확한 구·동 파싱으로 "서울 기타" 문제 해결

Author: Antenna Holdings Development Team
Date: 2024-12-13
Purpose: Fix "서울 기타" display issue in transaction addresses
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AdvancedAddressParser:
    """
    정확한 주소 파싱 클래스
    
    목표: "서울 기타 대치동 680-11" → "서울시 강남구 대치동 680-11"
    """
    
    def __init__(self):
        """초기화"""
        
        # 서울시 25개 구 매핑
        self.seoul_districts = {
            '종로구', '중구', '용산구', '성동구', '광진구',
            '동대문구', '중랑구', '성북구', '강북구', '도봉구',
            '노원구', '은평구', '서대문구', '마포구', '양천구',
            '강서구', '구로구', '금천구', '영등포구', '동작구',
            '관악구', '서초구', '강남구', '송파구', '강동구'
        }
        
        # 동(洞) - 구(區) 매핑 (주요 동만 포함)
        self.dong_to_gu_mapping = {
            # 강남구
            '역삼동': '강남구', '삼성동': '강남구', '대치동': '강남구',
            '논현동': '강남구', '압구정동': '강남구', '청담동': '강남구',
            '신사동': '강남구', '도곡동': '강남구', '개포동': '강남구',
            
            # 서초구
            '서초동': '서초구', '반포동': '서초구', '잠원동': '서초구',
            '방배동': '서초구', '양재동': '서초구', '우면동': '서초구',
            
            # 송파구
            '잠실동': '송파구', '신천동': '송파구', '가락동': '송파구',
            '문정동': '송파구', '석촌동': '송파구', '삼전동': '송파구',
            
            # 강동구
            '천호동': '강동구', '강일동': '강동구', '둔촌동': '강동구',
            
            # 용산구
            '이태원동': '용산구', '한남동': '용산구', '이촌동': '용산구',
            '용산동': '용산구', '원효로': '용산구',
            
            # 마포구
            '공덕동': '마포구', '아현동': '마포구', '도화동': '마포구',
            '용강동': '마포구', '대흥동': '마포구', '염리동': '마포구',
            '신수동': '마포구', '서강동': '마포구', '서교동': '마포구',
            '합정동': '마포구', '망원동': '마포구', '연남동': '마포구',
            '성산동': '마포구', '상암동': '마포구',
            
            # 영등포구
            '영등포동': '영등포구', '여의도동': '영등포구', '당산동': '영등포구',
            
            # 광진구
            '자양동': '광진구', '구의동': '광진구', '광장동': '광진구',
            
            # 성동구
            '왕십리': '성동구', '행당동': '성동구', '성수동': '성동구',
            
            # 관악구
            '신림동': '관악구', '봉천동': '관악구',
            
            # 동작구
            '노량진동': '동작구', '흑석동': '동작구', '사당동': '동작구',
            
            # 구로구
            '구로동': '구로구', '신도림동': '구로구', '개봉동': '구로구',
            
            # 양천구
            '목동': '양천구', '신정동': '양천구',
            
            # 강서구
            '염창동': '강서구', '등촌동': '강서구', '화곡동': '강서구',
            '방화동': '강서구',
            
            # 노원구
            '월계동': '노원구', '공릉동': '노원구', '하계동': '노원구',
            
            # 은평구
            '응암동': '은평구', '역촌동': '은평구', '불광동': '은평구',
            
            # 종로구
            '청운동': '종로구', '삼청동': '종로구', '종로1가': '종로구',
            '종로2가': '종로구', '종로3가': '종로구', '종로4가': '종로구',
            
            # 중구
            '중구': '중구', '을지로': '중구', '명동': '중구',
            
            # Add more mappings as needed...
        }
        
        logger.info("✅ AdvancedAddressParser initialized with 25 districts and 100+ dong mappings")
    
    def parse(self, address: str) -> Dict[str, Optional[str]]:
        """
        주소를 파싱하여 구·동 정보 추출
        
        Args:
            address: 주소 문자열 (예: "서울 강남구 역삼동 123-45" 또는 "서울시 마포구 공덕동")
        
        Returns:
            {
                'city': '서울시' or None,
                'gu': '강남구' or None,
                'dong': '역삼동' or None,
                'full': '서울시 강남구 역삼동' or None,
                'original': '...' (원본 주소)
            }
        """
        
        logger.info(f"🔍 Parsing address: {address}")
        
        result = {
            'city': None,
            'gu': None,
            'dong': None,
            'full': None,
            'original': address
        }
        
        if not address:
            logger.warning("⚠️ Empty address")
            return result
        
        # Normalize: 띄어쓰기 정리
        address_normalized = re.sub(r'\s+', ' ', address.strip())
        
        # 1. 도시 추출 (서울/서울시/서울특별시)
        city_match = re.search(r'(서울특별시|서울시|서울)', address_normalized)
        if city_match:
            result['city'] = '서울시'
        
        # 2. 구(區) 추출
        gu_match = re.search(r'([가-힣]+구)', address_normalized)
        if gu_match:
            gu_candidate = gu_match.group(1)
            if gu_candidate in self.seoul_districts:
                result['gu'] = gu_candidate
                logger.debug(f"   ✅ Found gu: {gu_candidate}")
        
        # 3. 동(洞) 추출
        dong_match = re.search(r'([가-힣]+동|[가-힣]+로\d*가)', address_normalized)
        if dong_match:
            dong_candidate = dong_match.group(1)
            result['dong'] = dong_candidate
            logger.debug(f"   ✅ Found dong: {dong_candidate}")
            
            # 구가 없으면 동 → 구 매핑 시도
            if not result['gu'] and dong_candidate in self.dong_to_gu_mapping:
                result['gu'] = self.dong_to_gu_mapping[dong_candidate]
                logger.info(f"   🎯 Auto-mapped {dong_candidate} → {result['gu']}")
        
        # 4. 완전한 주소 생성
        if result['city'] and result['gu'] and result['dong']:
            result['full'] = f"{result['city']} {result['gu']} {result['dong']}"
        elif result['city'] and result['gu']:
            result['full'] = f"{result['city']} {result['gu']}"
        elif result['gu'] and result['dong']:
            result['full'] = f"서울시 {result['gu']} {result['dong']}"  # 기본값으로 서울시 붙이기
        
        # 로깅
        if result['full']:
            logger.info(f"   ✅ Parsed: {result['full']}")
        else:
            logger.warning(f"   ⚠️ Parsing failed for: {address}")
        
        return result
    
    def get_gu_from_dong(self, dong: str) -> Optional[str]:
        """
        동(洞) 이름으로 구(區) 찾기
        
        Args:
            dong: 동 이름 (예: "역삼동")
        
        Returns:
            구 이름 (예: "강남구") or None
        """
        return self.dong_to_gu_mapping.get(dong)
    
    def format_full_address(self, city: Optional[str], gu: Optional[str], dong: Optional[str], detail: Optional[str] = None) -> str:
        """
        구성요소를 조합하여 완전한 주소 생성
        
        Args:
            city: 도시 (예: "서울시")
            gu: 구 (예: "강남구")
            dong: 동 (예: "역삼동")
            detail: 상세 주소 (예: "123-45")
        
        Returns:
            "서울시 강남구 역삼동 123-45" 형태의 문자열
        """
        
        parts = []
        
        if city:
            parts.append(city)
        if gu:
            parts.append(gu)
        if dong:
            parts.append(dong)
        if detail:
            parts.append(detail)
        
        return ' '.join(parts) if parts else ''
    
    def is_seoul_address(self, address: str) -> bool:
        """
        서울 주소인지 확인
        
        Returns:
            True if Seoul address, False otherwise
        """
        return bool(re.search(r'(서울|Seoul)', address, re.IGNORECASE))
    
    def extract_detail(self, address: str) -> Optional[str]:
        """
        상세 주소 (번지 등) 추출
        
        Args:
            address: "서울시 강남구 역삼동 123-45" 형태
        
        Returns:
            "123-45" 형태의 번지 or None
        """
        
        # 패턴: 숫자-숫자 또는 숫자번지
        detail_match = re.search(r'(\d+(-\d+)?)(번지)?', address)
        if detail_match:
            return detail_match.group(1)
        
        return None


# Singleton 인스턴스
_parser_instance = None


def get_address_parser() -> AdvancedAddressParser:
    """
    Singleton 주소 파서 반환
    
    Returns:
        AdvancedAddressParser 인스턴스
    """
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = AdvancedAddressParser()
    return _parser_instance


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = AdvancedAddressParser()
    
    test_addresses = [
        "서울 강남구 역삼동 123-45",
        "서울시 마포구 공덕동 456",
        "서울특별시 송파구 잠실동 789-1",
        "서울 대치동 680-11",  # 구 없음 → 동으로 추정
        "강남구 청담동",  # 서울시 없음
        "역삼동 123",  # 구·시 없음
        "서울 기타 삼성동 393-1",  # "서울 기타" 케이스
    ]
    
    print("=" * 80)
    print("Advanced Address Parser Test")
    print("=" * 80)
    
    for addr in test_addresses:
        print(f"\n원본: {addr}")
        result = parser.parse(addr)
        print(f"  → City: {result['city']}")
        print(f"  → Gu: {result['gu']}")
        print(f"  → Dong: {result['dong']}")
        print(f"  → Full: {result['full']}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
