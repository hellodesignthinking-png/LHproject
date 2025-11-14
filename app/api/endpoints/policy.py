"""
정책 모니터링 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.modules.policy_monitor.models import (
    PolicyUpdate,
    PolicyChange,
    PolicyReport,
    PolicySource,
    PolicyCategory
)
from app.modules.policy_monitor.analyzer import PolicyAnalyzer
from app.services.policy_ai_service import get_policy_ai_service

router = APIRouter(prefix="/api/policy", tags=["policy-monitoring"])

# 정책 분석기 인스턴스 (메모리 캐시용)
policy_analyzer = PolicyAnalyzer()


class PolicyMonitorRequest(BaseModel):
    """정책 모니터링 요청"""
    category: str = Field(..., description="모니터링 카테고리 (LH공고/정책변경/건축제도)")
    keywords: List[str] = Field(default_factory=list, description="검색 키워드")
    days: int = Field(default=30, description="조회 기간 (일)")


class PolicyComparisonRequest(BaseModel):
    """정책 비교 요청"""
    policy_id_1: str = Field(..., description="첫 번째 정책 ID")
    policy_id_2: str = Field(..., description="두 번째 정책 ID")


@router.get("/")
async def policy_monitor_home():
    """정책 모니터링 API 정보"""
    return {
        "message": "정책 모니터링 API",
        "version": "1.0.0",
        "endpoints": {
            "LH 공고 모니터링": "GET /api/policy/lh-announcements",
            "정책 변경 모니터링": "GET /api/policy/policy-changes",
            "건축/제도 변경 모니터링": "GET /api/policy/building-regulations",
            "정책 리포트 생성": "POST /api/policy/generate-report",
            "정책 비교": "POST /api/policy/compare"
        }
    }


@router.get("/lh-announcements")
async def get_lh_announcements(days: int = 30, keywords: Optional[str] = None):
    """
    LH 사업공고 모니터링
    
    최근 LH 공고의 변경사항을 모니터링합니다.
    - 입주자격 변경
    - 사업유형별 타겟 변경 (예: 행복주택)
    - 월별 비교 분석
    """
    
    # 샘플 데이터 (실제로는 크롤러에서 수집)
    sample_announcements = [
        {
            "id": "lh_2024_001",
            "source": {
                "name": "LH 한국토지주택공사",
                "url": "https://www.lh.or.kr"
            },
            "category": {
                "main": "매입임대",
                "sub": "신축매입임대"
            },
            "title": "2024년 1분기 신축매입임대 사업 공고",
            "content": """
[변경사항]
1. 입주자격 변경
   - 기존: 무주택 세대구성원, 소득기준 70% 이하
   - 변경: 무주택 세대구성원, 소득기준 80% 이하 (완화)
   
2. 청년형 주택 공급 확대
   - 기존: 전체 물량의 30%
   - 변경: 전체 물량의 40%
   
3. 사전약정 기간 단축
   - 기존: 준공 3개월 전
   - 변경: 준공 6개월 전 (매입심사 기간 확대)

4. 건축비 상한액 조정
   - 서울: ㎡당 350만원 → 380만원 (8.6% 인상)
   - 경기: ㎡당 320만원 → 340만원 (6.3% 인상)
            """,
            "url": "https://www.lh.or.kr/notice/2024/001",
            "published_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "importance": "high",
            "keywords": ["신축매입임대", "입주자격", "청년형", "건축비"],
            "changes": [
                {
                    "field": "입주자격_소득기준",
                    "old_value": "70% 이하",
                    "new_value": "80% 이하",
                    "impact": "high",
                    "description": "소득기준 완화로 대상자 확대"
                },
                {
                    "field": "청년형_공급비율",
                    "old_value": "30%",
                    "new_value": "40%",
                    "impact": "high",
                    "description": "청년형 주택 공급 확대"
                },
                {
                    "field": "건축비_서울",
                    "old_value": "350만원/㎡",
                    "new_value": "380만원/㎡",
                    "impact": "high",
                    "description": "건축비 상한 8.6% 인상"
                }
            ]
        },
        {
            "id": "lh_2024_002",
            "source": {
                "name": "LH 한국토지주택공사",
                "url": "https://www.lh.or.kr"
            },
            "category": {
                "main": "매입임대",
                "sub": "행복주택"
            },
            "title": "행복주택 매입임대 시범사업 공고",
            "content": """
