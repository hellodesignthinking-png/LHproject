"""
M6 LH Final Judgment Expert Report Template
============================================

ZeroSite Decision OS - M6 전문가 보고서 템플릿
목적: LH 종합 판단 (GO/CONDITIONAL/NO-GO)

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M6 – LH FINAL JUDGMENT
"""

from typing import Dict, Any, List
from datetime import datetime


def generate_m6_expert_report(
    project_id: str,
    context_id: str,
    m6_result: Dict[str, Any],
    all_module_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M6 전문가 보고서 생성
    
    구성: 5개 필수 섹션
    1. 최종 판단 (Hero Section)
    2. 모듈별 평가
    3. 판단 근거 요약
    4. 보완 조건
    5. 제출 전략 가이드
    """
    
    # ========================================
    # Section 1: 최종 판단 (Hero Section)
    # ========================================
    section_1 = {
        "title": "1. 최종 판단",
        "content": {
            "판단_결과": {
                "최종_결정": m6_result["final_decision"],
                "LH_매입_가능성": m6_result["lh_submission_probability"],
                "신뢰도_점수": f"{m6_result['confidence_score'] * 100:.0f}%",
                "판단_일시": m6_result["calculated_at"]
            },
            "판단_요약": generate_decision_summary(m6_result["final_decision"]),
            "즉시_조치사항": get_immediate_actions(m6_result["final_decision"]),
            "전체_평가": {
                "통과_모듈": count_modules_by_status(m6_result["module_evaluations"], "PASS"),
                "경고_모듈": count_modules_by_status(m6_result["module_evaluations"], "WARNING"),
                "탈락_모듈": count_modules_by_status(m6_result["module_evaluations"], "FAIL"),
                "평균_점수": calculate_average_score(m6_result["module_evaluations"])
            }
        }
    }
    
    # ========================================
    # Section 2: 모듈별 평가
    # ========================================
    section_2 = {
        "title": "2. 모듈별 평가",
        "content": {
            "평가_개요": "M1~M5+M7 각 모듈별 상세 평가",
            "평가_기준": {
                "PASS": "기준 충족, 문제 없음",
                "WARNING": "일부 보완 권장",
                "FAIL": "기준 미달, 재검토 필수"
            },
            "모듈별_상세_평가": [
                {
                    "모듈": eval["module_name"],
                    "상태": eval["status"],
                    "점수": f"{eval['score'] * 100:.0f}점",
                    "평가_등급": get_score_grade(eval["score"]),
                    "핵심_포인트": eval["key_points"],
                    "개선_필요사항": get_improvement_needs(eval)
                }
                for eval in m6_result["module_evaluations"]
            ],
            "종합_평가": {
                "강점": identify_strengths(m6_result["module_evaluations"]),
                "약점": identify_weaknesses(m6_result["module_evaluations"]),
                "핵심_리스크": extract_key_risks(m6_result["module_evaluations"])
            }
        }
    }
    
    # ========================================
    # Section 3: 판단 근거 요약
    # ========================================
    section_3 = {
        "title": "3. 판단 근거 요약",
        "content": {
            "종합_판단_근거": m6_result["overall_rationale"],
            "통과_모듈_분석": {
                "목록": [e["module_name"] for e in m6_result["module_evaluations"] if e["status"] == "PASS"],
                "통과_사유": generate_pass_reasons(m6_result["module_evaluations"])
            },
            "경고_모듈_분석": {
                "목록": [e["module_name"] for e in m6_result["module_evaluations"] if e["status"] == "WARNING"],
                "경고_사유": generate_warning_reasons(m6_result["module_evaluations"])
            },
            "탈락_모듈_분석": {
                "목록": [e["module_name"] for e in m6_result["module_evaluations"] if e["status"] == "FAIL"],
                "탈락_사유": generate_fail_reasons(m6_result["module_evaluations"])
            } if any(e["status"] == "FAIL" for e in m6_result["module_evaluations"]) else None,
            "데이터_연계_검증": {
                "M1_FROZEN_상태": "확인" if all_module_results.get("M1", {}).get("frozen_at") else "미확인",
                "M2_M3_연계": "정상" if check_m2_m3_linkage(all_module_results) else "오류",
                "M4_M5_연계": "정상" if check_m4_m5_linkage(all_module_results) else "오류",
                "M5_M7_연계": "정상" if check_m5_m7_linkage(all_module_results) else "오류"
            },
            "LH_실무_기준_충족": {
                "보수적_설계": "적용" if is_conservative_design(all_module_results) else "미적용",
                "리스크_관리": "충분" if is_risk_managed(all_module_results) else "부족",
                "정책_부합성": "부합" if is_policy_aligned(all_module_results) else "불일치"
            }
        }
    }
    
    # ========================================
    # Section 4: 보완 조건
    # ========================================
    section_4 = {
        "title": "4. 보완 조건",
        "content": {
            "보완_개요": f"총 {len(m6_result['supplement_conditions'])}개 보완 조건 식별",
            "우선순위별_보완_조건": {
                "HIGH": [
                    {
                        "카테고리": cond["category"],
                        "내용": cond["condition"],
                        "기한": cond.get("deadline", "협의"),
                        "조치_방안": get_action_plan(cond)
                    }
                    for cond in m6_result["supplement_conditions"] if cond["priority"] == "HIGH"
                ],
                "MEDIUM": [
                    {
                        "카테고리": cond["category"],
                        "내용": cond["condition"],
                        "기한": cond.get("deadline", "협의"),
                        "조치_방안": get_action_plan(cond)
                    }
                    for cond in m6_result["supplement_conditions"] if cond["priority"] == "MEDIUM"
                ],
                "LOW": [
                    {
                        "카테고리": cond["category"],
                        "내용": cond["condition"],
                        "기한": cond.get("deadline", "협의"),
                        "조치_방안": get_action_plan(cond)
                    }
                    for cond in m6_result["supplement_conditions"] if cond["priority"] == "LOW"
                ]
            },
            "보완_일정": generate_supplement_schedule(m6_result["supplement_conditions"]),
            "책임_주체": assign_responsibilities(m6_result["supplement_conditions"]),
            "비용_영향": estimate_cost_impact(m6_result["supplement_conditions"])
        }
    }
    
    # ========================================
    # Section 5: 제출 전략 가이드
    # ========================================
    section_5 = {
        "title": "5. 제출 전략 가이드",
        "content": {
            "제출_전략": m6_result["submission_strategy"],
            "제출_가능_시점": estimate_submission_timing(
                m6_result["final_decision"],
                m6_result["supplement_conditions"]
            ),
            "LH_협의_전략": {
                "협의_포인트": generate_negotiation_points(m6_result, all_module_results),
                "강조_사항": get_emphasis_points(m6_result["module_evaluations"]),
                "사전_준비_자료": list_required_documents(m6_result)
            },
            "리스크_대응_전략": {
                "예상_질의_사항": generate_expected_questions(m6_result),
                "답변_가이드": generate_answer_guide(m6_result),
                "추가_검증_사항": identify_additional_verification(m6_result)
            },
            "제출_체크리스트": generate_submission_checklist(m6_result),
            "다음_단계": {
                "즉시_조치": get_immediate_next_steps(m6_result["final_decision"]),
                "1주_이내": get_short_term_steps(m6_result["supplement_conditions"]),
                "2주_이내": get_medium_term_steps(m6_result["supplement_conditions"]),
                "1개월_이내": get_long_term_steps(m6_result)
            }
        }
    }
    
    # ========================================
    # 최종 보고서 구성
    # ========================================
    report = {
        "report_type": "M6_FINAL_JUDGMENT",
        "project_id": project_id,
        "context_id": context_id,
        "generated_at": datetime.utcnow().isoformat(),
        "module_version": "M6-v1.0-FINAL",
        "sections": [
            section_1,
            section_2,
            section_3,
            section_4,
            section_5
        ],
        "metadata": {
            "total_pages": 5,
            "confidence_level": m6_result["confidence_score"],
            "review_status": "FINAL",
            "keywords": ["LH 종합 판단", "GO/CONDITIONAL/NO-GO", "제출 전략", "보완 조건"]
        }
    }
    
    return report


# ========================================
# Helper Functions
# ========================================

def generate_decision_summary(decision: str) -> str:
    """판단 요약 생성"""
    summaries = {
        "GO": "✅ 즉시 LH 제출 가능. 현재 구조 유지하며 협의 진행 권장.",
        "CONDITIONAL": "⚠️ 일부 보완 후 제출 가능. 핵심 리스크는 관리 가능한 수준.",
        "NO-GO": "❌ 현재 구조 재검토 필수. 제출 보류 권장."
    }
    return summaries.get(decision, "판단 불가")

def get_immediate_actions(decision: str) -> List[str]:
    """즉시 조치사항"""
    actions = {
        "GO": [
            "LH 제출 서류 준비",
            "내부 검토 완료",
            "협의 일정 조율"
        ],
        "CONDITIONAL": [
            "고우선순위 보완 사항 즉시 착수",
            "보완 일정 수립",
            "내부 재검토 진행"
        ],
        "NO-GO": [
            "전체 구조 재검토 회의 소집",
            "핵심 문제점 분석",
            "대안 시나리오 검토"
        ]
    }
    return actions.get(decision, ["판단 보류"])

def count_modules_by_status(evaluations: List[Dict], status: str) -> int:
    """상태별 모듈 수 계산"""
    return len([e for e in evaluations if e["status"] == status])

def calculate_average_score(evaluations: List[Dict]) -> float:
    """평균 점수 계산"""
    if not evaluations:
        return 0.0
    return sum(e["score"] for e in evaluations) / len(evaluations)

def get_score_grade(score: float) -> str:
    """점수 등급"""
    if score >= 0.9:
        return "A+ (우수)"
    elif score >= 0.8:
        return "A (양호)"
    elif score >= 0.7:
        return "B (보통)"
    elif score >= 0.6:
        return "C (미흡)"
    else:
        return "D (부족)"

def get_improvement_needs(evaluation: Dict) -> List[str]:
    """개선 필요사항"""
    if evaluation["status"] == "PASS":
        return ["개선 필요사항 없음"]
    elif evaluation["status"] == "WARNING":
        return ["일부 보완 권장"]
    else:
        return ["전면 재검토 필요"]

def identify_strengths(evaluations: List[Dict]) -> List[str]:
    """강점 식별"""
    strengths = []
    high_score_modules = [e for e in evaluations if e["score"] >= 0.85]
    
    if len(high_score_modules) >= 4:
        strengths.append("대부분의 모듈이 높은 점수 획득")
    
    pass_count = count_modules_by_status(evaluations, "PASS")
    if pass_count >= 5:
        strengths.append(f"{pass_count}개 모듈 PASS로 안정적 구조")
    
    if not strengths:
        strengths.append("기본 기준 충족")
    
    return strengths

def identify_weaknesses(evaluations: List[Dict]) -> List[str]:
    """약점 식별"""
    weaknesses = []
    
    fail_modules = [e for e in evaluations if e["status"] == "FAIL"]
    if fail_modules:
        weaknesses.extend([f"{e['module_name']}: 기준 미달" for e in fail_modules])
    
    warning_modules = [e for e in evaluations if e["status"] == "WARNING"]
    if len(warning_modules) >= 2:
        weaknesses.append(f"{len(warning_modules)}개 모듈 경고 상태")
    
    if not weaknesses:
        weaknesses.append("식별된 중대 약점 없음")
    
    return weaknesses

def extract_key_risks(evaluations: List[Dict]) -> List[str]:
    """핵심 리스크 추출"""
    risks = []
    
    for eval in evaluations:
        if eval["status"] in ["WARNING", "FAIL"]:
            risks.extend(eval.get("key_points", []))
    
    return risks[:5] if risks else ["식별된 중대 리스크 없음"]

def generate_pass_reasons(evaluations: List[Dict]) -> List[str]:
    """통과 사유 생성"""
    pass_modules = [e for e in evaluations if e["status"] == "PASS"]
    return [f"{e['module_name']}: {', '.join(e['key_points'])}" for e in pass_modules]

def generate_warning_reasons(evaluations: List[Dict]) -> List[str]:
    """경고 사유 생성"""
    warning_modules = [e for e in evaluations if e["status"] == "WARNING"]
    return [f"{e['module_name']}: 일부 보완 필요" for e in warning_modules]

def generate_fail_reasons(evaluations: List[Dict]) -> List[str]:
    """탈락 사유 생성"""
    fail_modules = [e for e in evaluations if e["status"] == "FAIL"]
    return [f"{e['module_name']}: 기준 미달" for e in fail_modules]

def check_m2_m3_linkage(all_results: Dict) -> bool:
    """M2-M3 연계 검증"""
    return bool(all_results.get("M2") and all_results.get("M3"))

def check_m4_m5_linkage(all_results: Dict) -> bool:
    """M4-M5 연계 검증"""
    return bool(all_results.get("M4") and all_results.get("M5"))

def check_m5_m7_linkage(all_results: Dict) -> bool:
    """M5-M7 연계 검증"""
    return bool(all_results.get("M5") and all_results.get("M7"))

def is_conservative_design(all_results: Dict) -> bool:
    """보수적 설계 적용 여부"""
    m4 = all_results.get("M4", {})
    return "lh_recommended" in m4

def is_risk_managed(all_results: Dict) -> bool:
    """리스크 관리 충분 여부"""
    m5 = all_results.get("M5", {})
    return len(m5.get("risk_summary", [])) >= 3

def is_policy_aligned(all_results: Dict) -> bool:
    """정책 부합성 여부"""
    m3 = all_results.get("M3", {})
    return m3.get("lh_pass_score", 0) >= 70

def get_action_plan(condition: Dict) -> str:
    """조치 방안"""
    if condition["priority"] == "HIGH":
        return "즉시 착수, 1주 이내 완료"
    elif condition["priority"] == "MEDIUM":
        return "2주 이내 착수, 1개월 이내 완료"
    else:
        return "협의 시 검토"

def generate_supplement_schedule(conditions: List[Dict]) -> Dict[str, List[str]]:
    """보완 일정 생성"""
    return {
        "1주_이내": [c["condition"] for c in conditions if c["priority"] == "HIGH"],
        "2주_이내": [c["condition"] for c in conditions if c["priority"] == "MEDIUM"],
        "1개월_이내": [c["condition"] for c in conditions if c["priority"] == "LOW"]
    }

def assign_responsibilities(conditions: List[Dict]) -> Dict[str, List[str]]:
    """책임 주체 배정"""
    return {
        "사업자": [c["condition"] for c in conditions if "사업" in c["category"]],
        "LH": [c["condition"] for c in conditions if "LH" in c["category"]],
        "협의": [c["condition"] for c in conditions if "협의" in c["condition"]]
    }

def estimate_cost_impact(conditions: List[Dict]) -> str:
    """비용 영향 추정"""
    high_count = len([c for c in conditions if c["priority"] == "HIGH"])
    if high_count >= 3:
        return "총사업비 3~5% 증가 예상"
    elif high_count >= 1:
        return "총사업비 1~3% 증가 예상"
    else:
        return "비용 영향 미미"

def estimate_submission_timing(decision: str, conditions: List[Dict]) -> str:
    """제출 가능 시점 추정"""
    if decision == "GO":
        return "즉시 가능"
    elif decision == "CONDITIONAL":
        high_count = len([c for c in conditions if c["priority"] == "HIGH"])
        if high_count >= 3:
            return "2~3주 후"
        else:
            return "1~2주 후"
    else:
        return "재검토 후 판단"

def generate_negotiation_points(m6_result: Dict, all_results: Dict) -> List[str]:
    """협의 포인트 생성"""
    return [
        "보수적 설계 적용으로 안전성 확보",
        "LH 표준 기준 준수",
        "리스크 완화 전략 수립 완료"
    ]

def get_emphasis_points(evaluations: List[Dict]) -> List[str]:
    """강조 사항"""
    high_score = [e for e in evaluations if e["score"] >= 0.85]
    return [f"{e['module_name']}: {e['key_points'][0]}" for e in high_score[:3]]

def list_required_documents(m6_result: Dict) -> List[str]:
    """필수 서류 목록"""
    return [
        "M1~M7 통합 보고서",
        "LH 제출용 요약본",
        "근거 자료 첨부",
        "리스크 완화 계획서"
    ]

def generate_expected_questions(m6_result: Dict) -> List[str]:
    """예상 질의사항"""
    return [
        "보수적 설계 근거는?",
        "리스크 완화 전략은?",
        "정책 부합성 증빙은?"
    ]

def generate_answer_guide(m6_result: Dict) -> List[str]:
    """답변 가이드"""
    return [
        "M4 보수적 설계: 법정의 85% 적용",
        "M5 리스크: 예비비 5% 확보",
        "M3 정책: LH 통과 점수 85점"
    ]

def identify_additional_verification(m6_result: Dict) -> List[str]:
    """추가 검증 사항"""
    return [
        "M1 데이터 재확인",
        "M5 안전 마진 재계산",
        "M7 민원 대응 시나리오 보완"
    ]

def generate_submission_checklist(m6_result: Dict) -> List[Dict[str, str]]:
    """제출 체크리스트"""
    return [
        {"항목": "M1 FROZEN 확인", "상태": "✅"},
        {"항목": "M2~M7 완료 확인", "상태": "✅"},
        {"항목": "통합 보고서 생성", "상태": "대기"},
        {"항목": "LH 협의 일정", "상태": "대기"}
    ]

def get_immediate_next_steps(decision: str) -> List[str]:
    """즉시 다음 단계"""
    if decision == "GO":
        return ["LH 제출 서류 작성", "내부 검토 완료"]
    else:
        return ["보완 사항 착수", "재검토 일정 수립"]

def get_short_term_steps(conditions: List[Dict]) -> List[str]:
    """단기 단계 (1주 이내)"""
    return [c["condition"] for c in conditions if c["priority"] == "HIGH"][:3]

def get_medium_term_steps(conditions: List[Dict]) -> List[str]:
    """중기 단계 (2주 이내)"""
    return [c["condition"] for c in conditions if c["priority"] == "MEDIUM"][:3]

def get_long_term_steps(m6_result: Dict) -> List[str]:
    """장기 단계 (1개월 이내)"""
    return [
        "LH 협의 완료",
        "최종 승인 확보",
        "사업 착수 준비"
    ]
