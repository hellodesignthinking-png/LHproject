#!/usr/bin/env python3
"""
보고서 데이터 디버깅 도구
파이프라인 실행 후 실제 데이터 구조 확인
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.api.endpoints.pipeline_reports_v4 import results_cache

def check_pipeline_data():
    """파이프라인 데이터 구조 확인"""
    
    print("=" * 70)
    print("📊 Results Cache 상태 확인")
    print("=" * 70)
    
    if not results_cache:
        print("\n❌ results_cache가 비어있습니다!")
        print("\n🔥 조치 필요:")
        print("  1. 프론트엔드에서 주소 검색 (M1)")
        print("  2. 파이프라인 분석 실행 (M2-M6)")
        print("  3. 이 스크립트 다시 실행")
        return
    
    print(f"\n✅ 캐시에 {len(results_cache)}개의 결과 있음")
    print(f"Keys: {list(results_cache.keys())}")
    
    # 첫 번째 결과 상세 분석
    for parcel_id, result in list(results_cache.items())[:1]:
        print(f"\n" + "=" * 70)
        print(f"📋 상세 분석: {parcel_id}")
        print("=" * 70)
        
        # M2 Appraisal
        if hasattr(result, 'appraisal'):
            print("\n✅ M2 Appraisal Context:")
            appraisal = result.appraisal
            
            print(f"  - land_value: {appraisal.land_value:,.0f}원")
            print(f"  - unit_price_sqm: {appraisal.unit_price_sqm:,.0f}원/㎡")
            print(f"  - unit_price_pyeong: {appraisal.unit_price_pyeong:,.0f}원/평")
            print(f"  - confidence_score: {appraisal.confidence_metrics.confidence_score * 100:.1f}%")
            
            # 거래사례
            if hasattr(appraisal, 'transaction_samples'):
                samples = appraisal.transaction_samples
                print(f"\n  📊 거래사례: {len(samples) if samples else 0}건")
                
                if samples and len(samples) > 0:
                    print(f"\n  첫 번째 사례:")
                    sample = samples[0]
                    print(f"    - address: {sample.address if hasattr(sample, 'address') else 'N/A'}")
                    print(f"    - transaction_date: {sample.transaction_date if hasattr(sample, 'transaction_date') else 'N/A'}")
                    print(f"    - price_total: {sample.price_total if hasattr(sample, 'price_total') else 0:,.0f}원")
                    print(f"    - area_sqm: {sample.area_sqm if hasattr(sample, 'area_sqm') else 0:.1f}㎡")
                    print(f"    - distance_km: {sample.distance_km if hasattr(sample, 'distance_km') else 0:.2f}km")
                else:
                    print(f"    ❌ 거래사례가 비어있습니다!")
            else:
                print(f"  ❌ transaction_samples 속성 없음!")
        
        # M3 Housing Type
        if hasattr(result, 'housing_type'):
            print("\n✅ M3 Housing Type Context:")
            housing = result.housing_type
            print(f"  - selected_type: {housing.selected_type}")
            print(f"  - selected_type_name: {housing.selected_type_name}")
            
        # M4 Capacity
        if hasattr(result, 'capacity'):
            print("\n✅ M4 Capacity Context:")
            capacity = result.capacity
            if hasattr(capacity, 'legal_capacity'):
                print(f"  - legal_units: {capacity.legal_capacity.total_units}")
            if hasattr(capacity, 'incentive_capacity'):
                print(f"  - incentive_units: {capacity.incentive_capacity.total_units}")
            if hasattr(capacity, 'parking_solutions'):
                parking = capacity.parking_solutions
                print(f"  - parking type: {type(parking)}")
                if hasattr(parking, 'total_parking_spaces'):
                    print(f"  - parking_spaces: {parking.total_parking_spaces}")
        
        # M5 Feasibility
        if hasattr(result, 'feasibility'):
            print("\n✅ M5 Feasibility Context:")
            feas = result.feasibility
            if hasattr(feas, 'financial_metrics'):
                metrics = feas.financial_metrics
                print(f"  - NPV: {metrics.npv_public:,.0f}원")
                if hasattr(metrics, 'irr'):
                    print(f"  - IRR: {metrics.irr * 100:.2f}%")
        
        # M6 LH Review
        if hasattr(result, 'lh_review'):
            print("\n✅ M6 LH Review Context:")
            review = result.lh_review
            if hasattr(review, 'final_decision'):
                print(f"  - decision: {review.final_decision}")
            if hasattr(review, 'total_score'):
                print(f"  - score: {review.total_score}")

if __name__ == "__main__":
    try:
        check_pipeline_data()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
