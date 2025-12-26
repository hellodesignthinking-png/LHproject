"""
M1 Full Pipeline: Address → Coordinates → Land Use → Building Registry
===========================================================================

This module integrates all APIs to build complete M1 context:
1. Kakao: Address search & geocoding
2. V-World: PNU (Parcel Number) extraction
3. MOLIT Land: Land use regulation data
4. MOLIT Building: Building registry data

Author: ZeroSite Backend Team
Date: 2025-12-26
"""

import httpx
import json
import os
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from pathlib import Path

# Load .env file
def load_env_file():
    """Load .env file if it exists"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded .env file\n")
    else:
        print(f"⚠️ No .env file found\n")

# Load environment variables at module import
load_env_file()

# API Keys (loaded from .env)
KAKAO_API_KEY = os.environ.get('KAKAO_REST_API_KEY', '')
VWORLD_API_KEYS = [
    os.environ.get('VWORLD_API_KEY', ''),
    os.environ.get('VWORLD_API_KEY_2', ''),
    os.environ.get('VWORLD_API_KEY_3', '')
]
DATA_GO_KR_API_KEY = os.environ.get('DATA_GO_KR_API_KEY', '')

# API Endpoints
KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"
VWORLD_ADDRESS_URL = "https://api.vworld.kr/req/address"
LAND_USE_URL = "https://apis.data.go.kr/1611000/nsdi/LandUseService/attr/getLandUseAttr"
BUILDING_REGISTRY_URL = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo"


class M1PipelineError(Exception):
    """M1 Pipeline specific error"""
    pass


def search_address_full_pipeline(query: str) -> Dict[str, Any]:
    """
    Full M1 pipeline: Address → Coordinates → Land → Building
    
    Args:
        query: Address search query
        
    Returns:
        Complete M1 context with all data
        
    Raises:
        M1PipelineError: If any critical step fails
    """
    print(f"\n{'='*70}")
    print(f"🚀 M1 FULL PIPELINE START")
    print(f"📍 Query: {query}")
    print(f"{'='*70}\n")
    
    # STEP 1: Kakao Address Search
    print("STEP 1: Kakao Address Search")
    kakao_result = step1_kakao_search(query)
    if not kakao_result:
        raise M1PipelineError("STEP 1 FAILED: Kakao address search")
    
    print(f"✅ Address: {kakao_result['address_name']}")
    print(f"✅ Coordinates: ({kakao_result['lat']}, {kakao_result['lng']})\n")
    
    # STEP 2: V-World PNU Extraction
    print("STEP 2: V-World PNU Extraction")
    vworld_result = step2_vworld_pnu(kakao_result['lng'], kakao_result['lat'])
    if not vworld_result:
        print("⚠️ V-World PNU extraction failed, using Kakao data")
        vworld_result = {'pnu': None, 'jibun_address': kakao_result.get('jibun_address', '')}
    
    pnu = vworld_result.get('pnu')
    print(f"✅ PNU: {pnu}")
    print(f"✅ Jibun: {vworld_result.get('jibun_address', 'N/A')}\n")
    
    # STEP 3: Land Use Regulation
    print("STEP 3: Land Use Regulation")
    land_use_result = {}
    if pnu:
        land_use_result = step3_land_use_regulation(pnu)
        if land_use_result:
            print(f"✅ Land use data retrieved")
        else:
            print(f"⚠️ Land use data not available")
    else:
        print(f"⚠️ Skipped (no PNU)")
    print()
    
    # STEP 4: Building Registry
    print("STEP 4: Building Registry")
    building_result = {}
    if pnu:
        building_result = step4_building_registry(pnu)
        if building_result:
            print(f"✅ Building data retrieved")
        else:
            print(f"⚠️ No existing building or data unavailable")
    else:
        print(f"⚠️ Skipped (no PNU)")
    print()
    
    # Build M1 Context
    m1_context = {
        'address': kakao_result['address_name'],
        'road_address': kakao_result.get('road_address', ''),
        'jibun_address': vworld_result.get('jibun_address', kakao_result.get('jibun_address', '')),
        'zone_no': kakao_result.get('zone_no', ''),
        'lat': kakao_result['lat'],
        'lng': kakao_result['lng'],
        'pnu': pnu,
        'land_use': land_use_result,
        'building_registry': building_result,
        'pipeline_status': 'SUCCESS'
    }
    
    print(f"{'='*70}")
    print(f"🎉 M1 PIPELINE COMPLETE")
    print(f"{'='*70}\n")
    
    return m1_context


def step1_kakao_search(query: str) -> Optional[Dict[str, Any]]:
    """
    STEP 1: Kakao Address Search
    """
    try:
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        params = {"query": query}
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(KAKAO_ADDRESS_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            documents = data.get("documents", [])
            
            if not documents:
                return None
            
            doc = documents[0]
            address_info = doc.get("address", {})
            road_address_info = doc.get("road_address", {})
            
            return {
                'address_name': doc.get('address_name', ''),
                'road_address': road_address_info.get('address_name', '') if road_address_info else '',
                'jibun_address': address_info.get('address_name', ''),
                'zone_no': road_address_info.get('zone_no', '') if road_address_info else '',
                'lat': float(doc.get('y', 0)),
                'lng': float(doc.get('x', 0)),
                'b_code': address_info.get('b_code', ''),
                'h_code': address_info.get('h_code', '')
            }
            
    except Exception as e:
        print(f"❌ Kakao API Error: {str(e)}")
        return None


def step2_vworld_pnu(lng: float, lat: float) -> Optional[Dict[str, Any]]:
    """
    STEP 2: V-World PNU Extraction
    """
    for idx, api_key in enumerate(VWORLD_API_KEYS):
        if not api_key:
            continue
            
        try:
            print(f"  Trying V-World key #{idx + 1}...")
            
            params = {
                'service': 'address',
                'request': 'getAddress',
                'point': f"{lng},{lat}",
                'type': 'PARCEL',
                'key': api_key
            }
            
            url = f"{VWORLD_ADDRESS_URL}?{urlencode(params)}"
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('response', {}).get('status') == 'OK':
                    result = data.get('response', {}).get('result', [])
                    if result:
                        item = result[0]
                        structure = item.get('structure', {})
                        
                        # Extract PNU
                        pnu = None
                        if 'parcel' in structure:
                            pnu = structure['parcel'].get('pnu')
                        
                        return {
                            'pnu': pnu,
                            'jibun_address': item.get('text', '')
                        }
            
        except Exception as e:
            print(f"  ⚠️ V-World key #{idx + 1} failed: {str(e)}")
            continue
    
    return None


def step3_land_use_regulation(pnu: str) -> Dict[str, Any]:
    """
    STEP 3: Land Use Regulation (행안부 토지이용규제정보)
    """
    try:
        params = {
            'pnu': pnu,
            'serviceKey': DATA_GO_KR_API_KEY,
            'type': 'json'
        }
        
        url = f"{LAND_USE_URL}?{urlencode(params)}"
        
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response based on actual API structure
            # Note: Actual structure may vary, adjust as needed
            items = data.get('items', {}).get('item', [])
            if not isinstance(items, list):
                items = [items] if items else []
            
            if items:
                item = items[0] if isinstance(items, list) else items
                return {
                    'zone_type': item.get('prposAreaDstrcCodeNm', ''),  # 용도지역
                    'district': item.get('spfcDstrtNm', ''),  # 용도지구
                    'area': item.get('prposAreaCodeNm', ''),  # 용도구역
                    'restrictions': item.get('etc', ''),
                    'raw_data': item
                }
            
            return {}
            
    except Exception as e:
        print(f"  ⚠️ Land use API error: {str(e)}")
        return {}


def step4_building_registry(pnu: str) -> Dict[str, Any]:
    """
    STEP 4: Building Registry (건축물대장)
    """
    try:
        # Parse PNU to extract sigunguCd, bjdongCd, etc.
        # PNU format: 시군구(5) + 법정동(5) + 구분(1) + 본번(4) + 부번(4) = 19자
        if len(pnu) < 19:
            print(f"  ⚠️ Invalid PNU length: {len(pnu)}")
            return {}
        
        sigungu_cd = pnu[:5]
        bjdong_cd = pnu[5:10]
        plat_gb = pnu[10:11]  # 0=대지, 1=산
        bun = pnu[11:15].lstrip('0') or '0'
        ji = pnu[15:19].lstrip('0') or '0'
        
        params = {
            'sigunguCd': sigungu_cd,
            'bjdongCd': bjdong_cd,
            'platGb': plat_gb,
            'bun': bun,
            'ji': ji,
            'serviceKey': DATA_GO_KR_API_KEY,
            'numOfRows': '1',
            'type': 'json'
        }
        
        url = f"{BUILDING_REGISTRY_URL}?{urlencode(params)}"
        
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            items = data.get('items', {}).get('item', [])
            if not isinstance(items, list):
                items = [items] if items else []
            
            if items:
                item = items[0] if isinstance(items, list) else items
                return {
                    'main_purpose': item.get('mainPurpsCdNm', ''),  # 주용도
                    'total_area': item.get('totArea', 0),  # 연면적
                    'floors': item.get('grndFlrCnt', 0),  # 지상층수
                    'approval_date': item.get('useAprDay', ''),  # 사용승인일
                    'structure': item.get('strctCdNm', ''),  # 구조
                    'exists': True,
                    'raw_data': item
                }
            
            return {'exists': False}
            
    except Exception as e:
        print(f"  ⚠️ Building registry API error: {str(e)}")
        return {}


if __name__ == "__main__":
    # Test the pipeline
    test_addresses = [
        "서울특별시 강남구 테헤란로 123",
        "부산광역시 해운대구 우동",
        "경기도 성남시 분당구 판교역로 166"
    ]
    
    for addr in test_addresses:
        try:
            result = search_address_full_pipeline(addr)
            print(f"✅ SUCCESS: {addr}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except M1PipelineError as e:
            print(f"❌ FAILED: {addr}")
            print(f"   Reason: {str(e)}")
        print()