[신규 사업]
행복주택 유형의 신축매입임대 시범사업을 진행합니다.

1. 사업 개요
   - 대상: 대학생, 사회초년생, 신혼부부
   - 위치: 대중교통 접근성 우수 지역
   - 규모: 500세대 (시범)

2. 특별 지원
   - 공용시설 설치비 지원 (커뮤니티센터, 피트니스 등)
   - 스마트홈 설비 필수 (IoT 기반)
   - 제로에너지 건물 인증 시 가점 부여

3. 매입 조건
   - 기본 매입가 + 특별설비 가산금 (최대 10%)
   - 20년 장기 임대 보장
            """,
            "url": "https://www.lh.or.kr/notice/2024/002",
            "published_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "importance": "high",
            "keywords": ["행복주택", "시범사업", "스마트홈", "제로에너지"],
            "changes": []
        }
    ]
    
    # 키워드 필터링
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',')]
        filtered = []
        for ann in sample_announcements:
            if any(kw in ann['title'] or kw in ann['content'] for kw in keyword_list):
                filtered.append(ann)
        sample_announcements = filtered
    
    return {
        "success": True,
        "category": "LH 사업공고",
        "period": f"최근 {days}일",
        "total_count": len(sample_announcements),
        "data": sample_announcements,
        "summary": {
            "new_announcements": 2,
            "revised_announcements": 1,
            "high_importance": 2,
            "key_changes": [
                "입주자격 소득기준 완화 (70% → 80%)",
                "청년형 주택 공급비율 확대 (30% → 40%)",
                "건축비 상한액 인상 (서울 8.6%, 경기 6.3%)",
                "행복주택 신축매입임대 시범사업 신규 공고"
            ]
        }
    }


@router.get("/policy-changes")
async def get_policy_changes(days: int = 30, keywords: Optional[str] = None):
    """
    정책 변경 모니터링
    
    국토교통부 및 관련 부처의 정책 변화를 모니터링합니다.
    - 부동산 규제 변화
    - ESG 경영 정책
    - 청년/신혼부부 주거지원 정책
    """
    
    sample_policy_changes = [
        {
            "id": "molit_2024_001",
            "source": {
                "name": "국토교통부",
                "url": "https://www.molit.go.kr"
            },
            "category": {
                "main": "주거정책",
                "sub": "임대주택"
            },
            "title": "임대주택 등록 활성화 방안",
            "content": """
[정책 변경]
임대주택 등록을 활성화하기 위한 세제 혜택 및 규제 완화 방안

1. 세제 혜택 확대
   - 기존: 종합부동산세 합산 배제
   - 변경: + 양도소득세 장기보유특별공제 추가 (최대 50%)
   
2. 임대료 인상률 개선
   - 기존: 연 5% 이내
   - 변경: 연 5% 또는 전년도 소비자물가상승률 중 높은 것 (단, 최대 7%)

3. 의무임대기간 조정
   - 기존: 10년
   - 변경: 8년 (단, 세제혜택은 10년 유지 시 전액)

4. LH 매입임대 연계
   - 민간 임대주택 → LH 매입 전환 시 우대 조건 적용
   - 우량 임대사업자 인증 시 매입가 가산 (최대 5%)
            """,
            "url": "https://www.molit.go.kr/policy/2024/001",
            "published_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "importance": "high",
            "keywords": ["임대주택", "세제혜택", "규제완화", "LH매입"],
            "impact_analysis": {
                "positive": [
                    "세제혜택 확대로 민간 투자 유인 증가",
                    "LH 매입 전환 우대로 출구전략 다양화",
                    "임대료 인상률 개선으로 수익성 향상"
                ],
                "negative": [
                    "의무임대기간 단축은 단기 매물 증가 우려",
                    "세제혜택 전액은 여전히 10년 유지 필요"
                ],
                "recommendations": [
                    "LH 매입 전환 우대조건 적극 활용 검토",
                    "우량 임대사업자 인증 취득 추진",
                    "10년 장기 보유 전략 수립 (세제혜택 최대화)"
                ]
            }
        },
        {
            "id": "molit_2024_002",
            "source": {
                "name": "국토교통부",
                "url": "https://www.molit.go.kr"
            },
            "category": {
                "main": "ESG정책",
                "sub": "녹색건축"
            },
            "title": "공공임대주택 ESG 경영 강화 방안",
            "content": """
