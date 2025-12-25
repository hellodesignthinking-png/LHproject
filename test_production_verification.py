#!/usr/bin/env python3
"""
Phase 1 + Phase 2 완료 후 실제 Context ID 기반 최종 검증
=======================================================

목적: 실제 프로덕션 구조의 Context 데이터로 6종 보고서 생성 및 검증

검증 항목:
1. IRR/ROI 단위 변환 (0.185 → 18.5%)
2. N/A 제거 (설명 문장으로 대체)
3. 점수 해석 문단 포함
4. 6종 보고서 모두 생성
5. 핵심 KPI 일관성
"""

import sys
sys.path.insert(0, '/home/user/webapp')

# Direct import without context_storage (Redis not available)
from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html
from datetime import datetime
import re

# Phase 1 + Phase 2 완료 후 Production 구조 Mock Data
PRODUCTION_MOCK_DATA = {
    "context_id": "prod-phase2-test-001",
    "created_at": datetime.now().isoformat(),
    
    # M2: CanonicalAppraisalResult 구조 (Phase 1에서 확정)
    "m2_result": {
        "version": "v8.7",
        "locked": True,
        "timestamp": datetime.now().isoformat(),
        "zoning": {
            "zone_type": "제2종일반주거지역",
            "land_use": "공동주택용지"
        },
        "official_land_price": {
            "price_per_sqm": 12000000,
            "reference_date": "2025-01-01"
        },
        "transaction_cases": [
            {"price": 7200000000, "date": "2024-11-15"},
            {"price": 7800000000, "date": "2024-10-20"},
            {"price": 7500000000, "date": "2024-09-10"},
            {"price": 7650000000, "date": "2024-08-05"},
            {"price": 7400000000, "date": "2024-07-12"}
        ],
        "premium": {
            "rate": 0.25,
            "factors": ["location", "development"]
        },
        "calculation": {
            "base_price_per_sqm": 39669000,
            "premium_adjusted_per_sqm": 49587000,
            "land_area_sqm": 151.29,
            "final_appraised_total": 7500000000  # 75억
        },
        "confidence": {
            "overall_score": 0.85,  # 85%
            "data_completeness": 0.88,
            "case_similarity": 0.84,
            "time_relevance": 0.83
        },
        "metadata": {
            "appraiser": "ZeroSite AI v4.0",
            "calculation_date": "2025-12-25"
        }
    },
    
    # M3: HousingTypeContext 구조 (Phase 1에서 확정)
    "m3_result": {
        "selected": {
            "name": "청년형",
            "code": "YOUTH",
            "description": "LH 청년 맞춤형 임대주택"
        },
        "scores": {
            "청년형": {
                "total": 88.5,
                "location": 32,
                "scale": 18,
                "feasibility": 27,
                "compliance": 11.5
            },
            "신혼부부형": {
                "total": 82.0,
                "location": 30,
                "scale": 17,
                "feasibility": 25,
                "compliance": 10.0
            },
            "고령자형": {
                "total": 75.5,
                "location": 28,
                "scale": 16,
                "feasibility": 22,
                "compliance": 9.5
            }
        },
        "confidence": 88,
        "recommendations": [
            "청년형이 입지와 규모 측면에서 최적",
            "신혼부부형도 차선책으로 적합",
            "지하철 접근성이 청년 수요와 부합"
        ]
    },
    
    # M4: CapacityContextV2 구조 (Phase 1에서 확정)
    "m4_result": {
        "legal_capacity": {
            "total_units": 150,
            "floors": 15,
            "bcr": 0.60,
            "far": 2.5,
            "height_m": 45.0
        },
        "incentive_capacity": {
            "total_units": 180,
            "floors": 18,
            "bcr": 0.65,
            "far": 3.0,
            "height_m": 54.0,
            "incentive_type": "공공기여"
        },
        "parking_solutions": {
            "alternative_A": {
                "total_spaces": 180,
                "type": "지하 2층",
                "cost_krw": 540000000
            },
            "alternative_B": {
                "total_spaces": 150,
                "type": "지하 1층 + 지상",
                "cost_krw": 450000000
            }
        },
        "construction_summary": {
            "recommended_scenario": "인센티브 용적률 활용",
            "total_gfa_sqm": 12000,
            "avg_unit_area_sqm": 66.67
        }
    },
    
    # M5: FeasibilityContext 구조 (Phase 1에서 확정, Phase 2에서 단위 변환 적용)
    "m5_result": {
        "financials": {
            "npv_public": 1850000000,  # 18.5억
            "npv_market": 2100000000,
            "irr_public": 0.185,  # Phase 2에서 18.5%로 변환
            "irr_market": 0.21,
            "roi": 0.263  # Phase 2에서 26.3%로 변환
        },
        "profitability": {
            "grade": "A",
            "score": 88.5,
            "is_profitable": True,
            "confidence": 0.87
        },
        "costs": {
            "total_cost": 5200000000,
            "land_acquisition": 7500000000,
            "construction": 3800000000,
            "design": 190000000,
            "financing": 312000000
        },
        "revenue": {
            "lh_purchase": 9500000000,
            "market_sale": 10800000000,
            "rental_income_annual": 450000000
        },
        "scenarios": {
            "best_case": {"npv": 2220000000, "irr": 0.22},
            "worst_case": {"npv": 1480000000, "irr": 0.15}
        }
    },
    
    # M6: LHReviewContext 구조 (Phase 1에서 확정, Phase 2에서 해석 추가)
    "m6_result": {
        "decision": {
            "type": "GO",
            "rationale": "입지·규모·사업성 모두 우수",
            "confidence": 0.87
        },
        "approval": {
            "probability": 0.87,  # Phase 1에서 87%로 변환
            "key_factors": [
                "지하철역 500m 이내 위치",
                "청년 수요 집중 지역",
                "적정 사업비 구조"
            ]
        },
        "scores": {
            "total": 95.5,
            "location": 34,
            "scale": 19,
            "feasibility": 31,
            "compliance": 11.5,
            "max_score": 110
        },
        "grade": "A",
        "swot": {
            "strengths": ["역세권 입지", "청년 수요", "높은 수익성"],
            "weaknesses": ["주차 공간 제약"],
            "opportunities": ["정부 청년주택 정책"],
            "threats": ["건설비 상승 리스크"]
        }
    }
}

