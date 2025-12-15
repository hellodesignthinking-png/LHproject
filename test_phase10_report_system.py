"""
ZeroSite Phase 10: 5-Type Report System Test

Tests all 5 report types with mock decision data.

Usage:
    python test_phase10_report_system.py
"""

from pathlib import Path
from datetime import datetime
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.report_types_v11.base_report_engine import (
    ZeroSiteDecision,
    ParcelData,
    CapexData,
    ROIData,
    LHScoreData,
    ComparableValuation,
    VerifiedCostData,
    BuildingScaleData
)
from app.report_types_v11.community_injector import (
    inject_community_auto,
    CommunitySelector
)
from app.report_types_v11.export_engine import export_all_reports


def create_mock_decision() -> ZeroSiteDecision:
    """Create mock decision object for testing"""
    
    # Parcel data
    parcels = [
        ParcelData(
            address="서울특별시 강남구 역삼동 123-45",
            land_area=500.0,
            building_coverage_ratio=60.0,
            floor_area_ratio=300.0,
            land_use_zone="제2종일반주거지역",
            current_land_price=2500000.0
        )
    ]
    
    # Building scale
    scale = BuildingScaleData(
        max_building_area=300.0,
        max_floor_area=1500.0,
        estimated_units=20,
        avg_unit_size=60.0,
        total_floors=8
    )
    
    # CAPEX
    capex = CapexData(
        land_acquisition=1250000000,
        construction_cost=3000000000,
        design_supervision=180000000,
        financing_cost=150000000,
        contingency=220000000,
        total_capex=4800000000
    )
    
    # ROI
    roi = ROIData(
        roi_percent=12.5,
        irr_percent=10.8,
        npv=580000000,
        payback_period_months=96,
        annual_rental_income=650000000,
        total_rental_income=5200000000
    )
    
    # LH Score
    lh_score = LHScoreData(
        location_score=22.0,
        transportation_score=18.5,
        education_score=19.0,
        amenities_score=13.5,
        demand_score=17.0,
        total_score=90.0,
        grade="A"
    )
    
    # Comparable Valuation
    comparable_valuation = ComparableValuation(
        estimated_price_per_m2=2650000,
        estimated_total_price=1325000000,
        confidence_level=0.92,
        comparable_transactions=15,
        valuation_method="Comparable Sales Analysis",
        price_range_min=2450000,
        price_range_max=2850000
    )
    
    # Verified Cost (Phase 8 placeholder)
    verified_cost = VerifiedCostData(
        cost_per_m2=None,
        year=2025,
        region="서울",
        unit_type="Youth",
        status="pending_phase8"
    )
    
    # Create decision
    decision = ZeroSiteDecision(
        address="서울특별시 강남구 역삼동 123-45",
        parcels=parcels,
        strategy="single",
        recommended_type="Youth",
        scale=scale,
        capex=capex,
        roi=roi,
        lh_score=lh_score,
        comparable_valuation=comparable_valuation,
        verified_cost=verified_cost,
        final_grade="A",
        recommendation="GO",
        key_strengths=[
            "우수한 교통 접근성 (지하철 2호선 역삼역 도보 5분)",
            "강남구 핵심 상권 인접 (테헤란로 IT밸리)",
            "높은 투자수익률 (ROI 12.5%, IRR 10.8%)",
            "청년층 수요 집중 지역 (스타트업 밀집)",
            "우수한 교육 환경 (초·중·고 도보권)"
        ],
        key_weaknesses=[
            "높은 토지 매입 단가 (㎡당 250만원)",
            "주차 공간 확보 제약",
            "인근 경쟁 단지 존재 (반경 500m 내 3개 단지)"
        ],
        next_steps=[
            "토지주와 매매 협상 개시",
            "건축 설계 용역 발주",
            "LH 사전 상담 신청",
            "금융기관 대출 심사 진행",
            "환경영향평가 착수"
        ]
    )
    
    return decision


def test_phase10_system():
    """Test Phase 10 report system"""
    
    print("\n" + "="*80)
    print("🚀 ZeroSite Phase 10: 5-Type Report System Test")
    print("="*80 + "\n")
    
    # Step 1: Create mock decision
    print("📊 Step 1: Creating mock decision data...")
    decision = create_mock_decision()
    print(f"✓ Decision created: {decision.analysis_id}")
    print(f"   Address: {decision.address}")
    print(f"   Recommended Type: {decision.recommended_type}")
    print(f"   Strategy: {decision.strategy}")
    print(f"   Final Grade: {decision.final_grade}")
    print()
    
    # Step 2: Inject community module
    print("🏘️  Step 2: Injecting community module...")
    inject_community_auto(decision)
    
    if decision.community:
        print(f"✓ Community module injected: {decision.community.module_name}")
        print(f"   Target Type: {decision.community.target_type}")
        print(f"   Facilities: {len(decision.community.facilities)}")
        print(f"   Estimated Cost: {decision.community.estimated_cost:,}원")
    else:
        print("✗ Community module injection failed")
    print()
    
    # Step 3: Export all reports
    print("📄 Step 3: Exporting all 5 report types...")
    print("   Formats: HTML, JSON")
    print("   (PDF export requires WeasyPrint - optional)")
    print()
    
    start_time = datetime.now()
    
    # Export in HTML and JSON (PDF optional)
    try:
        results = export_all_reports(
            decision,
            formats=["html", "json"],  # PDF requires WeasyPrint
            output_dir=Path("./reports")
        )
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Display results
        print("\n" + "-"*80)
        print("📊 Export Results:")
        print("-"*80 + "\n")
        
        success_count = 0
        failed_count = 0
        
        for report_type, format_results in results.items():
            print(f"\n{report_type.upper()}:")
            for format_type, result in format_results.items():
                if result.success:
                    success_count += 1
                    if format_type == "html" and result.html_path:
                        print(f"  ✓ {format_type.upper()}: {result.html_path}")
                    elif format_type == "json" and result.json_path:
                        print(f"  ✓ {format_type.upper()}: {result.json_path}")
                    elif format_type == "pdf" and result.file_path:
                        print(f"  ✓ {format_type.upper()}: {result.file_path}")
                    print(f"     Generation time: {result.generation_time_seconds:.3f}s")
                else:
                    failed_count += 1
                    print(f"  ✗ {format_type.upper()} failed: {result.error_message}")
        
        # Summary
        print("\n" + "="*80)
        print(f"🎯 SUMMARY")
        print("="*80)
        print(f"Total exports: {success_count + failed_count}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {failed_count}")
        print(f"⏱  Total time: {total_time:.2f}s")
        print(f"⏱  Average time: {total_time / (success_count + failed_count):.2f}s per export")
        print()
        
        if success_count > 0:
            print("✅ Phase 10 Test PASSED!")
            print()
            print("📂 Check ./reports/ directory for generated files")
        else:
            print("❌ Phase 10 Test FAILED!")
            print("   No reports were successfully generated")
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return success_count > 0


if __name__ == "__main__":
    success = test_phase10_system()
    sys.exit(0 if success else 1)