[신규 정책]
공공임대주택 사업의 ESG 경영 강화 및 평가 기준 도입

1. 환경 (Environmental)
   - 2025년부터 모든 신축 공공임대주택 제로에너지 건축물 인증 의무화
   - 태양광 발전설비 설치 의무 (지붕면적의 30% 이상)
   - 친환경 자재 사용 비율 70% 이상

2. 사회 (Social)
   - 장애인 편의시설 설치 기준 강화
   - 커뮤니티 공간 의무 확보 (전용면적의 5% 이상)
   - 입주민 만족도 조사 연 2회 실시

3. 지배구조 (Governance)
   - 투명한 입찰 및 심사 기준 공개
   - 입주민 참여 운영위원회 구성

4. 인센티브
   - ESG 평가 우수등급(S등급 이상) 획득 시
   - LH 매입가 가산금 +3% 추가
   - 사업자 선정 시 가점 부여
            """,
            "url": "https://www.molit.go.kr/policy/2024/002",
            "published_at": (datetime.now() - timedelta(days=8)).isoformat(),
            "importance": "high",
            "keywords": ["ESG", "제로에너지", "친환경", "인센티브"],
            "impact_analysis": {
                "positive": [
                    "ESG 우수등급 획득 시 매입가 가산으로 수익성 증대",
                    "제로에너지 건축물 인증으로 장기 운영비 절감",
                    "사업자 선정 가점으로 경쟁력 확보"
                ],
                "negative": [
                    "초기 건축비 증가 (제로에너지 인증, 친환경 자재)",
                    "ESG 평가 및 인증 비용 추가 발생",
                    "커뮤니티 공간으로 인한 임대 가능 면적 감소"
                ],
                "recommendations": [
                    "제로에너지 건축물 설계 전문 컨설팅 필요",
                    "ESG 평가 S등급 달성을 위한 체크리스트 작성",
                    "친환경 자재 공급처 사전 확보 및 가격 협상",
                    "초기 투자비 증가분과 매입가 가산금 비교 분석 필수"
                ]
            }
        }
    ]
    
    # 키워드 필터링
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',')]
        filtered = []
        for policy in sample_policy_changes:
            if any(kw in policy['title'] or kw in policy['content'] for kw in keyword_list):
                filtered.append(policy)
        sample_policy_changes = filtered
    
    return {
        "success": True,
        "category": "정책 변경",
        "period": f"최근 {days}일",
        "total_count": len(sample_policy_changes),
        "data": sample_policy_changes,
        "summary": {
            "new_policies": 2,
            "revised_policies": 0,
            "high_importance": 2,
            "key_changes": [
                "임대주택 세제혜택 확대 (양도소득세 장기보유특별공제)",
                "임대료 인상률 개선 (최대 7%까지 허용)",
                "LH 매입 전환 우대조건 신설",
                "공공임대주택 ESG 경영 의무화 (2025년부터)",
                "제로에너지 건축물 인증 필수",
                "ESG S등급 획득 시 매입가 +3% 가산"
            ]
        }
    }


@router.get("/building-regulations")
async def get_building_regulations(days: int = 30, keywords: Optional[str] = None):
    """
    건축/제도 변경 모니터링
    
    건축법, 주택법 등 관련 법령 및 제도의 변화를 모니터링합니다.
    - 건축법/주택법 개정
    - 제로에너지 건축물 인증 기준
    - LH 설계기준 및 시방서
    - 중대재해처벌법 관련
    - 스마트홈 기술 및 건설 혁신
    """
    
    sample_regulations = [
        {
            "id": "law_2024_001",
            "source": {
                "name": "법제처",
                "url": "https://www.moleg.go.kr"
            },
            "category": {
                "main": "건축법령",
                "sub": "건축법 시행령"
            },
            "title": "건축법 시행령 개정 - 주택 건축 기준 완화",
            "content": """
[법령 개정]
주택 공급 활성화를 위한 건축 기준 일부 완화

