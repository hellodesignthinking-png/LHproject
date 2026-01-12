"""
M3 – HOUSING TYPE SUITABILITY (LH-GRADE)
공급유형 적합성 전문가 보고서 템플릿

출력 규칙:
- LH 심사 통과 확률 중심
- 6개 필수 섹션
- "떨어질 확률이 가장 낮은 유형" 명시

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime

def generate_m3_expert_report(
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    m3_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M3 전문가 보고서 생성
    
    Args:
        m1_data: M1 FROZEN 데이터
        m2_data: M2 계산 결과
        m3_result: M3 분석 결과
    
    Returns:
        구조화된 전문가 보고서 (JSON)
    """
    
    # M1 데이터 추출
    land_info = m1_data.get('land_info', {})
    cadastral = land_info.get('cadastral', {})
    zoning = land_info.get('zoning', {})
    address_info = land_info.get('address', {})
    
    # M2 데이터 추출
    adjusted_land_value = m2_data.get('adjusted_land_value', 0)
    unit_price_sqm = m2_data.get('unit_price_sqm', 0)
    
    # M3 결과 추출
    recommended_type = m3_result.get('recommended_type')
    lh_pass_score = m3_result.get('lh_pass_score')
    ranking = m3_result.get('ranking', [])
    rejection_reasons = m3_result.get('rejection_reasons', {})
    persuasion_text = m3_result.get('lh_persuasion_text', '')
    
    # 보고서 구조
    report = {
        "module": "M3",
        "title": "공급유형 적합성 검토서",
        "subtitle": "LH 심사 통과 확률 기반 공급유형 선정",
        "status": "ANALYSIS_COMPLETED",
        "generated_at": datetime.utcnow().isoformat(),
        "context_id": m3_result.get('context_id'),
        
        # 검증 플래그
        "validation": {
            "lh_pass_probability": True,
            "policy_based": True,
            "rejection_logic": True,
            "single_recommendation": True
        },
        
        # 6개 필수 섹션
        "sections": []
    }
    
    # ============================================================
    # Section 1: 적용 가능 공급유형 목록
    # ============================================================
    
    section_1 = {
        "section_number": "1",
        "section_title": "적용 가능 공급유형 목록",
        "content": {
            "description": "LH 공급유형 Pool (5가지)을 대상으로 심사 통과 확률을 평가합니다.",
            
            "housing_types_table": {
                "columns": ["코드", "공급유형", "LH 통과 점수", "순위"],
                "rows": [
                    [
                        f"T{i+1}",
                        score.get('type'),
                        f"{score.get('total_score')}점",
                        f"{i+1}위"
                    ]
                    for i, score in enumerate(ranking)
                ]
            },
            
            "evaluation_criteria": [
                "✅ 정책 적합성 (30점)",
                "✅ 입지·수요 일치 (25점)",
                "✅ 토지가격 부담 (20점)",
                "✅ 인허가 리스크 (15점)",
                "✅ 운영·민원 안정성 (10점)"
            ],
            
            "note": "⚠️ 본 평가는 '최적 유형'이 아닌 'LH 심사 통과 확률이 가장 높은 유형'을 선정합니다."
        }
    }
    
    report["sections"].append(section_1)
    
    # ============================================================
    # Section 2: 정책·지침 기준
    # ============================================================
    
    section_2 = {
        "section_number": "2",
        "section_title": "정책·지침 기준",
        "content": {
            "description": "LH 공급유형별 정책 기준 및 지침을 검토합니다.",
            
            "policy_compliance_table": {
                "columns": ["공급유형", "정책 적합성 점수", "주요 정책 근거"],
                "rows": [
                    [
                        score.get('type'),
                        f"{score.get('policy_score')}/30점",
                        "도심 청년 주거 지원 정책 부합" if "청년" in score.get('type') else
                        "신혼부부 주거 안정 정책 부합" if "신혼" in score.get('type') else
                        "고령자 복지 정책 부합" if "고령" in score.get('type') else
                        "역세권 개발 정책 부합" if "역세권" in score.get('type') else
                        "공공임대 공급 확대 정책"
                    ]
                    for score in ranking
                ]
            },
            
            "key_policies": [
                f"✅ 추천 유형 '{recommended_type}'은(는) 현 정부 주거 정책과 부합도가 높습니다.",
                "✅ 지역 특성과 LH 공급 방향성이 일치합니다.",
                "✅ 정책 변화에 따른 리스크가 낮습니다."
            ]
        }
    }
    
    report["sections"].append(section_2)
    
    # ============================================================
    # Section 3: 유형별 적합성 비교
    # ============================================================
    
    top_3 = ranking[:3]
    
    section_3 = {
        "section_number": "3",
        "section_title": "유형별 적합성 비교",
        "content": {
            "description": "상위 3개 유형의 세부 점수를 비교 분석합니다.",
            
            "comparison_table": {
                "columns": ["항목", top_3[0].get('type'), top_3[1].get('type'), top_3[2].get('type')],
                "rows": [
                    ["정책 적합성 (30)", f"{top_3[0].get('policy_score')}점", f"{top_3[1].get('policy_score')}점", f"{top_3[2].get('policy_score')}점"],
                    ["입지·수요 (25)", f"{top_3[0].get('location_score')}점", f"{top_3[1].get('location_score')}점", f"{top_3[2].get('location_score')}점"],
                    ["토지가격 (20)", f"{top_3[0].get('price_score')}점", f"{top_3[1].get('price_score')}점", f"{top_3[2].get('price_score')}점"],
                    ["인허가 (15)", f"{top_3[0].get('permit_score')}점", f"{top_3[1].get('permit_score')}점", f"{top_3[2].get('permit_score')}점"],
                    ["운영 안정성 (10)", f"{top_3[0].get('operation_score')}점", f"{top_3[1].get('operation_score')}점", f"{top_3[2].get('operation_score')}점"],
                    ["총점 (100)", f"🏆 {top_3[0].get('total_score')}점", f"{top_3[1].get('total_score')}점", f"{top_3[2].get('total_score')}점"]
                ]
            },
            
            "key_differentiators": [
                f"1위 '{top_3[0].get('type')}': {top_3[0].get('rationale')}",
                f"2위 '{top_3[1].get('type')}': {top_3[1].get('rationale')}",
                f"3위 '{top_3[2].get('type')}': {top_3[2].get('rationale')}"
            ]
        }
    }
    
    report["sections"].append(section_3)
    
    # ============================================================
    # Section 4: 탈락 유형 사유
    # ============================================================
    
    section_4 = {
        "section_number": "4",
        "section_title": "탈락 유형 사유",
        "content": {
            "description": "70점 미만 유형은 LH 심사 통과 확률이 낮아 탈락 처리합니다.",
            
            "rejection_table": {
                "columns": ["공급유형", "점수", "탈락 사유"],
                "rows": [
                    [
                        housing_type,
                        f"{next((s.get('total_score') for s in ranking if s.get('type') == housing_type), 0)}점",
                        reason
                    ]
                    for housing_type, reason in rejection_reasons.items()
                ]
            } if rejection_reasons else {
                "note": "✅ 모든 유형이 70점 이상으로 탈락 유형이 없습니다."
            },
            
            "rejection_logic": [
                "❌ 70점 미만: LH 심사 통과 확률 낮음",
                "❌ 정책 부합도 부족",
                "❌ 입지·수요 불일치",
                "❌ 토지가격 부담 과도"
            ] if rejection_reasons else [
                "✅ 대상지는 다양한 공급유형에 적합합니다.",
                "✅ 최종 유형 선정은 LH 정책 방향에 따라 조정 가능합니다."
            ]
        }
    }
    
    report["sections"].append(section_4)
    
    # ============================================================
    # Section 5: 최종 추천 유형 (1개)
    # ============================================================
    
    section_5 = {
        "section_number": "5",
        "section_title": "최종 추천 유형",
        "content": {
            "recommended_type": recommended_type,
            "lh_pass_score": f"{lh_pass_score}점 (100점 만점)",
            
            "recommendation_box": {
                "title": f"🏆 추천: {recommended_type}",
                "score": lh_pass_score,
                "rationale": ranking[0].get('rationale') if ranking else ""
            },
            
            "detailed_scores": {
                "columns": ["평가 항목", "점수", "만점"],
                "rows": [
                    ["정책 적합성", f"{ranking[0].get('policy_score')}점", "30점"],
                    ["입지·수요 일치", f"{ranking[0].get('location_score')}점", "25점"],
                    ["토지가격 부담", f"{ranking[0].get('price_score')}점", "20점"],
                    ["인허가 리스크", f"{ranking[0].get('permit_score')}점", "15점"],
                    ["운영·민원 안정성", f"{ranking[0].get('operation_score')}점", "10점"]
                ]
            },
            
            "lh_persuasion_text": persuasion_text,
            
            "note": "⚠️ 본 추천은 LH 심사 통과 확률을 최대화하는 유형이며, 최종 결정은 LH 정책 방향과 협의가 필요합니다."
        }
    }
    
    report["sections"].append(section_5)
    
    # ============================================================
    # Section 6: 정책적 설득 논리
    # ============================================================
    
    section_6 = {
        "section_number": "6",
        "section_title": "정책적 설득 논리",
        "content": {
            "description": "LH 내부 검토 및 외부 협의 시 활용 가능한 설득 논리를 제공합니다.",
            
            "persuasion_points": [
                {
                    "point": "정책 부합성",
                    "logic": f"{recommended_type}은(는) 현 정부의 주거 정책 방향과 일치합니다.",
                    "evidence": f"정책 적합성 점수: {ranking[0].get('policy_score')}/30점"
                },
                {
                    "point": "입지 최적화",
                    "logic": f"대상지({zoning.get('zone_type')})는 {recommended_type} 수요층의 주거 선호도가 높습니다.",
                    "evidence": f"입지·수요 일치 점수: {ranking[0].get('location_score')}/25점"
                },
                {
                    "point": "사업성 확보",
                    "logic": f"토지가치(₩{adjusted_land_value:,.0f})는 {recommended_type} 사업 구조에 적합합니다.",
                    "evidence": f"토지가격 부담 점수: {ranking[0].get('price_score')}/20점"
                },
                {
                    "point": "리스크 최소화",
                    "logic": "인허가 및 운영 단계의 리스크가 상대적으로 낮습니다.",
                    "evidence": f"인허가 리스크: {ranking[0].get('permit_score')}/15점, 운영 안정성: {ranking[0].get('operation_score')}/10점"
                }
            ],
            
            "lh_internal_review": [
                f"✅ {recommended_type}은(는) LH 심사 기준 {lh_pass_score}점으로 통과 확률이 가장 높습니다.",
                f"✅ 다른 유형 대비 정책·입지·가격 측면에서 우위를 보입니다.",
                "✅ 감사·민원 대응 시 명확한 선정 논리를 제시할 수 있습니다."
            ],
            
            "next_steps": [
                "1단계: LH 내부 정책 검토 및 승인",
                f"2단계: {recommended_type} 세부 사업 계획 수립",
                "3단계: M4 (건축 규모·형태 검토) 진행",
                "4단계: M5 (사업성·리스크 검증) 수행"
            ],
            
            "final_statement": f"본 검토서는 {recommended_type} 유형이 대상지에서 LH 심사 통과 확률이 가장 높다는 결론을 제시하며, 실제 공급유형 결정은 LH 정책 방향 및 지역 수요를 종합적으로 고려하여 최종 확정되어야 합니다."
        }
    }
    
    report["sections"].append(section_6)
    
    return report
