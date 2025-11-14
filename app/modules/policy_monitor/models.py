"""
정책 모니터링 데이터 모델
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PolicySource(BaseModel):
    """정책 출처"""
    name: str = Field(..., description="출처 이름 (LH, 국토부 등)")
    url: str = Field(..., description="출처 URL")
    
    
class PolicyCategory(BaseModel):
    """정책 카테고리"""
    main: str = Field(..., description="주 카테고리 (매입임대, 건축비, 감정평가 등)")
    sub: Optional[str] = Field(None, description="세부 카테고리")


class PolicyUpdate(BaseModel):
    """정책 업데이트 정보"""
    id: Optional[str] = Field(None, description="정책 ID")
    source: PolicySource = Field(..., description="출처")
    category: PolicyCategory = Field(..., description="카테고리")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    url: str = Field(..., description="상세 URL")
    published_at: datetime = Field(..., description="발행일시")
    collected_at: datetime = Field(default_factory=datetime.now, description="수집일시")
    importance: str = Field(default="medium", description="중요도 (low/medium/high)")
    keywords: List[str] = Field(default_factory=list, description="키워드")
    

class PolicyChange(BaseModel):
    """정책 변화 분석"""
    policy_id: str = Field(..., description="정책 ID")
    change_type: str = Field(..., description="변화 유형 (신규/개정/폐지)")
    old_value: Optional[str] = Field(None, description="이전 값")
    new_value: Optional[str] = Field(None, description="변경 값")
    impact_level: str = Field(..., description="영향도 (low/medium/high)")
    description: str = Field(..., description="변화 설명")
    detected_at: datetime = Field(default_factory=datetime.now, description="감지일시")


class PolicyAlert(BaseModel):
    """정책 알림"""
    alert_id: str = Field(..., description="알림 ID")
    policy_update: PolicyUpdate = Field(..., description="정책 업데이트 정보")
    alert_type: str = Field(..., description="알림 유형 (신규공고/제도변경/긴급)")
    recipients: List[str] = Field(..., description="수신자 목록")
    sent_at: datetime = Field(default_factory=datetime.now, description="발송일시")
    

class PolicyReport(BaseModel):
    """정책 리포트"""
    report_id: str = Field(..., description="리포트 ID")
    period_start: datetime = Field(..., description="기간 시작")
    period_end: datetime = Field(..., description="기간 종료")
    total_updates: int = Field(..., description="총 업데이트 수")
    important_changes: List[PolicyChange] = Field(..., description="주요 변화")
    summary: str = Field(..., description="요약")
    recommendations: List[str] = Field(..., description="권장사항")
    created_at: datetime = Field(default_factory=datetime.now, description="생성일시")


class CrawlerConfig(BaseModel):
    """크롤러 설정"""
    enabled: bool = Field(default=True, description="활성화 여부")
    schedule: str = Field(default="0 9 * * *", description="스케줄 (cron 표현식)")
    target_urls: List[str] = Field(..., description="대상 URL 목록")
    keywords: List[str] = Field(..., description="모니터링 키워드")
    max_pages: int = Field(default=5, description="최대 페이지 수")
    timeout: int = Field(default=30, description="타임아웃 (초)")