1. 일조권 규제 완화
   - 기존: 인접 대지경계선으로부터 높이 9m 이내
   - 변경: 높이 10m 이내 (1m 완화)
   
2. 건폐율/용적률 완화 (정비구역 내)
   - 건폐율: 기존 60% → 65%
   - 용적률: 기존 200% → 250%
   
3. 층고 제한 완화
   - 기존: 주거용 층고 3.5m 이하
   - 변경: 4.0m 이하 (복층형 주택 허용 확대)

4. 주차장 설치기준 조정
   - 60㎡ 이하 소형주택: 세대당 0.7대 → 0.5대
   - 대중교통 인접 지역 추가 완화 가능

5. 시행일
   - 공포 후 6개월 (2024년 7월 1일 시행 예정)
            """,
            "url": "https://www.moleg.go.kr/law/2024/001",
            "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "importance": "high",
            "keywords": ["건축법", "규제완화", "건폐율", "용적률"],
            "impact_analysis": {
                "opportunities": [
                    "건폐율/용적률 완화로 동일 대지 내 세대수 증가 가능",
                    "층고 완화로 복층형 청년주택 설계 다양화",
                    "주차장 기준 완화로 건축비 절감 효과",
                    "세대수 증가 → LH 매입물량 증가 → 총 매출 증대"
                ],
                "considerations": [
                    "일조권 완화는 인접 주민 민원 가능성 고려 필요",
                    "주차장 완화는 해당 지역 대중교통 여건 확인 필수",
                    "기존 설계 변경 시 인허가 재검토 기간 소요"
                ],
                "action_items": [
                    "현재 진행 중인 프로젝트 설계 변경 검토 (용적률 활용)",
                    "신규 프로젝트 기획 시 완화 기준 반영",
                    "주차장 기준 완화 적용 가능 지역 리스트업",
                    "세대수 증가에 따른 ROI 재계산"
                ]
            }
        },
        {
            "id": "cert_2024_001",
            "source": {
                "name": "한국에너지공단",
                "url": "https://www.energy.or.kr"
            },
            "category": {
                "main": "인증기준",
                "sub": "제로에너지건축물"
            },
            "title": "제로에너지건축물 인증 기준 개정 (5차)",
            "content": """
[인증 기준 개정]
제로에너지건축물 인증 기준 5차 개정안 발표

1. 1차 에너지 소요량 기준 강화
   - 기존 ZEB 5등급: 140 kWh/㎡·년 이하
   - 변경 ZEB 5등급: 120 kWh/㎡·년 이하 (14% 강화)
   
2. 신재생에너지 생산비율 상향
   - ZEB 1등급(최우수): 기존 20% → 25%
   - ZEB 2등급: 기존 15% → 20%
   
3. BEMS(건물에너지관리시스템) 의무화 확대
   - 기존: 1,000㎡ 이상
   - 변경: 500㎡ 이상
   
4. 공동주택 특례 기준 신설
   - 공동주택은 기존 기준 대비 10% 완화 적용
   - 단, 세대별 계량시스템 필수 설치
   
5. 인증 인센티브 강화
   - ZEB 1등급: 용적률 +15% (기존 +12%)
   - ZEB 2-3등급: 용적률 +12% (기존 +10%)
   
6. 시행일
   - 2024년 7월 1일부터 신규 인증 신청분부터 적용
            """,
            "url": "https://www.energy.or.kr/cert/2024/001",
            "published_at": (datetime.now() - timedelta(days=7)).isoformat(),
            "importance": "high",
            "keywords": ["제로에너지", "인증기준", "BEMS", "용적률"],
            "impact_analysis": {
                "opportunities": [
                    "공동주택 특례로 주거용 프로젝트 인증 유리",
                    "인증 인센티브 강화로 용적률 추가 확보 (최대 15%)",
                    "ESG 정책과 연계하여 LH 매입가 가산 가능"
                ],
                "challenges": [
                    "에너지 기준 강화로 초기 설계비용 증가",
                    "BEMS 의무화로 설비투자 추가 필요",
                    "신재생에너지 비율 상향으로 태양광 설비 확대 필수"
                ],
                "cost_impact": {
                    "additional_cost_per_sqm": "약 8~12만원/㎡ 추가 예상",
                    "incentive_value": "용적률 15% 확보 시 세대수 증가로 상쇄 가능",
                    "payback_period": "약 3~5년 (에너지비용 절감 효과)"
                },
                "action_items": [
                    "제로에너지 전문 설계사무소와 협력 체계 구축",
                    "BEMS 시스템 공급업체 선정 및 견적 비교",
                    "태양광 패널 설치 최적화 방안 검토",
                    "인증 인센티브(용적률)를 반영한 ROI 재계산",
                    "LH ESG 가산금(+3%)과 제로에너지 인센티브 중복 적용 확인"
                ]
            }
        },
        {
            "id": "lh_standard_2024_001",
            "source": {
                "name": "LH 한국토지주택공사",
                "url": "https://www.lh.or.kr"
            },
            "category": {
                "main": "설계기준",
                "sub": "LH 시방서"
            },
            "title": "LH 공공주택 설계기준 개정 (2024년 상반기)",
            "content": """
