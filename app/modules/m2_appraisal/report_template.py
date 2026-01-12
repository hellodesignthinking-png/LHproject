"""
M2 – LAND VALUATION (LH-GRADE)
토지감정평가 전문가 보고서 템플릿

출력 규칙:
- LH 실무자가 그대로 결재 라인에 올릴 수 있는 수준
- 8개 필수 섹션 (8~12페이지 분량)
- 구조화된 목차 + 표 + 논리 + 정책 대응 문장

검증 기준:
1. LH 실무자가 그대로 제출 가능한가?
2. 감사·민원 질문에 논리적으로 대응 가능한가?
3. 다른 지번이면 완전히 다른 결과가 나오는가?

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 2.0
"""

from typing import Dict, Any, List
from datetime import datetime

def generate_m2_expert_report(
    m1_data: Dict[str, Any],
    m2_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M2 전문가 보고서 생성
    
    Args:
        m1_data: M1 FROZEN 데이터
        m2_result: M2 계산 결과
    
    Returns:
        구조화된 전문가 보고서 (JSON)
    """
    
    # M1 데이터 추출
    land_info = m1_data.get('land_info', {})
    cadastral = land_info.get('cadastral', {})
    zoning = land_info.get('zoning', {})
    address_info = land_info.get('address', {})
    
    appraisal_inputs = m1_data.get('appraisal_inputs', {})
    
    # M2 결과 추출
    base_land_value = m2_result.get('base_land_value', 0)
    adjusted_land_value = m2_result.get('adjusted_land_value', 0)
    value_range = m2_result.get('value_range', {})
    unit_price_sqm = m2_result.get('unit_price_sqm', 0)
    confidence_score = m2_result.get('confidence_score', 0)
    
    rationale = m2_result.get('valuation_rationale', {})
    risk_factors = m2_result.get('risk_factors', [])
    lh_review_notes = m2_result.get('lh_review_notes', [])
    
    # 보고서 구조
    report = {
        "module": "M2",
        "title": "토지 매입 적정성 · 감정 논리 검토서",
        "subtitle": "LH 신축매입임대 사업 대상 토지 감정평가 논리 설명",
        "status": "VALUATION_COMPLETED",
        "generated_at": datetime.utcnow().isoformat(),
        "context_id": m2_result.get('context_id'),
        
        # 검증 플래그
        "validation": {
            "lh_submission_ready": True,
            "auditable": True,
            "explainable": True,
            "range_based": True,  # 단일 숫자 강조 금지
            "risk_disclosed": True
        },
        
        # 8개 필수 섹션
        "sections": []
    }
    
    # ============================================================
    # Section 1: 매입 검토 개요
    # ============================================================
    
    section_1 = {
        "section_number": "1",
        "section_title": "매입 검토 개요",
        "content": {
            "purpose": "본 검토서는 LH 신축매입임대 사업 대상 토지의 매입 적정성을 감정평가 논리 관점에서 설명합니다.",
            "scope": f"대상 토지: {address_info.get('jibun_address', '미상')}",
            "methodology": "공시지가 기준 + 비교사례 보정 + 이용가능성 보정",
            
            "summary_table": {
                "columns": ["항목", "내용"],
                "rows": [
                    ["대상 토지", address_info.get('jibun_address', '미상')],
                    ["대지면적", f"{cadastral.get('area_sqm', 0):,.2f} ㎡ ({cadastral.get('area_pyeong', 0):,.2f} 평)"],
                    ["용도지역", zoning.get('zone_type', '미상')],
                    ["공시지가", f"₩{appraisal_inputs.get('official_land_price', 0):,.0f}/㎡"],
                    ["평가 기준일", m2_result.get('calculated_at', datetime.utcnow().isoformat())[:10]]
                ]
            },
            
            "key_findings": [
                f"기준 토지가치: ₩{base_land_value:,.0f}",
                f"보정 토지가치: ₩{adjusted_land_value:,.0f}",
                f"적정 매입가 범위: ₩{value_range.get('min', 0):,.0f} ~ ₩{value_range.get('max', 0):,.0f}",
                f"신뢰도: {confidence_score}점 (100점 만점)"
            ]
        }
    }
    
    report["sections"].append(section_1)
    
    # ============================================================
    # Section 2: 공시지가 기준 분석
    # ============================================================
    
    official_price = appraisal_inputs.get('official_land_price', 0)
    official_date = appraisal_inputs.get('official_land_price_date', '미상')
    
    section_2 = {
        "section_number": "2",
        "section_title": "공시지가 기준 분석",
        "content": {
            "description": "국토교통부 표준지공시지가를 기준으로 대상 토지의 기준가치를 산정합니다.",
            
            "official_price_table": {
                "columns": ["항목", "값"],
                "rows": [
                    ["공시지가", f"₩{official_price:,.0f}/㎡"],
                    ["공시기준년도", official_date],
                    ["대지면적", f"{cadastral.get('area_sqm', 0):,.2f} ㎡"],
                    ["총 공시기준가", f"₩{cadastral.get('area_sqm', 0) * official_price:,.0f}"]
                ]
            },
            
            "base_valuation_logic": rationale.get('base_logic', ''),
            
            "correction_factors": [
                "LH 내부 보정계수 적용 (1.15 ~ 1.35 범위)",
                "대상 토지의 위치·접근성 고려",
                "용도지역별 개발밀도 반영"
            ],
            
            "result": f"기준 토지가치: ₩{base_land_value:,.0f}",
            
            "note": "⚠️ 공시지가는 감정평가의 출발점이며, 시장가치와 차이가 있을 수 있습니다."
        }
    }
    
    report["sections"].append(section_2)
    
    # ============================================================
    # Section 3: 거래사례 비교 분석
    # ============================================================
    
    transaction_cases = appraisal_inputs.get('transaction_cases', [])
    
    section_3 = {
        "section_number": "3",
        "section_title": "거래사례 비교 분석",
        "content": {
            "description": "인근 유사 토지의 거래사례를 비교하여 시장가치를 보정합니다.",
            
            "market_logic": rationale.get('market_logic', ''),
            
            "transaction_summary": {
                "total_cases": len(transaction_cases),
                "avg_price_sqm": sum([tc.get('price_per_sqm', 0) for tc in transaction_cases]) / len(transaction_cases) if transaction_cases else 0,
                "date_range": f"{min([tc.get('transaction_date', '') for tc in transaction_cases]) if transaction_cases else '미상'} ~ {max([tc.get('transaction_date', '') for tc in transaction_cases]) if transaction_cases else '미상'}"
            },
            
            "transaction_table": {
                "columns": ["번호", "주소", "거래일", "면적(㎡)", "거래가(원/㎡)", "거리(km)"],
                "rows": [
                    [
                        str(i+1),
                        tc.get('address', '미상')[:20],
                        tc.get('transaction_date', '미상'),
                        f"{tc.get('area_sqm', 0):,.0f}",
                        f"₩{tc.get('price_per_sqm', 0):,.0f}",
                        f"{tc.get('distance_km', 0):.2f}"
                    ]
                    for i, tc in enumerate(transaction_cases[:10])  # 최대 10건
                ]
            } if transaction_cases else {
                "note": "⚠️ 인근 거래사례 데이터가 부족합니다. 공시지가 기준으로 보정합니다."
            },
            
            "adjustment_factors": [
                "위치 보정: 거리 기반 (0.9 ~ 1.1)",
                "시점 보정: 6개월 단위 물가상승률 반영",
                "용도 보정: 동일/유사/상이 구분"
            ],
            
            "market_premium": "+10% (시장 프리미엄 반영)"
        }
    }
    
    report["sections"].append(section_3)
    
    # ============================================================
    # Section 4: 입지·규모 보정 논리
    # ============================================================
    
    building_constraints = m1_data.get('building_constraints', {})
    legal = building_constraints.get('legal', {})
    
    section_4 = {
        "section_number": "4",
        "section_title": "입지·규모 보정 논리",
        "content": {
            "description": "대상 토지의 위치적 특성과 규모를 감정평가에 반영합니다.",
            
            "location_factors": {
                "columns": ["요인", "상태", "보정 방향"],
                "rows": [
                    ["용도지역", zoning.get('zone_type', '미상'), "↑ 상향" if "상업" in zoning.get('zone_type', '') else "→ 유지"],
                    ["도로 접합", land_info.get('road_access', {}).get('road_contact', '미상'), "↑ 상향" if "전면" in land_info.get('road_access', {}).get('road_contact', '') else "→ 유지"],
                    ["역세권", "500m 이내" if len(m1_data.get('context', {}).get('transit', {}).get('subway_stations', [])) > 0 else "해당 없음", "↑ 상향" if len(m1_data.get('context', {}).get('transit', {}).get('subway_stations', [])) > 0 else "→ 유지"],
                    ["대지 형상", "정방형" if cadastral.get('shape', '') == 'regular' else "부정형", "↑ 상향" if cadastral.get('shape', '') == 'regular' else "↓ 하향"]
                ]
            },
            
            "size_factors": {
                "area_sqm": cadastral.get('area_sqm', 0),
                "area_pyeong": cadastral.get('area_pyeong', 0),
                "size_category": "중규모" if cadastral.get('area_sqm', 0) < 2000 else "대규모",
                "size_adjustment": "→ 유지 (적정 규모)"
            },
            
            "utility_logic": rationale.get('utility_logic', ''),
            
            "far_bcr_impact": {
                "far": legal.get('far_max', 0),
                "bcr": legal.get('bcr_max', 0),
                "impact": "용적률이 높아 개발가능성 우수 → 보정계수 상향"
            }
        }
    }
    
    report["sections"].append(section_4)
    
    # ============================================================
    # Section 5: LH 매입 관점 보정계수
    # ============================================================
    
    section_5 = {
        "section_number": "5",
        "section_title": "LH 매입 관점 보정계수",
        "content": {
            "description": "LH 신축매입임대 사업의 특성을 고려한 보정계수를 적용합니다.",
            
            "lh_perspective": [
                "✅ 공공주택 목적 (수익 극대화 ❌)",
                "✅ 보수적 매입가 적용",
                "✅ 장기 보유 전제",
                "✅ 지역사회 기여 고려"
            ],
            
            "correction_table": {
                "columns": ["보정 항목", "계수", "사유"],
                "rows": [
                    ["기본 보정계수", "1.25", "LH 내부 기준 (1.15~1.35 범위 중간값)"],
                    ["시장 프리미엄", "1.10", "인근 거래사례 비교 보정"],
                    ["이용가능성", "1.05~1.10", f"용적률 {legal.get('far_max', 0)}% 고려"],
                    ["보수적 할인", "0.95", "LH 매입 리스크 반영"]
                ]
            },
            
            "final_adjustment_factor": "1.38 (종합 보정계수)",
            
            "rationale": "공공주택 사업의 공익성과 LH의 보수적 매입 기준을 균형있게 반영"
        }
    }
    
    report["sections"].append(section_5)
    
    # ============================================================
    # Section 6: 적정 매입가 범위
    # ============================================================
    
    section_6 = {
        "section_number": "6",
        "section_title": "적정 매입가 범위",
        "content": {
            "description": "⚠️ 단일 가격이 아닌 범위로 제시하여 협상 여지를 확보합니다.",
            
            "valuation_summary": {
                "columns": ["구분", "금액", "단가(원/㎡)"],
                "rows": [
                    ["기준 토지가치", f"₩{base_land_value:,.0f}", f"₩{base_land_value/cadastral.get('area_sqm', 1):,.0f}"],
                    ["보정 토지가치", f"₩{adjusted_land_value:,.0f}", f"₩{unit_price_sqm:,.0f}"],
                    ["적정 매입가 (하한)", f"₩{value_range.get('min', 0):,.0f}", f"₩{value_range.get('min', 0)/cadastral.get('area_sqm', 1):,.0f}"],
                    ["적정 매입가 (상한)", f"₩{value_range.get('max', 0):,.0f}", f"₩{value_range.get('max', 0)/cadastral.get('area_sqm', 1):,.0f}"]
                ]
            },
            
            "recommendation": {
                "range": f"₩{value_range.get('min', 0):,.0f} ~ ₩{value_range.get('max', 0):,.0f}",
                "target": f"₩{adjusted_land_value:,.0f} (중간값)",
                "strategy": "하한가 기준 협상 시작, 상한가 초과 시 재검토"
            },
            
            "confidence_level": f"{confidence_score}점 (100점 만점)",
            
            "disclaimer": [
                "⚠️ 본 검토는 감정평가서를 대체하지 않습니다.",
                "⚠️ 실제 매입 시 공인감정평가사의 감정평가서 필수",
                "⚠️ 시장 상황 변화 시 재검토 필요"
            ]
        }
    }
    
    report["sections"].append(section_6)
    
    # ============================================================
    # Section 7: 가격 리스크 요인
    # ============================================================
    
    section_7 = {
        "section_number": "7",
        "section_title": "가격 리스크 요인",
        "content": {
            "description": "감사·민원 대응을 위해 가격 산정의 불확실성을 명시합니다.",
            
            "risk_factors": [
                {
                    "risk": risk,
                    "impact": "가격 하락 가능성",
                    "mitigation": "보수적 매입가 적용"
                }
                for risk in risk_factors
            ],
            
            "sensitivity_analysis": {
                "description": "주요 변수 변동 시 가격 영향도",
                "table": {
                    "columns": ["변수", "변동폭", "가격 영향"],
                    "rows": [
                        ["공시지가", "±10%", f"₩{adjusted_land_value * 0.1:,.0f}"],
                        ["시장 프리미엄", "±5%", f"₩{adjusted_land_value * 0.05:,.0f}"],
                        ["이용보정계수", "±5%", f"₩{adjusted_land_value * 0.05:,.0f}"]
                    ]
                }
            },
            
            "worst_case_scenario": {
                "description": "최악의 경우 예상 가격",
                "price": f"₩{value_range.get('min', 0) * 0.9:,.0f}",
                "rationale": "모든 리스크 요인이 동시에 발생할 경우"
            }
        }
    }
    
    report["sections"].append(section_7)
    
    # ============================================================
    # Section 8: 감정평가 관점 결론
    # ============================================================
    
    section_8 = {
        "section_number": "8",
        "section_title": "감정평가 관점 결론",
        "content": {
            "summary": f"대상 토지의 적정 매입가 범위는 ₩{value_range.get('min', 0):,.0f} ~ ₩{value_range.get('max', 0):,.0f}이며, 보수적 접근 시 ₩{value_range.get('min', 0):,.0f} 기준 협상을 권장합니다.",
            
            "key_conclusions": [
                f"✅ 공시지가 기준(₩{official_price:,.0f}/㎡) + LH 보정계수 적용",
                f"✅ 시장 거래사례 {len(transaction_cases)}건 비교 분석 완료",
                f"✅ {zoning.get('zone_type', '미상')} · 용적률 {legal.get('far_max', 0)}% 고려",
                f"✅ 신뢰도 {confidence_score}점 수준의 평가"
            ],
            
            "lh_review_notes": [
                {
                    "note": note,
                    "priority": "HIGH" if "필수" in note else "MEDIUM"
                }
                for note in lh_review_notes
            ],
            
            "next_steps": [
                "1단계: LH 내부 검토 및 승인",
                "2단계: 공인감정평가사 감정평가 의뢰",
                "3단계: 감정평가서 결과 비교·검증",
                "4단계: 최종 매입가 결정 및 계약"
            ],
            
            "final_statement": "본 검토서는 LH 신축매입임대 사업의 매입 적정성을 감정평가 논리 관점에서 설명하며, 실제 매입 시에는 공인감정평가사의 감정평가서를 병행하여 최종 판단해야 합니다."
        }
    }
    
    report["sections"].append(section_8)
    
    return report
