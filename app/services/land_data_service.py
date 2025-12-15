"""
ZeroSite 토지 데이터 통합 수집 서비스
공공 API를 통해 실제 토지 정보 자동 수집
"""

import os
import requests
import xmltodict
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from urllib.parse import quote
import json
from datetime import datetime, timedelta


@dataclass
class LandBasicInfo:
    """토지 기본정보"""
    pnu: str = ""                       # 필지고유번호 (19자리)
    address: str = ""                   # 주소
    area: float = 0.0                   # 면적 (㎡)
    land_category: str = ""             # 지목
    land_use_zone: str = ""             # 용도지역
    land_use_situation: str = ""        # 이용상황
    ownership_type: str = ""            # 소유구분
    change_date: str = ""               # 변동일자
    road_side: str = ""                 # 도로접면
    terrain_height: str = ""            # 지형높이
    terrain_shape: str = ""             # 지형형상


@dataclass
class LandPriceInfo:
    """공시지가 정보"""
    official_price: int = 0             # 개별공시지가 (원/㎡)
    base_year: str = ""                 # 기준년도
    total_price: int = 0                # 총 공시지가 (공시지가 × 면적)


@dataclass
class LandTransaction:
    """거래사례"""
    transaction_date: str = ""          # 거래일
    transaction_amount: int = 0         # 거래금액 (만원)
    land_area: float = 0.0              # 거래면적 (㎡)
    price_per_sqm: int = 0              # ㎡당 가격 (원)
    land_category: str = ""             # 지목
    land_use: str = ""                  # 용도


@dataclass 
class BuildingInfo:
    """건축물대장 정보"""
    building_name: str = ""             # 건물명
    main_purpose: str = ""              # 주용도
    total_floor_area: float = 0.0       # 연면적
    building_area: float = 0.0          # 건축면적
    floor_count: int = 0                # 층수
    approval_date: str = ""             # 사용승인일


@dataclass
class RegulationInfo:
    """토지이용규제 정보"""
    use_zone: str = ""                  # 용도지역
    use_district: str = ""              # 용도지구
    floor_area_ratio: int = 0           # 용적률
    building_coverage_ratio: int = 0    # 건폐율
    max_height: int = 0                 # 최고높이
    regulations: List[str] = None       # 규제 목록


