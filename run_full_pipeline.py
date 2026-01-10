#!/usr/bin/env python3
"""
실제 파이프라인 실행 및 결과 저장
M1-M6 전체 분석 수행
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Import all pipeline modules
from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline

async def run_pipeline():
    """실제 파이프라인 실행"""
    
    # Test address
    test_address = "서울특별시 강남구 역삼동 123-45"
    test_context_id = "real_pipeline_test_001"
    
    print("=" * 60)
    print("🚀 ZeroSite 전체 파이프라인 실행")
    print("=" * 60)
    print(f"주소: {test_address}")
    print(f"Context ID: {test_context_id}")
    print()
    
    # Initialize pipeline
    pipeline = ZeroSitePipeline()
    
    print("📊 파이프라인 실행 중...")
    print()
    
    try:
        # Run full pipeline (M1-M6)
        result = await pipeline.run_full_analysis(
            address=test_address,
            context_id=test_context_id
        )
        
        print("✅ 파이프라인 실행 완료!")
        print()
        
        # Display results summary
        if result.land:
            print(f"✅ M1 토지 정보: {result.land.address}")
            print(f"   - 면적: {result.land.area_sqm:.2f}㎡ ({result.land.area_pyeong:.2f}평)")
            print(f"   - 용도지역: {result.land.zone_type}")
            print()
        
        if result.appraisal:
            print(f"✅ M2 토지감정평가: {result.appraisal.land_value:,.0f}원")
            print(f"   - 단가: {result.appraisal.unit_price_sqm:,.0f}원/㎡")
            print(f"   - 신뢰도: {result.appraisal.confidence_level} ({result.appraisal.confidence_score*100:.1f}%)")
            print(f"   - 거래사례: {result.appraisal.transaction_count}건")
            print()
        
        if result.housing_type:
            print(f"✅ M3 공급 유형: {result.housing_type.selected_type}")
            print(f"   - 수요 예측: {result.housing_type.demand_prediction}")
            print()
        
        if result.capacity:
            print(f"✅ M4 건축 규모")
            print(f"   - 법정 용적률: {result.capacity.legal_capacity.applied_far}%")
            print(f"   - 인센티브 용적률: {result.capacity.incentive_capacity.applied_far}%")
            print(f"   - 총 세대수: {result.capacity.incentive_capacity.total_units}세대")
            print()
        
        if result.feasibility:
            print(f"✅ M5 사업성 분석")
            print(f"   - IRR: {result.feasibility.irr*100:.2f}%")
            print(f"   - NPV: {result.feasibility.npv:,.0f}원")
            print(f"   - 총 사업비: {result.feasibility.total_cost:,.0f}원")
            print()
        
        if result.lh_review:
            print(f"✅ M6 LH 종합 판단")
            print(f"   - 총점: {result.lh_review.total_score}/100점")
            print(f"   - 등급: {result.lh_review.grade}")
            print(f"   - 판정: {result.lh_review.decision}")
            print()
        
        # Save to cache
        cache_dir = Path("/home/user/webapp/.cache/pipeline")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_file = cache_dir / f"{test_context_id}.json"
        
        # Convert result to dict (simplified for JSON)
        result_dict = {
            "context_id": test_context_id,
            "created_at": datetime.now().isoformat(),
            "address": test_address,
            "land": {
                "parcel_id": result.land.parcel_id if result.land else None,
                "address": result.land.address if result.land else None,
                "area_sqm": result.land.area_sqm if result.land else None,
            } if result.land else None,
            "appraisal_value": result.appraisal.land_value if result.appraisal else None,
            "housing_type": result.housing_type.selected_type if result.housing_type else None,
            "total_units": result.capacity.incentive_capacity.total_units if result.capacity else None,
            "irr": result.feasibility.irr if result.feasibility else None,
            "lh_score": result.lh_review.total_score if result.lh_review else None,
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과 저장됨: {cache_file}")
        print()
        
        print("=" * 60)
        print("🎉 파이프라인 실행 완료!")
        print("=" * 60)
        print()
        print("📊 다음 단계: M2-M6 보고서 생성 테스트")
        print(f"   curl http://localhost:49999/api/v4/reports/phase8/modules/m2/html?context_id={test_context_id}")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ 파이프라인 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(run_pipeline())
