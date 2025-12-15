#!/usr/bin/env python3
"""
V-World API Comprehensive Test & Diagnosis
Tests all V-World API endpoints with multiple methods
"""

import requests
import json
from typing import Dict, Any
import time

class VWorldAPITester:
    """Comprehensive V-World API testing"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vworld.kr"
        self.results = []
    
    def test_endpoint(self, name: str, method: str, url: str, params: Dict) -> Dict[str, Any]:
        """Test a single endpoint"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print(f"Params: {json.dumps(params, indent=2, ensure_ascii=False)}")
        print(f"{'='*60}")
        
        result = {
            "name": name,
            "url": url,
            "method": method,
            "params": params,
            "success": False,
            "error": None,
            "response": None,
            "status_code": None
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.post(url, data=params, timeout=10)
            
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                try:
                    result["response"] = response.json()
                    result["success"] = True
                    print(f"✅ SUCCESS: {response.status_code}")
                    print(f"Response preview: {str(result['response'])[:200]}...")
                except:
                    result["response"] = response.text[:500]
                    print(f"✅ SUCCESS: {response.status_code} (text response)")
                    print(f"Response: {result['response']}")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.reason}"
                print(f"❌ FAILED: {result['error']}")
                print(f"Response: {response.text[:500]}")
        
        except requests.exceptions.Timeout:
            result["error"] = "Timeout (10s exceeded)"
            print(f"❌ FAILED: {result['error']}")
        
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection Error: {str(e)[:100]}"
            print(f"❌ FAILED: {result['error']}")
        
        except Exception as e:
            result["error"] = f"Error: {str(e)[:100]}"
            print(f"❌ FAILED: {result['error']}")
        
        self.results.append(result)
        return result
    
    def test_all(self):
        """Run all tests"""
        print(f"\n{'#'*80}")
        print(f"V-World API Comprehensive Test")
        print(f"API Key: {self.api_key}")
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}")
        
        # Test 1: Address Search (방법 1 - request=search)
        self.test_endpoint(
            name="Address Search (request=search)",
            method="GET",
            url=f"{self.base_url}/req/address",
            params={
                "service": "address",
                "request": "search",
                "key": self.api_key,
                "query": "서울특별시 종로구",
                "type": "road",
                "format": "json"
            }
        )
        
        # Test 2: Address Search (방법 2 - request=getAddress)
        self.test_endpoint(
            name="Address Search (request=getAddress)",
            method="GET",
            url=f"{self.base_url}/req/address",
            params={
                "service": "address",
                "request": "getAddress",
                "key": self.api_key,
                "address": "서울특별시 강남구 역삼동",
                "format": "json"
            }
        )
        
        # Test 3: Coordinate to Address (좌표 → 주소)
        self.test_endpoint(
            name="Coordinate to Address",
            method="GET",
            url=f"{self.base_url}/req/address",
            params={
                "service": "address",
                "request": "getAddress",
                "key": self.api_key,
                "point": "127.027619,37.497942",
                "type": "PARCEL",
                "format": "json"
            }
        )
        
        # Test 4: Land Price Data (개별공시지가)
        self.test_endpoint(
            name="Land Price Data (LP_PA_CBND_BUBUN)",
            method="GET",
            url=f"{self.base_url}/req/data",
            params={
                "service": "data",
                "request": "GetFeature",
                "data": "LP_PA_CBND_BUBUN",
                "key": self.api_key,
                "geometry": "false",
                "attribute": "true",
                "crs": "EPSG:4326",
                "geomFilter": "POINT(127.027619 37.497942)",
                "buffer": "10",
                "format": "json"
            }
        )
        
        # Test 5: Zoning Data (용도지역)
        self.test_endpoint(
            name="Zoning Data (LT_C_UQ111)",
            method="GET",
            url=f"{self.base_url}/req/data",
            params={
                "service": "data",
                "request": "GetFeature",
                "data": "LT_C_UQ111",
                "key": self.api_key,
                "geometry": "false",
                "attribute": "true",
                "crs": "EPSG:4326",
                "geomFilter": "POINT(127.027619 37.497942)",
                "buffer": "10",
                "format": "json"
            }
        )
        
        # Test 6: WMS GetCapabilities (WMS 서비스)
        self.test_endpoint(
            name="WMS GetCapabilities",
            method="GET",
            url=f"{self.base_url}/req/wms",
            params={
                "service": "WMS",
                "request": "GetCapabilities",
                "key": self.api_key,
                "format": "json"
            }
        )
        
        # Test 7: Static Map (정적 지도)
        self.test_endpoint(
            name="Static Map",
            method="GET",
            url=f"{self.base_url}/req/image",
            params={
                "service": "image",
                "request": "GetMap",
                "key": self.api_key,
                "width": "400",
                "height": "300",
                "center": "127.027619,37.497942",
                "level": "10",
                "format": "png"
            }
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        if failed > 0:
            print(f"\n{'='*80}")
            print(f"FAILED TESTS")
            print(f"{'='*80}")
            for r in self.results:
                if not r["success"]:
                    print(f"\n❌ {r['name']}")
                    print(f"   Error: {r['error']}")
                    print(f"   URL: {r['url']}")
        
        if passed > 0:
            print(f"\n{'='*80}")
            print(f"SUCCESSFUL TESTS")
            print(f"{'='*80}")
            for r in self.results:
                if r["success"]:
                    print(f"\n✅ {r['name']}")
                    print(f"   Status: {r['status_code']}")


if __name__ == "__main__":
    # Use the API key from config
    API_KEY = "B6B0B6F1-E572-304A-9742-384510D86FE4"
    
    tester = VWorldAPITester(API_KEY)
    tester.test_all()
    
    print(f"\n{'#'*80}")
    print(f"Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")
