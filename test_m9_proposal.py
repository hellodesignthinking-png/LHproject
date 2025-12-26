#!/usr/bin/env python3
"""
ZeroSite v4.0 M9 LH Proposal Generator Test
===========================================

LH 공식 제안서 자동 생성 테스트

Author: ZeroSite M9 Team
Date: 2025-12-26
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.context.canonical_land import CanonicalLandContext
from app.modules.m2_appraisal.service import AppraisalService
from app.modules.m3_lh_demand.service import LHDemandService
from app.modules.m4_capacity.service_v2 import CapacityServiceV2
from app.modules.m5_feasibility.service import FeasibilityService
from app.modules.m6_lh_review.service_v3 import LHReviewServiceV3
from app.modules.m9_lh_proposal.proposal_generator import LHProposalGenerator


def main():
    """M9 LH 제안서 생성 테스트"""
    
    print("\n" + "="*80)
    print("  ZeroSite v4.0 M9 LH Proposal Generator Test")
    print("  LH 공식 제안서 자동 생성")
    print("="*80 + "\n")
    
    # 테스트 부지: 서울 강남구 역삼동 648-23
    land_ctx = CanonicalLandContext(
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
    
    # M2-M6 파이프라인 실행
    print("[STEP 0] M2→M6 파이프라인 실행 중...\n")
    
    # M2: 감정평가
    print("  M2: 감정평가...")
    m2_service = AppraisalService(use_enhanced_services=True)
    m2_result = m2_service.run(land_ctx, asking_price=None)
    print(f"  ✓ 감정평가액: ₩{m2_result.land_value:,}\n")
    
    # M3: 세대 유형
    print("  M3: 세대 유형 선정...")
    m3_service = LHDemandService()
    m3_result = m3_service.run(land_ctx)
    print(f"  ✓ 선정 유형: {m3_result.selected_type_name}\n")
    
    # M4: 건축 규모
    print("  M4: 건축 규모 산출...")
    m4_service = CapacityServiceV2()
    m4_result = m4_service.run(land_ctx, m3_result)
    print(f"  ✓ 인센티브 세대수: {m4_result.incentive_capacity.total_units}세대\n")
    
    # M5: 사업성
    print("  M5: 사업성 분석...")
    m5_service = FeasibilityService()
    m5_result = m5_service.run(m2_result, m4_result)
    print(f"  ✓ NPV: ₩{m5_result.financial_metrics.npv_public:,}\n")
    
    # M6: LH 종합 평가
    print("  M6: LH 종합 평가...")
    m6_service = LHReviewServiceV3()
    m6_result = m6_service.run(
        land_ctx=land_ctx,
        appraisal_ctx=m2_result,
        housing_type_ctx=m3_result,
        capacity_ctx=m4_result,
        feasibility_ctx=m5_result
    )
    print(f"  ✓ 판정: {m6_result.judgement.value} ({m6_result.lh_score_total:.1f}/100)\n")
    
    print("="*80 + "\n")
    
    # M9: LH 제안서 생성
    print("[STEP 1] M9: LH 제안서 생성 시작\n")
    
    generator = LHProposalGenerator(output_dir="output/proposals")
    
    # Word + PDF + 첨부 서류 + 제출 패키지 생성
    result = generator.generate_full_proposal(
        land_ctx=land_ctx,
        appraisal_ctx=m2_result,
        housing_type_ctx=m3_result,
        capacity_ctx=m4_result,
        feasibility_ctx=m5_result,
        m6_result=m6_result,
        format="both"  # Word + PDF
    )
    
    # 결과 출력
    print("\n" + "="*80)
    print("  M9 LH 제안서 생성 완료")
    print("="*80)
    print(f"\n📄 Word 문서:")
    print(f"   {result['word_path']}")
    print(f"\n📕 PDF 문서:")
    print(f"   {result['pdf_path']}")
    print(f"\n📎 첨부 파일 ({len(result['attachments'])}개):")
    for attachment in result['attachments']:
        print(f"   - {os.path.basename(attachment)}")
    print(f"\n📦 제출 패키지:")
    print(f"   {result['package_path']}")
    print("\n" + "="*80)
    
    print("\n✓ M9 LH Proposal Generator Test COMPLETED\n")


if __name__ == "__main__":
    main()
