"""
ZeroSite v36.0 NATIONWIDE - Enhanced Address Parser
전국 17개 광역시·도 주소 파싱 지원

Author: Antenna Holdings Development Team
Date: 2025-12-13
Purpose: Support ALL nationwide addresses (not just Seoul)
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AdvancedAddressParserV36:
    """
    전국 주소 파싱 클래스 (v36.0)
    
    목표: 서울뿐만 아니라 전국 17개 광역시·도 모두 지원
    """
    
    def __init__(self):
        """초기화"""
        
        # 17개 광역시·도
        self.provinces = {
            "서울특별시", "서울시", "서울",
            "부산광역시", "부산시", "부산",
            "인천광역시", "인천시", "인천",
            "대구광역시", "대구시", "대구",
            "광주광역시", "광주시", "광주",
            "대전광역시", "대전시", "대전",
            "울산광역시", "울산시", "울산",
            "세종특별자치시", "세종시", "세종",
            "경기도", "경기",
            "강원특별자치도", "강원도", "강원",
            "충청북도", "충북",
            "충청남도", "충남",
            "전북특별자치도", "전라북도", "전북",
            "전라남도", "전남",
            "경상북도", "경북",
            "경상남도", "경남",
            "제주특별자치도", "제주도", "제주"
        }
        
        # 정규화된 광역시·도 이름
        self.province_mapping = {
            "서울특별시": "서울특별시", "서울시": "서울특별시", "서울": "서울특별시",
            "부산광역시": "부산광역시", "부산시": "부산광역시", "부산": "부산광역시",
            "인천광역시": "인천광역시", "인천시": "인천광역시", "인천": "인천광역시",
            "대구광역시": "대구광역시", "대구시": "대구광역시", "대구": "대구광역시",
            "광주광역시": "광주광역시", "광주시": "광주광역시", "광주": "광주광역시",
            "대전광역시": "대전광역시", "대전시": "대전광역시", "대전": "대전광역시",
            "울산광역시": "울산광역시", "울산시": "울산광역시", "울산": "울산광역시",
            "세종특별자치시": "세종특별자치시", "세종시": "세종특별자치시", "세종": "세종특별자치시",
            "경기도": "경기도", "경기": "경기도",
            "강원특별자치도": "강원특별자치도", "강원도": "강원특별자치도", "강원": "강원특별자치도",
            "충청북도": "충청북도", "충북": "충청북도",
            "충청남도": "충청남도", "충남": "충청남도",
            "전북특별자치도": "전북특별자치도", "전라북도": "전북특별자치도", "전북": "전북특별자치도",
            "전라남도": "전라남도", "전남": "전라남도",
            "경상북도": "경상북도", "경북": "경상북도",
            "경상남도": "경상남도", "경남": "경상남도",
            "제주특별자치도": "제주특별자치도", "제주도": "제주특별자치도", "제주": "제주특별자치도"
        }
        
        logger.info("✅ AdvancedAddressParserV36 initialized with nationwide support (17 provinces)")
    
    def parse(self, address: str) -> Dict[str, Optional[str]]:
        """
        전국 주소 파싱
        
        Args:
            address: 주소 문자열
                예: "서울 강남구 역삼동 123-45"
                예: "부산 해운대구 우동 456"
                예: "경기도 성남시 분당구 정자동"
        
        Returns:
            {
                'sido': '서울특별시',  # 정규화된 시·도
                'sigungu': '강남구',  # 시·군·구
                'dong': '역삼동',     # 읍·면·동
                'detail': '123-45',   # 번지
                'full': '서울특별시 강남구 역삼동',
                'original': '...'
            }
        """
        
        logger.info(f"🔍 [v36] Parsing address: {address}")
        
        result = {
            'sido': None,
            'sigungu': None,
            'dong': None,
            'detail': None,
            'full': None,
            'original': address
        }
        
        if not address:
            logger.warning("⚠️ Empty address")
            return result
        
        # Normalize: 띄어쓰기 정리
        address_normalized = re.sub(r'\s+', ' ', address.strip())
        
        # 1. 시·도 추출
        sido_pattern = r'(서울특별시|서울시|서울|부산광역시|부산시|부산|인천광역시|인천시|인천|대구광역시|대구시|대구|광주광역시|광주시|광주|대전광역시|대전시|대전|울산광역시|울산시|울산|세종특별자치시|세종시|세종|경기도|경기|강원특별자치도|강원도|강원|충청북도|충북|충청남도|충남|전북특별자치도|전라북도|전북|전라남도|전남|경상북도|경북|경상남도|경남|제주특별자치도|제주도|제주)'
        sido_match = re.search(sido_pattern, address_normalized)
        if sido_match:
            sido_raw = sido_match.group(1)
            result['sido'] = self.province_mapping.get(sido_raw, sido_raw)
            logger.debug(f"   ✅ Found sido: {result['sido']}")
        
        # 2. 시·군·구 추출
        # 패턴: XXX시, XXX구, XXX군
        sigungu_pattern = r'([가-힣]+(?:시|구|군))'
        sigungu_matches = re.findall(sigungu_pattern, address_normalized)
        
        if sigungu_matches:
            # 첫 번째가 sido가 아닌 것을 sigungu로
            for match in sigungu_matches:
                if match not in self.provinces and match not in self.province_mapping:
                    result['sigungu'] = match
                    logger.debug(f"   ✅ Found sigungu: {match}")
                    break
        
        # 3. 읍·면·동 추출
        dong_pattern = r'([가-힣]+(?:읍|면|동|리|가))'
        dong_matches = re.findall(dong_pattern, address_normalized)
        
        if dong_matches:
            # 마지막 읍/면/동/리/가를 dong으로
            for match in reversed(dong_matches):
                # sigungu가 아닌 것을 dong으로
                if match != result['sigungu']:
                    result['dong'] = match
                    logger.debug(f"   ✅ Found dong: {match}")
                    break
        
        # 4. 번지 추출
        detail_match = re.search(r'(\d+(?:-\d+)?)(번지)?', address_normalized)
        if detail_match:
            result['detail'] = detail_match.group(1)
            logger.debug(f"   ✅ Found detail: {result['detail']}")
        
        # 5. 완전한 주소 생성
        parts = []
        if result['sido']:
            parts.append(result['sido'])
        if result['sigungu']:
            parts.append(result['sigungu'])
        if result['dong']:
            parts.append(result['dong'])
        
        result['full'] = ' '.join(parts) if parts else None
        
        # 로깅
        if result['full']:
            logger.info(f"   ✅ [v36] Parsed: {result['full']}")
        else:
            logger.warning(f"   ⚠️ [v36] Parsing failed for: {address}")
        
        return result
    
    def format_full_address(
        self,
        sido: Optional[str],
        sigungu: Optional[str],
        dong: Optional[str],
        detail: Optional[str] = None
    ) -> str:
        """
        구성요소를 조합하여 완전한 주소 생성
        """
        parts = []
        if sido:
            parts.append(sido)
        if sigungu:
            parts.append(sigungu)
        if dong:
            parts.append(dong)
        if detail:
            parts.append(detail)
        
        return ' '.join(parts) if parts else ''


# Singleton 인스턴스
_parser_instance = None


def get_address_parser_v36() -> AdvancedAddressParserV36:
    """
    Singleton 주소 파서 반환 (v36.0)
    """
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = AdvancedAddressParserV36()
    return _parser_instance


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = AdvancedAddressParserV36()
    
    test_addresses = [
        "서울특별시 강남구 역삼동 123-45",
        "부산광역시 해운대구 우동 456",
        "경기도 성남시 분당구 정자동 789",
        "강원특별자치도 춘천시 석사동 100",
        "제주특별자치도 제주시 연동 200",
        "대구 수성구 범어동",
        "광주 서구 치평동",
        "전북 전주시 완산구 서노송동",
        "충남 천안시 동남구 신부동",
        "경남 창원시 성산구 상남동",
    ]
    
    print("=" * 80)
    print("ZeroSite v36.0 NATIONWIDE - Address Parser Test")
    print("=" * 80)
    
    for addr in test_addresses:
        print(f"\n원본: {addr}")
        result = parser.parse(addr)
        print(f"  → Sido: {result['sido']}")
        print(f"  → Sigungu: {result['sigungu']}")
        print(f"  → Dong: {result['dong']}")
        print(f"  → Detail: {result['detail']}")
        print(f"  → Full: {result['full']}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
