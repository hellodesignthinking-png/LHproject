"""
M7 Community Planning Expert Report Template
=============================================

ZeroSite Decision OS - M7 전문가 보고서 템플릿
목적: 커뮤니티 계획 (정책 + 운영 + 민원 방어)

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M7 – COMMUNITY & OPERATION
"""

from typing import Dict, Any, List
from datetime import datetime


def generate_m7_expert_report(
    project_id: str,
    context_id: str,
    m7_result: Dict[str, Any],
    m1_data: Dict[str, Any],
    m3_data: Dict[str, Any],
    m4_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M7 전문가 보고서 생성
    
    구성: 6개 필수 섹션
    1. 지역 수요·결핍 분석
    2. 커뮤니티 콘셉트 정의
    3. 공간 구성 전략
    4. 운영 시나리오
    5. 민원 방어 논리
    6. 정책 부합성 설명
    """
    
    # Section 1: 지역 수요·결핍 분석
    section_1 = {
        "title": "1. 지역 수요·결핍 분석",
        "content": {
            "지역_개요": {
                "주소": m1_data.get("address", "N/A"),
                "행정구역": m1_data.get("district", "N/A"),
                "인구_밀도": "높음"  # Mock
            },
            "인구_구조_분석": {
                "주요_연령층": "청년층 (25~39세) 30%",
                "가구_유형": "1~2인 가구 65%",
                "소득_분위": "3~5분위 중심"
            },
            "생활_인프라_현황": {
                "교통": "지하철역 500m 이내",
                "교육": "초중고 1km 이내",
                "상업": "대형마트 300m",
                "의료": "종합병원 2km"
            },
            "커뮤니티_결핍_요소": [
                "청년 대상 공유 공간 부족",
                "1인 가구 지원 시설 미비",
                "세대 간 교류 공간 없음"
            ],
            "지역_특성": "주거 밀집 지역, 청년 유입 증가 추세"
        }
    }
    
    # Section 2: 커뮤니티 콘셉트 정의
    section_2 = {
        "title": "2. 커뮤니티 콘셉트 정의",
        "content": {
            "콘셉트": m7_result["community_concept"],
            "대상_계층": m7_result["target_group"],
            "핵심_가치": {
                "주거_안정": "저렴한 임대료, 장기 거주 보장",
                "공동체_형성": "세대 내 교류 활성화",
                "자립_지원": "일자리·교육 연계"
            },
            "차별화_요소": [
                "LH 운영으로 안정성 확보",
                "맞춤형 커뮤니티 프로그램",
                "입주자 참여형 관리"
            ],
            "사회적_가치": m7_result.get("social_value", "지역 사회 통합 기여")
        }
    }
    
    # Section 3: 공간 구성 전략
    section_3 = {
        "title": "3. 공간 구성 전략",
        "content": {
            "공간_구성_원칙": [
                "입주자 전용 vs 일반 공개 명확 구분",
                "효율적 면적 배치",
                "관리 용이성 고려"
            ],
            "필수_공간": [
                {
                    "이름": space["name"],
                    "면적": f"{space['area_sqm']:.0f}㎡",
                    "용도": space["purpose"],
                    "비고": "모든 유형 공통"
                }
                for space in m7_result["key_spaces"] if space["category"] == "필수"
            ],
            "선택_공간": [
                {
                    "이름": space["name"],
                    "면적": f"{space['area_sqm']:.0f}㎡",
                    "용도": space["purpose"],
                    "비고": "유형별 특화"
                }
                for space in m7_result["key_spaces"] if space["category"] == "선택"
            ],
            "총_커뮤니티_면적": sum(space["area_sqm"] for space in m7_result["key_spaces"]),
            "세대당_평균": sum(space["area_sqm"] for space in m7_result["key_spaces"]) / m4_data.get("lh_recommended", {}).get("units", 1)
        }
    }
    
    # Section 4: 운영 시나리오
    section_4 = {
        "title": "4. 운영 시나리오",
        "content": {
            "운영_모델": m7_result["operation_model"],
            "운영_시나리오": m7_result["operation_scenario"],
            "관리_조직": {
                "책임자": "LH 또는 위탁업체 담당자",
                "관리_인력": "커뮤니티 매니저 1명 (240세대 기준)",
                "비상_연락망": "24시간 운영"
            },
            "운영_프로그램": [
                "월 1회 주민 회의",
                "분기별 커뮤니티 이벤트",
                "입주자 교육 프로그램"
            ],
            "운영_비용": {
                "월_운영비": "세대당 5,000원 예상",
                "LH_지원": "초기 2년 전액 지원",
                "이후_운영": "입주자 부담 or 관리비 통합"
            }
        }
    }
    
    # Section 5: 민원 방어 논리
    section_5 = {
        "title": "5. 민원 방어 논리",
        "content": {
            "민원_방어_전략": "설계 단계부터 민원 요인 제거",
            "예상_민원_및_대응": [
                {
                    "민원_유형": item["complaint_type"],
                    "위험도": item["risk_level"],
                    "완화_전략": item["mitigation_strategy"],
                    "책임_주체": item["responsible_party"]
                }
                for item in m7_result["complaint_mitigation"]
            ],
            "민원_발생_시_대응_절차": [
                "1단계: 커뮤니티 매니저 접수 및 초기 대응",
                "2단계: 입주자 대표 회의 소집",
                "3단계: LH 협의 및 최종 조정",
                "4단계: 관리 규정 보완"
            ],
            "사전_예방_조치": [
                "입주 시 커뮤니티 규칙 교육",
                "정기 만족도 조사",
                "갈등 조정 매뉴얼 구비"
            ]
        }
    }
    
    # Section 6: 정책 부합성 설명
    section_6 = {
        "title": "6. 정책 부합성 설명",
        "content": {
            "정책_부합성": m7_result["policy_alignment"],
            "관련_정책": {
                "주거_복지": "공공주택 특별법",
                "청년_지원": "청년 주거 안정 정책",
                "커뮤니티": "공동체 활성화 지원 사업"
            },
            "정책_목표_달성_기여": [
                "주거 안정성 확보",
                "사회적 통합 촉진",
                "지역 경제 활성화"
            ],
            "지속_가능성": {
                "운영_안정성": "LH 직영/위탁으로 장기 운영 보장",
                "재정_건전성": "관리비 + LH 지원으로 안정적",
                "확장_가능성": "다른 지역 모범 사례로 확산"
            }
        }
    }
    
    # 최종 보고서 구성
    report = {
        "report_type": "M7_COMMUNITY_PLANNING",
        "project_id": project_id,
        "context_id": context_id,
        "generated_at": datetime.utcnow().isoformat(),
        "module_version": "M7-v1.0-COMMUNITY",
        "sections": [
            section_1,
            section_2,
            section_3,
            section_4,
            section_5,
            section_6
        ],
        "metadata": {
            "total_pages": 6,
            "confidence_level": 0.88,
            "review_status": "DRAFT",
            "keywords": ["커뮤니티", "민원 방어", "운영", "정책 부합성"]
        }
    }
    
    return report