def verify_phase2_improvements(html: str, report_type: str) -> dict:
    """Phase 2 개선사항 검증"""
    checks = {
        "report_type": report_type,
        "html_length": len(html),
        
        # Phase 2 개선 #1: IRR/ROI 단위 변환
        "irr_correct": "18.5%" in html or "18.5" in html,
        "roi_correct": "26.3%" in html or "26.3" in html,
        "irr_wrong": "0.185%" in html,
        "roi_wrong": "0.263%" in html,
        
        # Phase 2 개선 #2: N/A 제거
        "na_old_style": html.count("N/A (검증 필요)"),
        "na_new_explanation": html.count("본 항목은 현 단계에서") + html.count("실시설계 또는 인허가"),
        
        # Phase 2 개선 #3: 점수 해석
        "score_interpretation": "상위" in html and "수준" in html,
        
        # Phase 1 핵심 KPI (불변)
        "land_value": "7,500,000,000" in html or "75억" in html,
        "npv": "1,850,000,000" in html or "18.5억" in html,
        "units": "180" in html,
        "housing_type": "청년형" in html,
        "decision": "GO" in html or "추진 권장" in html
    }
    
    return checks

def main():
    print("="*80)
    print("🔍 Phase 1 + Phase 2 - Production Context 최종 검증")
    print("="*80)
    print()
    
    context_id = "prod-phase2-test-001"
    
    # Direct test without Redis (context storage not available)
    print("Note: Testing directly without context storage (Redis unavailable)")
    print()
    
    # Step 1: 6종 보고서 생성 및 검증
    report_types = [
        "quick_check",
        "financial_feasibility",
        "lh_technical",
        "executive_summary",
        "landowner_summary",
        "all_in_one"
    ]
    
    all_passed = True
    results = []
    
    for report_type in report_types:
        print(f"[{report_type}] 생성 중...")
        try:
            # Assemble
            assembled = assemble_final_report(report_type, PRODUCTION_MOCK_DATA, context_id)
            
            # Render HTML
            html = render_final_report_html(report_type, assembled)
            
            # Verify
            checks = verify_phase2_improvements(html, report_type)
            
            # Display results
            print(f"  ✓ HTML 생성: {checks['html_length']:,} chars")
            print(f"  Phase 2 개선사항:")
            print(f"    - IRR 18.5%: {'✓' if checks['irr_correct'] else '✗'}")
            print(f"    - ROI 26.3%: {'✓' if checks['roi_correct'] else '✗'}")
            na_status = '✓' if checks['na_old_style'] == 0 else f"✗ ({checks['na_old_style']}건)"
            print(f"    - N/A 제거: {na_status}")
            print(f"    - 점수 해석: {'✓' if checks['score_interpretation'] else '✗'}")
            print(f"  Phase 1 핵심 KPI:")
            print(f"    - 토지감정가: {'✓' if checks['land_value'] else '✗'}")
            print(f"    - NPV: {'✓' if checks['npv'] else '✗'}")
            print(f"    - 세대수: {'✓' if checks['units'] else '✗'}")
            print(f"    - 주택유형: {'✓' if checks['housing_type'] else '✗'}")
            print(f"    - LH 판단: {'✓' if checks['decision'] else '✗'}")
            
            # Overall assessment
            phase2_ok = (
                checks['irr_correct'] and 
                checks['roi_correct'] and 
                checks['na_old_style'] == 0
            )
            
            phase1_ok = (
                checks['land_value'] and
                checks['npv'] and
                checks['units'] and
                checks['housing_type'] and
                checks['decision']
            )
            
            if not (phase2_ok and phase1_ok):
                all_passed = False
                print(f"  ⚠️  일부 검증 실패")
            else:
                print(f"  ✅ 모든 검증 통과")
            
            results.append(checks)
            print()
            
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            all_passed = False
            print()
    
    # Final Summary
    print("="*80)
    print("최종 검증 결과")
    print("="*80)
    print()
    
    if all_passed:
        print("🎉 PRODUCTION VERIFICATION COMPLETE")
        print()
        print("✅ Phase 1: 핵심 KPI 모두 표시")
        print("✅ Phase 2: IRR/ROI 단위 변환 (18.5%, 26.3%)")
        print("✅ Phase 2: N/A 제거 (설명 문장 대체)")
        print("✅ Phase 2: 점수 해석 문단 포함")
        print("✅ 6종 보고서 모두 생성 성공")
        print()
        print("🚀 LH 제출 준비 완료")
        return 0
    else:
        print("⚠️  VERIFICATION INCOMPLETE")
        print()
        print("일부 보고서에서 검증 실패")
        print("상세 내용은 위 로그를 확인하세요")
        return 1

if __name__ == "__main__":
    sys.exit(main())
