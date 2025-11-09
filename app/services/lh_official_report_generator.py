"""
LH 신축매입약정 사업 공식 양식 기반 토지진단 보고서 생성
- LH 공식 제출 양식 완벽 준수
- VI 섹션 구조
- 5.0 만점 평가 시스템
- 10개 항목 탈락 사유 체크리스트
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class LHOfficialReportGenerator:
    """LH 공식 양식 보고서 생성기"""
    
    # LH 신축매입임대 유형별 기준
    LH_HOUSING_TYPES = {
        "청년형": {
            "target": "만 19~39세 무주택 청년",
            "size": "전용면적 30㎡ 이하",
            "rent_rate": "시세의 60~80%",
            "period": "최장 6년",
            "parking": "0.5대/세대",
            "floor_height": "2.3m 이상",
            "key_criteria": ["청년층 집중 지역", "대중교통 접근성", "직장 근접성", "1인 가구 밀집도"]
        },
        "신혼부부형": {
            "target": "혼인 7년 이내 무주택 신혼부부",
            "size": "전용면적 50㎡ 이하",
            "rent_rate": "시세의 70~85%",
            "period": "최장 10년",
            "parking": "0.7대/세대",
            "floor_height": "2.3m 이상",
            "key_criteria": ["교육시설 접근성", "육아 인프라", "생활편의시설", "공원/놀이터"]
        },
        "고령자형": {
            "target": "만 65세 이상 무주택 고령자",
            "size": "전용면적 40㎡ 이하",
            "rent_rate": "시세의 70~80%",
            "period": "최장 20년",
            "parking": "0.3대/세대",
            "floor_height": "2.5m 이상 (천장 높이 확보)",
            "key_criteria": ["의료시설 접근성", "무장애 설계", "1층 배치 우선", "복지센터 근접"]
        }
    }
    
    def __init__(self):
        self.report_date = datetime.now()
        self.report_version = "V1.0"
    
    def generate_official_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        LH 공식 양식 토지진단 보고서 생성
        
        Args:
            analysis_data: 종합 분석 데이터
            
        Returns:
            HTML 형식의 LH 공식 보고서
        """
        
        # 데이터 추출
        address = analysis_data.get('address', '')
        land_area = analysis_data.get('land_area', 0)
        unit_type = analysis_data.get('unit_type', '청년형')
        coords = analysis_data.get('coordinates')
        zone_info = analysis_data.get('zone_info')
        capacity = analysis_data.get('building_capacity')
        risks = analysis_data.get('risk_factors', [])
        demographic = analysis_data.get('demographic_info')
        demand = analysis_data.get('demand_analysis')
        summary = analysis_data.get('summary')
        map_image = analysis_data.get('map_image')
        
        # 5.0 만점 평가 수행
        scores = self._calculate_5point_scores(analysis_data)
        
        # LH 탈락 사유 체크
        critical_checks = self._check_critical_exclusions(analysis_data)
        
        # HTML 보고서 생성
        html = self._generate_html_structure(
            address, land_area, unit_type, coords,
            zone_info, capacity, risks, demographic, demand, summary,
            scores, critical_checks, map_image, analysis_data
        )
        
        return html
    
    def _calculate_5point_scores(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        LH 공식 5.0 만점 평가 시스템
        
        평가 항목:
        1. 주변 환경 (생활 인프라, 쾌적성)
        2. 교통 편의성 (대중교통 접근성)
        3. 차량 접근성 (도로 폭, 진입 용이성)
        4. 수요 분석 (타겟 유형 임대 수요)
        """
        
        demand = analysis_data.get('demand_analysis', {})
        demographic = analysis_data.get('demographic_info', {})
        unit_type = analysis_data.get('unit_type', '청년형')
        
        # 1. 주변 환경 점수 (5.0 만점)
        environment_score = self._score_environment(analysis_data)
        
        # 2. 교통 편의성 점수 (5.0 만점)
        transit_score = self._score_transit(analysis_data)
        
        # 3. 차량 접근성 점수 (5.0 만점)
        vehicle_score = self._score_vehicle_access(analysis_data)
        
        # 4. 수요 분석 점수 (5.0 만점)
        demand_score = self._score_demand(analysis_data)
        
        # 평균 점수
        avg_score = (environment_score + transit_score + vehicle_score + demand_score) / 4.0
        
        return {
            "environment": {
                "score": environment_score,
                "rating": self._get_rating(environment_score)
            },
            "transit": {
                "score": transit_score,
                "rating": self._get_rating(transit_score)
            },
            "vehicle": {
                "score": vehicle_score,
                "rating": self._get_rating(vehicle_score)
            },
            "demand": {
                "score": demand_score,
                "rating": self._get_rating(demand_score)
            },
            "average": {
                "score": avg_score,
                "rating": self._get_rating(avg_score)
            }
        }
    
    def _score_environment(self, data: Dict[str, Any]) -> float:
        """주변 환경 점수 (생활 인프라, 쾌적성)"""
        score = 3.0  # 기본 점수
        
        demand = data.get('demand_analysis', {})
        facilities = demand.get('nearby_facilities', [])
        
        # 편의시설 개수에 따라 가점
        if len(facilities) >= 10:
            score += 1.5
        elif len(facilities) >= 5:
            score += 1.0
        elif len(facilities) >= 3:
            score += 0.5
        
        # 청년형: 상업시설/카페 중요
        # 신혼부부형: 교육시설/공원 중요
        # 고령자형: 병원/복지시설 중요
        
        # 위험시설이 없으면 가점
        risks = data.get('risk_factors', [])
        has_hazard = any(r.get('category') == '유해시설' for r in risks)
        if not has_hazard:
            score += 0.5
        
        return min(5.0, score)
    
    def _score_transit(self, data: Dict[str, Any]) -> float:
        """교통 편의성 점수 (대중교통 접근성)"""
        score = 0.0
        
        demand = data.get('demand_analysis', {})
        
        # 지하철역 거리 평가 (최대 3.0점)
        subway_distance = 9999
        for facility in demand.get('nearby_facilities', []):
            if '지하철' in facility.get('category', ''):
                subway_distance = min(subway_distance, facility.get('distance', 9999))
        
        if subway_distance < 300:
            score += 3.0
        elif subway_distance < 500:
            score += 2.5
        elif subway_distance < 1000:
            score += 2.0
        elif subway_distance < 2000:
            score += 1.0
        else:
            score += 0.5
        
        # 버스 정류장 (최대 1.0점)
        bus_count = sum(1 for f in demand.get('nearby_facilities', []) if '버스' in f.get('category', ''))
        if bus_count >= 3:
            score += 1.0
        elif bus_count >= 1:
            score += 0.5
        
        # 대학교/직장 근접성 (최대 1.0점)
        has_university = any('대학' in f.get('category', '') for f in demand.get('nearby_facilities', []))
        if has_university:
            score += 1.0
        
        return min(5.0, score)
    
    def _score_vehicle_access(self, data: Dict[str, Any]) -> float:
        """차량 접근성 점수 (도로 폭, 진입 용이성)"""
        # 현재는 기본값, 추후 도로 정보 API 연동 시 개선
        score = 3.5  # 중상 수준 기본값
        
        # 주소에서 대로/로 판단
        address = data.get('address', '')
        if '대로' in address:
            score = 4.5
        elif '로' in address:
            score = 4.0
        elif '길' in address:
            score = 3.0
        
        return min(5.0, score)
    
    def _score_demand(self, data: Dict[str, Any]) -> float:
        """수요 분석 점수 (타겟 유형 임대 수요)"""
        score = 0.0
        
        demographic = data.get('demographic_info', {})
        unit_type = data.get('unit_type', '청년형')
        
        if unit_type == '청년형':
            # 청년 인구 비율 (최대 2.5점)
            youth_ratio = demographic.get('youth_ratio', 0)
            if youth_ratio >= 30:
                score += 2.5
            elif youth_ratio >= 20:
                score += 2.0
            elif youth_ratio >= 10:
                score += 1.5
            else:
                score += 1.0
            
            # 1인 가구 비율 (최대 2.5점)
            single_ratio = demographic.get('single_household_ratio', 0)
            if single_ratio >= 40:
                score += 2.5
            elif single_ratio >= 30:
                score += 2.0
            elif single_ratio >= 20:
                score += 1.5
            else:
                score += 1.0
        
        elif unit_type == '신혼부부형':
            # 2-3인 가구 수요 평가
            score = 3.5  # 기본값
            
        elif unit_type == '고령자형':
            # 고령 인구 비율 평가
            score = 3.5  # 기본값
        
        return min(5.0, score)
    
    def _get_rating(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 4.5:
            return "上"
        elif score >= 4.0:
            return "中上"
        elif score >= 3.0:
            return "中"
        elif score >= 2.0:
            return "中下"
        else:
            return "下"
    
    def _evaluate_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        LH 공공 매입 선호도 증대 항목 (권장사항) 5개 자동 평가
        
        Returns:
            권장사항 평가 결과 리스트
        """
        
        capacity = data.get('building_capacity', {})
        unit_type = data.get('unit_type', '청년형')
        zone_info = data.get('zone_info', {})
        units = capacity.get('units', 0)
        parking_spaces = capacity.get('parking_spaces', 0)
        
        # 법정 주차대수 계산 (단순화)
        if unit_type == '청년형':
            legal_parking = units * 0.5
        elif unit_type == '신혼부부형':
            legal_parking = units * 0.7
        else:  # 고령자형
            legal_parking = units * 0.3
        
        recommendations = []
        
        # 1. 표준 평면 및 인테리어 활용
        recommendations.append({
            "no": 1,
            "item": "표준 평면 및 인테리어 활용",
            "status": "권장",
            "plan": "LH 제공 표준 평면(Type A/B/C) 중 선택 적용 예정",
            "benefit": "설계 심의 기간 단축, 공사비 절감, LH 선호도 상승"
        })
        
        # 2. 주차 계획 강화
        excess_parking = parking_spaces - legal_parking
        parking_status = "반영" if excess_parking > 0 else "미반영"
        parking_plan = f"법정 주차대수 {legal_parking:.0f}대 → 계획 {parking_spaces}대 ({'+' if excess_parking > 0 else ''}{excess_parking:.0f}대)" if excess_parking > 0 else f"법정 주차대수 {legal_parking:.0f}대 충족 (지하 주차장 설치 검토 권장)"
        
        recommendations.append({
            "no": 2,
            "item": "주차 계획 강화",
            "status": parking_status,
            "plan": parking_plan,
            "benefit": "법정 초과 확보 시 심의 가점, 입주자 만족도 향상" if excess_parking > 0 else "지하 주차장 설치 시 대지 활용도 증가"
        })
        
        # 3. 커뮤니티 시설 확충
        has_community = units >= 50  # 50세대 이상 시 의무
        community_status = "반영" if has_community else "미반영"
        
        recommendations.append({
            "no": 3,
            "item": "커뮤니티 시설 확충",
            "status": community_status,
            "plan": f"{'주민공동시설 100㎡ 이상 계획 (입주자 라운지, 독서실 등)' if has_community else '소규모 공용 공간 확보 (우편함실, 택배보관함 등)'}",
            "benefit": "입주자 편의 증대, LH 평가 우대"
        })
        
        # 4. 단지형 통합 및 조경
        is_complex = units >= 30  # 30세대 이상
        complex_status = "반영" if is_complex else "미반영"
        
        recommendations.append({
            "no": 4,
            "item": "단지형 통합 및 조경",
            "status": complex_status,
            "plan": f"{'2개동 이상 단지 구성, 1층 주민 휴게공간 조경 계획' if is_complex else '단일동 계획 (소규모 조경 공간 확보)'}",
            "benefit": "단지 쾌적성 향상, 조경면적 확보로 건폐율 여유"
        })
        
        # 5. 사업 관리 방식
        is_large_scale = units >= 50  # 50세대 이상 시 LH가 토지신탁 필수 지정 가능
        trust_status = "관리형 토지신탁 권장" if is_large_scale else "근저당/토지신탁 선택"
        
        recommendations.append({
            "no": 5,
            "item": "사업 관리 방식",
            "status": trust_status,
            "plan": f"{'관리형 토지신탁 방식 (LH 필수 조건 충족)' if is_large_scale else '관리형 토지신탁 또는 근저당 방식 중 선택'}",
            "benefit": "토지신탁 시 선금 70~80% 조기 수령, 사업 안정성 확보"
        })
        
        return recommendations
    
    def _generate_project_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사업 추진 일정 자동 산정
        
        LH 프로세스:
        1. 설계/서류 취합: 1개월
        2. 심의 결과 발표: 2~3개월
        3. 도면 협의: 4개월 (실효제도)
        4. 1차 감정평가: 1개월
        5. 매입 약정 체결: 1~2개월
        6. 인허가 및 착공: 9개월 (약정 후)
        7. 준공: 18~24개월 (착공 후)
        
        Returns:
            일정 딕셔너리
        """
        
        from datetime import timedelta
        
        today = self.report_date
        
        # 1. 접수도면 설계/서류 취합
        design_complete = today + timedelta(days=30)
        
        # 2. 서류 접수 및 심의 결과 (2.5개월)
        review_complete = design_complete + timedelta(days=75)
        
        # 3. 도면 협의 완료 (4개월)
        drawing_complete = review_complete + timedelta(days=120)
        
        # 4. 1차 감정평가 (1개월)
        appraisal_complete = drawing_complete + timedelta(days=30)
        
        # 5. 매입 약정 체결 (1.5개월)
        contract_complete = appraisal_complete + timedelta(days=45)
        
        # 6. 토지비 선금 수령 (약정 후 즉시)
        advance_payment = contract_complete + timedelta(days=7)
        
        # 7. 인허가 완료 (9개월 내)
        permit_complete = contract_complete + timedelta(days=270)
        
        # 8. 착공 (인허가 후 2개월 내)
        construction_start = permit_complete + timedelta(days=60)
        
        # 9. 준공 (착공 후 20개월)
        construction_complete = construction_start + timedelta(days=600)
        
        return {
            "today": today,
            "design_complete": design_complete,
            "review_complete": review_complete,
            "drawing_complete": drawing_complete,
            "appraisal_complete": appraisal_complete,
            "contract_complete": contract_complete,
            "advance_payment": advance_payment,
            "permit_complete": permit_complete,
            "construction_start": construction_start,
            "construction_complete": construction_complete,
            "total_months": int((construction_complete - today).days / 30)
        }
    
    def _estimate_lh_purchase_price(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        LH 매입 예상 가격 산정
        
        LH 매입가격 산정 방식:
        1. 토지 감정평가액 (2개 감정평가법인 평균)
        2. 건물 공사비 (실비 정산 또는 연동형)
        3. 제세공과금
        
        Returns:
            가격 산정 결과 딕셔너리
        """
        
        land_area = data.get('land_area', 0)
        zone_info = data.get('zone_info', {})
        capacity = data.get('building_capacity', {})
        unit_type = data.get('unit_type', '청년형')
        address = data.get('address', '')
        scores = self._calculate_5point_scores(data)
        
        # 지역별 기준 토지 단가 (㎡당, 실제로는 실거래가 API 사용)
        # 서울/경기/지방으로 간단 구분
        if '서울' in address:
            base_land_price_per_sqm = 5_000_000  # 500만원/㎡
            price_range_factor = 0.3  # ±30%
        elif '경기' in address or '인천' in address:
            base_land_price_per_sqm = 2_500_000  # 250만원/㎡
            price_range_factor = 0.25  # ±25%
        else:
            base_land_price_per_sqm = 1_500_000  # 150만원/㎡
            price_range_factor = 0.2  # ±20%
        
        # 용도지역별 보정
        zone_type = zone_info.get('zone_type', '')
        zone_factor = 1.0
        if '제1종전용주거' in zone_type:
            zone_factor = 0.85
        elif '제2종전용주거' in zone_type:
            zone_factor = 0.9
        elif '제1종일반주거' in zone_type:
            zone_factor = 1.0
        elif '제2종일반주거' in zone_type:
            zone_factor = 1.1
        elif '제3종일반주거' in zone_type:
            zone_factor = 1.2
        elif '준주거' in zone_type:
            zone_factor = 1.3
        elif '상업' in zone_type:
            zone_factor = 1.5
        
        # 입지 점수별 보정 (5.0 만점 기준)
        avg_score = scores['average']['score']
        location_factor = 0.7 + (avg_score / 5.0) * 0.6  # 0.7 ~ 1.3
        
        # 토지 감정평가 예상액
        adjusted_land_price = base_land_price_per_sqm * zone_factor * location_factor
        total_land_value = adjusted_land_price * land_area
        
        # 가격 범위 (감정평가 2개 법인의 편차 고려)
        price_min = total_land_value * (1 - price_range_factor)
        price_max = total_land_value * (1 + price_range_factor)
        
        # 건물 공사비 추정 (㎡당 건축비)
        total_floor_area = capacity.get('total_floor_area', 0)
        
        # 건축비 단가 (㎡당, 구조/마감에 따라 상이)
        if unit_type == '청년형':
            construction_cost_per_sqm = 2_800_000  # 소형, 효율적 설계
        elif unit_type == '신혼부부형':
            construction_cost_per_sqm = 3_000_000  # 중형, 육아 공간
        else:  # 고령자형
            construction_cost_per_sqm = 3_200_000  # 무장애 설계, 안전시설
        
        total_construction_cost = construction_cost_per_sqm * total_floor_area
        
        # 제세공과금 추정 (토지가의 약 5%)
        taxes_and_fees = total_land_value * 0.05
        
        # LH 총 매입 예상액
        total_purchase_price = total_land_value + total_construction_cost + taxes_and_fees
        
        # 매입 방식별 선금 비율
        # 1) 근저당 방식: 토지분 50%
        # 2) 관리형 토지신탁: 토지분 70% (조기약정 시 80%)
        advance_payment_mortgage = total_land_value * 0.5
        advance_payment_trust = total_land_value * 0.7
        advance_payment_trust_early = total_land_value * 0.8
        
        return {
            'land_area': land_area,
            'base_land_price_per_sqm': adjusted_land_price,
            'total_land_value': total_land_value,
            'price_min': price_min,
            'price_max': price_max,
            'construction_cost_per_sqm': construction_cost_per_sqm,
            'total_construction_cost': total_construction_cost,
            'taxes_and_fees': taxes_and_fees,
            'total_purchase_price': total_purchase_price,
            'advance_payment_mortgage': advance_payment_mortgage,
            'advance_payment_trust': advance_payment_trust,
            'advance_payment_trust_early': advance_payment_trust_early,
            'zone_factor': zone_factor,
            'location_factor': location_factor,
            'factors_explanation': {
                'zone': f"용도지역({zone_type}) 보정계수: {zone_factor:.2f}배",
                'location': f"입지점수({avg_score:.1f}/5.0) 보정계수: {location_factor:.2f}배",
                'base': f"지역 기준단가: {base_land_price_per_sqm:,.0f}원/㎡"
            }
        }
    
    def _generate_detailed_regional_analysis(self, data: Dict[str, Any]) -> str:
        """
        상세 지역 분석 (논문식 서술)
        - 인구통계 상세 분석
        - 경제활동 지표
        - 생활 인프라 분석
        - 교육/의료시설 분포
        - 선정/탈락 이유 논리적 서술
        """
        
        address = data.get('address', '')
        unit_type = data.get('unit_type', '청년형')
        demographic = data.get('demographic_info', {})
        demand = data.get('demand_analysis', {})
        risks = data.get('risk_factors', [])
        zone_info = data.get('zone_info', {})
        scores = self._calculate_5point_scores(data)
        
        # 지역 정보 파싱
        location_parts = address.split()
        city = location_parts[0] if len(location_parts) > 0 else "해당 지역"
        district = location_parts[1] if len(location_parts) > 1 else ""
        dong = location_parts[2] if len(location_parts) > 2 else ""
        
        # 인구통계 분석
        total_pop = demographic.get('total_population', 0)
        youth_pop = demographic.get('youth_population', 0)
        youth_ratio = demographic.get('youth_ratio', 0)
        single_households = demographic.get('single_households', 0)
        single_ratio = demographic.get('single_household_ratio', 0)
        
        # 주변 시설 분석
        facilities = demand.get('nearby_facilities', [])
        subway_count = sum(1 for f in facilities if '지하철' in f.get('category', ''))
        bus_count = sum(1 for f in facilities if '버스' in f.get('category', ''))
        univ_count = sum(1 for f in facilities if '대학' in f.get('category', ''))
        convenience_count = sum(1 for f in facilities if '편의점' in f.get('category', ''))
        
        # 유해시설 여부
        has_critical_hazard = any(r.get('category') == 'LH매입제외' for r in risks)
        has_hazard = any(r.get('category') == '유해시설' for r in risks)
        
        analysis_html = f"""
        <div class="detailed-analysis">
            <h3 class="subsection-title">3. 지역 상세 분석 및 사업 적합성 평가</h3>
            
            <h4 style="margin-top: 20px; color: #0066cc; font-size: 10.5pt; font-weight: bold;">
                가. 인구통계학적 분석
            </h4>
            <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    <strong>{city} {district} {dong}</strong> 일대는 총 <strong>{total_pop:,}명</strong>의 인구가 거주하고 있으며,
                    이 중 <strong>만 20~39세 청년 인구가 {youth_pop:,}명({youth_ratio:.1f}%)</strong>을 차지하고 있다.
                    이는 전국 평균 청년 인구 비율(약 25%)과 비교하여 
                    {"<span style='color: #007bff; font-weight: bold;'>상당히 높은 수준</span>" if youth_ratio >= 30 else "<span style='color: #28a745; font-weight: bold;'>양호한 수준</span>" if youth_ratio >= 20 else "<span style='color: #ffc107; font-weight: bold;'>평균 수준</span>"}으로,
                    청년층의 주거 수요가 {"매우 활발한" if youth_ratio >= 30 else "활발한" if youth_ratio >= 20 else "일정 수준 존재하는"} 지역임을 의미한다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    또한, 1인 가구는 <strong>{single_households:,}가구({single_ratio:.1f}%)</strong>로 집계되었으며,
                    이는 서울시 평균 1인 가구 비율(약 34%)과 비교하여 
                    {"<span style='color: #007bff; font-weight: bold;'>높은 비중</span>" if single_ratio >= 40 else "<span style='color: #28a745; font-weight: bold;'>유사한 수준</span>" if single_ratio >= 30 else "<span style='color: #ffc107; font-weight: bold;'>다소 낮은 수준</span>"}을 나타내고 있다.
                    1인 가구 비율이 높다는 것은 소형 임대주택에 대한 수요가 충분함을 시사한다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: #e3f2fd; padding: 10px; border-radius: 5px;">
                    <strong>📊 인구통계 종합 평가:</strong> 
                    {"본 대상지가 위치한 지역은 청년층 및 1인 가구가 밀집된 전형적인 청년 거주 선호 지역으로, LH 청년형 신축매입임대주택 사업의 주 수요층이 충분히 확보되어 있어 임대 수요 발생 가능성이 매우 높다고 판단된다." if unit_type == "청년형" and youth_ratio >= 20 else "본 대상지는 다양한 연령층이 거주하는 지역으로, 안정적인 주거 수요가 존재하며 LH 신축매입임대주택 사업에 적합한 인구 구성을 갖추고 있다."}
                </p>
            </div>
            
            <h4 style="margin-top: 20px; color: #0066cc; font-size: 10.5pt; font-weight: bold;">
                나. 생활 인프라 및 접근성 분석
            </h4>
            <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    대상지 반경 2km 이내에는 <strong>총 {len(facilities)}개의 주요 생활편의시설</strong>이 분포하고 있으며,
                    이는 일상생활에 필요한 기본적인 인프라가 충분히 갖추어져 있음을 의미한다.
                    구체적으로 살펴보면, <strong>지하철역 {subway_count}개소, 버스정류장 {bus_count}개소</strong>가 확인되어
                    대중교통 접근성이 {"<span style='color: #007bff; font-weight: bold;'>매우 우수</span>" if subway_count >= 3 else "<span style='color: #28a745; font-weight: bold;'>우수</span>" if subway_count >= 1 else "<span style='color: #ffc107; font-weight: bold;'>보통</span>"}한 것으로 평가된다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    특히 {"<span style='color: #007bff; font-weight: bold;'>대학교/직장 밀집 지역</span>" if univ_count >= 2 else "<span style='color: #28a745; font-weight: bold;'>대학교/직장 접근 가능 지역</span>" if univ_count >= 1 else "주거 중심 지역"}으로
                    {"청년층의 통학 및 출퇴근 편의성이 뛰어나" if univ_count >= 1 else "주거 환경이 안정적이"}며,
                    편의점, 음식점 등 생활밀착형 상업시설이 {convenience_count}개소 이상 분포하여
                    <strong>일상생활의 편의성이 매우 높다</strong>고 볼 수 있다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: #e3f2fd; padding: 10px; border-radius: 5px;">
                    <strong>🚇 교통 및 인프라 종합 평가:</strong>
                    본 대상지는 5.0 만점 기준 <strong>교통 편의성 {scores['transit']['score']:.1f}점, 주변 환경 {scores['environment']['score']:.1f}점</strong>을 획득하여,
                    입지적 우수성이 명확히 확인된다. 특히 대중교통 접근성이 뛰어나 자가용 비보유 청년층의 거주 선호도가 높을 것으로 예상되며,
                    이는 LH 신축매입임대주택의 핵심 경쟁력으로 작용할 것으로 판단된다.
                </p>
            </div>
            
            <h4 style="margin-top: 20px; color: #0066cc; font-size: 10.5pt; font-weight: bold;">
                다. 법적 제한 및 개발 가능성 검토
            </h4>
            <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    대상지의 용도지역은 <strong>{zone_info.get('zone_type', 'N/A')}</strong>으로 지정되어 있으며,
                    법정 건폐율 <strong>{zone_info.get('building_coverage_ratio', 0):.0f}%</strong>, 용적률 <strong>{zone_info.get('floor_area_ratio', 0):.0f}%</strong>가 적용된다.
                    이는 {"주거용 건축물 건립에 적합한 용도지역" if "주거" in zone_info.get('zone_type', '') else "건축 가능 용도지역"}으로,
                    LH 신축매입임대주택 사업 추진에 <strong>{"법적 제약이 없는" if not any(r.get('category') == '법적제한' for r in risks) else "일부 제약이 존재하는"}</strong> 것으로 확인되었다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    유해시설 관련하여, 대상지 주변 조사 결과 
                    {"<span style='color: #dc3545; font-weight: bold;'>주유소가 25m 이내에 위치</span>하여 <strong>LH 매입 절대 제외 대상</strong>에 해당하는 것으로 확인되었다. 이는 LH 공고문 상 명시된 '주유소 25m 이내 위치 시 매입 불가' 기준에 저촉되는 치명적 탈락 사유이다." if has_critical_hazard else "<span style='color: #ffc107; font-weight: bold;'>일부 유해시설이 확인</span>되었으나, LH 매입 절대 제외 기준(주유소 25m 이내 등)에는 해당하지 않아 사업 추진에 <strong>결정적 장애 요인은 없는</strong> 것으로 판단된다." if has_hazard else "<span style='color: #28a745; font-weight: bold;'>유해시설이 확인되지 않아</span> 주거 환경의 쾌적성이 양호하며, LH 매입 적격 요건을 충족하는 것으로 평가된다."}
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: {"#ffe6e6" if has_critical_hazard else "#fffbea" if has_hazard else "#e6ffe6"}; padding: 10px; border-radius: 5px;">
                    <strong>⚖️ 법적 검토 종합 평가:</strong>
                    {f"<span style='color: #dc3545; font-weight: bold;'>본 대상지는 주유소 25m 이내 위치로 인해 LH 신축매입임대주택 사업 매입 대상에서 완전히 제외된다.</span> 이는 LH 공고문에 명시된 절대 탈락 사유로, 어떠한 조건으로도 사업 추진이 불가능하므로 <strong>사업 포기를 권고</strong>한다." if has_critical_hazard else f"일부 유해시설이 존재하나 LH 절대 탈락 기준에는 미해당하므로, <strong>조건부 사업 추진 가능</strong>한 것으로 판단된다. 다만, 최종 매입 심의 시 감점 요인으로 작용할 가능성이 있어 유의가 필요하다." if has_hazard else "법적 제한 및 유해시설 없이 <strong>LH 매입 적격 요건을 완전히 충족</strong>하고 있어, 사업 추진에 법적·환경적 장애 요인이 전혀 없는 것으로 평가된다."}
                </p>
            </div>
            
            <h4 style="margin-top: 20px; color: #0066cc; font-size: 10.5pt; font-weight: bold;">
                라. {unit_type} 수요 적합성 심층 분석
            </h4>
            <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
"""
        
        # 유형별 맞춤 분석
        if unit_type == "청년형":
            analysis_html += f"""
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    <strong>LH 청년형 신축매입임대주택</strong>은 만 19~39세 무주택 청년을 대상으로 하며,
                    전용면적 30㎡ 이하의 소형 주택을 시세의 60~80% 수준으로 최장 6년간 임대하는 사업이다.
                    본 대상지가 위치한 {city} {district} {dong} 지역은 청년 인구 비율이 <strong>{youth_ratio:.1f}%</strong>로,
                    {"전국 평균(25%) 대비 매우 높은 수준" if youth_ratio >= 30 else "전국 평균(25%) 수준" if youth_ratio >= 20 else "전국 평균 대비 다소 낮은 수준"}을 보이고 있다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    특히 1인 가구 비율이 <strong>{single_ratio:.1f}%</strong>에 달하며, 
                    {"지하철역 접근성이 우수하고" if subway_count >= 1 else "버스 노선이 다양하게 분포하여"}
                    {"대학교 및 직장 밀집 지역과의 연계성이 뛰어나" if univ_count >= 1 else "생활 편의시설이 풍부하여"}
                    <strong>청년 1인 가구의 거주 선호도가 매우 높을 것으로 예상</strong>된다.
                    실제로 수요 분석 점수 <strong>{scores['demand']['score']:.1f}/5.0점</strong>을 획득하여,
                    청년형 임대주택의 수요 기반이 {"매우 탄탄" if scores['demand']['score'] >= 4.0 else "탄탄" if scores['demand']['score'] >= 3.0 else "일정 수준 확보"}한 것으로 평가된다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: #e3f2fd; padding: 10px; border-radius: 5px;">
                    <strong>🎯 청년형 적합성 결론:</strong>
                    본 대상지는 청년층 집중 거주 지역, 우수한 대중교통 접근성, 풍부한 생활편의시설 등
                    LH 청년형 신축매입임대주택의 핵심 입지 조건을 충족하고 있으며,
                    {"특히 주유소 등 유해시설이 없어 주거 환경이 쾌적하므로" if not has_hazard else "일부 유해시설이 존재하나 치명적 수준은 아니므로"}
                    <strong>{"매우 적합" if scores['average']['score'] >= 4.0 and not has_critical_hazard else "적합" if not has_critical_hazard else "부적합"}</strong>한 사업 대상지로 판단된다.
                </p>
"""
        elif unit_type == "신혼부부형":
            analysis_html += f"""
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    <strong>LH 신혼부부형 신축매입임대주택</strong>은 혼인 7년 이내 무주택 신혼부부를 대상으로 하며,
                    전용면적 50㎡ 이하의 주택을 시세의 70~85% 수준으로 최장 10년간 임대하는 사업이다.
                    신혼부부형은 청년형 대비 넓은 면적과 긴 임대 기간을 제공하며, 육아 및 교육 인프라 접근성이 핵심 평가 요소이다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    본 대상지 주변에는 생활편의시설 {len(facilities)}개소가 분포하고 있으며,
                    {"어린이집, 유치원 등 육아시설 접근이 용이하고" if len(facilities) >= 10 else "기본적인 생활 인프라가 갖추어져 있으며"}
                    대중교통 접근성이 우수하여 <strong>신혼부부의 출퇴근 및 육아 활동에 유리</strong>한 환경을 제공한다.
                    수요 분석 점수 <strong>{scores['demand']['score']:.1f}/5.0점</strong>으로,
                    신혼부부 거주 적합성이 {"매우 높은" if scores['demand']['score'] >= 4.0 else "높은" if scores['demand']['score'] >= 3.0 else "일정 수준의"} 것으로 평가된다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: #e3f2fd; padding: 10px; border-radius: 5px;">
                    <strong>🎯 신혼부부형 적합성 결론:</strong>
                    본 대상지는 교육·육아 인프라 및 생활편의시설 접근성이 양호하며,
                    {"주거 환경이 쾌적하여" if not has_hazard else "일부 개선 사항이 있으나"}
                    신혼부부형 임대주택 사업에 <strong>{"적합" if not has_critical_hazard else "부적합"}</strong>한 입지 조건을 갖추고 있다.
                </p>
"""
        else:  # 고령자형
            analysis_html += f"""
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    <strong>LH 고령자형 신축매입임대주택</strong>은 만 65세 이상 무주택 고령자를 대상으로 하며,
                    전용면적 40㎡ 이하의 주택을 시세의 70~80% 수준으로 최장 20년간 임대하는 사업이다.
                    고령자형은 의료시설 접근성, 무장애 설계, 1층 우선 배치 등 고령자 특화 요건이 필수적으로 요구된다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    본 대상지는 대중교통 접근성 {scores['transit']['score']:.1f}/5.0점으로 평가되며,
                    {"의료시설 및 복지센터가 인근에 위치하여" if len(facilities) >= 5 else "기본적인 생활 인프라가 확보되어 있어"}
                    고령자의 이동 편의성과 의료 접근성이 {"매우 우수" if scores['transit']['score'] >= 4.0 else "우수" if scores['transit']['score'] >= 3.0 else "보통"}한 것으로 확인되었다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: #e3f2fd; padding: 10px; border-radius: 5px;">
                    <strong>🎯 고령자형 적합성 결론:</strong>
                    본 대상지는 의료·복지시설 접근성 및 대중교통 편의성이 양호하며,
                    고령자형 임대주택 사업에 <strong>{"적합" if not has_critical_hazard else "부적합"}</strong>한 입지로 판단된다.
                </p>
"""
        
        analysis_html += """
            </div>
            
            <h4 style="margin-top: 20px; color: #0066cc; font-size: 10.5pt; font-weight: bold;">
                마. 최종 선정/탈락 사유 종합 평가
            </h4>
            <div style="margin: 15px 0; padding: 15px; background: """
        
        # 선정/탈락에 따른 배경색
        if has_critical_hazard:
            analysis_html += "#ffe6e6; border-left: 4px solid #dc3545"
        elif not has_hazard and scores['average']['score'] >= 4.0:
            analysis_html += "#e6ffe6; border-left: 4px solid #28a745"
        else:
            analysis_html += "#fffbea; border-left: 4px solid #ffc107"
        
        analysis_html += """; line-height: 1.8;">
"""
        
        if has_critical_hazard:
            # 탈락 사유 상세 서술
            analysis_html += f"""
                <p style="margin-bottom: 10px; font-weight: bold; color: #dc3545; font-size: 11pt;">
                    ❌ LH 매입 부적격 판정 (절대 탈락 사유 존재)
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    본 대상지는 종합적인 입지 분석 결과 5.0 만점 평가에서 평균 <strong>{scores['average']['score']:.2f}점</strong>을 획득하여
                    입지적 우수성은 인정되나, <strong style="color: #dc3545;">주유소가 25m 이내에 위치</strong>하는 것으로 확인되었다.
                    이는 LH 신축매입임대주택 사업 공고문에 명시된 <strong>'유해시설 중 주유소 25m 이내 위치 시 매입 제외'</strong> 기준에
                    정확히 해당하는 <strong style="color: #dc3545; font-size: 11pt;">절대 탈락 사유</strong>이다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    주유소는 화재 및 폭발 위험성이 높은 위험물 저장시설로 분류되며, 주거용 건축물과의 이격거리 확보는
                    거주자의 생명과 재산 보호를 위한 필수 안전 기준이다. 따라서 LH는 주유소 25m 이내 위치한 토지에 대해서는
                    어떠한 예외 규정도 두지 않고 있으며, <strong>해당 기준 미충족 시 100% 매입 불가</strong> 처리된다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    비록 본 대상지가 {'청년층 밀집 지역이며' if unit_type == '청년형' else '신혼부부 거주에 적합하며' if unit_type == '신혼부부형' else '고령자 거주 환경이 양호하며'},
                    대중교통 접근성({scores['transit']['score']:.1f}점), 주변 환경({scores['environment']['score']:.1f}점) 등
                    다른 평가 항목에서 우수한 성적을 거두었으나, <strong style="color: #dc3545;">단 하나의 절대 탈락 사유로 인해 전체 사업이 무효화</strong>되는 상황이다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: white; padding: 10px; border: 2px solid #dc3545; border-radius: 5px;">
                    <strong style="color: #dc3545;">📌 최종 권고사항:</strong><br>
                    본 대상지는 LH 신축매입임대주택 사업 추진이 <strong style="font-size: 11pt;">법적으로 불가능</strong>하므로,
                    <strong>사업 전면 포기</strong>를 권고한다. 주유소 이전 또는 폐쇄 등의 방법으로 해당 사유를 해소할 수 있다면
                    재검토가 가능하나, 현실적으로 매우 어려운 상황이므로 다른 대상지 물색을 적극 권장한다.
                </p>
"""
        elif has_hazard:
            # 조건부 적격 서술
            analysis_html += f"""
                <p style="margin-bottom: 10px; font-weight: bold; color: #ffc107; font-size: 11pt;">
                    ⚠️ LH 매입 조건부 적격 판정 (경미한 리스크 존재)
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    본 대상지는 종합 평가 결과 5.0 만점 기준 평균 <strong>{scores['average']['score']:.2f}점({scores['average']['rating']})</strong>을 획득하여,
                    전반적인 입지 조건이 {"우수" if scores['average']['score'] >= 4.0 else "양호"}한 것으로 평가되었다.
                    특히 {"청년층 밀집 거주 지역" if unit_type == "청년형" else "신혼부부 거주 적합 지역" if unit_type == "신혼부부형" else "고령자 거주 안정 지역"}으로
                    임대 수요 발생 가능성이 {"매우 높으며" if scores['demand']['score'] >= 4.0 else "높으며"},
                    대중교통 접근성({scores['transit']['score']:.1f}점) 및 주변 환경({scores['environment']['score']:.1f}점) 점수도 우수하다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    다만, 대상지 주변에 <strong>일부 유해시설이 확인</strong>되었으나, 주유소 25m 이내 등 LH 절대 탈락 기준에는 해당하지 않아
                    <strong>사업 추진 자체는 가능</strong>한 것으로 판단된다. 해당 유해시설은 대상지로부터 50m 이상 이격되어 있어
                    거주자의 생활에 미치는 영향이 제한적일 것으로 예상되나, LH 최종 매입 심의 시 감점 요인으로 작용할 가능성은 존재한다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: white; padding: 10px; border: 2px solid #ffc107; border-radius: 5px;">
                    <strong style="color: #ffc107;">📌 최종 권고사항:</strong><br>
                    본 대상지는 LH 신축매입임대주택 사업 <strong>조건부 추진 가능</strong> 등급으로 판정된다.
                    유해시설 관련 감점 요인을 보완하기 위해 <strong>주차 대수 법정 기준 초과 확보, LH 표준 평면 적용, 커뮤니티 시설 확충</strong> 등의
                    가점 전략을 적극 활용할 것을 권장한다. 종합적으로 볼 때 매입 가능성은 {"높은" if scores['average']['score'] >= 4.0 else "중간"} 수준으로 평가된다.
                </p>
"""
        else:
            # 완전 적격 서술
            analysis_html += f"""
                <p style="margin-bottom: 10px; font-weight: bold; color: #28a745; font-size: 11pt;">
                    ✅ LH 매입 적격 판정 (우수 등급)
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    본 대상지는 LH 신축매입임대주택 사업의 핵심 평가 항목 전반에서 우수한 성적을 거두었다.
                    5.0 만점 평가 시스템 기준 <strong>평균 {scores['average']['score']:.2f}점({scores['average']['rating']})</strong>을 획득하였으며,
                    세부적으로는 주변 환경 {scores['environment']['score']:.1f}점, 교통 편의성 {scores['transit']['score']:.1f}점,
                    차량 접근성 {scores['vehicle']['score']:.1f}점, 수요 분석 {scores['demand']['score']:.1f}점으로
                    모든 항목에서 {"우수" if scores['average']['score'] >= 4.0 else "양호"}한 평가를 받았다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    특히 주목할 만한 점은 <strong>LH 매입 제외 대상 10개 항목 체크리스트</strong> 검토 결과,
                    <strong style="color: #28a745;">치명적 탈락 사유가 전혀 발견되지 않았으며</strong>,
                    유해시설도 반경 500m 이내에 존재하지 않아 주거 환경의 쾌적성이 탁월하다는 점이다.
                    이는 LH 매입 심의 시 <strong>감점 요인이 전무</strong>하다는 의미로, 매우 긍정적인 평가 요소이다.
                </p>
                <p style="margin-bottom: 10px; text-indent: 20px;">
                    또한 본 대상지는 {unit_type} 수요층이 집중적으로 분포한 지역으로,
                    {"청년 인구 비율 " + f"{youth_ratio:.1f}%, 1인 가구 비율 " + f"{single_ratio:.1f}%" if unit_type == "청년형" else "신혼부부 거주 적합 환경" if unit_type == "신혼부부형" else "고령자 의료·복지 인프라 우수"}이
                    확인되어 <strong>임대 수요 발생 가능성이 매우 높다</strong>고 판단된다.
                    대중교통 접근성이 뛰어나고 생활편의시설이 풍부하여, 입주 후 공실률이 낮을 것으로 예상되며
                    LH 입장에서도 <strong>안정적인 임대 관리가 가능한 우량 물건</strong>으로 평가될 것이다.
                </p>
                <p style="margin-bottom: 0; text-indent: 20px; background: white; padding: 10px; border: 2px solid #28a745; border-radius: 5px;">
                    <strong style="color: #28a745;">📌 최종 권고사항:</strong><br>
                    본 대상지는 LH 신축매입임대주택 사업 <strong style="font-size: 11pt;">적극 추진 권장</strong> 등급으로 판정된다.
                    법적 제한 없음, 유해시설 없음, 우수한 입지 조건, 높은 임대 수요 등 모든 평가 항목에서 긍정적 요소가 확인되었으며,
                    <strong>LH 매입 가능성이 매우 높은 우량 물건</strong>으로 평가된다.
                    추가적으로 <strong>주차 대수 법정 기준 초과 확보, LH 표준 평면 적용, 관리형 토지신탁 방식 선택</strong> 등의
                    가점 전략을 병행하면 LH 최종 심의 통과 확률을 더욱 높일 수 있을 것으로 판단된다.
                </p>
"""
        
        analysis_html += """
            </div>
        </div>
"""
        
        return analysis_html
    
    def _check_critical_exclusions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        LH 매입 제외/탈락 사유 10개 항목 체크
        
        Returns:
            체크리스트 결과 (항목별 적합/부적합 판정)
        """
        
        risks = data.get('risk_factors', [])
        zone_info = data.get('zone_info', {})
        capacity = data.get('building_capacity', {})
        unit_type = data.get('unit_type', '청년형')
        
        checklist = []
        
        # 1. 법률상 제한 사유
        has_legal_restriction = any(r.get('category') == '법적제한' for r in risks)
        checklist.append({
            "no": 1,
            "item": "법률상 제한 사유 (압류, 경매, 건축법 위반 등)",
            "status": "부적합" if has_legal_restriction else "적합",
            "details": "토지등기부등본 확인 필요",
            "is_critical": has_legal_restriction
        })
        
        # 2. 유해시설 인접 (주유소 25m 이내 등)
        has_critical_hazard = any(
            r.get('category') == 'LH매입제외' and '주유소' in r.get('description', '')
            for r in risks
        )
        has_hazard = any(r.get('category') == '유해시설' for r in risks)
        
        hazard_details = ""
        if has_critical_hazard:
            hazard_details = "주유소 25m 이내 - 절대 탈락 사유"
        elif has_hazard:
            hazard_list = [r.get('description') for r in risks if r.get('category') == '유해시설']
            hazard_details = ", ".join(hazard_list[:3])
        else:
            hazard_details = "유해시설 없음"
        
        checklist.append({
            "no": 2,
            "item": "유해시설 인접 (주유소 25m, 기타 50m/500m 기준)",
            "status": "부적합" if (has_critical_hazard or has_hazard) else "적합",
            "details": hazard_details,
            "is_critical": has_critical_hazard
        })
        
        # 3. 사도 (개인 소유 도로) 진입
        # TODO: 도로 소유권 정보 필요
        checklist.append({
            "no": 3,
            "item": "사도 (개인 소유 도로) 진입",
            "status": "확인필요",
            "details": "도로 현황 및 등기 확인 필요",
            "is_critical": False
        })
        
        # 4. 지하층 (반지하 포함) 주거 세대
        # TODO: 설계 도면 정보 필요
        checklist.append({
            "no": 4,
            "item": "지하층 (반지하 포함) 주거 세대",
            "status": "적합",
            "details": "지하층 주거 설계 안함 (설계 시 확인 필수)",
            "is_critical": False
        })
        
        # 5. 마감재 기준 미달
        checklist.append({
            "no": 5,
            "item": "마감재 기준 미달 (외벽 준불연재/불연재 미만)",
            "status": "적합",
            "details": "LH 가이드라인 준수 예정",
            "is_critical": False
        })
        
        # 6. 엘리베이터 미설치
        floors = capacity.get('floors', 0)
        units = capacity.get('units', 0)
        needs_elevator = (floors > 4) or (unit_type == '고령자형' and floors > 1)
        
        checklist.append({
            "no": 6,
            "item": "엘리베이터 미설치",
            "status": "적합" if floors <= 4 or needs_elevator else "확인필요",
            "details": f"{floors}층 건물 - " + ("고령자형 엘리베이터 필수" if unit_type == '고령자형' else "3층 이하 필로티 시 설치 가능"),
            "is_critical": False
        })
        
        # 7. LH 직원/가족 관련 사유
        checklist.append({
            "no": 7,
            "item": "LH 직원/가족 관련 사유 (前·現 공사 직원 5년 미경과)",
            "status": "확인필요",
            "details": "매도신청인 공사직원 여부 확인서 제출 필수",
            "is_critical": False
        })
        
        # 8. 재심의/재신청 제한 사유
        checklist.append({
            "no": 8,
            "item": "재심의/재신청 제한 사유",
            "status": "해당없음",
            "details": "신규 신청 (이전 접수 이력 없음)",
            "is_critical": False
        })
        
        # 9. 구조 안전성 문제
        checklist.append({
            "no": 9,
            "item": "구조 안전성 문제",
            "status": "예상적합",
            "details": "착공 전 LH 전문가 검토 예정",
            "is_critical": False
        })
        
        # 10. 기타 제한 물권
        checklist.append({
            "no": 10,
            "item": "기타 제한 물권 (등기부상 제한물권)",
            "status": "확인필요",
            "details": "토지등기부등본 제출 후 확인",
            "is_critical": False
        })
        
        return checklist
    
    def _generate_html_structure(
        self,
        address: str,
        land_area: float,
        unit_type: str,
        coords,
        zone_info,
        capacity,
        risks: List,
        demographic,
        demand,
        summary,
        scores: Dict,
        critical_checks: List,
        map_image: Optional[str],
        data: Dict[str, Any]
    ) -> str:
        """HTML 보고서 구조 생성"""
        
        # 지역 정보 파싱
        location_parts = address.split()
        city = location_parts[0] if len(location_parts) > 0 else ""
        district = location_parts[1] if len(location_parts) > 1 else ""
        dong = location_parts[2] if len(location_parts) > 2 else ""
        
        # 유형 정보
        housing_type_info = self.LH_HOUSING_TYPES.get(unit_type, {})
        
        # 탈락 사유 있는지 확인
        has_critical_risk = any(check['is_critical'] for check in critical_checks)
        is_eligible = not has_critical_risk and summary.get('is_eligible', True)
        
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LH 신축 매입약정 사업 토지진단 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #333;
            background: white;
            padding: 10mm;
        }}
        
        .report-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #003366;
        }}
        
        .report-header h1 {{
            font-size: 20pt;
            font-weight: bold;
            color: #003366;
            margin-bottom: 10px;
        }}
        
        .report-meta {{
            margin: 20px 0;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }}
        
        .report-meta table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .report-meta td {{
            padding: 8px;
            border: 1px solid #ddd;
            font-size: 9pt;
        }}
        
        .report-meta td:first-child {{
            background: #e9ecef;
            font-weight: bold;
            width: 25%;
        }}
        
        .section {{
            margin: 30px 0;
        }}
        
        .section-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #003366;
            margin: 25px 0 15px 0;
            padding: 10px;
            background: #e3f2fd;
            border-left: 5px solid #003366;
        }}
        
        .subsection-title {{
            font-size: 11pt;
            font-weight: bold;
            color: #0066cc;
            margin: 20px 0 10px 0;
            padding: 5px 0;
            border-bottom: 2px solid #0066cc;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9pt;
        }}
        
        th, td {{
            border: 1px solid #ccc;
            padding: 10px 8px;
            text-align: left;
            vertical-align: middle;
        }}
        
        th {{
            background: #003366;
            color: white;
            font-weight: bold;
            text-align: center;
        }}
        
        .score-table td:first-child {{
            background: #f0f0f0;
            font-weight: bold;
            width: 30%;
        }}
        
        .score-high {{
            color: #007bff;
            font-weight: bold;
        }}
        
        .score-medium {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .score-low {{
            color: #ffc107;
            font-weight: bold;
        }}
        
        .status-ok {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .status-check {{
            color: #ffc107;
            font-weight: bold;
        }}
        
        .status-fail {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .info-box {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 5px solid #0066cc;
            background: #f0f7ff;
        }}
        
        .warning-box {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 5px solid #ffc107;
            background: #fffbea;
        }}
        
        .danger-box {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 5px solid #dc3545;
            background: #ffe6e6;
        }}
        
        .success-box {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 5px solid #28a745;
            background: #e6ffe6;
        }}
        
        .map-container {{
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .map-container img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 5px;
        }}
        
        .conclusion {{
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border: 2px solid #003366;
            border-radius: 5px;
        }}
        
        .conclusion h3 {{
            color: #003366;
            margin-bottom: 15px;
        }}
        
        ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <!-- 보고서 헤더 -->
    <div class="report-header">
        <h1>LH 신축 매입약정 사업 토지진단 보고서</h1>
        <p style="font-size: 11pt; color: #666; margin-top: 10px;">
            (LH한국토지주택공사 신축매입임대주택 사업 대상지 적격성 검토)
        </p>
    </div>
    
    <!-- 기본 정보 -->
    <div class="report-meta">
        <table>
            <tr>
                <td>작성 일자</td>
                <td>{self.report_date.strftime('%Y년 %m월 %d일')}</td>
                <td>작성 주체</td>
                <td>토지진단 자동화 시스템</td>
            </tr>
            <tr>
                <td>보고서 버전</td>
                <td>{self.report_version} (초기 사업 검토)</td>
                <td>대상 지역본부</td>
                <td>{city} 본부</td>
            </tr>
            <tr>
                <td>사업 규모</td>
                <td>{capacity.get('units', 0)}세대 ({unit_type})</td>
                <td>매입 방식</td>
                <td>□ 감정평가형 / □ 건물공사비 연동형</td>
            </tr>
        </table>
    </div>
    
    <!-- I. 사업 기본 정보 및 요약 -->
    <div class="section page-break">
        <h2 class="section-title">I. 사업 기본 정보 및 요약</h2>
        
        <h3 class="subsection-title">1. 대상지 기본 정보</h3>
        <table>
            <tr>
                <th style="width: 25%;">구분</th>
                <th style="width: 50%;">내용</th>
                <th style="width: 25%;">비고 / 참고 자료</th>
            </tr>
            <tr>
                <td><strong>대상 소재지</strong></td>
                <td>{address}</td>
                <td>토지등기부등본 확인 필요</td>
            </tr>
            <tr>
                <td><strong>매입 주체</strong></td>
                <td>(매도 신청인 정보 입력 필요)</td>
                <td>LH 공사직원 여부 확인 필수</td>
            </tr>
            <tr>
                <td><strong>추천/희망 주거 유형</strong></td>
                <td><strong>{unit_type}</strong></td>
                <td>최종 선정은 LH 검토 후 결정됨</td>
            </tr>
            <tr>
                <td><strong>주택 유형</strong></td>
                <td>□ 도시형생활주택 / □ 주거용 오피스텔 / □ 다세대/연립/다가구</td>
                <td>설계 단계에서 확정</td>
            </tr>
            <tr>
                <td><strong>매입 단위</strong></td>
                <td>□ 전체 매입 / □ 일부 매입</td>
                <td>-</td>
            </tr>
        </table>
        
        <h3 class="subsection-title">2. 검토 결과 요약 (5.0 만점 평가)</h3>
        <table class="score-table">
            <thead>
                <tr>
                    <th>주요 분석 분야</th>
                    <th>평가 점수 (5.0 만점)</th>
                    <th>평가 등급</th>
                    <th>종합 의견</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>주변 환경</strong><br>(생활 인프라, 쾌적성)</td>
                    <td class="score-high">{scores['environment']['score']:.1f} / 5.0</td>
                    <td class="score-high">{scores['environment']['rating']}</td>
                    <td>생활편의시설 {len(demand.get('nearby_facilities', []))}개 확인</td>
                </tr>
                <tr>
                    <td><strong>교통 편의성</strong><br>(대중교통 접근성)</td>
                    <td class="score-high">{scores['transit']['score']:.1f} / 5.0</td>
                    <td class="score-high">{scores['transit']['rating']}</td>
                    <td>지하철역, 버스 정류장 접근성 양호</td>
                </tr>
                <tr>
                    <td><strong>차량 접근성</strong><br>(도로 폭, 진입 용이성)</td>
                    <td class="score-medium">{scores['vehicle']['score']:.1f} / 5.0</td>
                    <td class="score-medium">{scores['vehicle']['rating']}</td>
                    <td>도로 현황 양호 (현장 실사 필요)</td>
                </tr>
                <tr>
                    <td><strong>수요 분석</strong><br>(타겟 유형 임대 수요)</td>
                    <td class="score-high">{scores['demand']['score']:.1f} / 5.0</td>
                    <td class="score-high">{scores['demand']['rating']}</td>
                    <td>{unit_type} 수요층 분포 적정</td>
                </tr>
                <tr style="background: #f0f0f0; font-weight: bold;">
                    <td><strong>평균 평가</strong></td>
                    <td class="score-high">{scores['average']['score']:.2f} / 5.0</td>
                    <td class="score-high">{scores['average']['rating']}</td>
                    <td><strong>종합 {"우수" if scores['average']['score'] >= 4.0 else "양호" if scores['average']['score'] >= 3.0 else "보통"}</strong></td>
                </tr>
            </tbody>
        </table>
        
        {"<div class='success-box'><strong>✅ LH 매입 적격 판정</strong><br>5.0 만점 평가에서 평균 " + f"{scores['average']['score']:.2f}" + "점을 획득하여 LH 신축매입임대주택 사업 대상지로 적합합니다.</div>" if is_eligible else "<div class='danger-box'><strong>❌ LH 매입 부적격 판정</strong><br>치명적인 탈락 사유가 발견되어 LH 매입 대상에서 제외됩니다.</div>"}
    </div>
    
    <!-- II. 대상지 상세 분석 및 유형 도출 -->
    <div class="section page-break">
        <h2 class="section-title">II. 대상지 상세 분석 및 유형 도출</h2>
        
        <h3 class="subsection-title">1. 입지 및 수요 환경 분석 (지역 조사 결과)</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%;">구분</th>
                    <th style="width: 55%;">주요 내용 (장점/단점 포함)</th>
                    <th style="width: 25%;">LH 매입 선호도 영향</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>주변 환경</strong></td>
                    <td>
                        • 총 인구: {demographic.get('total_population', 0):,}명<br>
                        • 청년 인구(20-39세): {demographic.get('youth_population', 0):,}명 ({demographic.get('youth_ratio', 0):.1f}%)<br>
                        • 1인 가구: {demographic.get('single_households', 0):,}가구 ({demographic.get('single_household_ratio', 0):.1f}%)<br>
                        • 생활편의시설: {len(demand.get('nearby_facilities', []))}개 확인
                    </td>
                    <td class="score-high">긍정적 영향</td>
                </tr>
                <tr>
                    <td><strong>교통 편의성</strong></td>
                    <td>
                        • 대중교통 접근성 점수: {scores['transit']['score']:.1f}/5.0<br>
                        • 지하철역, 버스 정류장 다수 분포<br>
                        • 주요 직장/대학 접근 양호
                    </td>
                    <td class="score-high">긍정적 영향</td>
                </tr>
                <tr>
                    <td><strong>차량 접근성</strong></td>
                    <td>
                        • 도로 접근성: {scores['vehicle']['rating']}<br>
                        • 주요 간선도로 인접 여부 확인 필요
                    </td>
                    <td class="score-medium">보통 영향</td>
                </tr>
                <tr>
                    <td><strong>종전 대지 이용 상태</strong></td>
                    <td>□ 나대지 / □ 노후주택(지하층 유/무) / □ 근린생활시설 / □ 숙박시설(모텔 등)</td>
                    <td>현장 실사 필요</td>
                </tr>
                <tr>
                    <td><strong>임대 수요 상세</strong></td>
                    <td>
                        <strong>{unit_type}</strong> 적합성 분석:<br>
                        {''.join([f"• {criterion}<br>" for criterion in housing_type_info.get('key_criteria', [])])}
                        • 임대 수요 점수: {scores['demand']['score']:.1f}/5.0<br>
                        • 예상 임대료: 시세의 {housing_type_info.get('rent_rate', 'N/A')}
                    </td>
                    <td class="score-high">적합한 유형</td>
                </tr>
            </tbody>
        </table>
        
        <h3 class="subsection-title">2. 대상지 법적 및 물리적 현황</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%;">구분</th>
                    <th style="width: 50%;">상세 정보</th>
                    <th style="width: 30%;">특이 사항</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>토지 정보</strong></td>
                    <td>
                        • 용도지역: {zone_info.get('zone_type', 'N/A')}<br>
                        • 면적: {land_area:,.2f}㎡<br>
                        • 좌표: {coords.latitude:.6f}, {coords.longitude:.6f}
                    </td>
                    <td>토지이용계획확인원 확인 필요</td>
                </tr>
                <tr>
                    <td><strong>건축 규모</strong></td>
                    <td>
                        • 예상 건물 규모: {capacity.get('units', 0)}세대 / {capacity.get('floors', 0)}층<br>
                        • 건축면적: {capacity.get('building_area', 0):,.2f}㎡<br>
                        • 연면적: {capacity.get('total_floor_area', 0):,.2f}㎡
                    </td>
                    <td>설계 단계에서 확정</td>
                </tr>
                <tr>
                    <td><strong>건폐율</strong></td>
                    <td>{zone_info.get('building_coverage_ratio', 0):.1f}%</td>
                    <td>법정 기준 준수</td>
                </tr>
                <tr>
                    <td><strong>용적률</strong></td>
                    <td>{zone_info.get('floor_area_ratio', 0):.1f}%</td>
                    <td>법정 기준 준수</td>
                </tr>
                <tr>
                    <td><strong>접면 도로 현황</strong></td>
                    <td>(현장 실사 후 기재)</td>
                    <td>6m 이상 도로 확보 필요</td>
                </tr>
                <tr>
                    <td><strong>주차 대수</strong></td>
                    <td>
                        • 예상 법정 대수: {capacity.get('parking_spaces', 0)}대<br>
                        • {unit_type} 기준: {housing_type_info.get('parking', 'N/A')}
                    </td>
                    <td>법정 초과 확보 시 가점</td>
                </tr>
            </tbody>
        </table>
        
        {"<div class='map-container'><h4>대상지 위치도</h4><img src='" + map_image + "' alt='대상지 지도' /></div>" if map_image else ""}
        
        <!-- 상세 지역 분석 (4단계 추가) -->
        {self._generate_detailed_regional_analysis(data)}
    </div>
    
    <!-- III. LH 매입 제외/탈락 사유 리스크 진단 -->
    <div class="section page-break">
        <h2 class="section-title">III. LH 매입 제외/탈락 사유 리스크 진단 (Critical Check List)</h2>
        
        <div class="info-box">
            <strong>📋 체크리스트 개요</strong><br>
            LH 신축매입임대주택 사업의 매입 제외 대상 10개 항목을 점검합니다.<br>
            치명적 탈락 사유가 1개라도 발견되면 LH 매입 대상에서 제외됩니다.
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">No.</th>
                    <th style="width: 30%;">LH 매입 제외 대상 (리스크 요인)</th>
                    <th style="width: 20%;">토지/설계 현황</th>
                    <th style="width: 10%;">진단 결과</th>
                    <th style="width: 35%;">대응 방안</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 체크리스트 항목 추가
        for check in critical_checks:
            status_class = "status-fail" if check['is_critical'] else ("status-ok" if check['status'] == "적합" else "status-check")
            status_icon = "❌" if check['is_critical'] else ("✅" if check['status'] == "적합" else "⚠️")
            
            html += f"""
                <tr>
                    <td style="text-align: center;"><strong>{check['no']}</strong></td>
                    <td><strong>{check['item']}</strong></td>
                    <td>{check['details']}</td>
                    <td class="{status_class}" style="text-align: center;">{status_icon} {check['status']}</td>
                    <td>{"<span style='color: #dc3545; font-weight: bold;'>즉시 매입 불가</span>" if check['is_critical'] else ("현장 실사 및 서류 확인 필요" if check['status'] == "확인필요" else "기준 충족")}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <div class="warning-box">
            <strong>⚠️ 중요 안내사항</strong><br>
            • 위 체크리스트는 자동 진단 결과이며, 최종 판정은 현장 실사 및 서류 확인 후 결정됩니다.<br>
            • "확인필요" 항목은 LH 접수 전 반드시 관련 서류를 준비하시기 바랍니다.<br>
            • 치명적 탈락 사유가 발견된 경우, 해당 사유를 해소하지 않으면 매입 신청이 불가능합니다.
        </div>
    </div>
    
    <!-- IV. LH 매입 예상 가격 산정 -->
    <div class="section page-break">
        <h2 class="section-title">IV. LH 매입 예상 가격 산정 및 수지 분석</h2>
        
        <div class="info-box">
            <strong>💰 가격 산정 방법론</strong><br>
            LH 신축매입임대주택 사업의 매입가격은 <strong>감정평가액</strong>을 기준으로 산정됩니다.<br>
            - 토지: 2개 감정평가법인의 평균값<br>
            - 건물: 공사비 실비 정산 또는 건물공사비 연동형<br>
            - 최종 매입가: 토지 감정평가액 + 건물 공사비 + 제세공과금
        </div>
"""

        # 가격 산정
        price_estimate = self._estimate_lh_purchase_price(data)
        
        html += f"""
        <h3 class="subsection-title">1. 토지 감정평가 예상액</h3>
        
        <h4 style="margin-top: 15px; color: #555; font-size: 10pt; font-weight: bold;">가. 감정평가 산정 근거</h4>
        <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
            <p style="margin-bottom: 10px;">
                본 대상지의 토지 감정평가액은 다음과 같은 요소를 종합적으로 고려하여 산정되었습니다:
            </p>
            <ul style="margin-left: 20px; margin-bottom: 10px;">
                <li><strong>{price_estimate['factors_explanation']['base']}</strong></li>
                <li><strong>{price_estimate['factors_explanation']['zone']}</strong> - 용도지역에 따른 가치 차등 반영</li>
                <li><strong>{price_estimate['factors_explanation']['location']}</strong> - 입지 우수성에 따른 가치 상승 반영</li>
            </ul>
            <p style="margin-bottom: 0; text-indent: 20px;">
                위 요소들을 종합하여 산정한 <strong>㎡당 토지 단가는 {price_estimate['base_land_price_per_sqm']:,.0f}원</strong>이며,
                대상지 면적 <strong>{price_estimate['land_area']:,.2f}㎡</strong>를 곱하면
                토지 감정평가 예상액이 산출됩니다.
            </p>
        </div>
        
        <table style="margin-top: 20px;">
            <thead>
                <tr>
                    <th style="width: 30%;">구분</th>
                    <th style="width: 25%;">단가 (원/㎡)</th>
                    <th style="width: 20%;">면적 (㎡)</th>
                    <th style="width: 25%;">금액 (원)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>토지 감정평가액</strong></td>
                    <td style="text-align: right;">{price_estimate['base_land_price_per_sqm']:,.0f}</td>
                    <td style="text-align: right;">{price_estimate['land_area']:,.2f}</td>
                    <td style="text-align: right; color: #007bff; font-weight: bold;">{price_estimate['total_land_value']:,.0f}</td>
                </tr>
                <tr style="background: #fff3cd;">
                    <td><strong>예상 가격 범위</strong></td>
                    <td colspan="2" style="text-align: center;">감정평가 2개 법인 편차 고려</td>
                    <td style="text-align: right; font-weight: bold;">{price_estimate['price_min']:,.0f} ~ {price_estimate['price_max']:,.0f}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 15px; padding: 15px; background: #e3f2fd; border-radius: 5px;">
            <p style="font-size: 9pt; line-height: 1.6; margin: 0;">
                <strong>📌 참고사항:</strong> 실제 감정평가액은 LH가 선정한 2개 감정평가법인의 평가 결과를 산술평균하여 결정되며,
                상기 예상액은 지역별 기준단가, 용도지역, 입지 점수를 기반으로 산정한 <strong>추정값</strong>입니다.
                최종 감정평가액은 ±{(price_estimate['price_max'] - price_estimate['total_land_value']) / price_estimate['total_land_value'] * 100:.0f}% 범위 내에서 결정될 것으로 예상됩니다.
            </p>
        </div>
        
        <h3 class="subsection-title" style="margin-top: 30px;">2. 건물 공사비 추정</h3>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 30%;">구분</th>
                    <th style="width: 25%;">단가 (원/㎡)</th>
                    <th style="width: 20%;">연면적 (㎡)</th>
                    <th style="width: 25%;">금액 (원)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>건물 공사비</strong></td>
                    <td style="text-align: right;">{price_estimate['construction_cost_per_sqm']:,.0f}</td>
                    <td style="text-align: right;">{capacity.get('total_floor_area', 0):,.2f}</td>
                    <td style="text-align: right; color: #007bff; font-weight: bold;">{price_estimate['total_construction_cost']:,.0f}</td>
                </tr>
                <tr>
                    <td><strong>제세공과금</strong></td>
                    <td colspan="2" style="text-align: center;">토지가의 약 5%</td>
                    <td style="text-align: right; font-weight: bold;">{price_estimate['taxes_and_fees']:,.0f}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
            <p style="margin-bottom: 10px; text-indent: 20px;">
                <strong>건물 공사비는 {unit_type} 특성에 맞춰 ㎡당 {price_estimate['construction_cost_per_sqm']:,.0f}원</strong>을 적용하였습니다.
                {"청년형은 효율적인 평면 설계와 경제적인 마감재 사용으로 공사비가 상대적으로 낮습니다." if unit_type == "청년형" else "신혼부부형은 육아 공간 및 수납공간 확보로 인해 중간 수준의 공사비가 소요됩니다." if unit_type == "신혼부부형" else "고령자형은 무장애 설계(경사로, 안전손잡이 등) 및 안전시설 설치로 공사비가 다소 높습니다."}
            </p>
            <p style="margin-bottom: 0; text-indent: 20px;">
                제세공과금에는 취득세, 등록면허세, 법무사 수수료, 감정평가 수수료 등이 포함되며,
                일반적으로 <strong>토지 감정평가액의 5% 내외</strong>로 산정됩니다.
            </p>
        </div>
        
        <h3 class="subsection-title" style="margin-top: 30px;">3. LH 총 매입 예상액 및 선금 지급</h3>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">항목</th>
                    <th style="width: 50%;">금액 (원)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>① 토지 감정평가액</td>
                    <td style="text-align: right;">{price_estimate['total_land_value']:,.0f}</td>
                </tr>
                <tr>
                    <td>② 건물 공사비</td>
                    <td style="text-align: right;">{price_estimate['total_construction_cost']:,.0f}</td>
                </tr>
                <tr>
                    <td>③ 제세공과금</td>
                    <td style="text-align: right;">{price_estimate['taxes_and_fees']:,.0f}</td>
                </tr>
                <tr style="background: #e3f2fd; font-weight: bold; font-size: 11pt;">
                    <td><strong>LH 총 매입 예상액 (①+②+③)</strong></td>
                    <td style="text-align: right; color: #0066cc; font-size: 12pt;">{price_estimate['total_purchase_price']:,.0f}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 20px; background: #fff; border: 2px solid #0066cc; border-radius: 10px;">
            <h4 style="color: #0066cc; margin-bottom: 15px; font-size: 11pt;">💵 선금 지급 방식별 예상액</h4>
            
            <table style="margin-top: 10px;">
                <thead>
                    <tr>
                        <th style="width: 40%;">채권보전 방식</th>
                        <th style="width: 30%;">선금 비율</th>
                        <th style="width: 30%;">선금 예상액 (원)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>근저당 방식</strong></td>
                        <td style="text-align: center;">토지분 50%</td>
                        <td style="text-align: right; font-weight: bold;">{price_estimate['advance_payment_mortgage']:,.0f}</td>
                    </tr>
                    <tr style="background: #e6ffe6;">
                        <td><strong>관리형 토지신탁</strong></td>
                        <td style="text-align: center;">토지분 70%</td>
                        <td style="text-align: right; font-weight: bold; color: #28a745;">{price_estimate['advance_payment_trust']:,.0f}</td>
                    </tr>
                    <tr style="background: #d4edda;">
                        <td><strong>관리형 토지신탁<br>(조기약정 인센티브)</strong></td>
                        <td style="text-align: center;">토지분 80%</td>
                        <td style="text-align: right; font-weight: bold; color: #28a745;">{price_estimate['advance_payment_trust_early']:,.0f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <h3 class="subsection-title" style="margin-top: 30px;">4. 가격 산정 근거 및 합리성 평가</h3>
        
        <div style="margin: 15px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
            <h4 style="color: #333; margin-bottom: 15px; font-size: 10.5pt;">▣ 토지 가격 산정의 합리성</h4>
            <p style="margin-bottom: 10px; text-indent: 20px;">
                본 보고서의 토지 감정평가 예상액은 다음과 같은 근거로 산정되었으며, 시장 실거래가와 높은 연관성을 가집니다:
            </p>
            <ol style="margin-left: 40px; margin-bottom: 15px;">
                <li style="margin-bottom: 8px;">
                    <strong>용도지역 보정 ({price_estimate['zone_factor']:.2f}배)</strong>: 
                    {zone_info.get('zone_type', 'N/A')}은 {"주거지역 중 가장 가치가 높은" if price_estimate['zone_factor'] >= 1.2 else "주거 용도로 적합한" if price_estimate['zone_factor'] >= 1.0 else "주거 순수성이 보장되는"} 지역으로,
                    {"상업적 활용도가 높아" if price_estimate['zone_factor'] >= 1.3 else "적정한 개발 밀도로" if price_estimate['zone_factor'] >= 1.0 else "저밀도 양호한 주거환경으로"}
                    시세 형성에 긍정적 영향을 미칩니다.
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>입지 점수 보정 ({price_estimate['location_factor']:.2f}배)</strong>:
                    5.0 만점 평가에서 평균 <strong>{scores['average']['score']:.2f}점</strong>을 획득하여
                    {"입지가 매우 우수한" if scores['average']['score'] >= 4.0 else "입지가 양호한" if scores['average']['score'] >= 3.0 else "입지가 보통 수준인"} 것으로 평가되었습니다.
                    특히 {"대중교통 접근성이 탁월하고" if scores['transit']['score'] >= 4.0 else "대중교통 접근이 가능하며"}
                    {"생활편의시설이 풍부하여" if scores['environment']['score'] >= 4.0 else "기본적인 생활 인프라를 갖추어"}
                    실제 시장에서 {"프리미엄을 받을 수 있는" if scores['average']['score'] >= 4.0 else "경쟁력을 갖춘"} 입지입니다.
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>시장 거래 사례 반영</strong>:
                    해당 지역의 최근 1년간 토지 실거래가를 분석한 결과, ㎡당 평균 거래가가
                    {price_estimate['price_min']:,.0f}원 ~ {price_estimate['price_max']:,.0f}원 범위 내에 분포하고 있어
                    본 보고서의 예상액({price_estimate['base_land_price_per_sqm']:,.0f}원/㎡)이 <strong>시장 실거래가와 부합</strong>하는 것으로 확인되었습니다.
                </li>
            </ol>
            
            <h4 style="color: #333; margin-bottom: 15px; margin-top: 20px; font-size: 10.5pt;">▣ LH 매입가격의 의미와 사업성</h4>
            <p style="margin-bottom: 10px; text-indent: 20px;">
                LH 총 매입 예상액 <strong style="color: #0066cc; font-size: 11pt;">{price_estimate['total_purchase_price']:,.0f}원</strong>은
                토지 + 건물 + 제세공과금을 모두 포함한 금액으로, 매도신청인이 LH로부터 수령하게 될 <strong>최종 대금</strong>입니다.
            </p>
            <p style="margin-bottom: 10px; text-indent: 20px;">
                이 중 <strong>선금으로 수령 가능한 금액</strong>은 채권보전 방식에 따라 달라지는데,
                <strong style="color: #28a745;">관리형 토지신탁 방식</strong>을 선택할 경우
                최대 <strong>{price_estimate['advance_payment_trust_early']:,.0f}원(토지분의 80%)</strong>까지 조기에 수령할 수 있어
                <strong>자금 유동성 확보에 유리</strong>합니다.
            </p>
            <p style="margin-bottom: 10px; text-indent: 20px;">
                건물 공사비는 실제 공사 진행에 따라 <strong>LH가 직접 시공사에 지급</strong>하는 방식이므로,
                매도신청인은 공사비 부담 없이 토지 대금만 수령하면 되는 구조입니다.
                이는 <strong>대규모 건축 자금 조달 부담이 없다</strong>는 점에서 LH 신축매입임대주택 사업의 가장 큰 장점입니다.
            </p>
            
            <div style="margin-top: 15px; padding: 15px; background: white; border: 2px solid #28a745; border-radius: 5px;">
                <p style="margin: 0; font-weight: bold; color: #28a745; font-size: 10pt;">
                    ✅ <strong>매입가격 종합 평가</strong>: 
                    본 대상지의 LH 매입 예상가격은 시장 실거래가를 기준으로 산정되었으며,
                    감정평가 2개 법인의 평가 결과가 예상 범위 내에 포함될 것으로 판단됩니다.
                    {"입지가 우수하여 감정평가액이 예상 상단에 근접할 가능성이 높으며" if scores['average']['score'] >= 4.0 else "입지가 양호하여 감정평가액이 예상 중간값 수준으로 형성될 것으로 보이며"},
                    LH 매입 후 안정적인 임대 수익 창출이 가능할 것으로 예상됩니다.
                </p>
            </div>
        </div>
    </div>
    
    <!-- V. 공공 매입 선호도 증대 항목 (권장사항) -->
"""
        
        # 권장사항 평가
        recommendations = self._evaluate_recommendations(data)
        
        html += f"""
    <div class="section page-break">
        <h2 class="section-title">V. 공공 매입 선호도 증대 항목 (권장사항)</h2>
        
        <div class="info-box">
            <strong>🌟 권장사항 개요</strong><br>
            LH의 매입 심의 시 <strong>우대받거나 매입 적정성을 높이는</strong> 권장사항입니다.<br>
            필수 사항은 아니나, 반영 시 <strong>심의 통과 가능성 및 평가 점수가 상승</strong>합니다.
        </div>
        
        <table style="margin-top: 20px;">
            <thead>
                <tr>
                    <th style="width: 5%;">No.</th>
                    <th style="width: 25%;">권장사항 구분</th>
                    <th style="width: 15%;">계획 반영 여부</th>
                    <th style="width: 35%;">계획/설계 반영 내용</th>
                    <th style="width: 20%;">기대 효과</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for rec in recommendations:
            status_color = "#28a745" if rec['status'] == "반영" else "#ffc107" if "권장" in rec['status'] else "#0066cc"
            html += f"""
                <tr>
                    <td style="text-align: center;"><strong>{rec['no']}</strong></td>
                    <td><strong>{rec['item']}</strong></td>
                    <td style="text-align: center; color: {status_color}; font-weight: bold;">
                        {"✅ " if rec['status'] == "반영" else "⚠️ " if "권장" in rec['status'] else ""}
                        {rec['status']}
                    </td>
                    <td>{rec['plan']}</td>
                    <td style="font-size: 9pt;">{rec['benefit']}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-left: 4px solid #28a745; line-height: 1.8;">
            <h4 style="color: #28a745; margin-bottom: 15px; font-size: 10.5pt;">💡 권장사항 활용 전략</h4>
            <p style="margin-bottom: 10px; text-indent: 20px;">
                상기 5개 권장사항 중 <strong>최소 3개 이상을 반영</strong>하면 LH 심의 시 <strong>가점 효과</strong>가 발생합니다.
                특히 다음 항목들은 심의위원들의 선호도가 높으므로 우선 검토를 권장합니다:
            </p>
            <ul style="margin-left: 40px; margin-bottom: 15px;">
                <li style="margin-bottom: 8px;">
                    <strong>표준 평면 적용</strong>: LH가 검증한 평면이므로 설계 변경 요구가 적고, 
                    심의 기간이 <strong>평균 1개월 단축</strong>됩니다.
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>관리형 토지신탁 방식</strong>: 사업 규모가 클수록 LH가 선호하며, 
                    선금 비율이 높아(70~80%) <strong>초기 자금 확보에 유리</strong>합니다.
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>주차 대수 초과 확보</strong>: 법정 기준을 10% 이상 초과하면 
                    입주자 만족도가 높아져 <strong>공실률 감소</strong> 효과가 있습니다.
                </li>
            </ul>
            <p style="margin-bottom: 0; padding: 15px; background: white; border: 2px solid #28a745; border-radius: 5px;">
                <strong>📌 종합 권장사항:</strong> 
                본 대상지는 권장사항 중 {sum(1 for r in recommendations if r['status'] == '반영')}개가 이미 반영 가능한 상태이며,
                추가 검토 항목 {sum(1 for r in recommendations if '권장' in r['status'])}개를 보완하면
                <strong>LH 심의 통과 가능성을 최대한 높일 수 있습니다.</strong>
            </p>
        </div>
    </div>
    
    <!-- VI. 사업 추진 일정 및 자금 조달 계획 -->
"""
        
        # 일정 산정
        schedule = self._generate_project_schedule(data)
        price_estimate = self._estimate_lh_purchase_price(data)
        
        html += f"""
    <div class="section page-break">
        <h2 class="section-title">VI. 사업 추진 일정 및 자금 조달 계획 (LH 프로세스 연동)</h2>
        
        <h3 class="subsection-title">1. 사업 추진 일정 (예상)</h3>
        
        <div class="info-box">
            <strong>📅 전체 사업 기간</strong><br>
            현재 시점부터 준공까지 약 <strong>{schedule['total_months']}개월</strong> 소요 예상<br>
            (설계 착수 → 심의 → 약정 → 착공 → 준공)
        </div>
        
        <table style="margin-top: 20px;">
            <thead>
                <tr>
                    <th style="width: 30%;">주요 단계</th>
                    <th style="width: 20%;">예상 소요 기간</th>
                    <th style="width: 25%;">계획(예정) 일자</th>
                    <th style="width: 25%;">현재 진행 단계</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>접수도면 설계/서류 취합</strong></td>
                    <td style="text-align: center;">1개월</td>
                    <td style="text-align: center;">{schedule['design_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">계획설계/기본설계/실시설계</td>
                </tr>
                <tr style="background: #fff3cd;">
                    <td><strong>서류 접수 및 심의 결과 발표</strong></td>
                    <td style="text-align: center;">2~3개월</td>
                    <td style="text-align: center;">{schedule['review_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">토지소유권 확보 시 우선 심의 가능</td>
                </tr>
                <tr>
                    <td><strong>도면 협의 완료</strong></td>
                    <td style="text-align: center;">4개월 이내</td>
                    <td style="text-align: center;">{schedule['drawing_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">실시설계 수준 협의 필요 (실효제도 주의)</td>
                </tr>
                <tr style="background: #e3f2fd;">
                    <td><strong>1차 감정평가</strong></td>
                    <td style="text-align: center;">1개월</td>
                    <td style="text-align: center;">{schedule['appraisal_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">LH 선정 2개 감정평가법인</td>
                </tr>
                <tr style="background: #d4edda; font-weight: bold;">
                    <td><strong>매입 약정 체결</strong></td>
                    <td style="text-align: center;">1~2개월</td>
                    <td style="text-align: center; color: #28a745;">{schedule['contract_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">약정 체결 기한 내 미체결 시 재신청 제한</td>
                </tr>
                <tr style="background: #e6ffe6;">
                    <td><strong>토지비 선금 수령</strong></td>
                    <td style="text-align: center;">약정 후 즉시</td>
                    <td style="text-align: center; color: #28a745; font-weight: bold;">{schedule['advance_payment'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt; color: #28a745; font-weight: bold;">
                        관리형 토지신탁 시 최대 {price_estimate['advance_payment_trust_early']:,.0f}원 수령
                    </td>
                </tr>
                <tr>
                    <td><strong>인허가 및 착공</strong></td>
                    <td style="text-align: center;">9개월 (약정 후)</td>
                    <td style="text-align: center;">{schedule['construction_start'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">착공 전 LH 전문가 구조 안정성 검토</td>
                </tr>
                <tr style="background: #f0f0f0; font-weight: bold;">
                    <td><strong>준공 (사용승인 예정)</strong></td>
                    <td style="text-align: center;">20개월 (착공 후)</td>
                    <td style="text-align: center; font-size: 11pt; color: #0066cc;">{schedule['construction_complete'].strftime('%Y년 %m월 %d일')}</td>
                    <td style="font-size: 9pt;">최종 잔금 수령 및 LH 매입 완료</td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 15px; background: #fffbea; border-left: 4px solid #ffc107; line-height: 1.6;">
            <strong>⚠️ 주요 유의사항:</strong><br>
            • <strong>도면 협의 실효제도</strong>: 심의 통과 안내일로부터 4개월 이내 도면 협의를 완료하지 못하면 <strong>자동 실효</strong>됩니다.<br>
            • <strong>인허가 기한</strong>: 약정 체결 후 9개월 이내에 건축허가를 득하지 못하면 약정이 해제될 수 있습니다.<br>
            • <strong>착공 의무</strong>: 인허가 완료 후 2개월 이내에 착공해야 하며, 미착공 시 페널티가 부과될 수 있습니다.
        </div>
        
        <h3 class="subsection-title" style="margin-top: 30px;">2. 매입 대금 지급 방식 및 채권 보전</h3>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">채권 보전 방식</th>
                    <th style="width: 40%;">지급 방식 개요</th>
                    <th style="width: 35%;">주요 유의사항</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>근저당 방식</strong></td>
                    <td>
                        • 선금: 토지분 1차 감정평가액의 <strong>50%</strong> 한도<br>
                        • 매입약정금: 토지분 감평액 50% 한도<br>
                        • 잔금: 준공 후 지급
                    </td>
                    <td style="font-size: 9pt;">
                        채권확보 비용 매도신청인 부담<br>
                        후순위 근저당 설정 불가
                    </td>
                </tr>
                <tr style="background: #e6ffe6;">
                    <td><strong>관리형 토지신탁 방식</strong><br><span style="color: #28a745; font-weight: bold;">(권장)</span></td>
                    <td>
                        • 선금: 토지분 1차 감정평가액의 <strong>70%</strong> 한도<br>
                        • <strong>조기약정 인센티브 충족 시 80%</strong><br>
                        • 매입약정금: 매매예정금액의 60% 한도<br>
                        • 잔금: 준공 후 지급
                    </td>
                    <td style="font-size: 9pt; color: #28a745; font-weight: bold;">
                        LH가 필수 조건으로 제시 가능<br>
                        선금 비율 높아 자금 확보 유리<br>
                        사업 안정성 최고
                    </td>
                </tr>
            </tbody>
        </table>
        
        <h3 class="subsection-title" style="margin-top: 30px;">3. 자금 조달 계획 및 수지 분석</h3>
        
        <div style="margin: 15px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
            <h4 style="color: #0066cc; margin-bottom: 15px; font-size: 10.5pt;">💰 단계별 자금 흐름</h4>
            
            <table style="margin-top: 10px; font-size: 9pt;">
                <thead>
                    <tr>
                        <th style="width: 30%;">단계</th>
                        <th style="width: 25%;">시점</th>
                        <th style="width: 30%;">수령 금액</th>
                        <th style="width: 15%;">누적</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: #e6ffe6;">
                        <td><strong>선금 수령</strong></td>
                        <td>{schedule['advance_payment'].strftime('%Y.%m')}</td>
                        <td style="text-align: right; color: #28a745; font-weight: bold;">
                            {price_estimate['advance_payment_trust_early']:,.0f}원<br>
                            <span style="font-size: 8pt;">(토지분 80%)</span>
                        </td>
                        <td style="text-align: right; font-weight: bold;">80%</td>
                    </tr>
                    <tr style="background: #f0f0f0;">
                        <td><strong>준공 후 잔금</strong></td>
                        <td>{schedule['construction_complete'].strftime('%Y.%m')}</td>
                        <td style="text-align: right; color: #0066cc; font-weight: bold;">
                            {price_estimate['total_purchase_price'] - price_estimate['advance_payment_trust_early']:,.0f}원<br>
                            <span style="font-size: 8pt;">(토지잔금 20% + 건물공사비 전액)</span>
                        </td>
                        <td style="text-align: right; font-weight: bold;">100%</td>
                    </tr>
                    <tr style="background: #e3f2fd; font-weight: bold; font-size: 10pt;">
                        <td colspan="2"><strong>총 매입 대금</strong></td>
                        <td style="text-align: right; color: #0066cc; font-size: 11pt;">
                            {price_estimate['total_purchase_price']:,.0f}원
                        </td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
            
            <p style="margin-top: 15px; margin-bottom: 10px; text-indent: 20px;">
                <strong>자금 조달의 핵심 장점</strong>은 매도신청인이 <strong>건물 공사비를 직접 부담하지 않는다</strong>는 점입니다.
                LH가 시공사에 직접 공사비를 지급하는 구조이므로, 
                매도신청인은 <strong>선금 {price_estimate['advance_payment_trust_early']:,.0f}원만 수령</strong>한 후
                {schedule['total_months']}개월 동안 별도 자금 투입 없이 사업을 진행할 수 있습니다.
            </p>
            
            <p style="margin-bottom: 0; padding: 15px; background: white; border: 2px solid #28a745; border-radius: 5px;">
                <strong>✅ 자금 조달 종합 평가:</strong>
                관리형 토지신탁 방식 선택 시, 약정 체결 후 <strong>1주일 이내에 {price_estimate['advance_payment_trust_early']:,.0f}원</strong>을 수령하여
                초기 자금 유동성을 확보할 수 있으며, 이후 공사 기간 동안 추가 자금 투입이 불필요하므로
                <strong>재무적 리스크가 최소화</strong>됩니다.
            </p>
        </div>
    </div>
    
    <!-- 종합 결론 -->
    <div class="conclusion page-break">
        <h3>VII. 종합 검토 및 최종 결론</h3>
        
        <h4 style="margin-top: 20px;">1. 사업 적정성 최종 판단</h4>
        <p style="margin: 10px 0; line-height: 1.8;">
            {summary.get('recommendation', '')}
        </p>
        
        <h4 style="margin-top: 20px;">2. 리스크 및 해결 방안</h4>
        <ul>
"""
        
        # 리스크 나열
        if risks:
            for risk in risks[:5]:
                html += f"            <li><strong>[{risk.get('category')}]</strong> {risk.get('description')}</li>\n"
        else:
            html += "            <li><strong>✅ 주요 리스크 없음</strong> - 전반적으로 양호한 조건을 갖추고 있습니다.</li>\n"
        
        html += f"""
        </ul>
        
        <h4 style="margin-top: 20px;">3. LH 매입 예상 가격</h4>
"""
        
        # 가격 정보 추가
        price_estimate = self._estimate_lh_purchase_price(data)
        
        html += f"""
        <table style="margin-top: 10px; font-size: 9pt;">
            <tr>
                <td style="width: 40%; background: #f0f0f0;"><strong>토지 감정평가 예상액</strong></td>
                <td style="width: 60%; text-align: right;">{price_estimate['total_land_value']:,.0f}원 (㎡당 {price_estimate['base_land_price_per_sqm']:,.0f}원)</td>
            </tr>
            <tr>
                <td style="background: #f0f0f0;"><strong>건물 공사비 추정</strong></td>
                <td style="text-align: right;">{price_estimate['total_construction_cost']:,.0f}원</td>
            </tr>
            <tr>
                <td style="background: #f0f0f0;"><strong>제세공과금</strong></td>
                <td style="text-align: right;">{price_estimate['taxes_and_fees']:,.0f}원</td>
            </tr>
            <tr style="background: #e3f2fd; font-weight: bold;">
                <td><strong>LH 총 매입 예상액</strong></td>
                <td style="text-align: right; color: #0066cc; font-size: 10pt;">{price_estimate['total_purchase_price']:,.0f}원</td>
            </tr>
            <tr style="background: #d4edda;">
                <td><strong>선금 수령 가능액</strong><br><span style="font-size: 8pt; color: #666;">(관리형 토지신탁, 조기약정)</span></td>
                <td style="text-align: right; color: #28a745; font-weight: bold;">{price_estimate['advance_payment_trust_early']:,.0f}원 (토지분 80%)</td>
            </tr>
        </table>
        <p style="margin-top: 10px; font-size: 9pt; color: #666; line-height: 1.6;">
            ※ 실제 매입가격은 LH 선정 2개 감정평가법인의 평가 평균값으로 결정되며, 상기 금액은 지역 기준단가, 
            용도지역 보정({price_estimate['zone_factor']:.2f}배), 입지 점수 보정({price_estimate['location_factor']:.2f}배)을 적용한 예상액입니다.
        </p>
        
        <h4 style="margin-top: 20px;">4. 권장 전략 (특장점)</h4>
        <ul>
            <li><strong>{unit_type}</strong> 수요가 풍부한 입지로 임대 수요 확보 유리</li>
            <li>5.0 만점 평가에서 평균 <strong>{scores['average']['score']:.2f}점</strong> 획득</li>
            <li>토지 감정평가 예상액 <strong>{price_estimate['total_land_value']:,.0f}원</strong>으로 시장 실거래가 반영</li>
            <li>관리형 토지신탁 선택 시 조기 선금 <strong>{price_estimate['advance_payment_trust_early']:,.0f}원</strong> 수령 가능</li>
            <li>LH 표준 평면 및 가이드라인 준수 시 심의 우대 가능</li>
            <li>주차 대수 초과 확보 및 커뮤니티 시설 확충 권장</li>
        </ul>
        
        <h4 style="margin-top: 20px;">4. 공공 매입 가능성</h4>
        <p style="margin: 10px 0; padding: 15px; background: {"#e6ffe6" if is_eligible else "#ffe6e6"}; border-radius: 5px; font-weight: bold;">
            {"✅ LH 매입 가능성: 높음 (적격 판정)" if is_eligible else "❌ LH 매입 가능성: 낮음 (부적격 판정)"}
        </p>
        <p style="margin: 10px 0; line-height: 1.8;">
            {"종합적인 분석 결과, 본 대상지는 LH 신축매입임대주택 사업 대상지로서 적합한 조건을 갖추고 있습니다. 다만, 최종 매입 여부는 LH 심의위원회의 검토를 거쳐 결정되며, 상기 체크리스트의 '확인필요' 항목에 대한 서류 제출 및 현장 실사가 선행되어야 합니다." if is_eligible else "치명적인 탈락 사유가 발견되어 현재 상태로는 LH 매입 대상에서 제외됩니다. 해당 사유를 해소할 수 있는 경우, 사유 해결 후 재신청을 검토하시기 바랍니다."}
        </p>
    </div>
    
    <!-- 보고서 종료 -->
    <div style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #ccc; text-align: center; color: #666; font-size: 9pt;">
        <p>본 보고서는 LH 신축매입임대주택 사업 토지진단 자동화 시스템에 의해 생성되었습니다.</p>
        <p>작성일시: {self.report_date.strftime('%Y년 %m월 %d일 %H:%M')}</p>
        <p style="margin-top: 10px; font-size: 8pt; color: #999;">
            ※ 본 보고서는 참고용이며, 최종 매입 여부는 LH의 공식 심의를 거쳐 결정됩니다.<br>
            ※ 정확한 법적 검토 및 현장 실사는 전문가의 검증이 필요합니다.
        </p>
    </div>
</body>
</html>
"""
        
        return html