class LandDataService:
    """
    토지 데이터 통합 서비스
    
    사용 API:
    - 카카오: 주소 → 좌표 변환
    - VWorld: 토지이용규제정보
    - 공공데이터포털: 토지특성정보, 개별공시지가, 실거래가, 건축물대장
    """
    
    def __init__(self):
        # API 키 로드
        self.kakao_api_key = os.getenv("KAKAO_REST_API_KEY", "1b172a21a17b8b51dd47884b45228483")
        self.data_go_kr_key = os.getenv("DATA_GO_KR_API_KEY", "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d")
        self.vworld_api_key = os.getenv("VWORLD_API_KEY", "B6B0B6F1-E572-304A-9742-384510D86FE4")
        
        # API 엔드포인트
        self.KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"
        self.VWORLD_LAND_USE_URL = "https://api.vworld.kr/ned/data/getLandUseAttr"
        self.VWORLD_PARCEL_URL = "https://api.vworld.kr/req/data"
        
        # 공공데이터포털 URL
        self.LAND_CHARACTERISTIC_URL = "http://apis.data.go.kr/1611000/nsdi/LandCharacteristicsService/wfs/getLandCharacteristics"
        self.LAND_PRICE_URL = "http://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/wfs/getIndvdLandPriceAttr"
        self.LAND_TRANSACTION_URL = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPage/service/RTMSOBJSvc/getRTMSDataSvcLandTrade"
        self.BUILDING_URL = "http://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo"
    
    def fetch_all_by_address(self, address: str) -> Dict[str, Any]:
        """
        주소로 모든 토지 정보 조회
        
        Args:
            address: 토지 주소 (지번 주소)
                    예: "서울특별시 강남구 역삼동 123-45"
                    예: "경기도 성남시 분당구 정자동 100"
        
        Returns:
            {
                "success": bool,
                "basic_info": LandBasicInfo,
                "price_info": LandPriceInfo,
                "transactions": List[LandTransaction],
                "building_info": BuildingInfo or None,
                "regulation_info": RegulationInfo,
                "error": str or None
            }
        """
        result = {
            "success": False,
            "basic_info": None,
            "price_info": None,
            "transactions": [],
            "building_info": None,
            "regulation_info": None,
            "raw_data": {},
            "error": None
        }
        
        try:
            print(f"[1/6] 주소 파싱 및 좌표 변환 중: {address}")
            
            # 1. 주소 → 좌표 및 PNU 변환 (카카오 API)
            location_info = self._get_location_from_address(address)
            if not location_info:
                result["error"] = "주소를 찾을 수 없습니다. 정확한 지번 주소를 입력해주세요."
                return result
            
            pnu = location_info.get("pnu", "")
            sido_code = pnu[:2] if pnu else ""
            sigungu_code = pnu[:5] if pnu else ""
            
            result["raw_data"]["location"] = location_info
            print(f"   → PNU: {pnu}")
            
            # 2. 토지 기본정보 조회
            print(f"[2/6] 토지 기본정보 조회 중...")
            basic_info = self._fetch_land_characteristics(pnu, address)
            result["basic_info"] = basic_info
            print(f"   → 면적: {basic_info.area}㎡, 지목: {basic_info.land_category}")
            
            # 3. 개별공시지가 조회
            print(f"[3/6] 개별공시지가 조회 중...")
            price_info = self._fetch_land_price(pnu)
            if price_info and basic_info:
                price_info.total_price = int(price_info.official_price * basic_info.area)
            result["price_info"] = price_info
            print(f"   → 공시지가: {price_info.official_price:,}원/㎡" if price_info else "   → 조회 실패")
            
            # 4. 토지이용규제 조회 (VWorld)
            print(f"[4/6] 토지이용규제 정보 조회 중...")
            regulation_info = self._fetch_land_use_regulation(pnu, location_info)
            result["regulation_info"] = regulation_info
            print(f"   → 용적률: {regulation_info.floor_area_ratio}%, 건폐율: {regulation_info.building_coverage_ratio}%")
            
            # 5. 실거래가 조회
            print(f"[5/6] 실거래가 조회 중...")
            transactions = self._fetch_transactions(sigungu_code)
            result["transactions"] = transactions
            print(f"   → {len(transactions)}건 조회됨")
            
            # 6. 건축물대장 조회 (건물이 있는 경우)
            print(f"[6/6] 건축물대장 조회 중...")
            building_info = self._fetch_building_info(sigungu_code, pnu)
            result["building_info"] = building_info
            
            result["success"] = True
            print(f"✅ 모든 데이터 조회 완료")
            
        except Exception as e:
            result["error"] = f"데이터 조회 중 오류 발생: {str(e)}"
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def _get_location_from_address(self, address: str) -> Optional[Dict]:
        """
        카카오 API로 주소 → 좌표/PNU 변환
        """
        headers = {
            "Authorization": f"KakaoAK {self.kakao_api_key}"
        }
        params = {
            "query": address,
            "analyze_type": "exact"
        }
        
        try:
            response = requests.get(
                self.KAKAO_ADDRESS_URL, 
                headers=headers, 
                params=params,
                timeout=10
            )
            data = response.json()
            
            if data.get("documents"):
                doc = data["documents"][0]
                address_info = doc.get("address", {})
                
                # PNU 생성 (19자리)
                # 시도(2) + 시군구(3) + 읍면동(3) + 리(2) + 산여부(1) + 본번(4) + 부번(4)
                b_code = address_info.get("b_code", "")  # 법정동코드 (10자리)
                main_no = address_info.get("main_address_no", "0").zfill(4)
                sub_no = address_info.get("sub_address_no", "0").zfill(4)
                mountain = "2" if address_info.get("mountain_yn") == "Y" else "1"
                
                pnu = f"{b_code}{mountain}{main_no}{sub_no}"
                
                return {
                    "pnu": pnu,
                    "x": doc.get("x"),  # 경도
                    "y": doc.get("y"),  # 위도
                    "address_name": doc.get("address_name"),
                    "sido": address_info.get("region_1depth_name"),
                    "sigungu": address_info.get("region_2depth_name"),
                    "dong": address_info.get("region_3depth_name"),
                    "b_code": b_code
                }
        except Exception as e:
            print(f"카카오 API 오류: {e}")
        
        return None
    
    def _fetch_land_characteristics(self, pnu: str, address: str) -> LandBasicInfo:
        """
        토지특성정보 조회 (공공데이터포털)
        """
        info = LandBasicInfo(pnu=pnu, address=address)
        
        params = {
            "ServiceKey": self.data_go_kr_key,
            "pnu": pnu,
            "format": "json",
            "numOfRows": 1,
            "pageNo": 1
        }
        
        try:
            response = requests.get(
                self.LAND_CHARACTERISTIC_URL,
                params=params,
                timeout=10
            )
            
            # XML 또는 JSON 파싱
            try:
                data = response.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if isinstance(items, dict):
                    items = [items]
            except:
                # XML 파싱 시도
                data = xmltodict.parse(response.content)
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if isinstance(items, dict):
                    items = [items]
            
            if items:
                item = items[0]
                info.area = float(item.get("lndpclAr", 0) or 0)
                info.land_category = item.get("lndcgrCodeNm", "")
                info.land_use_zone = item.get("prposArea1Nm", "")
                info.land_use_situation = item.get("ladUseSittnNm", "")
                info.ownership_type = item.get("posesnSeCodeNm", "")
                info.road_side = item.get("roadSideCodeNm", "")
                info.terrain_height = item.get("tpgrphHgCodeNm", "")
                info.terrain_shape = item.get("tpgrphFrmCodeNm", "")
                info.change_date = item.get("lastUpdtDt", "")
                
        except Exception as e:
            print(f"토지특성정보 조회 오류: {e}")
            
            # VWorld로 대체 조회
            info = self._fetch_land_info_vworld(pnu, address)
        
        return info
    
    def _fetch_land_info_vworld(self, pnu: str, address: str) -> LandBasicInfo:
        """
        VWorld API로 토지정보 조회 (대체)
        """
        info = LandBasicInfo(pnu=pnu, address=address)
        
        params = {
            "key": self.vworld_api_key,
            "domain": "localhost",
            "service": "data",
            "request": "GetFeature",
            "data": "LP_PA_CBND_BUBUN",  # 연속지적도
            "format": "json",
            "pnu": pnu
        }
        
        try:
            response = requests.get(
                self.VWORLD_PARCEL_URL,
                params=params,
                timeout=10
            )
            data = response.json()
            
            features = data.get("response", {}).get("result", {}).get("featureCollection", {}).get("features", [])
            if features:
                props = features[0].get("properties", {})
                info.area = float(props.get("area", 0) or 0)
                info.land_category = props.get("jibun", "")
                
        except Exception as e:
            print(f"VWorld 토지정보 조회 오류: {e}")
        
        return info
    
    def _fetch_land_price(self, pnu: str) -> Optional[LandPriceInfo]:
        """
        개별공시지가 조회 (공공데이터포털)
        """
        params = {
            "ServiceKey": self.data_go_kr_key,
            "pnu": pnu,
            "format": "json",
            "numOfRows": 1,
            "pageNo": 1,
            "stdrYear": "2024"
        }
        
        try:
            response = requests.get(
                self.LAND_PRICE_URL,
                params=params,
                timeout=10
            )
            
            try:
                data = response.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if isinstance(items, dict):
                    items = [items]
            except:
                data = xmltodict.parse(response.content)
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if isinstance(items, dict):
                    items = [items]
            
            if items:
                item = items[0]
                return LandPriceInfo(
                    official_price=int(item.get("pblntfPclnd", 0) or 0),
                    base_year=item.get("stdrYear", "2024")
                )
                
        except Exception as e:
            print(f"공시지가 조회 오류: {e}")
        
        return LandPriceInfo()
    
    def _fetch_land_use_regulation(self, pnu: str, location_info: Dict) -> RegulationInfo:
        """
        토지이용규제정보 조회 (VWorld)
        """
        info = RegulationInfo()
        
        params = {
            "key": self.vworld_api_key,
            "domain": "localhost",
            "pnu": pnu,
            "format": "json"
        }
        
        try:
            response = requests.get(
                self.VWORLD_LAND_USE_URL,
                params=params,
                timeout=10
            )
            data = response.json()
            
            result = data.get("landUses", {}).get("landUse", [])
            if isinstance(result, dict):
                result = [result]
            
            if result:
                for item in result:
                    if "용도지역" in item.get("prposAreaDstrcCodeNm", ""):
                        info.use_zone = item.get("prposAreaDstrcCodeNm", "")
                    elif "용도지구" in item.get("prposAreaDstrcCodeNm", ""):
                        info.use_district = item.get("prposAreaDstrcCodeNm", "")
                    
                    if info.regulations is None:
                        info.regulations = []
                    info.regulations.append(item.get("prposAreaDstrcCodeNm", ""))
            
            # 용적률/건폐율 계산
            info.floor_area_ratio = self._get_far_by_zone(info.use_zone)
            info.building_coverage_ratio = self._get_bcr_by_zone(info.use_zone)
            info.max_height = self._get_max_height_by_zone(info.use_zone)
            
        except Exception as e:
            print(f"토지이용규제 조회 오류: {e}")
        
        return info
    
    def _fetch_transactions(self, sigungu_code: str, limit: int = 5) -> List[LandTransaction]:
        """
        토지 실거래가 조회 (공공데이터포털)
        """
        transactions = []
        
        # 최근 6개월 조회
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            deal_ymd = date.strftime("%Y%m")
            
            params = {
                "ServiceKey": self.data_go_kr_key,
                "LAWD_CD": sigungu_code,
                "DEAL_YMD": deal_ymd,
                "numOfRows": 100,
                "pageNo": 1
            }
            
            try:
                response = requests.get(self.LAND_TRANSACTION_URL, params=params, timeout=10)
                
                data = xmltodict.parse(response.content)
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                if isinstance(items, dict):
                    items = [items]
                
                for item in items[:limit]:
                    amount_str = str(item.get("거래금액", "0")).replace(",", "").strip()
                    amount = int(amount_str) if amount_str.isdigit() else 0
                    area = float(item.get("거래면적", 0) or 0)
                    
                    tx = LandTransaction(
                        transaction_date=f"{item.get('년', '')}-{item.get('월', '').zfill(2)}-{item.get('일', '').zfill(2)}",
                        transaction_amount=amount,
                        land_area=area,
                        price_per_sqm=int(amount * 10000 / area) if area > 0 else 0,
                        land_category=item.get("지목", ""),
                        land_use=item.get("용도지역", "")
                    )
                    transactions.append(tx)
                    
                if len(transactions) >= limit:
                    break
                    
            except Exception as e:
                print(f"실거래가 조회 오류 ({deal_ymd}): {e}")
                continue
        
        return transactions[:limit]
    
    def _fetch_building_info(self, sigungu_code: str, pnu: str) -> Optional[BuildingInfo]:
        """
        건축물대장 정보 조회 (공공데이터포털)
        """
        params = {
            "ServiceKey": self.data_go_kr_key,
            "sigunguCd": sigungu_code,
            "bjdongCd": pnu[5:10],
            "bun": pnu[11:15],
            "ji": pnu[15:19],
            "numOfRows": 1,
            "pageNo": 1
        }
        
        try:
            response = requests.get(
                self.BUILDING_URL,
                params=params,
                timeout=10
            )
            
            data = xmltodict.parse(response.content)
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            if isinstance(items, dict):
                items = [items]
            
            if items:
                item = items[0]
                return BuildingInfo(
                    building_name=item.get("bldNm", ""),
                    main_purpose=item.get("mainPurpsCdNm", ""),
                    total_floor_area=float(item.get("totArea", 0) or 0),
                    building_area=float(item.get("archArea", 0) or 0),
                    floor_count=int(item.get("grndFlrCnt", 0) or 0),
                    approval_date=item.get("useAprDay", "")
                )
                
        except Exception as e:
            print(f"건축물대장 조회 오류: {e}")
        
        return None
    
    def _get_far_by_zone(self, zone: str) -> int:
        """용도지역별 용적률"""
        zone_far = {
            "제1종전용주거지역": 100, "제2종전용주거지역": 150,
            "제1종일반주거지역": 200, "제2종일반주거지역": 250,
            "제3종일반주거지역": 300, "준주거지역": 500,
            "중심상업지역": 1500, "일반상업지역": 1300,
            "근린상업지역": 900, "유통상업지역": 1100,
            "준공업지역": 400, "일반공업지역": 350,
            "전용공업지역": 300, "자연녹지지역": 100,
            "생산녹지지역": 100, "보전녹지지역": 80
        }
        for key, value in zone_far.items():
            if key in zone:
                return value
        return 250
    
    def _get_bcr_by_zone(self, zone: str) -> int:
        """용도지역별 건폐율"""
        zone_bcr = {
            "제1종전용주거지역": 50, "제2종전용주거지역": 50,
            "제1종일반주거지역": 60, "제2종일반주거지역": 60,
            "제3종일반주거지역": 50, "준주거지역": 70,
            "중심상업지역": 90, "일반상업지역": 80,
            "근린상업지역": 70, "유통상업지역": 80,
            "준공업지역": 70, "일반공업지역": 70,
            "전용공업지역": 70, "자연녹지지역": 20,
            "생산녹지지역": 20, "보전녹지지역": 20
        }
        for key, value in zone_bcr.items():
            if key in zone:
                return value
        return 60
    
    def _get_max_height_by_zone(self, zone: str) -> int:
        """용도지역별 최고높이 (미터)"""
        zone_height = {
            "제1종전용주거지역": 10, "제2종전용주거지역": 12,
            "제1종일반주거지역": 16, "제2종일반주거지역": 20,
            "제3종일반주거지역": 50, "준주거지역": 50
        }
        for key, value in zone_height.items():
            if key in zone:
                return value
        return 50
    
    def to_appraisal_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        조회된 데이터를 AppraisalContext 형식으로 변환
        """
        basic = data.get("basic_info") or LandBasicInfo()
        price = data.get("price_info") or LandPriceInfo()
        regulation = data.get("regulation_info") or RegulationInfo()
        transactions = data.get("transactions", [])
        building = data.get("building_info")
        
        return {
            # 기본 정보
            "parcel_id": basic.pnu,
            "address": basic.address,
            "land_area": basic.area,
            "land_category": basic.land_category,
            "zoning_code": basic.land_use_zone or regulation.use_zone,
            "land_use_situation": basic.land_use_situation,
            "ownership_type": basic.ownership_type,
            "road_side": basic.road_side,
            "terrain_height": basic.terrain_height,
            "terrain_shape": basic.terrain_shape,
            "change_date": basic.change_date,
            
            # 가격 정보
            "public_price": price.official_price,
            "public_price_per_sqm": price.official_price,
            "total_public_price": price.total_price,
            "public_price_year": price.base_year,
            
            # 규제 정보
            "regulations": {
                "floor_area_ratio": regulation.floor_area_ratio,
                "building_coverage_ratio": regulation.building_coverage_ratio,
                "max_height": regulation.max_height,
                "use_zone": regulation.use_zone,
                "use_district": regulation.use_district,
                "regulation_list": regulation.regulations or []
            },
            
            # 거래사례
            "recent_transactions": [
                {
                    "date": tx.transaction_date,
                    "amount": tx.transaction_amount,
                    "area": tx.land_area,
                    "price_per_sqm": tx.price_per_sqm,
                    "land_category": tx.land_category,
                    "land_use": tx.land_use
                }
                for tx in transactions
            ],
            
            # 건물 정보 (있는 경우)
            "building_info": {
                "name": building.building_name if building else "",
                "purpose": building.main_purpose if building else "",
                "total_area": building.total_floor_area if building else 0,
                "floor_count": building.floor_count if building else 0
            } if building else None,
            
            # 감정평가 (별도 입력)
            "appraisal_price": 0,
            "appraisal_date": ""
        }