[설계기준 개정]
LH 공공주택 설계기준 및 시방서 개정 사항

1. 마감재 기준 강화
   - 바닥재: 강마루(8T → 10T), 내구성 등급 상향
   - 벽지: 실크벽지 → 항균벽지 의무 적용
   - 주방: 엔지니어드스톤 상판 필수
   
2. 설비 기준 변경
   - 개별난방: 콘덴싱 보일러(에너지효율 1등급) 필수
   - 환기: 열회수형 환기장치(전열교환효율 70% 이상)
   - 급수: 세대별 IoT 계량기 설치
   
3. 방음/단열 기준 강화
   - 층간소음: 경량충격음 58dB → 55dB
   - 중량충격음: 50dB → 47dB
   - 외벽단열: 지역별 +20% 강화
   
4. 스마트홈 기준 신설
   - 세대별 홈네트워크 시스템 필수
   - IoT 연동 기능 (조명, 가스, 난방, 도어락)
   - 공용부 무인택배시스템 의무 설치
   
5. 안전 기준 추가
   - 발코니 안전난간 높이 120cm 이상
   - 미끄럼 방지 바닥재 적용 (화장실, 주방)
   - 소화기 비치 공간 확보

6. 예상 건축비 영향
   - 마감재 고급화: +약 50만원/㎡
   - 설비 강화: +약 30만원/㎡
   - 스마트홈: +약 20만원/㎡
   - 합계: +약 100만원/㎡ (기존 대비 약 15% 증가)
            """,
            "url": "https://www.lh.or.kr/standard/2024/001",
            "published_at": (datetime.now() - timedelta(days=15)).isoformat(),
            "importance": "high",
            "keywords": ["설계기준", "시방서", "마감재", "스마트홈"],
            "impact_analysis": {
                "cost_impact": {
                    "construction_cost_increase": "약 100만원/㎡ (15% 증가)",
                    "typical_project_example": "1,000㎡ 프로젝트 시 약 1억원 추가 비용",
                    "lh_purchase_price_reflection": "LH 매입가 산정 시 실비 반영 가능 여부 확인 필요"
                },
                "quality_impact": [
                    "입주민 만족도 상승 예상",
                    "하자 발생률 감소 기대",
                    "브랜드 가치 향상"
                ],
                "risks": [
                    "건축비 증가로 사업성 악화 가능",
                    "LH 매입가에 미반영 시 수익률 하락",
                    "공사기간 연장 가능성 (설비 복잡도 증가)"
                ],
                "action_items": [
                    "LH 담당자와 매입가 산정 시 신규 기준 반영 여부 협의",
                    "마감재 및 설비 자재 공급처 재검토 (대량구매 할인 협상)",
                    "스마트홈 통합 솔루션 업체 선정 (패키지 가격 확인)",
                    "신규 기준 반영한 건축비 재산정 및 ROI 재계산",
                    "기존 설계안 검토 및 변경 필요 부분 식별"
                ]
            }
        },
        {
            "id": "safety_2024_001",
            "source": {
                "name": "고용노동부",
                "url": "https://www.moel.go.kr"
            },
            "category": {
                "main": "안전규제",
                "sub": "중대재해처벌법"
            },
            "title": "중대재해처벌법 건설업 안전관리 가이드라인 개정",
            "content": """
