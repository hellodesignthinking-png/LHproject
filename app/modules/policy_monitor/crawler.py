"""
LH 및 국토교통부 웹사이트 크롤러
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from datetime import datetime
import logging
from .models import PolicyUpdate, PolicySource, PolicyCategory

logger = logging.getLogger(__name__)


class BaseCrawler:
    """기본 크롤러 클래스"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """HTML 페이지 가져오기"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """HTML 파싱"""
        return BeautifulSoup(html, 'html.parser')


class LHCrawler(BaseCrawler):
    """LH 공사 홈페이지 크롤러"""
    
    BASE_URL = "https://www.lh.or.kr"
    NOTICE_URL = f"{BASE_URL}/portal/contents.do?menuNo=200093"  # LH 공지사항
    BIDDING_URL = f"{BASE_URL}/portal/contents.do?menuNo=200094"  # 입찰정보
    
    KEYWORDS = [
        "신축매입임대",
        "매입임대주택",
        "공공임대",
        "건축비",
        "감정평가",
        "사전약정",
        "준공검사",
        "매입단가"
    ]
    
    async def crawl_notices(self, max_pages: int = 5) -> List[PolicyUpdate]:
        """공지사항 크롤링"""
        logger.info("LH 공지사항 크롤링 시작")
        updates = []
        
        try:
            # 데모 데이터 (실제로는 웹페이지 파싱)
            demo_updates = [
                {
                    "title": "[중요] 2024년 신축매입임대 사업 기준 개정 안내",
                    "content": "2024년 신축매입임대주택 사업의 건축비 기준 및 매입단가가 조정되었습니다.",
                    "url": f"{self.BASE_URL}/notice/12345",
                    "published_at": datetime.now(),
                    "category": "매입임대",
                    "importance": "high"
                },
                {
                    "title": "서울·경기 신축매입임대 입찰 공고",
                    "content": "서울특별시 및 경기도 지역 신축매입임대주택 입찰을 공고합니다.",
                    "url": f"{self.BASE_URL}/notice/12346",
                    "published_at": datetime.now(),
                    "category": "입찰공고",
                    "importance": "medium"
                },
                {
                    "title": "감정평가 기준 변경 사전 안내",
                    "content": "2024년 2분기부터 감정평가 기준이 일부 변경됩니다.",
                    "url": f"{self.BASE_URL}/notice/12347",
                    "published_at": datetime.now(),
                    "category": "감정평가",
                    "importance": "high"
                }
            ]
            
            # PolicyUpdate 객체로 변환
            for item in demo_updates:
                update = PolicyUpdate(
                    source=PolicySource(name="LH 공사", url=self.BASE_URL),
                    category=PolicyCategory(main=item["category"]),
                    title=item["title"],
                    content=item["content"],
                    url=item["url"],
                    published_at=item["published_at"],
                    importance=item["importance"],
                    keywords=self._extract_keywords(item["title"] + " " + item["content"])
                )
                updates.append(update)
            
            logger.info(f"LH 공지사항 {len(updates)}건 수집 완료")
            
        except Exception as e:
            logger.error(f"LH 공지사항 크롤링 오류: {str(e)}")
        
        return updates
    
    async def crawl_bidding(self, max_pages: int = 5) -> List[PolicyUpdate]:
        """입찰정보 크롤링"""
        logger.info("LH 입찰정보 크롤링 시작")
        updates = []
        
        try:
            # 데모 데이터
            demo_updates = [
                {
                    "title": "서울 강남구 역삼동 신축매입임대 입찰",
                    "content": "대지면적 500㎡, 청년형/신혼부부형 혼합",
                    "url": f"{self.BIDDING_URL}/bid/12345",
                    "published_at": datetime.now(),
                    "category": "입찰공고",
                    "importance": "medium"
                }
            ]
            
            for item in demo_updates:
                update = PolicyUpdate(
                    source=PolicySource(name="LH 입찰정보", url=self.BIDDING_URL),
                    category=PolicyCategory(main=item["category"]),
                    title=item["title"],
                    content=item["content"],
                    url=item["url"],
                    published_at=item["published_at"],
                    importance=item["importance"],
                    keywords=self._extract_keywords(item["title"] + " " + item["content"])
                )
                updates.append(update)
            
            logger.info(f"LH 입찰정보 {len(updates)}건 수집 완료")
            
        except Exception as e:
            logger.error(f"LH 입찰정보 크롤링 오류: {str(e)}")
        
        return updates
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        found_keywords = []
        for keyword in self.KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)
        return found_keywords
    
    async def crawl_all(self) -> List[PolicyUpdate]:
        """모든 데이터 크롤링"""
        logger.info("LH 전체 크롤링 시작")
        
        # 병렬 크롤링
        notices_task = self.crawl_notices()
        bidding_task = self.crawl_bidding()
        
        notices, bidding = await asyncio.gather(notices_task, bidding_task)
        
        all_updates = notices + bidding
        logger.info(f"LH 전체 {len(all_updates)}건 수집 완료")
        
        return all_updates


class MOLITCrawler(BaseCrawler):
    """국토교통부 홈페이지 크롤러"""
    
    BASE_URL = "https://www.molit.go.kr"
    NEWS_URL = f"{BASE_URL}/USR/NEWS/m_71/lst.jsp"  # 보도자료
    POLICY_URL = f"{BASE_URL}/USR/policyTarget/m_25652/dtl.jsp"  # 정책자료
    
    KEYWORDS = [
        "공공임대",
        "매입임대",
        "공공주택",
        "주택정책",
        "건축법",
        "주거복지"
    ]
    
    async def crawl_news(self, max_pages: int = 3) -> List[PolicyUpdate]:
        """보도자료 크롤링"""
        logger.info("국토부 보도자료 크롤링 시작")
        updates = []
        
        try:
            # 데모 데이터
            demo_updates = [
                {
                    "title": "2024년 공공임대주택 공급 확대 방안 발표",
                    "content": "정부는 2024년 공공임대주택 공급을 전년 대비 20% 확대하기로 했습니다.",
                    "url": f"{self.NEWS_URL}/news/12345",
                    "published_at": datetime.now(),
                    "category": "주택정책",
                    "importance": "high"
                },
                {
                    "title": "신축매입임대 제도 개선 추진",
                    "content": "신축매입임대주택의 건축비 연동 방식이 개선됩니다.",
                    "url": f"{self.NEWS_URL}/news/12346",
                    "published_at": datetime.now(),
                    "category": "매입임대",
                    "importance": "high"
                }
            ]
            
            for item in demo_updates:
                update = PolicyUpdate(
                    source=PolicySource(name="국토교통부", url=self.BASE_URL),
                    category=PolicyCategory(main=item["category"]),
                    title=item["title"],
                    content=item["content"],
                    url=item["url"],
                    published_at=item["published_at"],
                    importance=item["importance"],
                    keywords=self._extract_keywords(item["title"] + " " + item["content"])
                )
                updates.append(update)
            
            logger.info(f"국토부 보도자료 {len(updates)}건 수집 완료")
            
        except Exception as e:
            logger.error(f"국토부 보도자료 크롤링 오류: {str(e)}")
        
        return updates
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        found_keywords = []
        for keyword in self.KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)
        return found_keywords
    
    async def crawl_all(self) -> List[PolicyUpdate]:
        """모든 데이터 크롤링"""
        logger.info("국토부 전체 크롤링 시작")
        news = await self.crawl_news()
        logger.info(f"국토부 전체 {len(news)}건 수집 완료")
        return news


async def run_all_crawlers() -> List[PolicyUpdate]:
    """모든 크롤러 실행"""
    logger.info("전체 크롤링 시작")
    
    async with LHCrawler() as lh_crawler:
        lh_updates = await lh_crawler.crawl_all()
    
    async with MOLITCrawler() as molit_crawler:
        molit_updates = await molit_crawler.crawl_all()
    
    all_updates = lh_updates + molit_updates
    
    logger.info(f"전체 크롤링 완료: 총 {len(all_updates)}건")
    
    return all_updates


# 테스트용
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        updates = await run_all_crawlers()
        for update in updates:
            print(f"\n제목: {update.title}")
            print(f"출처: {update.source.name}")
            print(f"카테고리: {update.category.main}")
            print(f"중요도: {update.importance}")
            print(f"키워드: {', '.join(update.keywords)}")
    
    asyncio.run(test())
