#!/usr/bin/env python3
"""
Generate 10 Real LH Project Test Reports
Covers diverse scenarios for production validation
"""

import requests
import json
import time
from datetime import datetime

# Production server URL
API_URL = "http://localhost:8040/api/v21/generate-report"

# 10 Real LH Project Test Cases
test_projects = [
    {
        "name": "강남 역삼동 청년주택",
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area_sqm": 1650.0,  # 500평
        "supply_type": "청년",
        "expected_irr": "8-10%",
        "notes": "역세권, 강남 업무지구, 높은 청년 수요"
    },
    {
        "name": "마포 공덕동 신혼부부주택",
        "address": "서울특별시 마포구 공덕동 456-78",
        "land_area_sqm": 2145.0,  # 650평
        "supply_type": "신혼부부",
        "expected_irr": "9-11%",
        "notes": "공덕역 인근, 신혼부부 선호 지역"
    },
    {
        "name": "송파 잠실동 혼합주택",
        "address": "서울특별시 송파구 잠실동 789-12",
        "land_area_sqm": 2640.0,  # 800평
        "supply_type": "혼합",
        "expected_irr": "8-9%",
        "notes": "잠실 신축 단지, 교통 편의 우수"
    },
    {
        "name": "서초 서초동 청년주택",
        "address": "서울특별시 서초구 서초동 234-56",
        "land_area_sqm": 1485.0,  # 450평
        "supply_type": "청년",
        "expected_irr": "9-10%",
        "notes": "서초역 도보권, IT 벤처 밀집"
    },
    {
        "name": "용산 한강로동 행복주택",
        "address": "서울특별시 용산구 한강로동 567-89",
        "land_area_sqm": 1980.0,  # 600평
        "supply_type": "행복주택",
        "expected_irr": "8-9%",
        "notes": "한강변 조망, 용산역 접근성"
    },
    {
        "name": "성동 성수동 청년주택",
        "address": "서울특별시 성동구 성수동 890-12",
        "land_area_sqm": 1320.0,  # 400평
        "supply_type": "청년",
        "expected_irr": "10-12%",
        "notes": "성수 IT 타운, 젊은층 유입 활발"
    },
    {
        "name": "영등포 여의도동 신혼부부주택",
        "address": "서울특별시 영등포구 여의도동 345-67",
        "land_area_sqm": 2310.0,  # 700평
        "supply_type": "신혼부부",
        "expected_irr": "9-10%",
        "notes": "금융 중심지, 공원 인접"
    },
    {
        "name": "광진 자양동 청년주택",
        "address": "서울특별시 광진구 자양동 678-90",
        "land_area_sqm": 1155.0,  # 350평
        "supply_type": "청년",
        "expected_irr": "9-11%",
        "notes": "건국대 인근, 대학가 수요"
    },
    {
        "name": "노원 상계동 일반주택",
        "address": "서울특별시 노원구 상계동 123-45",
        "land_area_sqm": 2970.0,  # 900평
        "supply_type": "일반",
        "expected_irr": "7-8%",
        "notes": "대규모 단지, 가족 중심 커뮤니티"
    },
    {
        "name": "강서 화곡동 행복주택",
        "address": "서울특별시 강서구 화곡동 456-78",
        "land_area_sqm": 1815.0,  # 550평
        "supply_type": "행복주택",
        "expected_irr": "8-9%",
        "notes": "공항 접근성, 신도시 개발 예정"
    }
]

def generate_report(project):
    """Generate a single report via API"""
    print(f"\n{'='*80}")
    print(f"🏗️  Generating: {project['name']}")
    print(f"{'='*80}")
    print(f"   📍 Address: {project['address']}")
    print(f"   📏 Land Area: {project['land_area_sqm']:.1f}㎡ ({project['land_area_sqm']/3.3:.1f}평)")
    print(f"   🏠 Supply Type: {project['supply_type']}")
    print(f"   📊 Expected IRR: {project['expected_irr']}")
    print(f"   📝 Notes: {project['notes']}")
    print()
    
    payload = {
        "address": project['address'],
        "land_area_sqm": project['land_area_sqm'],
        "supply_type": project['supply_type']
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS ({generation_time:.2f}s)")
            print(f"   📄 Report URL: {result['report_url']}")
            print(f"   💾 File Size: {result['file_size_kb']}KB")
            print(f"   📝 Narrative Lines: {result['narrative_lines']}")
            print(f"   📚 Policy Citations: {result['policy_citations']}")
            print(f"   💰 Financial Decision: {result['financial_decision']}")
            print(f"   🏛️  Policy Decision: {result['policy_decision']}")
            return {
                "success": True,
                "project": project['name'],
                "result": result,
                "generation_time": generation_time
            }
        else:
            print(f"❌ FAILED (HTTP {response.status_code})")
            print(f"   Error: {response.text}")
            return {
                "success": False,
                "project": project['name'],
                "error": response.text,
                "generation_time": generation_time
            }
            
    except Exception as e:
        generation_time = time.time() - start_time
        print(f"❌ EXCEPTION ({generation_time:.2f}s)")
        print(f"   Error: {str(e)}")
        return {
            "success": False,
            "project": project['name'],
            "error": str(e),
            "generation_time": generation_time
        }


def main():
    """Generate all 10 test reports"""
    print("\n" + "="*80)
    print("🚀 ZeroSite v21 - 10 LH Projects Batch Generation")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_URL}")
    print(f"Total Projects: {len(test_projects)}")
    print("="*80 + "\n")
    
    results = []
    total_start = time.time()
    
    for i, project in enumerate(test_projects, 1):
        print(f"\n[{i}/10] Processing...")
        result = generate_report(project)
        results.append(result)
        
        # Brief pause between requests
        if i < len(test_projects):
            time.sleep(1)
    
    total_time = time.time() - total_start
    
    # Summary
    print("\n" + "="*80)
    print("📊 BATCH GENERATION SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(test_projects)}")
    print(f"❌ Failed: {len(failed)}/{len(test_projects)}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"⏱️  Average Time: {total_time/len(test_projects):.2f}s per report")
    
    if successful:
        avg_gen_time = sum(r['generation_time'] for r in successful) / len(successful)
        print(f"📈 Average Generation Time: {avg_gen_time:.2f}s")
    
    print("\n" + "="*80)
    print("📋 DETAILED RESULTS")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{i}. {status} {result['project']} ({result['generation_time']:.2f}s)")
        if result['success']:
            r = result['result']
            print(f"      IRR: Financial {r['financial_decision']}, Policy {r['policy_decision']}")
        else:
            print(f"      Error: {result['error'][:80]}...")
    
    print("\n" + "="*80)
    print(f"🎉 Batch Generation Complete!")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Save results to JSON
    output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": len(test_projects),
                "successful": len(successful),
                "failed": len(failed),
                "total_time": total_time,
                "average_time_per_report": total_time / len(test_projects)
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Results saved to: {output_file}\n")
    
    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
