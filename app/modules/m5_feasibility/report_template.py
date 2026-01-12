"""
M5 Feasibility & Risk Expert Report Template
=============================================

ZeroSite Decision OS - M5 전문가 보고서 템플릿
목적: LH 매입 논리 중심의 사업성·리스크 검증 보고서

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M5 – FEASIBILITY & RISK (LH-SAFE)
"""

from typing import Dict, Any, List
from datetime import datetime


def generate_m5_expert_report(
    project_id: str,
    context_id: str,
    m5_result: Dict[str, Any],
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    m3_data: Dict[str, Any],
    m4_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M5 전문가 보고서 생성
    
    구성: 8개 필수 섹션
    1. 검토 개요
    2. 총사업비 구조
    3. LH 매입가 산정
    4. 손익 구조 분석
    5. 리스크 식별 및 평가
    6. 리스크 완화 전략
    7. 안정성 종합 평가
    8. 사업성 결론
    """
    
    cost = m5_result["cost_breakdown"]
    lh_purchase = m5_result["lh_purchase"]
    risks = m5_result["risk_summary"]
    
    # ========================================
    # Section 1: 검토 개요
    # ========================================
    section_1 = {
        "title": "1. 검토 개요",
        "content": {
            "목적": "LH 매입 논리 중심의 사업성·리스크 검증",
            "검토_기준": "LH 신축매입임대 표준 기준",
            "검토_범위": "총사업비, LH 매입가, 리스크, 안정성",
            "전제_조건": {
                "M1": "사실 확정 (FROZEN)",
                "M2": f"적정 매입가 {format_currency(m2_data.get('adjusted_land_value', 0))}",
                "M3": f"공급유형 {m3_data.get('recommended_type', 'N/A')}",
                "M4": f"세대수 {m4_data.get('lh_recommended', {}).get('units', 0)}세대"
            },
            "검토_일시": datetime.utcnow().isoformat()
        }
    }
    
    # ========================================
    # Section 2: 총사업비 구조
    # ========================================
    section_2 = {
        "title": "2. 총사업비 구조 (보수 기준)",
        "content": {
            "산정_원칙": [
                "LH 표준 단가 적용",
                "보수적 건축비 산정",
                "예비비 5% 확보"
            ],
            "비용_항목": {
                "토지비": {
                    "금액": cost["land_cost"],
                    "산정_근거": "M2 적정 매입가 하단값",
                    "비중": f"{(cost['land_cost'] / cost['total_cost'] * 100):.1f}%"
                },
                "건축비": {
                    "금액": cost["construction_cost"],
                    "산정_근거": f"LH 표준 건축비 2,800,000원/㎡ × {m4_data.get('lh_recommended', {}).get('total_floor_area', 0):.0f}㎡",
                    "비중": f"{(cost['construction_cost'] / cost['total_cost'] * 100):.1f}%"
                },
                "설계·감리비": {
                    "금액": cost["design_supervision"],
                    "산정_근거": "건축비의 9%",
                    "비중": f"{(cost['design_supervision'] / cost['total_cost'] * 100):.1f}%"
                },
                "예비비": {
                    "금액": cost["contingency"],
                    "산정_근거": "총사업비의 5% (리스크 흡수)",
                    "비중": f"{(cost['contingency'] / cost['total_cost'] * 100):.1f}%"
                }
            },
            "총사업비": {
                "금액": cost["total_cost"],
                "억원": f"{cost['total_cost'] / 100000000:.1f}억원"
            },
            "비교_기준": {
                "세대당_사업비": f"{(cost['total_cost'] / m4_data.get('lh_recommended', {}).get('units', 1)):.0f}원/세대",
                "연면적당_사업비": f"{(cost['total_cost'] / m4_data.get('lh_recommended', {}).get('total_floor_area', 1)):.0f}원/㎡"
            }
        }
    }
    
    # ========================================
    # Section 3: LH 매입가 산정
    # ========================================
    section_3 = {
        "title": "3. LH 매입가 산정",
        "content": {
            "산정_방식": "연면적 × 표준 매입단가 + 커뮤니티 가점",
            "기본_매입가": {
                "금액": lh_purchase["base_price"],
                "산정_근거": f"{m3_data.get('recommended_type', 'N/A')} 표준 매입단가 적용",
                "단가": f"{(lh_purchase['base_price'] / m4_data.get('lh_recommended', {}).get('total_floor_area', 1)):.0f}원/㎡"
            },
            "커뮤니티_가점": {
                "금액": lh_purchase["community_bonus"],
                "산정_근거": "M7 커뮤니티 계획 연계 (향후 반영)"
            },
            "총_매입가": {
                "금액": lh_purchase["total_purchase_price"],
                "억원": f"{lh_purchase['total_purchase_price'] / 100000000:.1f}억원"
            },
            "안전_마진": {
                "비율": f"{lh_purchase['buffer_ratio']:.2f}%",
                "금액": lh_purchase["total_purchase_price"] - cost["total_cost"],
                "평가": evaluate_buffer_ratio(lh_purchase["buffer_ratio"])
            }
        }
    }
    
    # ========================================
    # Section 4: 손익 구조 분석
    # ========================================
    section_4 = {
        "title": "4. 손익 구조 분석 (LH 관점)",
        "content": {
            "분석_관점": "사업자 과도 이익 방지 + LH 매입 적정성",
            "구조_평가": {
                "총사업비": f"{cost['total_cost'] / 100000000:.1f}억원",
                "LH_매입가": f"{lh_purchase['total_purchase_price'] / 100000000:.1f}억원",
                "차액": f"{(lh_purchase['total_purchase_price'] - cost['total_cost']) / 100000000:.1f}억원",
                "마진율": f"{lh_purchase['buffer_ratio']:.2f}%"
            },
            "적정성_판단": {
                "마진_수준": evaluate_margin_level(lh_purchase["buffer_ratio"]),
                "LH_입장": evaluate_lh_perspective(lh_purchase["buffer_ratio"]),
                "권고_사항": get_margin_recommendation(lh_purchase["buffer_ratio"])
            },
            "시나리오_분석": [
                {
                    "시나리오": "낙관 (공사비 -5%)",
                    "총사업비": cost["total_cost"] * 0.95,
                    "마진율": f"{((lh_purchase['total_purchase_price'] - cost['total_cost'] * 0.95) / (cost['total_cost'] * 0.95) * 100):.2f}%"
                },
                {
                    "시나리오": "기준 (현재 구조)",
                    "총사업비": cost["total_cost"],
                    "마진율": f"{lh_purchase['buffer_ratio']:.2f}%"
                },
                {
                    "시나리오": "비관 (공사비 +10%)",
                    "총사업비": cost["total_cost"] * 1.10,
                    "마진율": f"{((lh_purchase['total_purchase_price'] - cost['total_cost'] * 1.10) / (cost['total_cost'] * 1.10) * 100):.2f}%"
                }
            ]
        }
    }
    
    # ========================================
    # Section 5: 리스크 식별 및 평가
    # ========================================
    section_5 = {
        "title": "5. 리스크 식별 및 평가",
        "content": {
            "리스크_개요": f"총 {len(risks)}개 리스크 식별",
            "리스크_목록": [
                {
                    "순번": idx + 1,
                    "리스크_명": risk["risk"],
                    "위험도": risk["level"],
                    "발생_가능성": risk["probability"],
                    "영향도": risk["impact"],
                    "완화_전략": risk["mitigation"]
                }
                for idx, risk in enumerate(risks)
            ],
            "위험도_분포": {
                "HIGH": len([r for r in risks if r["level"] == "HIGH"]),
                "MEDIUM": len([r for r in risks if r["level"] == "MEDIUM"]),
                "LOW": len([r for r in risks if r["level"] == "LOW"])
            },
            "핵심_리스크": [
                risk for risk in risks if risk["level"] in ["HIGH", "MEDIUM"]
            ][:3]
        }
    }
    
    # ========================================
    # Section 6: 리스크 완화 전략
    # ========================================
    section_6 = {
        "title": "6. 리스크 완화 전략",
        "content": {
            "전략_개요": "리스크별 구체적 대응 방안",
            "완화_전략": [
                {
                    "리스크": risk["risk"],
                    "위험도": risk["level"],
                    "대응_방안": risk["mitigation"],
                    "책임_주체": get_responsible_party(risk["risk"]),
                    "시점": get_mitigation_timing(risk["risk"])
                }
                for risk in risks
            ],
            "통합_관리_방안": {
                "모니터링": "월 1회 리스크 점검 및 보고",
                "예산_관리": "예비비 5% 별도 확보",
                "의사결정": "중대 리스크 발생 시 LH 협의",
                "문서화": "리스크 관리 대장 작성 및 유지"
            }
        }
    }
    
    # ========================================
    # Section 7: 안정성 종합 평가
    # ========================================
    section_7 = {
        "title": "7. 안정성 종합 평가",
        "content": {
            "평가_결과": m5_result["stability_assessment"],
            "평가_근거": {
                "안전_마진": f"{lh_purchase['buffer_ratio']:.2f}% (적정 범위: 8~12%)",
                "고위험_요소": len([r for r in risks if r["level"] == "HIGH"]),
                "중위험_요소": len([r for r in risks if r["level"] == "MEDIUM"]),
                "저위험_요소": len([r for r in risks if r["level"] == "LOW"])
            },
            "강점": get_strengths(lh_purchase["buffer_ratio"], risks),
            "약점": get_weaknesses(lh_purchase["buffer_ratio"], risks),
            "종합_의견": {
                "재무적_안정성": evaluate_financial_stability(lh_purchase["buffer_ratio"]),
                "운영_안정성": "LH 직영 운영으로 장기 안정성 확보",
                "정책_부합성": f"{m3_data.get('recommended_type', 'N/A')} 정책 목표와 부합"
            }
        }
    }
    
    # ========================================
    # Section 8: 사업성 결론
    # ========================================
    section_8 = {
        "title": "8. 사업성 결론",
        "content": {
            "최종_결론": m5_result["feasibility_conclusion"],
            "핵심_지표": {
                "총사업비": f"{cost['total_cost'] / 100000000:.1f}억원",
                "LH_매입가": f"{lh_purchase['total_purchase_price'] / 100000000:.1f}억원",
                "안전_마진": f"{lh_purchase['buffer_ratio']:.2f}%",
                "위험도": assess_overall_risk_level(risks)
            },
            "LH_제출_가능성": evaluate_submission_readiness(
                lh_purchase["buffer_ratio"],
                risks,
                m5_result["stability_assessment"]
            ),
            "보완_필요사항": get_improvement_requirements(
                lh_purchase["buffer_ratio"],
                risks
            ),
            "다음_단계": [
                "M7 커뮤니티 계획 수립",
                "M6 LH 종합 판단 실행",
                "통합 보고서 생성 및 검토"
            ]
        }
    }
    
    # ========================================
    # 최종 보고서 구성
    # ========================================
    report = {
        "report_type": "M5_FEASIBILITY_RISK",
        "project_id": project_id,
        "context_id": context_id,
        "generated_at": datetime.utcnow().isoformat(),
        "module_version": "M5-v1.0-LH-SAFE",
        "sections": [
            section_1,
            section_2,
            section_3,
            section_4,
            section_5,
            section_6,
            section_7,
            section_8
        ],
        "metadata": {
            "total_pages": 8,
            "confidence_level": calculate_confidence_level(lh_purchase["buffer_ratio"], risks),
            "review_status": "DRAFT",
            "keywords": ["사업성", "리스크", "LH 매입", "안정성", "총사업비"]
        }
    }
    
    return report


# ========================================
# Helper Functions
# ========================================

def format_currency(amount: float) -> str:
    """금액 포맷팅"""
    if amount >= 100000000:
        return f"{amount / 100000000:.1f}억원"
    elif amount >= 10000:
        return f"{amount / 10000:.0f}만원"
    else:
        return f"{amount:,.0f}원"

def evaluate_buffer_ratio(ratio: float) -> str:
    """안전 마진 평가"""
    if ratio < 5:
        return "⚠️ 주의: 안전 마진 부족"
    elif ratio > 15:
        return "⚠️ 주의: 과도한 마진"
    elif 8 <= ratio <= 12:
        return "✅ 이상적: 적정 범위"
    else:
        return "✔ 양호: 허용 범위"

def evaluate_margin_level(ratio: float) -> str:
    """마진 수준 평가"""
    if ratio < 5:
        return "낮음 (리스크 흡수 여력 부족)"
    elif ratio > 15:
        return "높음 (LH 심사 시 부정적)"
    else:
        return "적정 (사업 추진 가능)"

def evaluate_lh_perspective(ratio: float) -> str:
    """LH 입장 평가"""
    if ratio < 5:
        return "사업자 리스크 과다 → 사업 안정성 우려"
    elif ratio > 15:
        return "사업자 과도 이익 → 매입가 인하 압력"
    else:
        return "사업자·LH 모두 수용 가능한 구조"

def get_margin_recommendation(ratio: float) -> str:
    """마진 권고사항"""
    if ratio < 5:
        return "총사업비 재검토 또는 LH 매입가 협상 필요"
    elif ratio > 15:
        return "커뮤니티 투자 확대 또는 매입가 자진 하향 검토"
    else:
        return "현재 구조 유지 권장"

def get_responsible_party(risk_name: str) -> str:
    """리스크 책임 주체"""
    if "공사비" in risk_name or "건축" in risk_name:
        return "사업자 + 시공사"
    elif "인허가" in risk_name:
        return "사업자 + 지자체"
    elif "LH" in risk_name:
        return "사업자 + LH"
    elif "민원" in risk_name or "커뮤니티" in risk_name:
        return "사업자 + 주민"
    else:
        return "사업자"

def get_mitigation_timing(risk_name: str) -> str:
    """리스크 완화 시점"""
    if "인허가" in risk_name:
        return "착공 전"
    elif "공사비" in risk_name:
        return "공사 중"
    elif "민원" in risk_name:
        return "사업 전 과정"
    elif "운영" in risk_name:
        return "입주 후"
    else:
        return "수시"

def get_strengths(ratio: float, risks: List[Dict]) -> List[str]:
    """강점 분석"""
    strengths = []
    
    if 5 <= ratio <= 15:
        strengths.append(f"안전 마진 {ratio:.1f}% 확보로 리스크 흡수 가능")
    
    low_risks = [r for r in risks if r["level"] == "LOW"]
    if len(low_risks) >= 3:
        strengths.append(f"저위험 요소 {len(low_risks)}개로 안정적 구조")
    
    strengths.append("LH 표준 기준 적용으로 심사 통과 가능성 높음")
    strengths.append("보수적 건축 규모로 인허가 리스크 최소화")
    
    return strengths

def get_weaknesses(ratio: float, risks: List[Dict]) -> List[str]:
    """약점 분석"""
    weaknesses = []
    
    if ratio < 5:
        weaknesses.append("안전 마진 부족으로 리스크 대응 여력 낮음")
    elif ratio > 15:
        weaknesses.append("과도한 마진으로 LH 심사 시 부정적 평가 우려")
    
    high_risks = [r for r in risks if r["level"] == "HIGH"]
    if high_risks:
        weaknesses.extend([r["risk"] for r in high_risks])
    
    return weaknesses if weaknesses else ["식별된 중대 약점 없음"]

def evaluate_financial_stability(ratio: float) -> str:
    """재무적 안정성 평가"""
    if ratio < 5:
        return "낮음 (보완 필요)"
    elif ratio > 15:
        return "과다 (조정 권장)"
    elif 8 <= ratio <= 12:
        return "매우 안정적"
    else:
        return "안정적"

def assess_overall_risk_level(risks: List[Dict]) -> str:
    """전체 위험도 평가"""
    high_count = len([r for r in risks if r["level"] == "HIGH"])
    medium_count = len([r for r in risks if r["level"] == "MEDIUM"])
    
    if high_count >= 2:
        return "높음"
    elif high_count == 1 or medium_count >= 3:
        return "중간"
    else:
        return "낮음"

def evaluate_submission_readiness(
    ratio: float,
    risks: List[Dict],
    stability: str
) -> str:
    """LH 제출 가능성 평가"""
    high_risks = len([r for r in risks if r["level"] == "HIGH"])
    
    if "안정적" in stability and 5 <= ratio <= 15 and high_risks == 0:
        return "✅ 높음 (제출 가능)"
    elif high_risks >= 2 or ratio < 3 or ratio > 20:
        return "⚠️ 낮음 (보완 필수)"
    else:
        return "✔ 보통 (일부 보완 후 제출)"

def get_improvement_requirements(
    ratio: float,
    risks: List[Dict]
) -> List[str]:
    """보완 필요사항"""
    requirements = []
    
    if ratio < 5:
        requirements.append("총사업비 재검토 또는 LH 매입가 상향 협의")
    elif ratio > 15:
        requirements.append("커뮤니티 투자 확대 또는 매입가 자진 하향")
    
    high_risks = [r for r in risks if r["level"] == "HIGH"]
    for risk in high_risks:
        requirements.append(f"{risk['risk']}: {risk['mitigation']}")
    
    if not requirements:
        requirements.append("식별된 보완 필요사항 없음")
    
    return requirements

def calculate_confidence_level(ratio: float, risks: List[Dict]) -> float:
    """신뢰도 계산 (0.0 ~ 1.0)"""
    score = 0.5  # 기본 점수
    
    # 안전 마진 평가
    if 8 <= ratio <= 12:
        score += 0.3
    elif 5 <= ratio <= 15:
        score += 0.2
    elif ratio < 5 or ratio > 20:
        score -= 0.2
    
    # 리스크 평가
    high_risks = len([r for r in risks if r["level"] == "HIGH"])
    medium_risks = len([r for r in risks if r["level"] == "MEDIUM"])
    
    if high_risks == 0:
        score += 0.2
    else:
        score -= 0.1 * high_risks
    
    if medium_risks <= 2:
        score += 0.1
    
    return max(0.0, min(1.0, score))
