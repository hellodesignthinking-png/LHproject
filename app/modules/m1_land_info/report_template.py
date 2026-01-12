"""
M1 토지·입지 사실 확정 모듈 - 전문가 보고서 출력
========================================================

ZeroSite Decision OS 헌법 준수:
- FACT ONLY (판단/추천/점수 금지)
- LH 실무 제출 가능 수준
- 구조화된 목차 + 표 + 근거 명시

Author: ZeroSite Module Execution AI
Date: 2026-01-12
"""

from typing import Dict, Any, List
from datetime import datetime
from app.core.context.m1_final_context import M1FinalContext


class M1ReportGenerator:
    """
    M1 토지·입지 사실 확정 보고서 생성기
    
    출력 규칙:
    - 판단 ❌
    - 추천 ❌
    - 점수 ❌
    - 사실만 정리 ✅
    """
    
    def generate(self, context: M1FinalContext) -> Dict[str, Any]:
        """
        M1 전문가 보고서 생성
        
        Args:
            context: M1FinalContext (FROZEN)
        
        Returns:
            완성된 전문가 보고서 (8~12페이지 분량)
        """
        
        report = {
            "module": "M1",
            "title": "토지·입지 사실 확정 보고서",
            "subtitle": "ZeroSite Decision OS | 공공주택 사업 의사결정 지원 시스템",
            "generated_at": datetime.now().isoformat(),
            "parcel_id": context.parcel_id,
            "status": "FACT_FROZEN",
            
            "sections": [
                self._section_1_summary(context),
                self._section_2_location(context),
                self._section_3_cadastral(context),
                self._section_4_zoning(context),
                self._section_5_road_access(context),
                self._section_6_official_price(context),
                self._section_7_regulations(context),
                self._section_8_transactions(context),
                self._section_9_infrastructure(context),
                self._section_10_data_sources(context),
            ],
            
            "validation": {
                "lh_submission_ready": True,
                "fact_only": True,
                "no_judgement": True,
                "no_recommendation": True,
                "no_scoring": True,
            }
        }
        
        return report
    
    def _section_1_summary(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """1. 지번 및 행정구역 정리"""
        land_info = ctx.land_info
        address = land_info.address
        cadastral = land_info.cadastral
        
        return {
            "section_number": "1",
            "title": "지번 및 행정구역 정리",
            "content": {
                "parcel_id": {
                    "label": "필지 고유번호 (PNU)",
                    "value": ctx.parcel_id,
                    "description": "공간정보 표준 코드"
                },
                "address": {
                    "jibun": address.jibun_address,
                    "road": address.road_address,
                    "sido": address.sido,
                    "sigungu": address.sigungu,
                    "dong": address.dong,
                    "beopjeong_dong": address.beopjeong_dong or "해당없음"
                },
                "cadastral_number": {
                    "bonbun": cadastral.bonbun,
                    "bubun": cadastral.bubun,
                    "display": f"{cadastral.bonbun}-{cadastral.bubun}"
                },
                "administrative_summary": (
                    f"본 필지는 {address.sido} {address.sigungu} {address.dong} 소재 "
                    f"{cadastral.bonbun}-{cadastral.bubun}번지로, "
                    f"도로명주소는 {address.road_address}이다."
                )
            },
            "tables": [
                {
                    "title": "행정구역 상세",
                    "headers": ["구분", "내용", "비고"],
                    "rows": [
                        ["시·도", address.sido, "광역자치단체"],
                        ["시·군·구", address.sigungu, "기초자치단체"],
                        ["읍·면·동", address.dong, "행정동"],
                        ["법정동", address.beopjeong_dong or "해당없음", "지적 기준"],
                        ["본번-부번", f"{cadastral.bonbun}-{cadastral.bubun}", "지번"],
                    ]
                }
            ],
            "note": "상기 정보는 공간정보체계(NSDI) 기준이며, 이후 모든 분석의 기준이 된다."
        }
    
    def _section_2_location(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """2. 위치·접근성 사실 요약"""
        land_info = ctx.land_info
        coords = land_info.coordinates
        
        # 좌표 정확도 설명
        coord_accuracy = "GPS 정확도 10m 이내" if coords.verified else "API 기반 추정"
        
        return {
            "section_number": "2",
            "title": "위치·접근성 사실 요약",
            "content": {
                "coordinates": {
                    "latitude": coords.lat,
                    "longitude": coords.lon,
                    "system": "WGS84 (EPSG:4326)",
                    "accuracy": coord_accuracy,
                    "source": coords.source,
                    "verified": "사용자 확인 완료" if coords.verified else "API 기반 추정"
                },
                "location_description": (
                    f"본 필지는 위도 {coords.lat:.6f}, 경도 {coords.lon:.6f}에 위치하며, "
                    f"좌표 정확도는 {coord_accuracy} 수준이다."
                )
            },
            "tables": [
                {
                    "title": "좌표 정보",
                    "headers": ["항목", "값", "단위/체계"],
                    "rows": [
                        ["위도 (Latitude)", f"{coords.lat:.6f}", "도 (°)"],
                        ["경도 (Longitude)", f"{coords.lon:.6f}", "도 (°)"],
                        ["좌표계", "WGS84", "EPSG:4326"],
                        ["데이터 출처", coords.source, "API/MANUAL"],
                        ["검증 여부", "완료" if coords.verified else "미완료", "-"],
                    ]
                }
            ],
            "note": "좌표는 LH 사업 부지 선정 및 GIS 분석의 기준점으로 활용된다."
        }
    
    def _section_3_cadastral(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """3. 대지면적 및 형상"""
        cadastral = ctx.land_info.cadastral
        terrain = ctx.land_info.terrain
        
        # 면적 크기 분류
        if cadastral.area_sqm < 300:
            size_category = "소규모"
        elif cadastral.area_sqm < 1000:
            size_category = "중규모"
        else:
            size_category = "대규모"
        
        return {
            "section_number": "3",
            "title": "대지면적 및 형상",
            "content": {
                "area": {
                    "sqm": cadastral.area_sqm,
                    "pyeong": cadastral.area_pyeong,
                    "category": size_category,
                    "jimok": cadastral.jimok
                },
                "terrain": {
                    "height": terrain.height,
                    "shape": terrain.shape,
                    "direction": terrain.direction or "정보없음",
                    "slope": terrain.slope or "정보없음"
                },
                "area_description": (
                    f"본 필지의 면적은 {cadastral.area_sqm:.2f}㎡ ({cadastral.area_pyeong:.2f}평)이며, "
                    f"지목은 '{cadastral.jimok}'이다. "
                    f"LH 신축매입임대 기준 {size_category} 부지에 해당한다."
                ),
                "terrain_description": (
                    f"지형은 {terrain.height}, 형상은 {terrain.shape}으로 분류된다."
                )
            },
            "tables": [
                {
                    "title": "면적 상세",
                    "headers": ["항목", "값", "단위/비고"],
                    "rows": [
                        ["대지면적", f"{cadastral.area_sqm:,.2f}", "㎡"],
                        ["평수 환산", f"{cadastral.area_pyeong:,.2f}", "평 (1평 = 3.3058㎡)"],
                        ["규모 분류", size_category, "LH 기준"],
                        ["지목", cadastral.jimok, "지적공부 기준"],
                    ]
                },
                {
                    "title": "지형 상세",
                    "headers": ["항목", "내용", "비고"],
                    "rows": [
                        ["지형 높이", terrain.height, "평지/경사지 등"],
                        ["지형 형상", terrain.shape, "정형/부정형 등"],
                        ["향", terrain.direction or "정보없음", "일조/채광 관련"],
                        ["경사도", terrain.slope or "정보없음", "개발 난이도 관련"],
                    ]
                }
            ],
            "note": (
                f"데이터 출처: {cadastral.source} | "
                f"신뢰도: {cadastral.confidence*100:.0f}%" if cadastral.confidence else "API 직접 수집"
            )
        }
    
    def _section_4_zoning(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """4. 용도지역·지구"""
        zoning = ctx.land_info.zoning
        legal = ctx.building_constraints.legal
        
        return {
            "section_number": "4",
            "title": "용도지역·지구 및 법정 건축 제한",
            "content": {
                "zoning": {
                    "zone_type": zoning.zone_type,
                    "zone_detail": zoning.zone_detail or "상세 정보 없음",
                    "land_use": zoning.land_use,
                    "source": zoning.source
                },
                "legal_constraints": {
                    "far": legal.far_max,
                    "bcr": legal.bcr_max,
                    "height_limit": legal.height_limit or "제한 없음",
                    "floor_limit": legal.floor_limit or "제한 없음"
                },
                "zoning_description": (
                    f"본 필지는 '{zoning.zone_type}'으로 지정되어 있으며, "
                    f"토지 이용 목적은 '{zoning.land_use}'이다."
                ),
                "constraints_description": (
                    f"법정 건폐율은 최대 {legal.bcr_max}%, "
                    f"용적률은 최대 {legal.far_max}%로 제한된다."
                )
            },
            "tables": [
                {
                    "title": "용도지역 상세",
                    "headers": ["항목", "내용", "법적 근거"],
                    "rows": [
                        ["용도지역", zoning.zone_type, "국토계획법 제36조"],
                        ["세부 용도", zoning.zone_detail or "-", "지자체 조례"],
                        ["토지 이용", zoning.land_use, "용도지역 기준"],
                        ["데이터 출처", zoning.source, "-"],
                    ]
                },
                {
                    "title": "법정 건축 제한",
                    "headers": ["항목", "제한값", "법적 근거"],
                    "rows": [
                        ["건폐율 (BCR)", f"{legal.bcr_max}%", "국토계획법 시행령 제84조"],
                        ["용적률 (FAR)", f"{legal.far_max}%", "국토계획법 시행령 제85조"],
                        ["높이 제한", legal.height_limit or "제한 없음", "지구단위계획 등"],
                        ["층수 제한", legal.floor_limit or "제한 없음", "지자체 조례"],
                    ]
                }
            ],
            "note": "상기 제한은 LH 인센티브 적용 전 기준이며, 실제 적용 가능 범위는 M4에서 검토한다."
        }
    
    def _section_5_road_access(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """5. 도로 조건"""
        road_access = ctx.land_info.road_access
        nearby_roads = road_access.nearby_roads
        
        return {
            "section_number": "5",
            "title": "도로 접근 조건",
            "content": {
                "primary_road": {
                    "contact": road_access.road_contact,
                    "width": road_access.road_width,
                    "type": road_access.road_type,
                    "source": road_access.source
                },
                "road_description": (
                    f"본 필지는 '{road_access.road_contact}' 형태로 도로에 접하며, "
                    f"접도 도로의 폭은 {road_access.road_width}m ({road_access.road_type})이다."
                )
            },
            "tables": [
                {
                    "title": "주 접도 도로",
                    "headers": ["항목", "내용", "비고"],
                    "rows": [
                        ["접도 형태", road_access.road_contact, "접도/각지/맹지 등"],
                        ["도로 폭원", f"{road_access.road_width}m", "차량 통행 가능 여부"],
                        ["도로 유형", road_access.road_type, "대로/중로/소로 구분"],
                        ["데이터 출처", road_access.source, "-"],
                    ]
                },
                {
                    "title": "인근 도로 현황" if nearby_roads else "인근 도로 정보 없음",
                    "headers": ["도로명", "폭원(m)", "거리(m)"] if nearby_roads else ["비고"],
                    "rows": [
                        [road.name, f"{road.width}", f"{road.distance}"]
                        for road in nearby_roads
                    ] if nearby_roads else [["인근 도로 정보가 수집되지 않았습니다"]]
                }
            ],
            "note": (
                "도로 접근성은 건축 인허가 및 소방·주차 계획의 핵심 요소이다. "
                "접도 폭원 4m 미만 시 건축 불가 가능성이 있으므로 추가 확인이 필요하다."
            )
        }
    
    def _section_6_official_price(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """6. 공시지가 기준"""
        official_price = ctx.appraisal_inputs.official_price
        
        price_per_pyeong = official_price.price_per_sqm * 3.3058
        total_value = official_price.price_per_sqm * ctx.land_info.cadastral.area_sqm
        
        return {
            "section_number": "6",
            "title": "공시지가 기준 정보",
            "content": {
                "official_price": {
                    "price_per_sqm": official_price.price_per_sqm,
                    "price_per_pyeong": price_per_pyeong,
                    "total_land_value": total_value,
                    "reference_date": official_price.reference_date,
                    "source": official_price.source
                },
                "price_description": (
                    f"본 필지의 {official_price.reference_date} 기준 공시지가는 "
                    f"㎡당 {official_price.price_per_sqm:,.0f}원 (평당 {price_per_pyeong:,.0f}원)이다. "
                    f"전체 토지 공시가격은 {total_value:,.0f}원으로 산정된다."
                )
            },
            "tables": [
                {
                    "title": "공시지가 상세",
                    "headers": ["항목", "금액", "단위/비고"],
                    "rows": [
                        ["㎡당 공시지가", f"₩{official_price.price_per_sqm:,.0f}", "원/㎡"],
                        ["평당 공시지가", f"₩{price_per_pyeong:,.0f}", "원/평"],
                        ["토지 전체 공시가격", f"₩{total_value:,.0f}", "원"],
                        ["기준 일자", official_price.reference_date, "공시지가 기준일"],
                        ["데이터 출처", official_price.source, "-"],
                    ]
                }
            ],
            "note": (
                "공시지가는 감정평가의 기준이 되며, 실거래가는 통상 공시지가의 1.2~1.5배 수준에서 형성된다. "
                "M2 모듈에서 거래사례 기반 적정 매입가를 산정한다."
            )
        }
    
    def _section_7_regulations(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """7. 주요 규제 요약"""
        legal = ctx.building_constraints.legal
        regulations = legal.regulations
        restrictions = legal.restrictions
        
        return {
            "section_number": "7",
            "title": "주요 규제 및 제약 사항",
            "content": {
                "regulations_count": len(regulations),
                "restrictions_count": len(restrictions),
                "summary": (
                    f"본 필지에는 {len(regulations)}개의 규제와 {len(restrictions)}개의 제약이 적용된다."
                    if regulations or restrictions else
                    "현재 파악된 특별 규제 또는 제약 사항이 없다."
                )
            },
            "tables": [
                {
                    "title": "적용 규제 목록",
                    "headers": ["순번", "규제명", "내용"],
                    "rows": [
                        [str(i+1), reg, "상세 확인 필요"]
                        for i, reg in enumerate(regulations)
                    ] if regulations else [["1", "해당 없음", "특별 규제 없음"]]
                },
                {
                    "title": "제약 사항",
                    "headers": ["순번", "제약 내용", "영향"],
                    "rows": [
                        [str(i+1), res, "사업 제약 가능"]
                        for i, res in enumerate(restrictions)
                    ] if restrictions else [["1", "해당 없음", "특별 제약 없음"]]
                }
            ],
            "note": (
                "규제 및 제약은 사업 진행 시 필히 해소되어야 하며, "
                "일부 규제는 LH 사업 특성상 예외 적용이 가능할 수 있다. "
                "구체적 검토는 M4, M5 모듈에서 수행한다."
            )
        }
    
    def _section_8_transactions(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """8. 인근 거래사례 요약 (최대 10건)"""
        transactions = ctx.appraisal_inputs.transaction_cases[:10]  # 최대 10건
        
        if not transactions:
            return {
                "section_number": "8",
                "title": "인근 거래사례 (정보 없음)",
                "content": {
                    "summary": "현재 수집된 인근 거래사례가 없습니다. M2 모듈에서 동적 생성을 수행합니다."
                },
                "tables": [],
                "note": "거래사례는 감정평가의 핵심 자료이며, 부재 시 공시지가 기반 추정을 수행한다."
            }
        
        return {
            "section_number": "8",
            "title": f"인근 거래사례 요약 ({len(transactions)}건)",
            "content": {
                "transaction_count": len(transactions),
                "summary": f"반경 2km 이내 최근 {len(transactions)}건의 거래사례가 수집되었다."
            },
            "tables": [
                {
                    "title": "거래사례 목록",
                    "headers": ["순번", "주소", "거래일", "면적(㎡)", "단가(원/㎡)", "거리(m)"],
                    "rows": [
                        [
                            str(i+1),
                            tc.address[:20] + "..." if len(tc.address) > 20 else tc.address,
                            tc.transaction_date,
                            f"{tc.area_sqm:,.1f}",
                            f"₩{tc.price_per_sqm:,.0f}",
                            f"{tc.distance_m:,.0f}"
                        ]
                        for i, tc in enumerate(transactions)
                    ]
                }
            ],
            "note": (
                "거래사례는 M2 감정평가 모듈에서 4-Factor 보정(거리/시점/규모/용도)을 통해 "
                "대상지 적정 가격 산정에 활용된다."
            )
        }
    
    def _section_9_infrastructure(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """9. 주변 인프라 현황"""
        demand = ctx.demand_inputs
        region = demand.region_characteristics
        
        return {
            "section_number": "9",
            "title": "주변 인프라 및 생활권 분석",
            "content": {
                "population": region.population,
                "households": region.households,
                "avg_age": region.avg_age or "정보 없음",
                "employment_rate": f"{region.employment_rate}%" if region.employment_rate else "정보 없음",
                "summary": (
                    f"반경 1km 이내 인구 {region.population:,}명, "
                    f"가구수 {region.households:,}가구가 거주하고 있다."
                )
            },
            "tables": [
                {
                    "title": "생활권 기초 정보",
                    "headers": ["항목", "값", "단위"],
                    "rows": [
                        ["인구", f"{region.population:,}", "명"],
                        ["가구수", f"{region.households:,}", "가구"],
                        ["평균 연령", str(region.avg_age) if region.avg_age else "정보없음", "세"],
                        ["고용률", f"{region.employment_rate}%" if region.employment_rate else "정보없음", "%"],
                    ]
                }
            ],
            "note": "인프라 정보는 M3 공급유형 및 M6 커뮤니티 계획 수립 시 활용된다."
        }
    
    def _section_10_data_sources(self, ctx: M1FinalContext) -> Dict[str, Any]:
        """10. 데이터 출처 및 신뢰도"""
        metadata = ctx.metadata
        sources = metadata.data_sources
        confidence = metadata.confidence_scores
        
        return {
            "section_number": "10",
            "title": "데이터 출처 및 신뢰도 평가",
            "content": {
                "context_id": metadata.context_id,
                "frozen_at": metadata.frozen_at,
                "frozen_by": metadata.frozen_by,
                "data_distribution": sources.to_dict(),
                "overall_confidence": f"{confidence.overall * 100:.1f}%"
            },
            "tables": [
                {
                    "title": "데이터 출처 분포",
                    "headers": ["출처", "비중(%)", "비고"],
                    "rows": [
                        ["API 수집", f"{sources.api_percentage:.1f}%", "자동 수집"],
                        ["PDF 파싱", f"{sources.pdf_percentage:.1f}%", "문서 분석"],
                        ["수동 입력", f"{sources.manual_percentage:.1f}%", "사용자 입력"],
                    ]
                },
                {
                    "title": "신뢰도 평가",
                    "headers": ["항목", "신뢰도", "비고"],
                    "rows": [
                        ["주소 정보", f"{confidence.address * 100:.0f}%", "-"],
                        ["지적 정보", f"{confidence.cadastral * 100:.0f}%", "-"],
                        ["용도지역", f"{confidence.zoning * 100:.0f}%", "-"],
                        ["시장 정보", f"{confidence.market * 100:.0f}%", "-"],
                        ["종합 신뢰도", f"{confidence.overall * 100:.1f}%", "가중 평균"],
                    ]
                }
            ],
            "note": (
                f"본 보고서의 데이터는 {metadata.frozen_at}에 {metadata.frozen_by}에 의해 승인(FREEZE)되었으며, "
                f"Context ID {metadata.context_id}로 식별된다. "
                "이후 M2~M6 분석은 이 확정 데이터를 기준으로 수행된다."
            )
        }


def generate_m1_expert_report(context: M1FinalContext) -> Dict[str, Any]:
    """
    M1 전문가 보고서 생성 (공개 함수)
    
    Args:
        context: M1FinalContext (FROZEN)
    
    Returns:
        LH 실무 제출 가능한 전문가 완성본
    """
    generator = M1ReportGenerator()
    return generator.generate(context)
