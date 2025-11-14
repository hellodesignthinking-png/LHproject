"""
정책 문서 파서
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PolicyParser:
    """정책 문서 파싱 클래스"""
    
    # 주요 정책 패턴
    PATTERNS = {
        "건축비": r"건축비[:\s]*([0-9,]+)\s*원",
        "매입단가": r"매입단가[:\s]*([0-9,]+)\s*원",
        "세대수": r"([0-9]+)\s*세대",
        "기간": r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*[~-]\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",
        "지역": r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[특별|광역]*[시도]",
    }
    
    def __init__(self):
        self.compiled_patterns = {
            key: re.compile(pattern) for key, pattern in self.PATTERNS.items()
        }
    
    def parse_document(self, text: str) -> Dict:
        """문서 파싱"""
        result = {
            "원문": text,
            "추출정보": {},
            "파싱시간": datetime.now()
        }
        
        # 각 패턴 매칭
        for key, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                result["추출정보"][key] = matches
        
        logger.info(f"문서 파싱 완료: {len(result['추출정보'])}개 항목 추출")
        return result
    
    def extract_numbers(self, text: str) -> List[int]:
        """숫자 추출 (금액, 세대수 등)"""
        # 쉼표가 포함된 숫자 패턴
        pattern = r'[0-9,]+'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                # 쉼표 제거 후 정수 변환
                num = int(match.replace(',', ''))
                numbers.append(num)
            except ValueError:
                continue
        
        return numbers
    
    def extract_dates(self, text: str) -> List[str]:
        """날짜 추출"""
        # 다양한 날짜 형식 지원
        date_patterns = [
            r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',  # 2024-01-01, 2024/01/01, 2024.01.01
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',  # 2024년 1월 1일
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    def extract_regions(self, text: str) -> List[str]:
        """지역 추출"""
        if "지역" in self.compiled_patterns:
            matches = self.compiled_patterns["지역"].findall(text)
            return list(set(matches))  # 중복 제거
        return []
    
    def parse_construction_cost(self, text: str) -> Optional[Dict]:
        """건축비 정보 파싱"""
        result = {
            "기본건축비": None,
            "평당건축비": None,
            "특별가산": None,
            "총금액": None
        }
        
        # 건축비 관련 숫자 추출
        numbers = self.extract_numbers(text)
        
        if numbers:
            # 가장 큰 숫자를 총금액으로 가정
            result["총금액"] = max(numbers)
            
            # 평당 단가 추정 (500만원 이하)
            평당_candidates = [n for n in numbers if n <= 5000000]
            if 평당_candidates:
                result["평당건축비"] = max(평당_candidates)
        
        logger.info(f"건축비 파싱: {result}")
        return result if any(result.values()) else None
    
    def parse_purchase_criteria(self, text: str) -> Optional[Dict]:
        """매입기준 파싱"""
        result = {
            "매입단가": None,
            "세대수범위": None,
            "평형대": None,
            "지역": None
        }
        
        # 매입단가 추출
        if "매입단가" in self.compiled_patterns:
            매입단가_match = self.compiled_patterns["매입단가"].search(text)
            if 매입단가_match:
                result["매입단가"] = 매입단가_match.group(1).replace(',', '')
        
        # 세대수 추출
        if "세대수" in self.compiled_patterns:
            세대수_matches = self.compiled_patterns["세대수"].findall(text)
            if 세대수_matches:
                result["세대수범위"] = 세대수_matches
        
        # 지역 추출
        regions = self.extract_regions(text)
        if regions:
            result["지역"] = regions
        
        logger.info(f"매입기준 파싱: {result}")
        return result if any(result.values()) else None
    
    def extract_key_changes(self, text: str) -> List[str]:
        """주요 변경사항 추출"""
        changes = []
        
        # 변경 관련 키워드
        change_keywords = ["변경", "개정", "신설", "폐지", "조정", "확대", "축소"]
        
        # 문장 분리
        sentences = re.split(r'[.!?]\s*', text)
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in change_keywords):
                changes.append(sentence.strip())
        
        logger.info(f"주요 변경사항 {len(changes)}건 추출")
        return changes
    
    def summarize_policy(self, text: str, max_length: int = 200) -> str:
        """정책 요약"""
        # 간단한 요약: 첫 문장 + 핵심 문장
        sentences = re.split(r'[.!?]\s*', text)
        
        if not sentences:
            return text[:max_length]
        
        # 첫 문장
        summary = sentences[0]
        
        # 중요 키워드가 포함된 문장 추가
        important_keywords = ["변경", "신설", "확대", "주요", "중요"]
        for sentence in sentences[1:]:
            if any(keyword in sentence for keyword in important_keywords):
                summary += ". " + sentence
                break
        
        # 길이 제한
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary


# 테스트용
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 문서
    test_text = """
    2024년 신축매입임대주택 사업 건축비 기준 변경 안내
    
    2024년 1월 1일부터 신축매입임대주택의 건축비 기준이 다음과 같이 변경됩니다.
    
    1. 건축비: 평당 5,500,000원 (기존 5,200,000원에서 300,000원 상향)
    2. 매입단가: 세대당 250,000,000원
    3. 대상지역: 서울특별시, 경기도 일부 지역
    4. 세대수: 10세대 이상 50세대 이하
    5. 시행기간: 2024.01.01 ~ 2024.12.31
    
    주요 변경사항:
    - 건축비 평당 단가 5.8% 상향 조정
    - 친환경 자재 사용 시 추가 가산금 지급
    - 에너지 효율 등급 의무화
    """
    
    parser = PolicyParser()
    
    # 전체 파싱
    result = parser.parse_document(test_text)
    print("\n=== 문서 파싱 결과 ===")
    for key, value in result["추출정보"].items():
        print(f"{key}: {value}")
    
    # 건축비 파싱
    print("\n=== 건축비 파싱 ===")
    construction = parser.parse_construction_cost(test_text)
    for key, value in construction.items():
        print(f"{key}: {value}")
    
    # 매입기준 파싱
    print("\n=== 매입기준 파싱 ===")
    purchase = parser.parse_purchase_criteria(test_text)
    for key, value in purchase.items():
        print(f"{key}: {value}")
    
    # 주요 변경사항
    print("\n=== 주요 변경사항 ===")
    changes = parser.extract_key_changes(test_text)
    for i, change in enumerate(changes, 1):
        print(f"{i}. {change}")
    
    # 요약
    print("\n=== 요약 ===")
    summary = parser.summarize_policy(test_text)
    print(summary)
