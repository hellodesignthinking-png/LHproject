#!/usr/bin/env python3
"""
ZeroSite v4.0 M8 Multi-Site Comparison Test
===========================================

3개 후보 부지 동시 분석 및 비교 테스트

Test Sites:
    1. 서울 강남구 역삼동 648-23 (기존 테스트 부지)
    2. 서울 송파구 잠실동 가상 부지
    3. 경기도 성남시 분당구 가상 부지

Author: ZeroSite M8 Team
Date: 2025-12-26
"""

import os
import sys
import json
from datetime import datetime

# Python path setup
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from app.core.context.canonical_land import CanonicalLandContext
from app.modules.m8_comparison.comparison_engine import MultiSiteComparisonEngine


def main():
    """M8 다중 부지 비교 테스트"""
    
    print("\n" + "="*80)
    print("  ZeroSite v4.0 M8 Multi-Site Comparison Test")
    print("  3개 후보 부지 동시 분석")
    print("="*80 + "\n")
    
    # 테스트 부지 3개 정의
    test_sites = [
        {
            "site_id": "site_1",
            "site_name": "서울 강남구 역삼동 648-23",
            "m1_context": CanonicalLandContext(
                parcel_id="1168010100106480023",
                address="서울특별시 강남구 역삼동 648-23",
                road_address="서울특별시 강남구 테헤란로 123",
                coordinates=(37.4995539438207, 127.031393491745),
                sido="서울특별시",
                sigungu="강남구",
                dong="역삼동",
                area_sqm=500.0,
                area_pyeong=151.25,
                land_category="대",
                land_use="주거용",
                zone_type="제2종일반주거지역",
                zone_detail="7층 이하",
                far=200.0,
                bcr=60.0,
                road_width=6.0,
                road_type="중로",
                terrain_height="평지",
                terrain_shape="정형",
                regulations={},
                restrictions=[],
                data_source="Test Data",
                retrieval_date="2025-12-26"
            )
        },
        {
            "site_id": "site_2",
            "site_name": "서울 송파구 잠실동 가상부지",
            "m1_context": CanonicalLandContext(
                parcel_id="1171010100101230045",
                address="서울특별시 송파구 잠실동 123-45",
                road_address="서울특별시 송파구 올림픽로 234",
                coordinates=(37.5133, 127.1028),
                sido="서울특별시",
                sigungu="송파구",
                dong="잠실동",
                area_sqm=800.0,
                area_pyeong=242.0,
                land_category="대",
                land_use="주거용",
                zone_type="제2종일반주거지역",
                zone_detail="7층 이하",
                far=200.0,
                bcr=60.0,
                road_width=8.0,
                road_type="중로",
                terrain_height="평지",
                terrain_shape="정형",
                regulations={},
                restrictions=[],
                data_source="Test Data",
                retrieval_date="2025-12-26"
            )
        },
        {
            "site_id": "site_3",
            "site_name": "경기 성남시 분당구 가상부지",
            "m1_context": CanonicalLandContext(
                parcel_id="4113510300102340056",
                address="경기도 성남시 분당구 정자동 234-56",
                road_address="경기도 성남시 분당구 불정로 345",
                coordinates=(37.3595, 127.1052),
                sido="경기도",
                sigungu="성남시",
                dong="정자동",
                area_sqm=650.0,
                area_pyeong=196.6,
                land_category="대",
                land_use="주거용",
                zone_type="제2종일반주거지역",
                zone_detail="7층 이하",
                far=200.0,
                bcr=60.0,
                road_width=7.0,
                road_type="중로",
                terrain_height="평지",
                terrain_shape="정형",
                regulations={},
                restrictions=[],
                data_source="Test Data",
                retrieval_date="2025-12-26"
            )
        }
    ]
    
    # M8 엔진 초기화
    engine = MultiSiteComparisonEngine()
    
    # 다중 부지 분석 실행
    comparison_report = engine.analyze_multiple_sites(test_sites)
    
    # 결과 출력
    print("\n" + "="*80)
    print("  M8 비교 분석 결과")
    print("="*80 + "\n")
    
    print(f"Report ID: {comparison_report.report_id}")
    print(f"Report Title: {comparison_report.report_title}")
    print(f"Generated: {comparison_report.generated_date}")
    print()
    
    # 비교 매트릭스
    matrix = comparison_report.comparison_matrix
    print("="*80)
    print("  비교 매트릭스 (Comparison Matrix)")
    print("="*80)
    print(f"총 부지 수: {matrix.total_sites}개")
    print(f"GO 부지: {matrix.go_sites}개")
    print(f"CONDITIONAL 부지: {matrix.conditional_sites}개")
    print(f"NO_GO 부지: {matrix.no_go_sites}개")
    print(f"평균 LH 점수: {matrix.avg_lh_score:.1f}/100")
    print(f"평균 NPV: ₩{matrix.avg_npv:,}")
    print(f"평균 IRR: {matrix.avg_irr:.2f}%")
    print()
    
    # 순위
    print("="*80)
    print("  종합 순위 (LH 점수 기준)")
    print("="*80)
    for idx, site in enumerate(matrix.sites, 1):
        print(f"{idx}위. {site.site_name}")
        print(f"    → LH Score: {site.lh_score_total:.1f}/100")
        print(f"    → Judgement: {site.judgement}")
        print(f"    → Grade: {site.grade}")
        print(f"    → NPV: ₩{site.npv_public:,}")
        print(f"    → IRR: {site.irr_public:.2f}%")
        print()
    
    # 카테고리별 최고 부지
    print("="*80)
    print("  카테고리별 최고 부지")
    print("="*80)
    for category, site_id in matrix.best_by_category.items():
        site = next(s for s in matrix.sites if s.site_id == site_id)
        print(f"{category.upper()}: {site.site_name} ({site.section_scores.get(category.upper()[0], 0):.1f}점)")
    print()
    
    # 티어별 분류
    print("="*80)
    print("  티어별 분류")
    print("="*80)
    print(f"TIER 1 (최우선 추천): {len(comparison_report.tier_1_sites)}개")
    for site in comparison_report.tier_1_sites:
        print(f"  - {site.site_name}")
    
    print(f"TIER 2 (적극 검토): {len(comparison_report.tier_2_sites)}개")
    for site in comparison_report.tier_2_sites:
        print(f"  - {site.site_name}")
    
    print(f"TIER 3 (조건부): {len(comparison_report.tier_3_sites)}개")
    for site in comparison_report.tier_3_sites:
        print(f"  - {site.site_name}")
    
    print(f"TIER 4 (미흡): {len(comparison_report.tier_4_sites)}개")
    for site in comparison_report.tier_4_sites:
        print(f"  - {site.site_name}")
    
    print(f"TIER 5 (제외): {len(comparison_report.tier_5_sites)}개")
    for site in comparison_report.tier_5_sites:
        print(f"  - {site.site_name}")
    print()
    
    # 최종 추천
    print("="*80)
    print("  최종 추천")
    print("="*80)
    if comparison_report.top_recommendation:
        top = comparison_report.top_recommendation
        print(f"🏆 1순위 추천: {top.site_name}")
        print(f"   → LH Score: {top.lh_score_total:.1f}/100")
        print(f"   → Judgement: {top.judgement}")
        print(f"   → 강점: {', '.join(top.strengths)}")
        print()
    else:
        print("⚠ 추천 가능한 부지 없음")
        print()
    
    if comparison_report.alternative_recommendations:
        print("대안 추천:")
        for idx, alt in enumerate(comparison_report.alternative_recommendations, 2):
            print(f"{idx}순위. {alt.site_name} ({alt.lh_score_total:.1f}점)")
        print()
    
    # 전략적 인사이트
    print("="*80)
    print("  전략적 인사이트")
    print("="*80)
    for insight in comparison_report.strategic_insights:
        print(f"  {insight}")
    print()
    
    # JSON 저장
    output_dir = os.path.join(script_dir, "output", "comparison")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{comparison_report.report_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_report.to_dict(), f, ensure_ascii=False, indent=2)
    
    print("="*80)
    print(f"  비교 분석 결과 저장")
    print(f"  File: {output_file}")
    print("="*80)
    print()
    
    print("✓ M8 Multi-Site Comparison Test COMPLETED")
    print()


if __name__ == "__main__":
    main()