[안전관리 가이드라인 개정]
중대재해처벌법 건설업 안전관리 강화

1. 안전관리 조직 의무화
   - 50억원 이상 공사: 안전관리자 1명 이상 상주
   - 안전보건총괄책임자 지정 및 교육 이수 필수
   
2. 안전교육 강화
   - 전 근로자 월 1회 이상 안전교육 실시
   - 교육 미이수 시 현장 투입 금지
   - 교육 이수 증명 시스템 구축
   
3. 위험작업 허가제
   - 고소작업, 중장비 작업 등 사전 허가 필수
   - 작업 전 안전점검표 작성 의무
   
4. 안전시설 투자 확대
   - 안전비 비율 상향: 공사비의 3% → 5%
   - 안전장비 최신화 의무 (추락방지망, CCTV 등)
   
5. 처벌 강화
   - 중대재해 발생 시 사업주 형사처벌
   - 법인: 50억원 이하 벌금
   - 개인: 1년 이상 징역 또는 10억원 이하 벌금

6. 시행일
   - 2024년 6월 1일부터 전면 시행
            """,
            "url": "https://www.moel.go.kr/safety/2024/001",
            "published_at": (datetime.now() - timedelta(days=20)).isoformat(),
            "importance": "high",
            "keywords": ["중대재해처벌법", "안전관리", "건설안전"],
            "impact_analysis": {
                "cost_impact": {
                    "safety_cost_increase": "안전비 3% → 5% (공사비의 2%p 증가)",
                    "example_50billion_project": "50억 프로젝트 시 1억원 추가 비용",
                    "safety_manager_cost": "안전관리자 인건비 월 500~700만원"
                },
                "compliance_requirements": [
                    "안전관리 조직 구성 및 인력 확보",
                    "안전교육 시스템 구축 (온라인 + 오프라인)",
                    "작업허가 시스템 도입",
                    "안전시설 및 장비 구매/렌탈"
                ],
                "legal_risks": [
                    "중대재해 발생 시 사업주 형사처벌 (최대 징역 1년)",
                    "법인 최대 50억원 벌금",
                    "공사 중단 및 영업정지 가능"
                ],
                "action_items": [
                    "안전관리 전문 업체와 컨설팅 계약 검토",
                    "안전관리자 채용 또는 아웃소싱 방안 검토",
                    "안전교육 프로그램 구축 (협력업체 포함)",
                    "안전비 증가분 반영한 건축비 재산정",
                    "보험 가입 확대 (중대재해 배상책임보험)",
                    "하도급 업체 안전관리 실태 점검 체계 마련"
                ]
            }
        }
    ]
    
    # 키워드 필터링
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',')]
        filtered = []
        for reg in sample_regulations:
            if any(kw in reg['title'] or kw in reg['content'] for kw in keyword_list):
                filtered.append(reg)
        sample_regulations = filtered
    
    return {
        "success": True,
        "category": "건축/제도 변경",
        "period": f"최근 {days}일",
        "total_count": len(sample_regulations),
        "data": sample_regulations,
        "summary": {
            "law_amendments": 1,
            "certification_changes": 1,
            "lh_standards": 1,
            "safety_regulations": 1,
            "high_importance": 4,
            "key_changes": [
                "건축법 시행령 개정 - 건폐율/용적률 완화",
                "제로에너지 인증 기준 강화 (에너지 소요량 14% 강화)",
                "LH 설계기준 개정 - 마감재 고급화 (건축비 15% 증가 예상)",
                "중대재해처벌법 안전비 비율 상향 (3% → 5%)"
            ],
            "total_cost_impact": "건축비 약 20~25% 증가 예상 (규제 강화 + 기준 상향)",
            "critical_deadlines": [
                "2024년 6월 1일: 중대재해처벌법 가이드라인 전면 시행",
                "2024년 7월 1일: 건축법 시행령 개정 시행",
                "2024년 7월 1일: 제로에너지 인증 신규 기준 적용"
            ]
        }
    }


@router.post("/generate-report")
async def generate_policy_report(days: int = 7):
    """
    정책 리포트 생성
    
    지정된 기간 동안의 정책 변화를 종합하여 리포트를 생성합니다.
    """
    
    # 각 카테고리별 데이터 수집
    lh_data = await get_lh_announcements(days=days)
    policy_data = await get_policy_changes(days=days)
    regulation_data = await get_building_regulations(days=days)
    
    # 종합 리포트 생성
    report = {
        "report_id": f"policy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "period": f"최근 {days}일",
        "categories": {
            "lh_announcements": {
                "count": lh_data["total_count"],
                "summary": lh_data["summary"]
            },
            "policy_changes": {
                "count": policy_data["total_count"],
                "summary": policy_data["summary"]
            },
            "building_regulations": {
                "count": regulation_data["total_count"],
                "summary": regulation_data["summary"]
            }
        },
        "overall_summary": {
            "total_updates": (
                lh_data["total_count"] + 
                policy_data["total_count"] + 
                regulation_data["total_count"]
            ),
            "high_priority_items": [
                "LH 입주자격 소득기준 완화 (70% → 80%) - 대상자 확대",
                "임대주택 세제혜택 확대 - 양도소득세 장기보유특별공제 추가",
                "건축법 시행령 개정 - 용적률 완화로 세대수 증가 가능",
                "제로에너지 인증 기준 강화 - 건축비 증가 예상",
                "LH 설계기준 개정 - 마감재 고급화로 건축비 15% 증가",
                "중대재해처벌법 안전비 상향 - 공사비 2%p 증가"
            ],
            "business_impact": {
                "opportunities": [
                    "용적률 완화로 동일 대지 내 세대수 증가 → 매출 증대",
                    "LH 매입 전환 우대조건으로 출구전략 다양화",
                    "ESG S등급 획득 시 매입가 +3% 가산 가능",
                    "제로에너지 인증 인센티브로 용적률 최대 +15% 확보"
                ],
                "challenges": [
                    "건축비 증가 요인 중첩 (설계기준 개정 + 제로에너지 + 안전비)",
                    "예상 건축비 증가율: 20~25%",
                    "중대재해처벌법 준수를 위한 안전관리 조직 구축 필요",
                    "ESG 및 제로에너지 인증 취득을 위한 전문성 확보 필요"
                ],
                "cost_breakdown": {
                    "lh_standard_upgrade": "+15% (마감재 고급화, 설비 강화, 스마트홈)",
                    "zero_energy_certification": "+5~8% (단열 강화, BEMS, 신재생에너지)",
                    "safety_regulation": "+2% (안전비 비율 상향)",
                    "total_estimated_increase": "+20~25%"
                }
            },
            "strategic_recommendations": [
                "🎯 우선순위 1: LH 담당자와 신규 기준 반영 매입가 협의 (건축비 증가분 반영 여부 확인)",
                "🎯 우선순위 2: 용적률 완화 활용 프로젝트 설계 변경 검토 (세대수 증가로 수익성 확보)",
                "🎯 우선순위 3: ESG S등급 + 제로에너지 1등급 목표 설정 (매입가 가산 +3% + 용적률 +15%)",
                "📋 단기 과제: 안전관리 조직 구축 및 안전교육 시스템 도입 (중대재해처벌법 대응)",
                "📋 중기 과제: 제로에너지 전문 설계사무소 협력 체계 구축",
                "📋 장기 과제: 스마트홈 통합 솔루션 자체 개발 또는 전략적 파트너십 구축",
                "💰 재무 전략: 건축비 증가분을 세대수 증가와 매입가 가산으로 상쇄하는 시뮬레이션 필수"
            ]
        },
        "action_plan": {
            "immediate": [
                "LH 신규 매입가 산정 기준 확인 (신규 설계기준 반영 여부)",
                "진행 중인 프로젝트 용적률 완화 적용 가능 여부 검토",
                "안전관리자 채용 공고 또는 아웃소싱 업체 선정"
            ],
            "short_term_1month": [
                "ESG 및 제로에너지 인증 컨설팅 업체 미팅",
                "마감재 및 설비 자재 공급처 재협상 (대량구매 할인)",
                "안전교육 프로그램 구축 및 시범 운영"
            ],
            "medium_term_3months": [
                "신규 기준 반영 표준 설계안 개발",
                "제로에너지 건축물 파일럿 프로젝트 착수",
                "스마트홈 통합 솔루션 도입 및 테스트"
            ],
            "long_term_6months": [
                "ESG S등급 인증 획득",
                "제로에너지 1등급 인증 프로젝트 완공",
                "신규 기준 기반 수익성 모델 정착"
            ]
        }
    }
    
    return {
        "success": True,
        "report": report
    }


@router.post("/compare")
async def compare_policies(request: PolicyComparisonRequest):
    """
    정책 비교
    
    두 정책 또는 공고를 비교하여 차이점을 분석합니다.
    """
    
    # 샘플 비교 결과 (실제로는 DB에서 조회)
    comparison = {
        "policy_1": {
            "id": request.policy_id_1,
            "title": "2023년 4분기 신축매입임대 사업 공고",
            "published_at": "2023-10-01"
        },
        "policy_2": {
            "id": request.policy_id_2,
            "title": "2024년 1분기 신축매입임대 사업 공고",
            "published_at": "2024-01-01"
        },
        "differences": [
            {
                "category": "입주자격",
                "field": "소득기준",
                "old_value": "70% 이하",
                "new_value": "80% 이하",
                "change_type": "완화",
                "impact": "대상자 확대"
            },
            {
                "category": "공급물량",
                "field": "청년형 비율",
                "old_value": "30%",
                "new_value": "40%",
                "change_type": "확대",
                "impact": "청년층 공급 확대"
            },
            {
                "category": "매입조건",
                "field": "건축비 상한 (서울)",
                "old_value": "350만원/㎡",
                "new_value": "380만원/㎡",
                "change_type": "인상",
                "impact": "수익성 개선"
            }
        ],
        "summary": "2024년 1분기 공고는 입주자격 완화, 청년형 공급 확대, 건축비 상한 인상 등 전반적으로 사업자 친화적인 방향으로 개정되었습니다."
    }
    
    return {
        "success": True,
        "comparison": comparison
    }


@router.post("/analyze-with-ai")
async def analyze_policy_with_ai(days: int = 30, category: Optional[str] = None):
    """
    AI 기반 정책 영향 분석 및 전략 생성
    
    정책 모니터링 결과를 AI가 종합 분석하여 구체적인 실행 전략을 제시합니다.
    """
    
    # 카테고리별 데이터 수집
    if category == "lh" or not category:
        lh_data = await get_lh_announcements(days=days)
    else:
        lh_data = None
    
    if category == "policy" or not category:
        policy_data = await get_policy_changes(days=days)
    else:
        policy_data = None
    
    if category == "regulation" or not category:
        regulation_data = await get_building_regulations(days=days)
    else:
        regulation_data = None
    
    # 종합 데이터 구성
    comprehensive_data = {
        "category": "종합 정책 분석" if not category else category,
        "period": f"최근 {days}일",
        "total_count": 0,
        "summary": {
            "key_changes": []
        }
    }
    
    # 데이터 통합
    all_data = []
    if lh_data:
        comprehensive_data["total_count"] += lh_data["total_count"]
        comprehensive_data["summary"]["key_changes"].extend(lh_data["summary"]["key_changes"])
        all_data.extend(lh_data["data"])
    
    if policy_data:
        comprehensive_data["total_count"] += policy_data["total_count"]
        comprehensive_data["summary"]["key_changes"].extend(policy_data["summary"]["key_changes"])
        all_data.extend(policy_data["data"])
    
    if regulation_data:
        comprehensive_data["total_count"] += regulation_data["total_count"]
        comprehensive_data["summary"]["key_changes"].extend(regulation_data["summary"]["key_changes"])
        all_data.extend(regulation_data["data"])
    
    comprehensive_data["data"] = all_data
    
    # AI 서비스로 분석
    ai_service = get_policy_ai_service()
    ai_analysis = await ai_service.analyze_policy_impact(
        comprehensive_data,
        analysis_type="comprehensive"
    )
    
    return {
        "success": True,
        "analysis_date": datetime.now().isoformat(),
        "period": f"최근 {days}일",
        "total_policies": comprehensive_data["total_count"],
        "ai_analysis": ai_analysis,
        "raw_data_summary": {
            "lh_count": lh_data["total_count"] if lh_data else 0,
            "policy_count": policy_data["total_count"] if policy_data else 0,
            "regulation_count": regulation_data["total_count"] if regulation_data else 0
        }
    }
