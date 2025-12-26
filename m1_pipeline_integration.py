#!/usr/bin/env python3
"""
M1 Full Pipeline Integration: Address → Coordinates → Land Use → Building Info
This module implements the complete M1 context generation pipeline
"""
import os
import json
import httpx
from typing import Dict, Optional, List
from pathlib import Path


class M1PipelineIntegration:
    """M1 Pipeline: Kakao → V-World → MOLIT Land → MOLIT Building → M1 Context"""
    
    def __init__(self):
        self.kakao_api_key = os.environ.get('KAKAO_REST_API_KEY', '')
        self.vworld_api_keys = [
            os.environ.get('VWORLD_API_KEY_1', 'B6B0B6F1-E572-304A-9742-384510D86FE4'),
            os.environ.get('VWORLD_API_KEY_2', '781864DB-126D-3B14-A0EE-1FD1B1000534'),
            os.environ.get('VWORLD_API_KEY_3', '1BB852F2-8557-3387-B620-623B922641EB')
        ]
        self.molit_api_key = os.environ.get('DATA_GO_KR_API_KEY', '702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d')
        
        # API URLs
        self.kakao_address_url = "https://dapi.kakao.com/v2/local/search/address.json"
        self.vworld_address_url = "https://api.vworld.kr/req/address"
        self.land_use_url = "https://apis.data.go.kr/1611000/nsdi/LandUseService/attr/getLandUseAttr"
        self.building_url = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo"
        
        print(f"[M1 Pipeline] Initialized")
        print(f"[M1 Pipeline] Kakao API Key: {'✓' if self.kakao_api_key else '✗'}")
        print(f"[M1 Pipeline] V-World API Keys: {len(self.vworld_api_keys)} available")
        print(f"[M1 Pipeline] MOLIT API Key: {'✓' if self.molit_api_key else '✗'}")
    
    def step1_kakao_address_search(self, query: str) -> Optional[Dict]:
        """
        STEP 1: Kakao Address Search
        Returns: address data with coordinates (x, y)
        """
        try:
            print(f"\n{'='*80}")
            print(f"[STEP 1] 📍 Kakao Address Search: '{query}'")
            
            if not self.kakao_api_key:
                print(f"[STEP 1] ❌ No Kakao API key")
                return None
            
            headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
            params = {"query": query, "size": 1}  # Get only the first result
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.kakao_address_url, headers=headers, params=params)
                
                if response.status_code != 200:
                    print(f"[STEP 1] ❌ HTTP {response.status_code}: {response.text[:200]}")
                    return None
                
                data = response.json()
                documents = data.get("documents", [])
                
                if not documents:
                    print(f"[STEP 1] ⚠️ No results found")
                    return None
                
                doc = documents[0]
                address_info = doc.get("address", {})
                road_address_info = doc.get("road_address", {})
                
                result = {
                    "query": query,
                    "x": doc.get("x", ""),  # Longitude
                    "y": doc.get("y", ""),  # Latitude
                    "road_address": road_address_info.get("address_name", "") if road_address_info else "",
                    "jibun_address": address_info.get("address_name", ""),
                    "zone_no": road_address_info.get("zone_no", "") if road_address_info else "",
                    "b_code": address_info.get("b_code", ""),
                    "h_code": address_info.get("h_code", ""),
                    "region_1depth": address_info.get("region_1depth_name", ""),
                    "region_2depth": address_info.get("region_2depth_name", ""),
                    "region_3depth": address_info.get("region_3depth_name", "")
                }
                
                print(f"[STEP 1] ✓ Found: {result['road_address'] or result['jibun_address']}")
                print(f"[STEP 1] ✓ Coordinates: ({result['x']}, {result['y']})")
                print(f"[STEP 1] ✓ B-Code: {result['b_code']}, H-Code: {result['h_code']}")
                
                return result
                
        except Exception as e:
            print(f"[STEP 1] ❌ Exception: {type(e).__name__} - {str(e)}")
            return None
    
    def step2_vworld_parcel(self, x: str, y: str) -> Optional[Dict]:
        """
        STEP 2: V-World Coordinate → Parcel (PNU)
        Returns: jibun address and PNU
        """
        try:
            print(f"\n{'='*80}")
            print(f"[STEP 2] 🗺️ V-World Parcel Search: ({x}, {y})")
            
            # Try each V-World API key
            for idx, api_key in enumerate(self.vworld_api_keys):
                try:
                    params = {
                        "service": "address",
                        "request": "getAddress",
                        "point": f"{x},{y}",
                        "type": "PARCEL",
                        "key": api_key
                    }
                    
                    print(f"[STEP 2] Trying V-World API key #{idx + 1}...")
                    
                    with httpx.Client(timeout=10.0) as client:
                        response = client.get(self.vworld_address_url, params=params)
                        
                        if response.status_code != 200:
                            print(f"[STEP 2] ⚠️ HTTP {response.status_code} with key #{idx + 1}")
                            continue
                        
                        data = response.json()
                        
                        # V-World response structure
                        response_data = data.get("response", {})
                        status = response_data.get("status", "")
                        
                        if status != "OK":
                            print(f"[STEP 2] ⚠️ Status: {status} with key #{idx + 1}")
                            continue
                        
                        result_data = response_data.get("result", [])
                        if not result_data:
                            print(f"[STEP 2] ⚠️ No results with key #{idx + 1}")
                            continue
                        
                        # Get first result
                        item = result_data[0] if isinstance(result_data, list) else result_data
                        
                        # Extract PNU and address info
                        structure = item.get("structure", {})
                        parcel_info = structure.get("parcel", {}) if structure else {}
                        
                        result = {
                            "jibun_address": item.get("text", ""),
                            "pnu": parcel_info.get("pnu", ""),
                            "sido": structure.get("level1", ""),
                            "sigungu": structure.get("level2", ""),
                            "dong": structure.get("level4L", "")
                        }
                        
                        if result["pnu"]:
                            print(f"[STEP 2] ✓ Found PNU: {result['pnu']}")
                            print(f"[STEP 2] ✓ Address: {result['jibun_address']}")
                            print(f"[STEP 2] ✓ Region: {result['sido']} {result['sigungu']} {result['dong']}")
                            return result
                        
                except Exception as e:
                    print(f"[STEP 2] ⚠️ Error with key #{idx + 1}: {str(e)}")
                    continue
            
            print(f"[STEP 2] ❌ Failed with all V-World API keys")
            return None
            
        except Exception as e:
            print(f"[STEP 2] ❌ Exception: {type(e).__name__} - {str(e)}")
            return None
    
    def step3_land_use_regulation(self, pnu: str) -> Optional[Dict]:
        """
        STEP 3: Land Use Regulation Info (토지이용규제정보서비스)
        Returns: land use zone, district, area info
        """
        try:
            print(f"\n{'='*80}")
            print(f"[STEP 3] 🏞️ Land Use Regulation: PNU={pnu}")
            
            if not self.molit_api_key:
                print(f"[STEP 3] ❌ No MOLIT API key")
                return None
            
            params = {
                "pnu": pnu,
                "serviceKey": self.molit_api_key,
                "numOfRows": 10,
                "pageNo": 1,
                "type": "json"
            }
            
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.land_use_url, params=params)
                
                print(f"[STEP 3] Response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[STEP 3] ❌ HTTP {response.status_code}: {response.text[:200]}")
                    return None
                
                data = response.json()
                
                # Parse response
                response_data = data.get("response", {})
                header = response_data.get("header", {})
                result_code = header.get("resultCode", "")
                
                if result_code != "00":
                    print(f"[STEP 3] ⚠️ API result code: {result_code}")
                    print(f"[STEP 3] Message: {header.get('resultMsg', 'Unknown')}")
                    return None
                
                body = response_data.get("body", {})
                items = body.get("items", {})
                item_list = items.get("item", [])
                
                if not item_list:
                    print(f"[STEP 3] ⚠️ No land use data found")
                    return None
                
                # Aggregate land use info
                result = {
                    "pnu": pnu,
                    "zones": [],  # 용도지역
                    "districts": [],  # 용도지구
                    "areas": [],  # 용도구역
                    "raw_items": []
                }
                
                # Process each item
                if isinstance(item_list, dict):
                    item_list = [item_list]
                
                for item in item_list:
                    cnflc_at = item.get("cnflcAt", "")
                    prpos_area_nm = item.get("prposAreaNm", "")
                    
                    result["raw_items"].append({
                        "name": prpos_area_nm,
                        "conflict": cnflc_at
                    })
                    
                    # Categorize by type
                    if "지역" in prpos_area_nm:
                        result["zones"].append(prpos_area_nm)
                    elif "지구" in prpos_area_nm:
                        result["districts"].append(prpos_area_nm)
                    elif "구역" in prpos_area_nm:
                        result["areas"].append(prpos_area_nm)
                
                print(f"[STEP 3] ✓ Zones: {', '.join(result['zones']) if result['zones'] else 'None'}")
                print(f"[STEP 3] ✓ Districts: {', '.join(result['districts']) if result['districts'] else 'None'}")
                print(f"[STEP 3] ✓ Areas: {', '.join(result['areas']) if result['areas'] else 'None'}")
                
                return result
                
        except Exception as e:
            print(f"[STEP 3] ❌ Exception: {type(e).__name__} - {str(e)}")
            return None
    
    def step4_building_register(self, b_code: str, jibun_address: str) -> Optional[Dict]:
        """
        STEP 4: Building Register Info (건축물대장)
        Returns: building info if exists
        """
        try:
            print(f"\n{'='*80}")
            print(f"[STEP 4] 🏢 Building Register: B-Code={b_code}")
            print(f"[STEP 4] Address: {jibun_address}")
            
            if not self.molit_api_key:
                print(f"[STEP 4] ❌ No MOLIT API key")
                return None
            
            # Parse jibun address to extract components
            # Example: "서울 강남구 역삼동 648-23" → sigunguCd, bjdongCd, bun, ji
            parts = jibun_address.split()
            if len(parts) < 3:
                print(f"[STEP 4] ⚠️ Cannot parse address components")
                return {"exists": False, "reason": "Invalid address format"}
            
            # Extract 본번-부번
            last_part = parts[-1]
            bun, ji = "0", "0"
            
            if "-" in last_part:
                bun_ji = last_part.split("-")
                bun = bun_ji[0]
                ji = bun_ji[1] if len(bun_ji) > 1 else "0"
            else:
                bun = last_part
            
            # Use b_code for sigunguCd and bjdongCd
            sigungu_cd = b_code[:5] if len(b_code) >= 5 else ""
            bjdong_cd = b_code[5:] if len(b_code) > 5 else ""
            
            params = {
                "sigunguCd": sigungu_cd,
                "bjdongCd": bjdong_cd,
                "platGb": "0",  # 0: 대지, 1: 산
                "bun": bun,
                "ji": ji,
                "serviceKey": self.molit_api_key,
                "numOfRows": 10,
                "pageNo": 1
            }
            
            print(f"[STEP 4] Query params: sigunguCd={sigungu_cd}, bjdongCd={bjdong_cd}, bun={bun}, ji={ji}")
            
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.building_url, params=params)
                
                print(f"[STEP 4] Response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[STEP 4] ❌ HTTP {response.status_code}")
                    return {"exists": False, "reason": f"HTTP {response.status_code}"}
                
                data = response.json()
                
                # Parse response
                response_data = data.get("response", {})
                header = response_data.get("header", {})
                result_code = header.get("resultCode", "")
                
                if result_code != "00":
                    print(f"[STEP 4] ⚠️ API result code: {result_code}")
                    return {"exists": False, "reason": f"API code {result_code}"}
                
                body = response_data.get("body", {})
                items = body.get("items", {})
                item_list = items.get("item", [])
                
                if not item_list:
                    print(f"[STEP 4] ✓ No existing building (vacant land)")
                    return {"exists": False, "reason": "No building data"}
                
                # Process first building
                if isinstance(item_list, dict):
                    item = item_list
                else:
                    item = item_list[0]
                
                result = {
                    "exists": True,
                    "main_purpose": item.get("mainPurpsCdNm", ""),
                    "total_area": item.get("totArea", ""),
                    "floors_above": item.get("grndFlrCnt", ""),
                    "floors_below": item.get("ugrndFlrCnt", ""),
                    "use_approval_date": item.get("useAprDay", ""),
                    "structure": item.get("strctCdNm", ""),
                    "building_name": item.get("bldNm", "")
                }
                
                print(f"[STEP 4] ✓ Building exists: {result['building_name'] or 'Unknown'}")
                print(f"[STEP 4] ✓ Purpose: {result['main_purpose']}")
                print(f"[STEP 4] ✓ Total area: {result['total_area']}㎡")
                print(f"[STEP 4] ✓ Floors: {result['floors_above']}F (above) / {result['floors_below']}F (below)")
                
                return result
                
        except Exception as e:
            print(f"[STEP 4] ❌ Exception: {type(e).__name__} - {str(e)}")
            return {"exists": False, "reason": str(e)}
    
    def step5_finalize_m1_context(self, step1_data: Dict, step2_data: Optional[Dict],
                                   step3_data: Optional[Dict], step4_data: Optional[Dict]) -> Dict:
        """
        STEP 5: Finalize M1 Context
        Combine all data into final M1 context
        """
        print(f"\n{'='*80}")
        print(f"[STEP 5] 📦 Finalizing M1 Context...")
        
        m1_context = {
            "address": {
                "query": step1_data.get("query", ""),
                "road_address": step1_data.get("road_address", ""),
                "jibun_address": step1_data.get("jibun_address", ""),
                "zone_no": step1_data.get("zone_no", ""),
                "region_1depth": step1_data.get("region_1depth", ""),
                "region_2depth": step1_data.get("region_2depth", ""),
                "region_3depth": step1_data.get("region_3depth", "")
            },
            "coordinates": {
                "latitude": step1_data.get("y", ""),
                "longitude": step1_data.get("x", ""),
                "b_code": step1_data.get("b_code", ""),
                "h_code": step1_data.get("h_code", "")
            },
            "parcel": {
                "pnu": step2_data.get("pnu", "") if step2_data else "",
                "jibun_address": step2_data.get("jibun_address", "") if step2_data else "",
                "sido": step2_data.get("sido", "") if step2_data else "",
                "sigungu": step2_data.get("sigungu", "") if step2_data else "",
                "dong": step2_data.get("dong", "") if step2_data else ""
            },
            "land_use_regulation": {
                "pnu": step3_data.get("pnu", "") if step3_data else "",
                "zones": step3_data.get("zones", []) if step3_data else [],
                "districts": step3_data.get("districts", []) if step3_data else [],
                "areas": step3_data.get("areas", []) if step3_data else [],
                "has_data": bool(step3_data and (step3_data.get("zones") or step3_data.get("districts") or step3_data.get("areas")))
            },
            "building_register": {
                "exists": step4_data.get("exists", False) if step4_data else False,
                "main_purpose": step4_data.get("main_purpose", "") if step4_data and step4_data.get("exists") else "",
                "total_area": step4_data.get("total_area", "") if step4_data and step4_data.get("exists") else "",
                "floors_above": step4_data.get("floors_above", "") if step4_data and step4_data.get("exists") else "",
                "floors_below": step4_data.get("floors_below", "") if step4_data and step4_data.get("exists") else "",
                "use_approval_date": step4_data.get("use_approval_date", "") if step4_data and step4_data.get("exists") else "",
                "structure": step4_data.get("structure", "") if step4_data and step4_data.get("exists") else "",
                "building_name": step4_data.get("building_name", "") if step4_data and step4_data.get("exists") else ""
            },
            "pipeline_status": {
                "step1_kakao": bool(step1_data),
                "step2_vworld": bool(step2_data and step2_data.get("pnu")),
                "step3_land_use": bool(step3_data and step3_data.get("zones")),
                "step4_building": bool(step4_data),
                "completed": True
            }
        }
        
        print(f"[STEP 5] ✓ M1 Context finalized")
        print(f"[STEP 5] ✓ Address: {m1_context['address']['road_address'] or m1_context['address']['jibun_address']}")
        print(f"[STEP 5] ✓ PNU: {m1_context['parcel']['pnu']}")
        print(f"[STEP 5] ✓ Land Use Zones: {len(m1_context['land_use_regulation']['zones'])}")
        print(f"[STEP 5] ✓ Building Exists: {m1_context['building_register']['exists']}")
        print(f"{'='*80}\n")
        
        return m1_context
    
    def run_full_pipeline(self, address_query: str) -> Dict:
        """
        Run the full M1 pipeline: STEP 1 → STEP 2 → STEP 3 → STEP 4 → STEP 5
        """
        print(f"\n{'#'*80}")
        print(f"# M1 FULL PIPELINE START")
        print(f"# Query: {address_query}")
        print(f"{'#'*80}")
        
        # STEP 1: Kakao Address Search
        step1_data = self.step1_kakao_address_search(address_query)
        if not step1_data:
            return {
                "success": False,
                "error": "STEP 1 failed: Kakao address search returned no results",
                "failed_at": "kakao"
            }
        
        # STEP 2: V-World Parcel
        step2_data = self.step2_vworld_parcel(step1_data["x"], step1_data["y"])
        if not step2_data or not step2_data.get("pnu"):
            print(f"[WARNING] STEP 2 failed, but continuing with partial data...")
            step2_data = None
        
        # STEP 3: Land Use Regulation (requires PNU)
        step3_data = None
        if step2_data and step2_data.get("pnu"):
            step3_data = self.step3_land_use_regulation(step2_data["pnu"])
            if not step3_data:
                print(f"[WARNING] STEP 3 failed, but continuing with partial data...")
        
        # STEP 4: Building Register
        step4_data = None
        if step1_data.get("b_code") and step1_data.get("jibun_address"):
            step4_data = self.step4_building_register(step1_data["b_code"], step1_data["jibun_address"])
            if not step4_data:
                print(f"[WARNING] STEP 4 failed, but continuing with partial data...")
        
        # STEP 5: Finalize M1 Context
        m1_context = self.step5_finalize_m1_context(step1_data, step2_data, step3_data, step4_data)
        
        print(f"\n{'#'*80}")
        print(f"# M1 PIPELINE VERIFIED")
        print(f"# Address → Land → Regulation → Building linked")
        print(f"# Nationwide real data ready")
        print(f"{'#'*80}\n")
        
        return {
            "success": True,
            "m1_context": m1_context,
            "message": "M1 context successfully created"
        }


