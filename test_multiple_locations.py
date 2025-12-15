"""
여러 토지 위치 비교 분석 테스트
"""

import requests
import json
from typing import List, Dict

# API 엔드포인트
API_URL = "http://localhost:8000/api/analyze-land"

# 테스트할 토지 목록
test_locations = [
    {
        "name": "강남 역삼동 (오피스 밀집)",
        "address": "서울특별시 강남구 역삼동 679",
        "land_area": 500,
        "unit_type": "청년형"
    },
    {
        "name": "마포 홍대 (대학가)",
        "address": "서울특별시 마포구 서교동 395-1",
        "land_area": 600,
        "unit_type": "청년형"
    },
    {
        "name": "성동 성수동 (창업 지구)",
        "address": "서울특별시 성동구 성수동1가 656-37",
        "land_area": 550,
        "unit_type": "청년형"
    },
    {
        "name": "서초 반포동 (고급 주거)",
        "address": "서울특별시 서초구 반포동 19-1",
        "land_area": 700,
        "unit_type": "신혼부부형"
    },
]


def analyze_location(data: Dict) -> Dict:
    """단일 토지 분석"""
    try:
        response = requests.post(API_URL, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def print_comparison_table(results: List[Dict]):
    """비교 결과 테이블 출력"""
    print("\n" + "="*120)
    print("📊 토지 비교 분석 결과")
    print("="*120)
    print()
    
    # 헤더
    header = f"{'위치':<30} {'면적(㎡)':>10} {'세대수':>8} {'층수':>6} {'수요점수':>10} {'리스크':>8} {'판단':>15}"
    print(header)
    print("-"*120)
    
    # 데이터 행
    for item in results:
        if 'error' in item['result']:
            continue
            
        result = item['result']
        name = item['name'][:28]
        area = result['land_area']
        units = result['building_capacity']['units']
        floors = result['building_capacity']['floors']
        score = result['demand_analysis']['demand_score']
        risks = len(result['risk_factors'])
        eligible = "✅ 적격" if result['summary']['is_eligible'] else "❌ 부적격"
        
        row = f"{name:<30} {area:>10.0f} {units:>8}세대 {floors:>6}층 {score:>9.1f}점 {risks:>8}개 {eligible:>15}"
        print(row)
    
    print()


def print_detailed_result(item: Dict):
    """상세 결과 출력"""
    result = item['result']
    if 'error' in result:
        print(f"\n❌ {item['name']}: {result['error']}")
        return
    
    print(f"\n{'='*80}")
    print(f"📍 {item['name']}")
    print(f"{'='*80}")
    
    # 기본 정보
    print(f"\n✅ 기본 정보")
    print(f"   주소: {result['address']}")
    print(f"   면적: {result['land_area']}㎡")
    print(f"   용도지역: {result['zone_info']['zone_type']}")
    
    # 건축 규모
    capacity = result['building_capacity']
    print(f"\n🏗️  건축 규모")
    print(f"   세대수: {capacity['units']}세대")
    print(f"   층수: {capacity['floors']}층")
    print(f"   주차: {capacity['parking_spaces']}대")
    
    # 수요 분석
    demand = result['demand_analysis']
    print(f"\n📈 수요 분석")
    print(f"   수요 점수: {demand['demand_score']}/100")
    print(f"   판단: {demand['recommendation']}")
    
    if demand['key_factors']:
        print(f"   핵심 요인:")
        for factor in demand['key_factors'][:3]:
            print(f"   • {factor}")
    
    # 리스크
    if result['risk_factors']:
        print(f"\n⚠️  리스크 ({len(result['risk_factors'])}개)")
        for risk in result['risk_factors'][:3]:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"   {severity_emoji.get(risk['severity'], '⚪')} {risk['description']}")
    else:
        print(f"\n✅ 리스크 없음")
    
    # 종합 판단
    summary = result['summary']
    print(f"\n🎯 종합 판단")
    print(f"   LH 매입 적격: {'✅ 예' if summary['is_eligible'] else '❌ 아니오'}")
    print(f"   최종 추천: {summary['recommendation']}")


def main():
    """메인 실행"""
    print("\n🚀 LH 토지진단 시스템 - 다중 위치 비교 분석")
    print("="*80)
    print(f"\n📋 분석할 토지: {len(test_locations)}개")
    print()
    
    results = []
    
    for i, location in enumerate(test_locations, 1):
        print(f"[{i}/{len(test_locations)}] 분석 중: {location['name']}...")
        
        result = analyze_location({
            "address": location['address'],
            "land_area": location['land_area'],
            "unit_type": location['unit_type']
        })
        
        results.append({
            "name": location['name'],
            "result": result
        })
        
        if 'error' not in result:
            print(f"    ✅ 완료 (세대수: {result['building_capacity']['units']}세대, "
                  f"수요점수: {result['demand_analysis']['demand_score']}/100)")
        else:
            print(f"    ❌ 실패: {result['error']}")
        print()
    
    # 비교 테이블 출력
    print_comparison_table(results)
    
    # 상세 결과 출력 (옵션)
    print("\n" + "="*80)
    print("📝 상세 분석 결과")
    print("="*80)
    
    for item in results:
        print_detailed_result(item)
    
    # 최고/최저 점수 토지
    valid_results = [r for r in results if 'error' not in r['result']]
    
    if valid_results:
        best = max(valid_results, key=lambda x: x['result']['demand_analysis']['demand_score'])
        worst = min(valid_results, key=lambda x: x['result']['demand_analysis']['demand_score'])
        
        print(f"\n{'='*80}")
        print(f"🏆 분석 요약")
        print(f"{'='*80}")
        print(f"\n✅ 최고 점수: {best['name']}")
        print(f"   수요 점수: {best['result']['demand_analysis']['demand_score']}/100")
        print(f"   예상 세대: {best['result']['building_capacity']['units']}세대")
        
        print(f"\n⚠️  최저 점수: {worst['name']}")
        print(f"   수요 점수: {worst['result']['demand_analysis']['demand_score']}/100")
        print(f"   예상 세대: {worst['result']['building_capacity']['units']}세대")
    
    print(f"\n{'='*80}")
    print(f"✅ 비교 분석 완료")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
