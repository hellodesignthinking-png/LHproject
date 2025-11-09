"""
LH 토지진단 시스템 사용 예제
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.schemas import LandAnalysisRequest, UnitType
from app.services.analysis_engine import AnalysisEngine


async def analyze_sample_land():
    """샘플 토지 분석 실행"""
    
    print("\n" + "="*70)
    print("🏢 LH 신축매입임대 토지진단 시스템 - 실전 예제")
    print("="*70 + "\n")
    
    # 분석 요청 생성
    request = LandAnalysisRequest(
        address="서울특별시 강남구 역삼동 679",
        land_area=500.0,
        unit_type=UnitType.YOUTH
    )
    
    print("📋 분석 요청 정보:")
    print(f"   주소: {request.address}")
    print(f"   면적: {request.land_area}㎡")
    print(f"   유형: {request.unit_type}")
    print()
    
    # 분석 엔진 실행
    try:
        engine = AnalysisEngine()
        result = await engine.analyze_land(request)
        
        # 결과 출력
        print("\n" + "="*70)
        print("📊 분석 결과 요약")
        print("="*70)
        
        # 1. 기본 정보
        print(f"\n✅ 1. 기본 정보")
        print(f"   좌표: ({result['coordinates'].latitude:.6f}, {result['coordinates'].longitude:.6f})")
        print(f"   용도지역: {result['zone_info'].zone_type}")
        print(f"   건폐율: {result['zone_info'].building_coverage_ratio}%")
        print(f"   용적률: {result['zone_info'].floor_area_ratio}%")
        
        # 2. 건축 규모
        print(f"\n🏗️  2. 건축 규모 산정")
        capacity = result['building_capacity']
        print(f"   건축면적: {capacity.building_area:.2f}㎡")
        print(f"   연면적: {capacity.total_floor_area:.2f}㎡")
        print(f"   층수: {capacity.floors}층")
        print(f"   세대수: {capacity.units}세대")
        print(f"   주차대수: {capacity.parking_spaces}대")
        
        # 3. 리스크 요인
        print(f"\n⚠️  3. 리스크 요인 분석 ({len(result['risk_factors'])}개)")
        if result['risk_factors']:
            for risk in result['risk_factors']:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"   {severity_emoji.get(risk.severity, '⚪')} [{risk.category}] {risk.description}")
        else:
            print(f"   ✅ 중대한 리스크 요인 없음")
        
        # 4. 인구통계
        print(f"\n👥 4. 인구통계 분석")
        demo = result['demographic_info']
        print(f"   총 인구: {demo.total_population:,}명")
        print(f"   청년 인구: {demo.youth_population:,}명 ({demo.youth_ratio}%)")
        print(f"   1인 가구: {demo.single_households:,}가구 ({demo.single_household_ratio}%)")
        
        # 5. 수요 분석
        print(f"\n📈 5. 입지 및 수요 분석")
        demand = result['demand_analysis']
        print(f"   수요 점수: {demand.demand_score}/100")
        print(f"   적합성 판단: {demand.recommendation}")
        print(f"\n   핵심 수요 요인:")
        for factor in demand.key_factors:
            print(f"   ✓ {factor}")
        
        if demand.nearby_facilities:
            print(f"\n   인근 주요 시설:")
            for facility in demand.nearby_facilities[:5]:
                print(f"   - {facility.name} ({int(facility.distance)}m)")
        
        # 6. 종합 판단
        print(f"\n{'='*70}")
        print(f"🎯 종합 판단")
        print(f"{'='*70}")
        summary = result['summary']
        
        status_emoji = "✅" if summary.is_eligible else "❌"
        print(f"\n{status_emoji} LH 매입 적격 여부: {'적격' if summary.is_eligible else '부적격'}")
        print(f"📊 예상 세대수: {summary.estimated_units}세대")
        print(f"📈 수요 점수: {summary.demand_score:.1f}/100")
        print(f"⚠️  리스크 개수: {summary.risk_count}개")
        print(f"\n💡 최종 추천: {summary.recommendation}")
        
        print(f"\n{'='*70}")
        print(f"✅ 분석 완료")
        print(f"{'='*70}\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


async def compare_multiple_locations():
    """여러 위치 비교 분석"""
    
    print("\n" + "="*70)
    print("🔍 다중 토지 비교 분석")
    print("="*70 + "\n")
    
    locations = [
        ("서울특별시 강남구 역삼동 679", 500, "청년형"),
        ("서울특별시 마포구 서교동 395-1", 600, "청년형"),
        ("서울특별시 성동구 성수동1가 656-37", 450, "청년형"),
    ]
    
    results = []
    engine = AnalysisEngine()
    
    for address, area, unit_type in locations:
        print(f"📍 분석 중: {address}")
        
        try:
            request = LandAnalysisRequest(
                address=address,
                land_area=area,
                unit_type=unit_type
            )
            result = await engine.analyze_land(request)
            results.append({
                "address": address,
                "result": result
            })
            print(f"   ✅ 완료\n")
        except Exception as e:
            print(f"   ❌ 실패: {e}\n")
    
    # 비교 결과 출력
    if results:
        print("\n" + "="*70)
        print("📊 비교 분석 결과")
        print("="*70 + "\n")
        
        print(f"{'위치':<40} {'세대수':>8} {'수요점수':>10} {'판단':>10}")
        print("-" * 70)
        
        for item in results:
            addr = item['address'][:37] + "..." if len(item['address']) > 40 else item['address']
            units = item['result']['summary'].estimated_units
            score = item['result']['summary'].demand_score
            rec = "적합" if item['result']['summary'].is_eligible else "부적합"
            
            print(f"{addr:<40} {units:>8}세대 {score:>9.1f} {rec:>10}")
        
        print()


async def main():
    """메인 실행"""
    print("\n🚀 LH 토지진단 시스템 시작\n")
    
    # 단일 토지 분석
    await analyze_sample_land()
    
    # 선택: 다중 토지 비교 (시간이 오래 걸릴 수 있음)
    # await compare_multiple_locations()


if __name__ == "__main__":
    asyncio.run(main())