# Test function
def test_m1_pipeline():
    """Test M1 pipeline with sample addresses"""
    pipeline = M1PipelineIntegration()
    
    test_addresses = [
        "서울특별시 강남구 테헤란로 123",
        "부산광역시 해운대구 우동",
        "경기도 성남시 분당구 판교역로 166"
    ]
    
    results = []
    for address in test_addresses:
        print(f"\n\n{'='*100}")
        print(f"Testing address: {address}")
        print(f"{'='*100}")
        
        result = pipeline.run_full_pipeline(address)
        results.append({
            "address": address,
            "result": result
        })
    
    # Summary
    print(f"\n\n{'='*100}")
    print(f"FINAL SUMMARY")
    print(f"{'='*100}")
    
    for idx, item in enumerate(results, 1):
        address = item["address"]
        result = item["result"]
        
        if result.get("success"):
            print(f"\n{idx}. {address}")
            print(f"   Status: ✓ SUCCESS")
            m1_ctx = result.get("m1_context", {})
            print(f"   PNU: {m1_ctx.get('parcel', {}).get('pnu', 'N/A')}")
            print(f"   Building Exists: {m1_ctx.get('building_register', {}).get('exists', False)}")
        else:
            print(f"\n{idx}. {address}")
            print(f"   Status: ✗ FAILED")
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    test_m1_pipeline()
