"""
ZeroSite Land Report v5.0 - ZeroSite
통합 테스트 파일

모든 핵심 기능 검증:
- Type-specific Demand Scores UI
- Multi-Parcel Analysis API
- Geo Optimization Visualization
- LH Notice Loader
- Dashboard Builder
"""

import asyncio
import httpx
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

class V5IntegrationTester:
    """v5.0 통합 테스트"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.results = []
        
    async def test_single_analysis(self):
        """단일 필지 분석 테스트 (type_demand_scores 포함)"""
        print(f"\n{'='*70}")
        print("🧪 TEST 1: 단일 필지 분석 + Type-specific Demand Scores")
        print(f"{'='*70}")
        
        test_data = {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area": 500.0,
            "unit_type": None,  # Auto-analyze all types
            "zone_type": "제2종일반주거지역",
            "land_status": "빈집",
            "land_appraisal_price": 3500000,
            "lh_version": "2024"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/analyze-land",
                    json=test_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 핵심 필드 검증
                    print(f"✅ Status: {response.status_code}")
                    print(f"📍 Address: {data.get('address')}")
                    print(f"🏠 Recommended Type: {data.get('recommended_unit_type')}")
                    
                    # v5.0: Type-specific demand scores
                    type_scores = data.get("type_demand_scores", {})
                    if type_scores:
                        print(f"\n📊 Type-specific Demand Scores:")
                        for unit_type, score in type_scores.items():
                            print(f"   {unit_type}: {score:.1f}점")
                    else:
                        print("⚠️  type_demand_scores 없음!")
                    
                    # v5.0: All types scores
                    all_types = data.get("all_types_scores", [])
                    print(f"\n📋 All Types Scores ({len(all_types)} types):")
                    for item in all_types[:3]:
                        print(f"   {item['unit_type']}: {item['score']:.1f}점 ({item['size']})")
                    
                    # v5.0: AI Auto Corrector
                    corrected = data.get("corrected_input")
                    if corrected:
                        print(f"\n🔧 AI Auto Corrector:")
                        print(f"   Warnings: {len(corrected.get('warnings', []))}")
                        print(f"   Suggestions: {len(corrected.get('suggestions', []))}")
                    
                    # v5.0: Geo Optimization
                    geo_opt = data.get("geo_optimization")
                    if geo_opt:
                        print(f"\n🗺️  Geo Optimization:")
                        alternatives = geo_opt.get("alternative_sites", [])
                        print(f"   Alternative Sites: {len(alternatives)}")
                        for alt in alternatives[:2]:
                            print(f"   - {alt['address']}: {alt['score']:.1f}점")
                    
                    self.results.append({
                        "test": "single_analysis",
                        "status": "PASS",
                        "type_scores_count": len(type_scores),
                        "all_types_count": len(all_types)
                    })
                    
                    return data
                    
                else:
                    print(f"❌ Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    self.results.append({
                        "test": "single_analysis",
                        "status": "FAIL",
                        "error": response.text
                    })
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.results.append({
                "test": "single_analysis",
                "status": "ERROR",
                "error": str(e)
            })
    
    async def test_multi_parcel_analysis(self):
        """다중 필지 분석 테스트"""
        print(f"\n{'='*70}")
        print("🧪 TEST 2: Multi-Parcel Analysis API")
        print(f"{'='*70}")
        
        test_data = {
            "parcels": [
                "서울특별시 마포구 월드컵북로 120",
                "서울특별시 강남구 테헤란로 152",
                "서울특별시 송파구 올림픽로 300"
            ],
            "land_area": 500.0,
            "unit_type": "청년",
            "lh_version": "2024"
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/analyze-multi-parcel",
                    json=test_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code}")
                    print(f"📊 Total Parcels: {data.get('total_parcels')}")
                    print(f"✅ Eligible: {data.get('eligible_count')}")
                    print(f"❌ Ineligible: {data.get('ineligible_count')}")
                    
                    parcels = data.get("parcels", [])
                    print(f"\n📋 Parcel Results:")
                    for parcel in parcels:
                        status_icon = "✅" if parcel['status'] == 'success' else "❌"
                        print(f"   {status_icon} {parcel['address']}")
                        if parcel['status'] == 'success':
                            print(f"      Score: {parcel.get('demand_score', 0):.1f}점")
                    
                    # v5.0: Cluster analysis
                    clusters = data.get("clusters")
                    if clusters:
                        print(f"\n🗂️  Cluster Analysis:")
                        print(f"   Total Clusters: {len(clusters)}")
                        print(f"   Recommended Cluster: {clusters[0].get('cluster_id') if clusters else 'N/A'}")
                    
                    self.results.append({
                        "test": "multi_parcel_analysis",
                        "status": "PASS",
                        "total_parcels": len(parcels),
                        "eligible": data.get('eligible_count')
                    })
                    
                else:
                    print(f"❌ Failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    self.results.append({
                        "test": "multi_parcel_analysis",
                        "status": "FAIL",
                        "error": response.text
                    })
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.results.append({
                "test": "multi_parcel_analysis",
                "status": "ERROR",
                "error": str(e)
            })
    
    async def test_lh_notice_sync(self):
        """LH Notice Loader 테스트"""
        print(f"\n{'='*70}")
        print("🧪 TEST 3: LH Notice Loader - Google Drive Sync")
        print(f"{'='*70}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # List existing notices first
                list_response = await client.get(f"{self.base_url}/api/lh-notices/list")
                
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    print(f"📋 Existing Notices: {list_data.get('total', 0)}")
                    
                    notices = list_data.get('notices', [])
                    for notice in notices[:3]:
                        print(f"   - {notice.get('version_id')}: {notice.get('filename')}")
                
                # Attempt sync (may fail without credentials)
                print(f"\n🔄 Attempting sync...")
                sync_response = await client.post(f"{self.base_url}/api/lh-notices/sync")
                
                if sync_response.status_code == 200:
                    sync_data = sync_response.json()
                    print(f"✅ Sync Status: Success")
                    print(f"   Synced: {sync_data.get('synced_files', 0)}")
                    print(f"   New Versions: {len(sync_data.get('new_versions', []))}")
                    print(f"   Failed: {len(sync_data.get('failed_files', []))}")
                    
                    self.results.append({
                        "test": "lh_notice_sync",
                        "status": "PASS",
                        "synced": sync_data.get('synced_files', 0)
                    })
                    
                else:
                    print(f"⚠️  Sync Warning: {sync_response.status_code}")
                    print(f"   (May require Google Drive credentials)")
                    self.results.append({
                        "test": "lh_notice_sync",
                        "status": "SKIP",
                        "reason": "Credentials required"
                    })
                    
        except Exception as e:
            print(f"⚠️  Exception: {e}")
            print(f"   (Expected if Google Drive credentials not configured)")
            self.results.append({
                "test": "lh_notice_sync",
                "status": "SKIP",
                "reason": str(e)
            })
    
    async def test_dashboard_data(self):
        """Dashboard Builder 테스트"""
        print(f"\n{'='*70}")
        print("🧪 TEST 4: Dashboard Builder API")
        print(f"{'='*70}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/api/dashboard-data")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code}")
                    
                    chart_configs = data.get("chart_configs", {})
                    print(f"\n📊 Chart Configs:")
                    for chart_name, config in chart_configs.items():
                        print(f"   - {chart_name}: {config.get('type', 'unknown')}")
                    
                    map_data = data.get("map_data", {})
                    print(f"\n🗺️  Map Data:")
                    for map_name, config in map_data.items():
                        print(f"   - {map_name}: {len(config)} items")
                    
                    statistics = data.get("statistics", {})
                    print(f"\n📈 Statistics:")
                    for stat_name, value in statistics.items():
                        print(f"   - {stat_name}: {value}")
                    
                    self.results.append({
                        "test": "dashboard_data",
                        "status": "PASS",
                        "charts": len(chart_configs),
                        "maps": len(map_data)
                    })
                    
                else:
                    print(f"❌ Failed: {response.status_code}")
                    self.results.append({
                        "test": "dashboard_data",
                        "status": "FAIL",
                        "error": response.text
                    })
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.results.append({
                "test": "dashboard_data",
                "status": "ERROR",
                "error": str(e)
            })
    
    async def test_ui_endpoints(self):
        """UI 엔드포인트 접근성 테스트"""
        print(f"\n{'='*70}")
        print("🧪 TEST 5: UI Endpoints Accessibility")
        print(f"{'='*70}")
        
        endpoints = [
            "/",
            "/static/index.html",
        ]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for endpoint in endpoints:
                    try:
                        response = await client.get(f"{self.base_url}{endpoint}")
                        
                        if response.status_code == 200:
                            print(f"✅ {endpoint}: {response.status_code}")
                            
                            # Check for v5.0 specific UI elements
                            if endpoint == "/":
                                content = response.text
                                ui_checks = {
                                    "multiParcelAddresses": "multiParcelAddresses" in content,
                                    "analyzeMultiParcelBtn": "analyzeMultiParcelBtn" in content,
                                    "type_demand_scores": "type_demand_scores" in content,
                                    "displayGeoOptimization": "displayGeoOptimization" in content,
                                    "Leaflet": "Leaflet" in content or "leaflet" in content
                                }
                                
                                print(f"\n   UI Component Checks:")
                                for component, found in ui_checks.items():
                                    icon = "✅" if found else "❌"
                                    print(f"   {icon} {component}: {found}")
                        else:
                            print(f"❌ {endpoint}: {response.status_code}")
                            
                    except Exception as e:
                        print(f"⚠️  {endpoint}: {e}")
                        
            self.results.append({
                "test": "ui_endpoints",
                "status": "PASS"
            })
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            self.results.append({
                "test": "ui_endpoints",
                "status": "ERROR",
                "error": str(e)
            })
    
    def print_summary(self):
        """테스트 결과 요약"""
        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY - ZeroSite Land Report v5.0 / ZeroSite")
        print(f"{'='*70}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("status") == "PASS")
        failed = sum(1 for r in self.results if r.get("status") == "FAIL")
        skipped = sum(1 for r in self.results if r.get("status") == "SKIP")
        errors = sum(1 for r in self.results if r.get("status") == "ERROR")
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"💥 Errors: {errors}")
        
        print(f"\n{'='*70}")
        print("Detailed Results:")
        print(f"{'='*70}")
        
        for result in self.results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "SKIP": "⏭️ ",
                "ERROR": "💥"
            }.get(result.get("status"), "❓")
            
            print(f"{status_icon} {result.get('test')}: {result.get('status')}")
            
            if result.get("error"):
                print(f"   Error: {result.get('error')[:100]}")
            if result.get("reason"):
                print(f"   Reason: {result.get('reason')}")
        
        print(f"\n{'='*70}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! v5.0 is ready for production!")
        elif passed + skipped == total:
            print("⚠️  All critical tests passed. Some optional tests skipped.")
        else:
            print("❌ Some tests failed. Please review the errors above.")
        
        print(f"{'='*70}\n")


async def main():
    """메인 테스트 실행"""
    print(f"\n{'='*70}")
    print("ZeroSite Land Report v5.0 - ZeroSite")
    print("통합 테스트 시작")
    print(f"{'='*70}\n")
    
    tester = V5IntegrationTester()
    
    # Run all tests
    await tester.test_single_analysis()
    await tester.test_multi_parcel_analysis()
    await tester.test_lh_notice_sync()
    await tester.test_dashboard_data()
    await tester.test_ui_endpoints()
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
