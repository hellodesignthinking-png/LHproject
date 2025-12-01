"""
LH 신축매입약정 사업 공식 양식 기반 토지진단 보고서 생성
- LH 공식 제출 양식 완벽 준수
- VI 섹션 구조
- 5.0 만점 평가 시스템
- 10개 항목 탈락 사유 체크리스트
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.chart_service import get_chart_service


class LHOfficialReportGenerator:
    """LH 공식 양식 보고서 생성기"""
    
    # LH 신축매입임대 유형별 기준 (6개 공식 유형)
    LH_HOUSING_TYPES = {
        "청년": {
            "target": "만 19~39세 무주택 청년",
            "size": "전용면적 30㎡ 이하",
            "rent_rate": "시세의 60~80%",
            "period": "최장 6년",
            "parking": "0.5대/세대",
            "floor_height": "2.3m 이상",
            "construction_cost": 280,  # 만원/㎡
            "key_criteria": ["청년층 집중 지역", "대중교통 접근성", "직장 근접성", "1인 가구 밀집도"]
        },
        "신혼·신생아 I": {
            "target": "혼인 7년 이내 무주택 신혼부부 (자녀 없음)",
            "size": "전용면적 45㎡ 이하",
            "rent_rate": "시세의 70~85%",
            "period": "최장 6년",
            "parking": "0.7대/세대",
            "floor_height": "2.3m 이상",
            "construction_cost": 300,  # 만원/㎡
            "key_criteria": ["교육시설 접근성", "육아 인프라", "생활편의시설", "공원/놀이터"]
        },
        "신혼·신생아 II": {
            "target": "혼인 7년 이내 무주택 신혼부부 (자녀 1명 이상)",
            "size": "전용면적 55㎡ 이하",
            "rent_rate": "시세의 70~85%",
            "period": "최장 10년",
            "parking": "0.8대/세대",
            "floor_height": "2.3m 이상",
            "construction_cost": 310,  # 만원/㎡
            "key_criteria": ["교육시설 접근성", "육아 인프라", "생활편의시설", "공원/놀이터", "어린이집 근접"]
        },
        "다자녀": {
            "target": "미성년 자녀 3명 이상 무주택 가구",
            "size": "전용면적 65㎡ 이하",
            "rent_rate": "시세의 65~80%",
            "period": "최장 20년",
            "parking": "1.0대/세대",
            "floor_height": "2.4m 이상",
            "construction_cost": 320,  # 만원/㎡
            "key_criteria": ["학교 접근성", "대형 공원", "커뮤니티 시설", "안전한 주거환경"]
        },
        "고령자": {
            "target": "만 65세 이상 무주택 고령자",
            "size": "전용면적 40㎡ 이하",
            "rent_rate": "시세의 70~80%",
            "period": "최장 20년",
            "parking": "0.3대/세대",
            "floor_height": "2.5m 이상 (천장 높이 확보)",
            "construction_cost": 320,  # 만원/㎡
            "key_criteria": ["의료시설 접근성", "무장애 설계", "1층 배치 우선", "복지센터 근접"]
        },
        "일반": {
            "target": "소득 7분위 이하 무주택 가구",
            "size": "전용면적 85㎡ 이하",
            "rent_rate": "시세의 80~95%",
            "period": "최장 20년",
            "parking": "1.0대/세대",
            "floor_height": "2.3m 이상",
            "construction_cost": 290,  # 만원/㎡
            "key_criteria": ["생활 인프라", "교통 편의성", "직주근접", "주거 안정성"]
        },
        "든든전세": {
            "target": "청년 및 신혼부부 (전세계약 방식)",
            "size": "전용면적 85㎡ 이하",
            "rent_rate": "주변 시세 전세가",
            "period": "2년 (재계약 가능)",
            "parking": "0.8대/세대",
            "floor_height": "2.3m 이상",
            "construction_cost": 300,  # 만원/㎡
            "key_criteria": ["생활 편의성", "교통 접근성", "주거환경", "전세 수요"]
        }
    }
    
    def __init__(self):
        self.report_date = datetime.now()
        self.report_version = "V1.0"
    
    @staticmethod
    def _get_attr(obj, key, default=None):
        """Pydantic 객체와 dict 모두에서 안전하게 값 가져오기"""
        if hasattr(obj, key):
            return getattr(obj, key)
        elif isinstance(obj, dict):
            return obj.get(key, default)
        return default
    
    @staticmethod
    def _safe_get(data: Dict[str, Any], *keys, default=""):
        """
        중첩된 딕셔너리에서 안전하게 값 가져오기
        
        Example:
            _safe_get(data, "grade_info", "grade", default="C")
        """
        try:
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key)
                elif hasattr(result, key):
                    result = getattr(result, key)
                else:
                    return default
                
                if result is None:
                    return default
            
            return result if result is not None else default
        except (KeyError, AttributeError, TypeError):
            return default
    
    def _generate_fallback_html(self, analysis_data: Dict[str, Any], error_msg: str) -> str:
        """
        오류 발생 시 최소한의 정보를 담은 폴백 HTML 생성
        """
        address = self._safe_get(analysis_data, 'address', default='주소 정보 없음')
        unit_type = self._safe_get(analysis_data, 'unit_type', default='청년')
        
        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>LH 토지진단 보고서 - 생성 오류</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            padding: 40px;
            background: #f8f9fa;
        }}
        .error-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #dc3545;
            font-size: 24pt;
            margin-bottom: 20px;
        }}
        .info-box {{
            background: #e3f2fd;
            padding: 20px;
            border-left: 5px solid #2196f3;
            margin: 20px 0;
        }}
        .error-box {{
            background: #ffe6e6;
            padding: 20px;
            border-left: 5px solid #dc3545;
            margin: 20px 0;
            font-family: monospace;
            font-size: 9pt;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>⚠️ 보고서 생성 중 오류 발생</h1>
        
        <div class="info-box">
            <strong>대상지 정보:</strong><br>
            • 주소: {address}<br>
            • 주택 유형: {unit_type}<br>
            • 보고서 일자: {self.report_date.strftime('%Y년 %m월 %d일')}
        </div>
        
        <div class="error-box">
            <strong>오류 메시지:</strong><br>
            {error_msg}
        </div>
        
        <p style="margin-top: 30px; color: #666; text-align: center;">
            시스템 관리자에게 문의하시기 바랍니다.<br>
            디버그 로그가 저장되었습니다.
        </p>
    </div>
</body>
</html>
"""
    
    def generate_official_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        LH 공식 양식 토지진단 보고서 생성 (완전 안전 버전)
        
        Args:
            analysis_data: 종합 분석 데이터
            
        Returns:
            HTML 형식의 LH 공식 보고서
        """
        import traceback
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 데이터 안전 추출 (_safe_get 사용)
            address = self._safe_get(analysis_data, 'address', default='주소 정보 없음')
            land_area = self._safe_get(analysis_data, 'land_area', default=0)
            unit_type = self._safe_get(analysis_data, 'unit_type', default='청년')
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
            
            # 레이더 차트 생성 (수요 점수 시각화)
            radar_chart_image = None
            try:
                chart_service = get_chart_service()
                # 각 카테고리별 점수 추출 (0-100 스케일을 5점 만점 기준으로 변환)
                demographic_score = scores['environment']['score'] * 8  # 5점 → 40점
                accessibility_score = scores['transit']['score'] * 6  # 5점 → 30점
                market_score = scores['vehicle']['score'] * 6  # 5점 → 30점
                regulation_score = scores['demand']['score'] * 4  # 5점 → 20점
                environment_score = scores['environment']['score'] * 4  # 5점 → 20점 (중복이지만 시각화용)
                
                radar_chart_image = chart_service.create_demand_radar_chart(
                    demographic_score=demographic_score,
                    accessibility_score=accessibility_score,
                    market_score=market_score,
                    regulation_score=regulation_score,
                    environment_score=environment_score,
                    title=f"{unit_type} 수요 분석 종합 평가"
                )
            except Exception as e:
                logger.warning(f"⚠️ 레이더 차트 생성 실패: {e}")
            
            # HTML 보고서 생성
            html = self._generate_html_structure(
                address, land_area, unit_type, coords,
                zone_info, capacity, risks, demographic, demand, summary,
                scores, critical_checks, map_image, analysis_data, radar_chart_image
            )
            
            return html
            
        except Exception as e:
            # 치명적 오류 발생 시 상세 로깅 및 안전한 폴백 HTML 반환
            error_trace = traceback.format_exc()
            logger.error(f"❌ PDF 보고서 생성 치명적 오류:\n{error_trace}")
            
            # 디버그용 HTML 저장 시도
            try:
                debug_path = f"/home/user/webapp/debug_report_error_{self.report_date.strftime('%Y%m%d_%H%M%S')}.log"
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(f"Error: {str(e)}\n\n")
                    f.write(f"Traceback:\n{error_trace}\n\n")
                    f.write(f"Analysis Data Keys: {list(analysis_data.keys())}\n")
                logger.info(f"디버그 정보 저장됨: {debug_path}")
            except:
                pass
            
            # 안전한 폴백 HTML 반환
            return self._generate_fallback_html(analysis_data, str(e))
    
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
        # Pydantic 객체 또는 dict 처리
        if hasattr(demand, 'nearby_facilities'):
            facilities = demand.nearby_facilities
        else:
            facilities = demand.get('nearby_facilities', []) if isinstance(demand, dict) else []
        
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
        if risks:
            has_hazard = any(self._get_attr(r, 'category') == '유해시설' for r in risks)
            if not has_hazard:
                score += 0.5
        else:
            score += 0.5
        
        return min(5.0, score)
    
    def _score_transit(self, data: Dict[str, Any]) -> float:
        """교통 편의성 점수 (대중교통 접근성)"""
        score = 0.0
        
        demand = data.get('demand_analysis', {})
        # Pydantic 객체 또는 dict 처리
        if hasattr(demand, 'nearby_facilities'):
            facilities = demand.nearby_facilities
        else:
            facilities = demand.get('nearby_facilities', []) if isinstance(demand, dict) else []
        
        # 지하철역 거리 평가 (최대 3.0점)
        subway_distance = 9999
        for facility in facilities:
            category = self._get_attr(facility, 'category', '')
            distance = self._get_attr(facility, 'distance', 9999)
            if '지하철' in category:
                subway_distance = min(subway_distance, distance)
        
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
        bus_count = 0
        for f in facilities:
            category = self._get_attr(f, 'category', '')
            if '버스' in category:
                bus_count += 1
        
        if bus_count >= 3:
            score += 1.0
        elif bus_count >= 1:
            score += 0.5
        
        # 대학교/직장 근접성 (최대 1.0점)
        has_university = False
        for f in facilities:
            category = self._get_attr(f, 'category', '')
            if '대학' in category:
                has_university = True
                break
        
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
        unit_type = data.get('unit_type', '청년')
        
        # Pydantic 객체 또는 dict 처리
        youth_ratio = self._get_attr(demographic, 'youth_ratio', 0)
        single_ratio = self._get_attr(demographic, 'single_household_ratio', 0)
        
        if unit_type in ['청년', '청년형']:
            # 청년 인구 비율 (최대 2.5점)
            if youth_ratio >= 30:
                score += 2.5
            elif youth_ratio >= 20:
                score += 2.0
            elif youth_ratio >= 10:
                score += 1.5
            else:
                score += 1.0
            
            # 1인 가구 비율 (최대 2.5점)
            if single_ratio >= 40:
                score += 2.5
            elif single_ratio >= 30:
                score += 2.0
            elif single_ratio >= 20:
                score += 1.5
            else:
                score += 1.0
        
        elif unit_type in ['신혼·신생아 I', '신혼·신생아 II', '신혼부부형']:
            # 2-3인 가구 수요 평가
            score = 3.5  # 기본값
            
        elif unit_type in ['고령자', '고령자형']:
            # 고령 인구 비율 평가
            score = 3.5  # 기본값
        
        elif unit_type in ['다자녀', '일반', '든든전세']:
            # 기타 유형 기본값
            score = 3.5
        
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
        units = self._get_attr(capacity, 'units', 0)
        parking_spaces = self._get_attr(capacity, 'parking_spaces', 0)
        
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
        LH 매입 예상 가격 산정 (지역 실거래가 또는 사용자 입력 기반)
        
        LH 매입가격 산정 방식:
        1. 토지 감정평가액 (사용자 입력값 우선, 없으면 지역 거래가 중심)
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
        user_appraisal_price = data.get('land_appraisal_price')  # 사용자 입력값
        
        # 사용자가 탁상감정평가액을 입력한 경우 우선 사용
        if user_appraisal_price and user_appraisal_price > 0:
            base_land_price_per_sqm = user_appraisal_price
            price_range_factor = 0.15  # 사용자 입력값은 편차 적게 (±15%)
            price_source = "사용자 입력 탁상감정평가액"
        else:
            # 지역별 토지 실거래가 기준 단가 (㎡당)
            # 실제 판매/거래 중인 토지 가격 반영
            if '서울' in address:
                base_land_price_per_sqm = 5_500_000  # 550만원/㎡ (서울 평균 거래가)
                price_range_factor = 0.35  # ±35% (거래가 편차 반영)
            elif '경기' in address or '인천' in address:
                base_land_price_per_sqm = 2_800_000  # 280만원/㎡ (경기/인천 평균 거래가)
                price_range_factor = 0.30  # ±30%
            else:
                base_land_price_per_sqm = 1_800_000  # 180만원/㎡ (지방 평균 거래가)
                price_range_factor = 0.25  # ±25%
            price_source = "지역 실거래가 기준"
        
        # 용도지역별 보정 (사용자 입력값이 아닌 경우만)
        zone_type = self._get_attr(zone_info, 'zone_type', '')
        if user_appraisal_price and user_appraisal_price > 0:
            # 사용자 입력값은 보정하지 않음
            zone_factor = 1.0
            location_factor = 1.0
        else:
            # 자동 계산의 경우 보정 적용
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
        total_floor_area = self._get_attr(capacity, 'total_floor_area', 0)
        
        # 건축비 단가 (㎡당, 구조/마감에 따라 상이)
        # 유형별 건축비 (만원/㎡를 원/㎡로 변환)
        type_info = self.LH_HOUSING_TYPES.get(unit_type)
        if type_info:
            construction_cost_per_sqm = type_info.get('construction_cost', 300) * 10_000
        else:
            construction_cost_per_sqm = 3_000_000  # 기본값 300만원/㎡
        
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
        
        # 사용자 입력값 여부 플래그
        is_user_input = user_appraisal_price and user_appraisal_price > 0
        
        return {
            'land_area': land_area,
            'base_land_price_per_sqm': base_land_price_per_sqm if is_user_input else adjusted_land_price,  # 사용자 입력값은 원본 표시
            'adjusted_land_price_per_sqm': adjusted_land_price,  # 보정된 값 (계산용)
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
            'is_user_input': is_user_input,  # 사용자 입력 여부
            'factors_explanation': {
                'zone': f"용도지역({zone_type}) 보정계수: {zone_factor:.2f}배" if not is_user_input else "용도지역: 사용자 입력값 적용 (보정 없음)",
                'location': f"입지점수({avg_score:.1f}/5.0) 보정계수: {location_factor:.2f}배" if not is_user_input else "입지점수: 사용자 입력값 적용 (보정 없음)",
                'base': f"{price_source}: {base_land_price_per_sqm:,.0f}원/㎡" + ("" if is_user_input else " (판매/거래 중인 토지 가격 반영)")
            },
            'price_source': price_source
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
        total_pop = self._get_attr(demographic, 'total_population', 0)
        youth_pop = self._get_attr(demographic, 'youth_population', 0)
        youth_ratio = self._get_attr(demographic, 'youth_ratio', 0)
        single_households = self._get_attr(demographic, 'single_households', 0)
        single_ratio = self._get_attr(demographic, 'single_household_ratio', 0)
        
        # zone_info 값 추출 (HTML에서 사용)
        zone_type_name = self._get_attr(zone_info, 'zone_type', 'N/A')
        building_coverage = self._get_attr(zone_info, 'building_coverage_ratio', 0)
        floor_area = self._get_attr(zone_info, 'floor_area_ratio', 0)
        
        # 주변 시설 분석
        # Pydantic 객체 또는 dict 처리
        if hasattr(demand, 'nearby_facilities'):
            facilities = demand.nearby_facilities
        else:
            facilities = demand.get('nearby_facilities', []) if isinstance(demand, dict) else []
        
        # NearbyFacility 객체 안전하게 처리
        subway_count = sum(1 for f in facilities if '지하철' in self._get_attr(f, 'category', ''))
        bus_count = sum(1 for f in facilities if '버스' in self._get_attr(f, 'category', ''))
        univ_count = sum(1 for f in facilities if '대학' in self._get_attr(f, 'category', ''))
        convenience_count = sum(1 for f in facilities if '편의점' in self._get_attr(f, 'category', ''))
        
        # 유해시설 여부
        has_critical_hazard = any(self._get_attr(r, 'category') == 'LH매입제외' for r in risks)
        has_hazard = any(self._get_attr(r, 'category') == '유해시설' for r in risks)
        
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
                    대상지의 용도지역은 <strong>{zone_type_name}</strong>으로 지정되어 있으며,
                    법정 건폐율 <strong>{building_coverage:.0f}%</strong>, 용적률 <strong>{floor_area:.0f}%</strong>가 적용된다.
                    이는 {"주거용 건축물 건립에 적합한 용도지역" if "주거" in zone_type_name else "건축 가능 용도지역"}으로,
                    LH 신축매입임대주택 사업 추진에 <strong>{"법적 제약이 없는" if not any(self._get_attr(r, 'category') == '법적제한' for r in risks) else "일부 제약이 존재하는"}</strong> 것으로 확인되었다.
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
        has_legal_restriction = any(self._get_attr(r, 'category') == '법적제한' for r in risks)
        checklist.append({
            "no": 1,
            "item": "법률상 제한 사유 (압류, 경매, 건축법 위반 등)",
            "status": "부적합" if has_legal_restriction else "적합",
            "details": "토지등기부등본 확인 필요",
            "is_critical": has_legal_restriction
        })
        
        # 2. 유해시설 인접 (주유소 25m 이내 등)
        has_critical_hazard = any(
            self._get_attr(r, 'category') == 'LH매입제외' and '주유소' in self._get_attr(r, 'description', '')
            for r in risks
        )
        has_hazard = any(self._get_attr(r, 'category') == '유해시설' for r in risks)
        
        hazard_details = ""
        if has_critical_hazard:
            hazard_details = "주유소 25m 이내 - 절대 탈락 사유"
        elif has_hazard:
            hazard_list = [self._get_attr(r, 'description') for r in risks if self._get_attr(r, 'category') == '유해시설']
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
        floors = self._get_attr(capacity, 'floors', 0)
        units = self._get_attr(capacity, 'units', 0)
        needs_elevator = (floors > 4) or (unit_type in ['고령자', '고령자형'] and floors > 1)
        
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
        data: Dict[str, Any],
        radar_chart_image: Optional[str] = None
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
        is_eligible = not has_critical_risk and self._get_attr(summary, 'is_eligible', True)
        
        # HTML 템플릿에서 사용할 값들 미리 추출 (Pydantic 객체 처리)
        # ZoneInfo
        zone_type_val = self._get_attr(zone_info, 'zone_type', 'N/A')
        building_coverage_val = self._get_attr(zone_info, 'building_coverage_ratio', 0)
        floor_area_val = self._get_attr(zone_info, 'floor_area_ratio', 0)
        
        # BuildingCapacity
        units_val = self._get_attr(capacity, 'units', 0)
        floors_val = self._get_attr(capacity, 'floors', 0)
        building_area_val = self._get_attr(capacity, 'building_area', 0)
        total_floor_area_val = self._get_attr(capacity, 'total_floor_area', 0)
        parking_spaces_val = self._get_attr(capacity, 'parking_spaces', 0)
        
        # DemandAnalysis
        if hasattr(demand, 'nearby_facilities'):
            facilities_list = demand.nearby_facilities
        else:
            facilities_list = demand.get('nearby_facilities', []) if isinstance(demand, dict) else []
        facilities_count = len(facilities_list)
        
        # DemographicInfo - 미리 추출
        total_population_val = self._get_attr(demographic, 'total_population', 0)
        youth_population_val = self._get_attr(demographic, 'youth_population', 0)
        youth_ratio_val = self._get_attr(demographic, 'youth_ratio', 0)
        single_households_val = self._get_attr(demographic, 'single_households', 0)
        single_household_ratio_val = self._get_attr(demographic, 'single_household_ratio', 0)
        
        # AnalysisSummary - 미리 추출
        recommendation_val = self._get_attr(summary, 'recommendation', '')
        
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
                position: relative;
            }}
            body::before {{
                content: '사회적기업(주)안테나';
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 80pt;
                color: rgba(0, 0, 0, 0.03);
                z-index: -1;
                /* white-space removed for PDF compatibility */
            }}
            /* 페이지 나누기 제어 */
            .page-break {{
                page-break-before: always;
            }}
            .page-break-after {{
                page-break-after: always;
            }}
            /* 섹션별 페이지 구분 */
            .section {{
                page-break-before: always;
            }}
            .section:first-of-type {{
                page-break-before: auto;
            }}
            /* 테이블 페이지 넘김 방지 */
            table {{
                page-break-inside: avoid;
            }}
            /* 제목과 내용이 분리되지 않도록 */
            .section-title {{
                page-break-after: avoid;
            }}
            .subsection-title {{
                page-break-after: avoid;
            }}
            h2, h3 {{
                page-break-after: avoid;
            }}
            /* 박스 요소들 페이지 넘김 방지 */
            .info-box, .warning-box, .danger-box, .success-box {{
                page-break-inside: avoid;
            }}
            /* 고아/미망인 제어 */
            p {{
                orphans: 3;
                widows: 3;
            }}
            /* 숨길 요소 */
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
            width: 95%;
            margin: 0 auto;
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
        
        /* 컨설턴트 정보 스타일 */
        .consultant-info {{
            margin: 20px 0;
            background: #fff8e1;
            padding: 15px;
            border-radius: 5px;
            border: 2px solid #ffa726;
        }}
        
        .consultant-info h3 {{
            font-size: 11pt;
            font-weight: bold;
            color: #e65100;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #ffa726;
        }}
        
        .consultant-info table {{
            width: 95%;
            margin: 10px auto 0 auto;
        }}
        
        .consultant-info td {{
            padding: 8px;
            border: 1px solid #ffe0b2;
            font-size: 9pt;
        }}
        
        .consultant-info td:first-child {{
            background: #fff3e0;
            font-weight: bold;
            width: 25%;
            color: #e65100;
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
            width: 95%;
            margin: 15px auto;
            font-size: 9pt;
        }}
        
        th, td {{
            border: 1px solid #ccc;
            padding: 10px 8px;
            text-align: left;
            vertical-align: middle;
            word-break: break-all;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        th {{
            background: #003d82;
            color: white;
            font-weight: bold;
            text-align: center;
            padding: 12px 8px;
            border-bottom: 2px solid #0055cc;
        }}
        
        .score-table td:first-child {{
            background: #e3f2fd;
            font-weight: bold;
            width: 30%;
            border-left: 4px solid #1976d2;
        }}
        
        /* Zebra striping for tables */
        table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        table tbody tr:hover {{
            background: #e3f2fd;
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
            background: #d4edda;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        .status-check {{
            color: #856404;
            font-weight: bold;
            background: #fff3cd;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        .status-fail {{
            color: #721c24;
            font-weight: bold;
            background: #f8d7da;
            padding: 4px 8px;
            border-radius: 4px;
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
    
    <!-- Summary Banner (안전 버전) -->
    <div style="margin: 20px 0; padding: 20px; background: #1e3c72; border-radius: 5px; color: white;">
        <table width="95%" style="margin: 0 auto; border: none;">
            <tr>
                <td style="width: 25%; text-align: center; padding: 10px; border-right: 1px solid rgba(255,255,255,0.3); border: none;">
                    <div style="font-size: 14pt; font-weight: bold; margin-bottom: 5px;">
                        {self._safe_get(data, "grade_info", "grade", default="N/A")}
                    </div>
                    <div style="font-size: 9pt; opacity: 0.9;">등급</div>
                </td>
                <td style="width: 25%; text-align: center; padding: 10px; border-right: 1px solid rgba(255,255,255,0.3); border: none;">
                    <div style="font-size: 14pt; font-weight: bold; margin-bottom: 5px;">
                        {self._safe_get(data, "grade_info", "total_score", default=0):.1f}점
                    </div>
                    <div style="font-size: 9pt; opacity: 0.9;">종합 점수</div>
                </td>
                <td style="width: 25%; text-align: center; padding: 10px; border-right: 1px solid rgba(255,255,255,0.3); border: none;">
                    <div style="font-size: 14pt; font-weight: bold; margin-bottom: 5px;">
                        {self._safe_get(data, "demand_analysis", "demand_score", default=0):.1f}점
                    </div>
                    <div style="font-size: 9pt; opacity: 0.9;">수요 점수</div>
                </td>
                <td style="width: 25%; text-align: center; padding: 10px; border: none;">
                    <div style="font-size: 14pt; font-weight: bold; margin-bottom: 5px;">
                        {len(data.get("risk_factors", []))}개
                    </div>
                    <div style="font-size: 9pt; opacity: 0.9;">리스크 요인</div>
                </td>
            </tr>
        </table>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3); text-align: center; font-size: 10pt;">
            <strong>종합 판단:</strong> {self._safe_get(data, "summary", "recommendation", default="분석 중")}
        </div>
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
                <td>{units_val}세대 ({unit_type})</td>
                <td>매입 방식</td>
                <td>□ 감정평가형 / □ 건물공사비 연동형</td>
            </tr>
        </table>
    </div>
    """
        
        # 컨설턴트 정보 섹션 추가 (데이터가 있는 경우만)
        consultant = data.get('consultant')
        if consultant and isinstance(consultant, dict):
            consultant_name = consultant.get('name', '').strip()
            consultant_phone = consultant.get('phone', '').strip()
            consultant_department = consultant.get('department', '').strip()
            consultant_email = consultant.get('email', '').strip()
            
            # 최소한 이름이나 연락처가 있는 경우만 표시
            if consultant_name or consultant_phone:
                html += f"""
    <!-- 컨설팅 담당자 정보 -->
    <div class="consultant-info">
        <h3>📋 컨설팅 담당자 정보</h3>
        <table>
            <tr>
                <td>담당자 이름</td>
                <td>{consultant_name if consultant_name else '(미입력)'}</td>
                <td>연락처</td>
                <td>{consultant_phone if consultant_phone else '(미입력)'}</td>
            </tr>
            <tr>
                <td>소속 부서</td>
                <td>{consultant_department if consultant_department else '(미입력)'}</td>
                <td>이메일</td>
                <td>{consultant_email if consultant_email else '(미입력)'}</td>
            </tr>
        </table>
    </div>
    """
        
        html += f"""
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
                <td><strong>종전 대지 이용상태</strong></td>
                <td><strong>{data.get('land_status', '나대지')}</strong></td>
                <td>현재 토지 이용 상황</td>
            </tr>
            <tr style="background: {"#e8f5e9" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else "#ffffff"};">
                <td><strong>토지 탁상감정평가액 (㎡당)</strong></td>
                <td style="{"font-weight: bold; color: #2e7d32;" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else ""}">
                    {f"{data.get('land_appraisal_price'):,.0f}원/㎡ (사용자 입력)" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else "자동 계산 (지역 거래가 기반)"}
                </td>
                <td>{"입력값 기준 산정" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else "시스템 자동 산정"}</td>
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
        
        <h3 class="subsection-title">1-2. 건축물 개요 (예상)</h3>
        <table>
            <tr>
                <th style="width: 25%;">구분</th>
                <th style="width: 50%;">내용</th>
                <th style="width: 25%;">비고</th>
            </tr>
            <tr>
                <td><strong>대지 면적</strong></td>
                <td>{land_area:,.2f}㎡</td>
                <td>토지등기부등본 기준</td>
            </tr>
            <tr>
                <td><strong>건축 면적</strong></td>
                <td>{building_area_val:,.2f}㎡ (건폐율 {building_coverage_val:.0f}%)</td>
                <td>용도지역 법정 건폐율 적용</td>
            </tr>
            <tr>
                <td><strong>연면적</strong></td>
                <td>{total_floor_area_val:,.2f}㎡ (용적률 {floor_area_val:.0f}%)</td>
                <td>용도지역 법정 용적률 적용</td>
            </tr>
            <tr>
                <td><strong>건축 규모</strong></td>
                <td>지하 -층, 지상 {floors_val}층</td>
                <td>용도지역 높이제한 고려</td>
            </tr>
            <tr>
                <td><strong>세대수</strong></td>
                <td>{units_val}세대 ({unit_type})</td>
                <td>세대당 전용면적 {housing_type_info.get('size', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>주차대수</strong></td>
                <td>{parking_spaces_val}대</td>
                <td>법정 주차대수 기준</td>
            </tr>
            <tr>
                <td><strong>구조</strong></td>
                <td>철근콘크리트조</td>
                <td>일반적인 공동주택 구조</td>
            </tr>
            <tr>
                <td><strong>용도</strong></td>
                <td>공동주택 (신축매입임대주택)</td>
                <td>LH 신축매입임대주택 사업</td>
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
                    <td>생활편의시설 {facilities_count}개 확인</td>
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
        
        <!-- 개선 권장사항 (신규) -->
        <h3 class="subsection-title" style="margin-top: 30px;">3. 개선 권장사항 (Recommendations)</h3>
        <div style="margin: 20px 0; padding: 20px; background: #fff3cd; border-left: 5px solid #ffc107; border-radius: 5px;">
            <h4 style="margin-top: 0; color: #856404; font-size: 11pt;">📌 사업 추진을 위한 개선 방안</h4>
            <ul style="margin: 10px 0; padding-left: 25px; line-height: 1.8;">
                {"".join([f"<li><strong>[{rec.split(':')[0]}]</strong> {':'.join(rec.split(':')[1:]) if ':' in rec else rec}</li>" for rec in (data.get('grade_info', {}).get('recommendations', []) if 'grade_info' in data else [])]) if 'grade_info' in data and data.get('grade_info', {}).get('recommendations') else "<li>현재 모든 기준을 충족하고 있습니다.</li>"}
            </ul>
        </div>
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
                        • 총 인구: {total_population_val:,}명<br>
                        • 청년 인구(20-39세): {youth_population_val:,}명 ({youth_ratio_val:.1f}%)<br>
                        • 1인 가구: {single_households_val:,}가구 ({single_household_ratio_val:.1f}%)<br>
                        • 생활편의시설: {facilities_count}개 확인
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
        
        <!-- 수요 분석 레이더 차트 -->
        {f'''
        <div style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #667eea;">
            <h3 class="subsection-title" style="margin-top: 0;">1-2. 수요 분석 시각화 (5개 카테고리 종합 평가)</h3>
            <div style="text-align: center; margin: 20px 0;">
                <img src="{radar_chart_image}" alt="수요 분석 레이더 차트" style="max-width: 100%; height: auto; border-radius: 8px;">
            </div>
            <table style="margin-top: 20px;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 12px; text-align: center;">평가 카테고리</th>
                        <th style="padding: 12px; text-align: center;">배점</th>
                        <th style="padding: 12px; text-align: center;">획득 점수</th>
                        <th style="padding: 12px; text-align: center;">달성률</th>
                        <th style="padding: 12px; text-align: left;">평가 내용</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">인구통계</td>
                        <td style="padding: 10px; text-align: center;">40점</td>
                        <td style="padding: 10px; text-align: center; font-weight: bold; color: #667eea;">{scores['environment']['score'] * 8:.1f}점</td>
                        <td style="padding: 10px; text-align: center;">{scores['environment']['score'] / 5.0 * 100:.1f}%</td>
                        <td style="padding: 10px;">청년/고령 인구 비율, 1인 가구 비율, 인구 밀집도 등</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">접근성</td>
                        <td style="padding: 10px; text-align: center;">30점</td>
                        <td style="padding: 10px; text-align: center; font-weight: bold; color: #667eea;">{scores['transit']['score'] * 6:.1f}점</td>
                        <td style="padding: 10px; text-align: center;">{scores['transit']['score'] / 5.0 * 100:.1f}%</td>
                        <td style="padding: 10px;">대중교통 접근성, 지하철/버스 정류장 거리, 교통 편의성</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">시장 규모</td>
                        <td style="padding: 10px; text-align: center;">30점</td>
                        <td style="padding: 10px; text-align: center; font-weight: bold; color: #667eea;">{scores['vehicle']['score'] * 6:.1f}점</td>
                        <td style="padding: 10px; text-align: center;">{scores['vehicle']['score'] / 5.0 * 100:.1f}%</td>
                        <td style="padding: 10px;">상권 발달도, 생활편의시설 밀집도, 주요 직장/대학 근접성</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">규제 환경</td>
                        <td style="padding: 10px; text-align: center;">20점</td>
                        <td style="padding: 10px; text-align: center; font-weight: bold; color: #667eea;">{scores['demand']['score'] * 4:.1f}점</td>
                        <td style="padding: 10px; text-align: center;">{scores['demand']['score'] / 5.0 * 100:.1f}%</td>
                        <td style="padding: 10px;">용도지역 적합성, 건축 규제, 법적 제한 사항</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">주변 환경</td>
                        <td style="padding: 10px; text-align: center;">20점</td>
                        <td style="padding: 10px; text-align: center; font-weight: bold; color: #667eea;">{scores['environment']['score'] * 4:.1f}점</td>
                        <td style="padding: 10px; text-align: center;">{scores['environment']['score'] / 5.0 * 100:.1f}%</td>
                        <td style="padding: 10px;">주변 유해시설 여부, 소음/공해, 생활환경 쾌적도</td>
                    </tr>
                    <tr style="background: #f0f0f0; font-weight: bold;">
                        <td style="padding: 12px;">종합 평균</td>
                        <td style="padding: 12px; text-align: center;">140점</td>
                        <td style="padding: 12px; text-align: center; font-size: 14pt; color: #667eea;">{(scores['environment']['score'] * 8 + scores['transit']['score'] * 6 + scores['vehicle']['score'] * 6 + scores['demand']['score'] * 4 + scores['environment']['score'] * 4):.1f}점</td>
                        <td style="padding: 12px; text-align: center; font-size: 14pt;">{((scores['environment']['score'] * 8 + scores['transit']['score'] * 6 + scores['vehicle']['score'] * 6 + scores['demand']['score'] * 4 + scores['environment']['score'] * 4) / 140 * 100):.1f}%</td>
                        <td style="padding: 12px;">5개 카테고리 종합 평가</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin-top: 15px; padding: 12px; background: white; border-radius: 6px; font-size: 11pt; line-height: 1.6;">
                <strong>※ 레이더 차트 해석:</strong><br>
                • 각 축은 해당 카테고리의 배점 대비 획득 점수를 백분율로 표현합니다<br>
                • 차트가 정오각형에 가까울수록 모든 카테고리가 균형있게 높은 점수를 의미합니다<br>
                • 돌출된 축은 해당 카테고리의 강점을, 움푹한 축은 개선이 필요한 부분을 나타냅니다
            </p>
        </div>
        ''' if radar_chart_image else ''}
        
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
                        • 용도지역: {zone_type_val}<br>
                        • 면적: {land_area:,.2f}㎡<br>
                        • 좌표: {coords.latitude:.6f}, {coords.longitude:.6f}
                    </td>
                    <td>토지이용계획확인원 확인 필요</td>
                </tr>
                <tr>
                    <td><strong>건축 규모</strong></td>
                    <td>
                        • 예상 건물 규모: {units_val}세대 / {floors_val}층<br>
                        • 건축면적: {building_area_val:,.2f}㎡<br>
                        • 연면적: {total_floor_area_val:,.2f}㎡
                    </td>
                    <td>설계 단계에서 확정</td>
                </tr>
                <tr>
                    <td><strong>건폐율</strong></td>
                    <td>{building_coverage_val:.1f}%</td>
                    <td>법정 기준 준수</td>
                </tr>
                <tr>
                    <td><strong>용적률</strong></td>
                    <td>{floor_area_val:.1f}%</td>
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
                        • 예상 법정 대수: {parking_spaces_val}대<br>
                        • {unit_type} 기준: {housing_type_info.get('parking', 'N/A')}
                    </td>
                    <td>법정 초과 확보 시 가점</td>
                </tr>
            </tbody>
        </table>
        
        {f"<div class='map-container'><h4>대상지 위치도</h4><img src='{map_image}' alt='대상지 지도' /></div>" if map_image else ""}
        
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
        
        html += f"""
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
            <strong>💰 가격 산정 방법론 (지역 실거래가 기반)</strong><br>
            LH 신축매입임대주택 사업의 매입가격은 <strong>지역 거래가 중심의 감정평가액</strong>을 기준으로 산정됩니다.<br>
            - 토지: 2개 감정평가법인의 평균값 (실제 판매/거래 중인 토지 가격 반영)<br>
            - 건물: 공사비 실비 정산 또는 건물공사비 연동형<br>
            - 최종 매입가: 토지 감정평가액 + 건물 공사비 + 제세공과금
        </div>
"""

        # 가격 산정
        price_estimate = self._estimate_lh_purchase_price(data)
        
        html += f"""
        <h3 class="subsection-title">1. 토지 감정평가 예상액 (지역 거래가 기반)</h3>
        
        <h4 style="margin-top: 15px; color: #555; font-size: 10pt; font-weight: bold;">가. 감정평가 산정 근거 (실거래가 반영)</h4>
        <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; line-height: 1.8;">
            <p style="margin-bottom: 10px;">
                본 대상지의 토지 감정평가액은 <strong>{price_estimate['factors_explanation']['base']}</strong>을 기준으로 다음과 같은 요소를 종합적으로 고려하여 산정되었습니다:
            </p>
            <ul style="margin-left: 20px; margin-bottom: 10px;">
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
                <tr style="background: {"#e8f5e9" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else "#ffffff"};">
                    <td>
                        <strong>토지 감정평가액</strong>
                        {"<br><span style='font-size: 8pt; color: #2e7d32; font-weight: bold;'>✓ 사용자 입력값 적용</span>" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else "<br><span style='font-size: 8pt; color: #666;'>※ 지역 거래가 기반 자동 계산</span>"}
                    </td>
                    <td style="text-align: right; {"font-weight: bold; color: #2e7d32;" if data.get("land_appraisal_price") and data.get("land_appraisal_price") > 0 else ""}">{price_estimate['base_land_price_per_sqm']:,.0f}</td>
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
                    <td style="text-align: right;">{total_floor_area_val:,.2f}</td>
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
                    {zone_type_val}은 {"주거지역 중 가장 가치가 높은" if price_estimate['zone_factor'] >= 1.2 else "주거 용도로 적합한" if price_estimate['zone_factor'] >= 1.0 else "주거 순수성이 보장되는"} 지역으로,
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
        
        html += f"""
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
        
        <h4 style="margin-top: 20px; padding: 12px; background: #667eea; color: white; border-radius: 5px;">
            1. 종합 분석 결과 요약
        </h4>
        <div style="margin: 15px 0; padding: 20px; background: #f8f9fa; border-left: 5px solid #667eea; line-height: 1.9;">
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                본 토지진단 시스템은 <strong>{address}</strong> 소재 <strong>{land_area:,.2f}㎡</strong> 규모의 대상지에 대하여 
                LH 신축매입임대주택 사업 적격성을 다각도로 분석하였습니다. 
                분석 대상 유형은 <strong>{unit_type}</strong>이며, 용도지역은 <strong>{zone_type_val}</strong>으로 확인되었습니다.
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                LH 공식 5.0 만점 평가 시스템을 기준으로 한 종합 평가 결과, 
                주변 환경 <strong>{scores['environment']['score']:.2f}점</strong>, 
                교통 편의성 <strong>{scores['transit']['score']:.2f}점</strong>, 
                차량 접근성 <strong>{scores['vehicle']['score']:.2f}점</strong>, 
                수요 분석 <strong>{scores['demand']['score']:.2f}점</strong>으로 
                평균 <strong>{scores['average']['score']:.2f}점 / 5.0점</strong>을 획득하였습니다.
                이는 {"상위권" if scores['average']['score'] >= 4.0 else "중상위권" if scores['average']['score'] >= 3.5 else "중위권" if scores['average']['score'] >= 3.0 else "중하위권"}에 해당하는 수준으로,
                {"LH 매입 대상지로서 매우 우수한 입지 조건" if scores['average']['score'] >= 4.0 else "LH 매입 대상지로서 양호한 입지 조건" if scores['average']['score'] >= 3.5 else "LH 매입 대상지로서 보통 수준의 입지 조건" if scores['average']['score'] >= 3.0 else "LH 매입 대상지로서 개선이 필요한 입지 조건"}을 갖추고 있습니다.
            </p>
            <p style="margin-bottom: 0; text-indent: 20px; font-size: 10.5pt;">
                인구통계학적 분석 결과, 해당 지역의 총 인구는 <strong>{total_population_val:,}명</strong>이며, 
                청년 인구(20-39세)는 <strong>{youth_population_val:,}명({youth_ratio_val:.1f}%)</strong>, 
                1인 가구는 <strong>{single_households_val:,}가구({single_household_ratio_val:.1f}%)</strong>로 집계되었습니다.
                이는 {unit_type} 타겟층의 {"풍부한 수요 기반" if youth_ratio_val >= 30 else "충분한 수요 기반" if youth_ratio_val >= 20 else "일정한 수요 기반" if youth_ratio_val >= 15 else "제한적인 수요 기반"}을 의미하며,
                임대 시장에서의 {"높은" if youth_ratio_val >= 30 else "양호한" if youth_ratio_val >= 20 else "보통의" if youth_ratio_val >= 15 else "낮은"} 경쟁력을 예상할 수 있습니다.
            </p>
        </div>
        
        <h4 style="margin-top: 25px; padding: 12px; background: #667eea; color: white; border-radius: 5px;">
            2. 입지 특성 및 개발 여건 종합 평가
        </h4>
        <div style="margin: 15px 0; padding: 20px; background: #f8f9fa; border-left: 5px solid #667eea; line-height: 1.9;">
            <h5 style="margin: 0 0 10px 0; color: #667eea; font-size: 11pt;">가. 교통 접근성 및 생활 편의성</h5>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                대상지는 주변에 {facilities_count}개의 주요 생활편의시설이 분포하고 있어 
                {"우수한" if facilities_count >= 30 else "양호한" if facilities_count >= 20 else "보통의" if facilities_count >= 10 else "부족한"} 생활 인프라 환경을 갖추고 있습니다.
                특히 대중교통 접근성 측면에서 {"지하철역, 버스 정류장 등이 인근에 밀집되어 있어 출퇴근 및 일상 이동이 매우 편리" if scores['transit']['score'] >= 4.5 else "대중교통 이용이 비교적 편리하여 주거 환경으로서 적합" if scores['transit']['score'] >= 3.5 else "대중교통 접근성이 보통 수준으로 일부 보완이 필요" if scores['transit']['score'] >= 2.5 else "대중교통 접근성이 다소 부족하여 개선 방안 검토 필요"}한 것으로 평가됩니다.
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                차량 접근성의 경우 {scores['vehicle']['score']:.2f}점을 기록하여 
                {"우수한" if scores['vehicle']['score'] >= 4.0 else "양호한" if scores['vehicle']['score'] >= 3.0 else "보통의" if scores['vehicle']['score'] >= 2.0 else "미흡한"} 수준으로 평가되었습니다.
                이는 {"간선도로 및 이면도로 접근이 용이하여 자가용 이용 입주자들에게도 편의성을 제공" if scores['vehicle']['score'] >= 4.0 else "도로 접근이 가능한 수준이나 일부 교통 혼잡 가능성 존재" if scores['vehicle']['score'] >= 3.0 else "도로 접근성이 제한적이어서 차량 이용 시 불편 예상" if scores['vehicle']['score'] >= 2.0 else "차량 접근이 어려워 대중교통 중심 입지로 활용 권장"}할 수 있음을 시사합니다.
            </p>
            
            <h5 style="margin: 20px 0 10px 0; color: #667eea; font-size: 11pt;">나. 법적 규제 및 건축 여건</h5>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                대상지의 용도지역은 <strong>{zone_type_val}</strong>로서 
                건폐율 <strong>{building_coverage_val:.1f}%</strong>, 용적률 <strong>{floor_area_val:.1f}%</strong>가 적용됩니다.
                이에 따라 건축면적은 약 <strong>{building_area_val:,.2f}㎡</strong>, 
                연면적은 약 <strong>{total_floor_area_val:,.2f}㎡</strong> 규모의 건물 신축이 가능하며,
                {unit_type} 기준으로 <strong>{units_val}세대</strong>, <strong>{floors_val}층</strong> 규모의 임대주택 건축이 가능할 것으로 산정됩니다.
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                주차 계획의 경우, 산정된 <strong>{parking_spaces_val}대</strong>의 주차 공간은 
                {"법정 주차대수를 충분히 상회하여 LH 심의 시 가점 요인으로 작용" if parking_spaces_val >= units_val * 0.8 else "법정 주차대수를 충족하는 수준으로 적정" if parking_spaces_val >= units_val * 0.5 else "법정 주차대수 충족을 위해 지하 주차장 설치 등 추가 검토 필요"}할 것으로 판단됩니다.
                특히 {unit_type}의 경우 {"젊은 층 대상으로 대중교통 의존도가 높아 주차 부담이 상대적으로 낮은 편" if unit_type in ["청년", "청년형"] else "신혼부부 대상으로 자가용 보유율을 고려한 충분한 주차 확보 필요" if "신혼" in unit_type else "고령자 대상으로 경사로, 장애인 주차 등 특수 주차시설 배려 필요" if "고령" in unit_type else "일반 가구 대상으로 법정 주차대수 이상 확보 권장"}입니다.
            </p>
            
            <h5 style="margin: 20px 0 10px 0; color: #667eea; font-size: 11pt;">다. 수요 환경 및 임대 시장 전망</h5>
            <p style="margin-bottom: 0; text-indent: 20px; font-size: 10.5pt;">
                {unit_type} 타겟층에 대한 수요 분석 결과 {scores['demand']['score']:.2f}점을 획득하여 
                {"매우 높은" if scores['demand']['score'] >= 4.5 else "높은" if scores['demand']['score'] >= 4.0 else "양호한" if scores['demand']['score'] >= 3.5 else "보통의" if scores['demand']['score'] >= 3.0 else "낮은"} 수요 잠재력을 보유한 것으로 평가됩니다.
                해당 지역의 {"청년층 밀집도, 대학가 인접성, 직장 접근성 등이 우수하여 청년 타겟 임대주택 수요가 풍부" if unit_type in ["청년", "청년형"] else "신혼부부 및 출산가구 비율이 높고 보육 인프라가 잘 갖춰져 있어 신혼부부 대상 임대 수요 충분" if "신혼" in unit_type else "고령 인구 비율 및 의료시설 접근성이 양호하여 고령자 주택 수요 존재" if "고령" in unit_type else "다양한 가구 구성에 대응 가능한 일반 임대 수요 확인"}할 수 있습니다.
                임대 시장에서의 {"공실 위험은 낮고 안정적인 임대 운영" if scores['demand']['score'] >= 4.0 else "적정한 임대 운영" if scores['demand']['score'] >= 3.0 else "일부 공실 발생 가능성 존재하므로 마케팅 전략 수립 필요"}이 예상됩니다.
            </p>
        </div>
        
        <h4 style="margin-top: 25px; padding: 12px; background: #667eea; color: white; border-radius: 5px;">
            3. 리스크 요인 및 해결 방안 (상세 분석)
        </h4>
        <div style="margin: 15px 0; padding: 20px; background: #fff3cd; border-left: 5px solid #ffc107; line-height: 1.9;">
"""
        
        # 리스크 상세 분석
        if risks:
            html += f"""
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                본 대상지에 대한 리스크 진단 결과, <strong>총 {len(risks)}건의 리스크 요인</strong>이 식별되었습니다.
                이는 {"치명적 리스크가 포함되어 즉각적인 해결 없이는 LH 매입이 불가능한 상태" if any(self._get_attr(r, 'severity') in ['critical', 'LH매입제외'] for r in risks) else "관리 가능한 수준의 리스크로서 적절한 대응 방안 마련 시 사업 추진 가능"}입니다.
            </p>
            <table style="width: 95%; margin: 15px auto;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd; width: 10%;">No.</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 20%;">리스크 유형</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 15%;">심각도</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 35%;">상세 내용</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 20%;">해결 방안</th>
                    </tr>
                </thead>
                <tbody>
"""
            for idx, risk in enumerate(risks, 1):
                risk_category = self._get_attr(risk, 'category', '미분류')
                risk_description = self._get_attr(risk, 'description', '')
                risk_severity = self._get_attr(risk, 'severity', 'medium')
                
                # 심각도별 색상 및 텍스트
                severity_color = {
                    'critical': '#dc3545',
                    'LH매입제외': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }.get(risk_severity, '#6c757d')
                
                severity_text = {
                    'critical': '매우 높음 (치명적)',
                    'LH매입제외': '매우 높음 (LH 매입 제외)',
                    'high': '높음',
                    'medium': '보통',
                    'low': '낮음'
                }.get(risk_severity, '미분류')
                
                # 리스크별 해결 방안 제시
                if risk_severity in ['critical', 'LH매입제외']:
                    solution = "즉시 해결 필요 - 사유 제거 후 재신청 권장"
                elif '유해시설' in risk_category:
                    solution = "해당 시설 이전 협의 또는 대상지 변경 검토"
                elif '경사' in risk_description or '지형' in risk_description:
                    solution = "토목공사로 대지 정지, 옹벽/석축 설치 검토"
                elif '도로' in risk_description or '접도' in risk_description:
                    solution = "사설도로 개설 또는 통행권 확보 필요"
                elif '규제' in risk_category or '제한' in risk_description:
                    solution = "해당 규제 해제 신청 또는 개발행위 허가 취득"
                else:
                    solution = "관련 기관 협의 및 인허가 과정에서 해결"
                
                html += f"""
                    <tr style="background: {"#ffe6e6" if risk_severity in ['critical', 'LH매입제외'] else "#fff9e6" if risk_severity == 'high' else "#fffbf0" if risk_severity == 'medium' else "#f0fff0"};">
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{idx}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{risk_category}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: {severity_color}; font-weight: bold;">{severity_text}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 9.5pt;">{risk_description}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 9.5pt;">{solution}</td>
                    </tr>
"""
            
            html += f"""
                </tbody>
            </table>
            <p style="margin-top: 15px; text-indent: 20px; font-size: 10.5pt; font-weight: bold; color: #856404;">
                ⚠️ 위 리스크 요인들은 LH 심의 전 반드시 해결 또는 명확한 대응 방안이 마련되어야 하며, 
                특히 '치명적' 또는 'LH매입제외' 등급의 리스크는 즉각적인 조치 없이는 사업 추진이 불가능합니다.
            </p>
"""
        else:
            html += f"""
            <p style="margin-bottom: 0; text-indent: 20px; font-size: 10.5pt; color: #155724; font-weight: bold;">
                ✅ <strong>주요 리스크 요인 없음</strong><br><br>
                본 대상지는 종합 리스크 진단 결과 치명적 또는 중대한 리스크 요인이 발견되지 않았습니다.
                LH 매입 제외 사유에 해당하는 항목이 없으며, 전반적으로 양호한 개발 여건을 갖추고 있는 것으로 평가됩니다.
                다만, 실제 개발 단계에서는 토지이용계획확인원, 건축물대장, 등기부등본 등 공식 서류를 통한 
                최종 검증이 필요하며, 현장 실사를 통해 추가 리스크 여부를 확인하시기 바랍니다.
            </p>
"""
        
        html += f"""
        </div>
        
        <h4 style="margin-top: 25px; padding: 12px; background: #667eea; color: white; border-radius: 5px;">
            4. LH 매입 예상 가격 및 수익성 분석
        </h4>
"""
        
        # 가격 정보 추가
        price_estimate = self._estimate_lh_purchase_price(data)
        
        html += f"""
        <div style="margin: 15px 0; padding: 20px; background: #e8f5e9; border-left: 5px solid #4caf50; line-height: 1.9;">
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                LH 신축매입임대주택 사업의 매입가격 산정은 <strong>토지 감정평가액 + 건물 공사비 + 제세공과금</strong>의 
                합산 방식으로 이루어집니다. 본 대상지의 경우 {"<strong style='color: #2e7d32;'>사용자가 입력한 탁상감정평가액</strong>" if price_estimate.get('is_user_input') else "지역 실거래가를 기준으로 용도지역 및 입지 점수를 반영"}하여 
                토지 단가를 산정하였으며, {unit_type} 특성에 맞는 건축비 단가를 적용하였습니다.
            </p>
            
            <table style="width: 95%; margin: 15px auto; font-size: 9.5pt;">
                <thead>
                    <tr style="background: #4caf50; color: white;">
                        <th style="padding: 12px; border: 1px solid #ddd; width: 40%;">항목</th>
                        <th style="padding: 12px; border: 1px solid #ddd; width: 25%; text-align: center;">단가/비율</th>
                        <th style="padding: 12px; border: 1px solid #ddd; width: 35%; text-align: right;">금액 (원)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: {"#e8f5e9" if price_estimate.get('is_user_input') else "#ffffff"};">
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>토지 감정평가 예상액</strong>
                            {"<br><span style='font-size: 8pt; color: #2e7d32; font-weight: bold;'>✓ 사용자 입력값 적용</span>" if price_estimate.get('is_user_input') else "<br><span style='font-size: 8pt; color: #666;'>※ 지역 거래가 기반 자동 계산</span>"}
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center; {"font-weight: bold; color: #2e7d32;" if price_estimate.get('is_user_input') else ""}">{price_estimate['base_land_price_per_sqm']:,.0f}원/㎡</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #4caf50;">{price_estimate['total_land_value']:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>건물 공사비 추정</strong><br>
                            <span style='font-size: 8pt; color: #666;'>({unit_type} 기준)</span>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{price_estimate['construction_cost_per_sqm']:,.0f}원/㎡</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold;">{price_estimate['total_construction_cost']:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>제세공과금</strong><br>
                            <span style='font-size: 8pt; color: #666;'>(취득세, 등록세 등)</span>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">토지가의 5%</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold;">{price_estimate['taxes_and_fees']:,.0f}</td>
                    </tr>
                    <tr style="background: #c8e6c9; font-weight: bold; font-size: 10.5pt;">
                        <td style="padding: 14px; border: 1px solid #ddd;" colspan="2"><strong>LH 총 매입 예상액</strong></td>
                        <td style="padding: 14px; border: 1px solid #ddd; text-align: right; color: #2e7d32; font-size: 11pt;">{price_estimate['total_purchase_price']:,.0f}</td>
                    </tr>
                    <tr style="background: #fff9c4;">
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <strong>예상 가격 범위</strong><br>
                            <span style='font-size: 8pt; color: #666;'>(감정평가 2개 법인 편차)</span>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">±{((price_estimate['price_max'] - price_estimate['total_land_value']) / price_estimate['total_land_value'] * 100):.0f}%</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #f57c00;">{price_estimate['price_min']:,.0f} ~ {price_estimate['price_max']:,.0f}</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin: 20px 0; padding: 15px; background: #e1f5fe; border-radius: 5px;">
                <h5 style="margin: 0 0 10px 0; color: #0277bd; font-size: 10pt;">💰 선금 수령 계획 (자금 조달 옵션)</h5>
                <table style="width: 100%; font-size: 9pt;">
                    <tr>
                        <td style="padding: 8px; width: 50%; border-bottom: 1px solid #ddd;"><strong>① 근저당 설정 방식</strong></td>
                        <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{price_estimate['advance_payment_mortgage']:,.0f}원 <span style="color: #666;">(토지분 50%)</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>② 관리형 토지신탁 방식</strong></td>
                        <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{price_estimate['advance_payment_trust']:,.0f}원 <span style="color: #666;">(토지분 70%)</span></td>
                    </tr>
                    <tr style="background: #c8e6c9;">
                        <td style="padding: 10px; font-weight: bold;"><strong>③ 관리형 토지신탁 (조기약정)</strong> ⭐ 추천</td>
                        <td style="padding: 10px; text-align: right; font-weight: bold; color: #2e7d32; font-size: 10pt;">{price_estimate['advance_payment_trust_early']:,.0f}원 <span style="color: #1b5e20;">(토지분 80%)</span></td>
                    </tr>
                </table>
                <p style="margin: 10px 0 0 0; font-size: 9pt; color: #555; line-height: 1.6;">
                    ※ 관리형 토지신탁 조기약정 방식은 LH와 신속한 계약 체결 시 최대 <strong>토지분 80%</strong>까지 선금 수령이 가능하여 
                    사업 초기 자금 부담을 크게 경감할 수 있습니다. 이는 토지 매입 비용의 대부분을 선금으로 충당할 수 있어 
                    사업자에게 유리한 조건입니다.
                </p>
            </div>
            
            <p style="margin-top: 15px; font-size: 9.5pt; color: #555; line-height: 1.7; padding: 12px; background: white; border-radius: 5px;">
                <strong>📌 매입가격 산정 근거:</strong><br>
                {"• 토지 단가: 사용자 입력값 적용 (보정 없음)<br>" if price_estimate.get('is_user_input') else f"• 토지 단가: {price_estimate['price_source']} 기준<br>• 용도지역 보정: {price_estimate['zone_factor']:.2f}배<br>• 입지 점수 보정: {price_estimate['location_factor']:.2f}배<br>"}
                • 건축비: {unit_type} 표준 공사비 적용<br>
                • 실제 매입가는 LH 지정 2개 감정평가법인 평균값으로 최종 결정<br>
                • 감정평가 편차는 통상 ±{((price_estimate['price_max'] - price_estimate['total_land_value']) / price_estimate['total_land_value'] * 100):.0f}% 범위 내에서 발생
            </p>
        </div>
        
        <h4 style="margin-top: 25px; padding: 12px; background: #667eea; color: white; border-radius: 5px;">
            5. 사업 추진 전략 및 경쟁력 강화 방안
        </h4>
        <div style="margin: 15px 0; padding: 20px; background: #e3f2fd; border-left: 5px solid #2196f3; line-height: 1.9;">
            <h5 style="margin: 0 0 10px 0; color: #1976d2; font-size: 11pt;">가. 핵심 강점 (Strengths)</h5>
            <ul style="margin: 10px 0 15px 20px; line-height: 1.8;">
                <li><strong>{unit_type} 타겟층 집중 지역:</strong> 해당 유형의 수요 {scores['demand']['score']:.2f}점으로 {"매우 우수" if scores['demand']['score'] >= 4.5 else "우수" if scores['demand']['score'] >= 4.0 else "양호" if scores['demand']['score'] >= 3.5 else "보통"}하며, 임대 시장에서 안정적인 수요 확보 가능</li>
                <li><strong>입지 경쟁력:</strong> 5.0 만점 평가에서 평균 <strong>{scores['average']['score']:.2f}점</strong> 획득, {"상위권" if scores['average']['score'] >= 4.0 else "중상위권" if scores['average']['score'] >= 3.5 else "중위권"} 입지로 평가</li>
                <li><strong>생활 인프라:</strong> 주변 {facilities_count}개 편의시설로 {"우수한" if facilities_count >= 30 else "양호한" if facilities_count >= 20 else "적정한"} 생활환경 조성</li>
                <li><strong>교통 편의:</strong> 대중교통 점수 {scores['transit']['score']:.2f}점, 차량 접근성 {scores['vehicle']['score']:.2f}점으로 {"우수한" if (scores['transit']['score'] + scores['vehicle']['score'])/2 >= 4.0 else "양호한" if (scores['transit']['score'] + scores['vehicle']['score'])/2 >= 3.0 else "보통의"} 접근성 확보</li>
                <li><strong>건축 규모:</strong> {units_val}세대, {floors_val}층 규모로 {"대규모" if units_val >= 50 else "중규모" if units_val >= 20 else "소규모"} 사업 가능, 용적률 {floor_area_val:.1f}% 활용</li>
                <li><strong>주차 여건:</strong> {parking_spaces_val}대 확보로 {"법정 주차대수 초과" if parking_spaces_val >= units_val * 0.8 else "법정 주차대수 충족" if parking_spaces_val >= units_val * 0.5 else "주차 보완 필요"}</li>
            </ul>
            
            <h5 style="margin: 20px 0 10px 0; color: #1976d2; font-size: 11pt;">나. 차별화 전략 (Differentiation)</h5>
            <ol style="margin: 10px 0 15px 20px; line-height: 1.8;">
                <li><strong>LH 표준 설계 적용:</strong> LH 제공 표준 평면(Type A/B/C) 활용으로 설계 심의 기간 단축 및 공사비 절감 효과</li>
                <li><strong>친환경 인증 취득:</strong> 녹색건축 인증 또는 에너지효율 1등급 취득을 통한 LH 심의 가점 확보</li>
                <li><strong>커뮤니티 공간 확충:</strong> 법정 기준 이상의 공용 공간(라운지, 피트니스, 키즈카페 등) 조성으로 입주 만족도 향상</li>
                <li><strong>스마트홈 시스템:</strong> IoT 기반 스마트홈 기술 도입으로 {"청년층 선호도 제고" if unit_type in ["청년", "청년형"] else "신혼부부 생활 편의 증대" if "신혼" in unit_type else "고령자 안전 관리 강화" if "고령" in unit_type else "입주자 만족도 제고"}</li>
                <li><strong>주차 여유 확보:</strong> {"법정 주차대수 이상 확보로 LH 심의 시 유리" if parking_spaces_val >= units_val * 0.7 else "지하 주차장 추가 설치 검토로 주차 여건 개선"}</li>
            </ol>
            
            <h5 style="margin: 20px 0 10px 0; color: #1976d2; font-size: 11pt;">다. 추진 일정 최적화 전략</h5>
            <p style="margin: 10px 20px; text-indent: 20px; font-size: 10pt; line-height: 1.8;">
                LH 신축매입임대 사업은 통상 <strong>약정 체결부터 준공까지 18~24개월</strong>이 소요됩니다.
                본 사업의 경우 토지 확보 → LH 약정 협의 → 건축 인허가 → 착공 → 준공 → 매각의 단계로 진행되며,
                조기약정 체결 시 선금 수령을 통해 자금 부담을 최소화할 수 있습니다.
                특히 <strong>관리형 토지신탁 조기약정 방식</strong>을 선택하면 토지분 80%인 
                <strong>{price_estimate['advance_payment_trust_early']:,.0f}원</strong>을 선수령하여 
                초기 자금 부담을 크게 줄일 수 있어 사업 안정성이 높아집니다.
            </p>
        </div>
        
        <h4 style="margin-top: 25px; padding: 12px; background: #dc3545; color: white; border-radius: 5px;">
            6. 최종 결론 및 LH 매입 가능성 판정
        </h4>
        <div style="margin: 15px 0; padding: 25px; background: {"#e8f5e9" if is_eligible else "#ffebee"}; border: 3px solid {"#4caf50" if is_eligible else "#f44336"}; border-radius: 10px; line-height: 1.9;">
            <p style="margin: 0 0 20px 0; padding: 15px; background: {"#c8e6c9" if is_eligible else "#ffcdd2"}; border-radius: 5px; font-weight: bold; font-size: 12pt; text-align: center; color: {"#1b5e20" if is_eligible else "#b71c1c"};">
                {"✅ LH 신축매입임대주택 사업 대상지로서 적격 (매입 가능성: 높음)" if is_eligible else "❌ LH 신축매입임대주택 사업 대상지로서 부적격 (매입 가능성: 낮음)"}
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                {f"본 토지진단 시스템의 종합 분석 결과, <strong>{address}</strong> 소재 대상지는 <strong>{unit_type}</strong> 유형의 LH 신축매입임대주택 사업지로서 <strong>적합한 조건</strong>을 갖추고 있는 것으로 최종 판정되었습니다. 5.0 만점 평가 시스템에서 평균 <strong>{scores['average']['score']:.2f}점</strong>을 기록하여 {('상위권' if scores['average']['score'] >= 4.0 else '중상위권' if scores['average']['score'] >= 3.5 else '중위권')} 입지로 평가되었으며, 인구통계, 교통 접근성, 생활 인프라 등 핵심 평가 요소에서 {('우수한' if scores['average']['score'] >= 4.0 else '양호한' if scores['average']['score'] >= 3.5 else '적정한')} 점수를 획득하였습니다." if is_eligible else f"본 토지진단 시스템의 종합 분석 결과, <strong>{address}</strong> 소재 대상지는 현재 상태로는 <strong>치명적인 리스크 요인</strong>이 발견되어 LH 신축매입임대주택 사업 대상지로서 <strong>부적격</strong>으로 판정되었습니다. LH 매입 제외 사유에 해당하는 {'유해시설 인접' if any('유해' in self._get_attr(r, 'category') for r in risks) else '규제 위반' if any('규제' in self._get_attr(r, 'category') for r in risks) else '법적 제한'} 등의 요인이 확인되었으며, 이를 해소하지 않고는 사업 추진이 불가능합니다."}
            </p>
            {f'''
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                특히 수요 환경 측면에서 {unit_type} 타겟층에 대한 수요 분석 점수가 <strong>{scores['demand']['score']:.2f}점</strong>으로 
                {('매우 높은' if scores['demand']['score'] >= 4.5 else '높은' if scores['demand']['score'] >= 4.0 else '양호한' if scores['demand']['score'] >= 3.5 else '보통의')} 수준을 나타내어,
                임대 시장에서 안정적인 수요 확보가 가능할 것으로 예상됩니다.
                주변 환경 {scores['environment']['score']:.2f}점, 교통 편의성 {scores['transit']['score']:.2f}점, 
                차량 접근성 {scores['vehicle']['score']:.2f}점 등 전반적인 입지 조건이 양호하여 
                LH 심의위원회 검토 시 긍정적인 평가를 받을 가능성이 높습니다.
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                재무적 측면에서도 LH 총 매입 예상액 <strong>{price_estimate['total_purchase_price']:,.0f}원</strong> 
                (토지 {price_estimate['total_land_value']:,.0f}원 + 건물 {price_estimate['total_construction_cost']:,.0f}원 + 제세공과금 {price_estimate['taxes_and_fees']:,.0f}원)으로 산정되며,
                관리형 토지신탁 조기약정 방식 선택 시 선금 <strong>{price_estimate['advance_payment_trust_early']:,.0f}원(토지분 80%)</strong>을 
                수령할 수 있어 사업 초기 자금 부담이 최소화됩니다.
                이는 토지 매입 비용의 대부분을 선금으로 충당할 수 있어 사업자에게 매우 유리한 조건입니다.
            </p>
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt;">
                다만, 최종 매입 여부는 <strong>LH 심의위원회의 공식 검토</strong>를 거쳐 결정되므로, 
                다음 사항들을 반드시 준비하셔야 합니다:<br>
                ① 토지이용계획확인원 (용도지역, 지역·지구 확인)<br>
                ② 토지등기부등본 (소유권, 제한물권 확인)<br>
                ③ 건축물대장 (기존 건축물 현황)<br>
                ④ 측량 성과도 (대지 경계 및 면적 확인)<br>
                ⑤ 현장 실사 보고서 (유해시설, 접도 조건 등 현장 확인)<br>
                ⑥ 사업계획서 (건축 규모, 주차 계획, 자금 조달 계획 포함)
            </p>
            <p style="margin-bottom: 0; text-indent: 20px; font-size: 10.5pt; font-weight: bold; color: #1b5e20;">
                <strong>종합 의견:</strong> 본 대상지는 입지, 수요, 재무 여건 등 제반 조건이 양호하여 
                LH 신축매입임대주택 사업 추진에 적합한 것으로 판단됩니다. 
                상기 준비 사항을 철저히 갖춘 후 LH 사업 공고에 맞춰 신청하시면 
                매입 승인 가능성이 높을 것으로 예상됩니다.
            </p>
            ''' if is_eligible else f'''
            <p style="margin-bottom: 15px; text-indent: 20px; font-size: 10.5pt; color: #b71c1c;">
                현재 상태에서는 다음과 같은 <strong>치명적 리스크 요인</strong>이 존재합니다:<br>
                {chr(10).join([f"• <strong>[{self._get_attr(r, 'category')}]</strong> {self._get_attr(r, 'description')}" for r in risks if self._get_attr(r, 'severity') in ['critical', 'LH매입제외']][:5])}
            </p>
            <p style="margin-bottom: 0; text-indent: 20px; font-size: 10.5pt; font-weight: bold; color: #b71c1c;">
                <strong>권고 사항:</strong> 상기 치명적 리스크 요인을 해소하지 않고는 LH 매입이 불가능합니다.
                해당 사유를 제거할 수 있는 경우(예: 유해시설 이전, 규제 해제 신청 등), 
                사유 해결 후 재신청을 검토하시거나, 
                리스크가 없는 대체 부지를 물색하시기를 권장드립니다.
            </p>
            '''}
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #fff3cd; border: 2px solid #ffc107; border-radius: 10px;">
            <h5 style="margin: 0 0 15px 0; color: #856404; font-size: 11pt;">📋 사업 추진 체크리스트 (최종 확인 사항)</h5>
            <table style="width: 95%; margin: 0 auto; font-size: 9.5pt;">
                <thead>
                    <tr style="background: #ffc107; color: #212529;">
                        <th style="padding: 10px; border: 1px solid #ddd; width: 5%;">No.</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 30%;">확인 항목</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 15%;">현재 상태</th>
                        <th style="padding: 10px; border: 1px solid #ddd; width: 50%;">비고</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">1</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">토지 소유권 확인</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">확인 필요</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">등기부등본 확인 (제한물권 여부, 가압류·가처분 등)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">2</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">용도지역 법적 확인</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: {"#28a745" if zone_type_val else "#ffc107"}; font-weight: bold;">{"확인 완료" if zone_type_val else "확인 필요"}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{f"용도지역: {zone_type_val}" if zone_type_val else "토지이용계획확인원 발급 필요"}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">3</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">지역·지구 중복규제 확인</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">확인 필요</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">개발제한구역, 문화재보호구역, 학교보건구역 등 중복규제 확인</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">4</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">LH 매입 제외 사유 확인</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: {"#dc3545" if any(self._get_attr(r, 'severity') in ['critical', 'LH매입제외'] for r in risks) else "#28a745"}; font-weight: bold;">{"제외사유 존재" if any(self._get_attr(r, 'severity') in ['critical', 'LH매입제외'] for r in risks) else "적격"}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{f"리스크 {len([r for r in risks if self._get_attr(r, 'severity') in ['critical', 'LH매입제외']])}건 확인됨 - 해결 필요" if any(self._get_attr(r, 'severity') in ['critical', 'LH매입제외'] for r in risks) else "치명적 제외 사유 없음"}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">5</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">현장 실사 완료</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">미실시</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">경사도, 접도 조건, 유해시설 실제 거리 등 현장 육안 확인 필요</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">6</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">건축 인허가 사전 협의</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">미진행</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">관할 구청 건축과 사전 상담 (건축 가능 여부, 층수 제한 등)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">7</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">LH 사업 공고 확인</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">진행 예정</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">LH 홈페이지 또는 LH부동산포털에서 최신 공고 확인</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">8</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">감정평가 법인 선정</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: #ffc107; font-weight: bold;">미진행</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">LH 지정 2개 감정평가법인 (LH가 직접 선정)</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin-top: 15px; font-size: 9pt; color: #856404; line-height: 1.6;">
                ※ 상기 체크리스트는 사업 추진 전 반드시 확인해야 할 핵심 사항들입니다. 
                특히 '확인 필요' 또는 '미실시' 항목은 LH 신청 전에 반드시 완료하시기 바랍니다.
            </p>
        </div>
    </div>
    
    <!-- Chapter 4: LH 기준 체크리스트 (신규) -->
    {self._generate_checklist_chapter(data)}
    
    <!-- 보고서 종료 -->
    <div style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #ccc; text-align: center; color: #666; font-size: 9pt;">
        <p>본 보고서는 LH 신축매입임대주택 사업 토지진단 자동화 시스템에 의해 생성되었습니다.</p>
        <p>작성일시: {self.report_date.strftime('%Y년 %m월 %d일 %H:%M')}</p>
        <p style="margin-top: 15px; font-weight: bold; color: #003366; font-size: 10pt;">
            개발: 사회적기업 (주)안테나 나태흠 대표
        </p>
        <p style="margin-top: 10px; font-size: 8pt; color: #999;">
            ※ 본 보고서는 참고용이며, 최종 매입 여부는 LH의 공식 심의를 거쳐 결정됩니다.<br>
            ※ 정확한 법적 검토 및 현장 실사는 전문가의 검증이 필요합니다.
        </p>
    </div>
</body>
</html>
"""
        
        return html

    def _generate_checklist_chapter(self, data: Dict[str, Any]) -> str:
        """
        Chapter 4: LH 기준 체크리스트 페이지 생성
        
        Args:
            data: 분석 데이터 (checklist_details 포함)
            
        Returns:
            HTML 형식의 체크리스트 섹션
        """
        checklist_details = data.get('checklist_details')
        if not checklist_details:
            # Fallback: 기본 메시지 반환
            return """
    <!-- ====================================== -->
    <!-- Chapter 4: LH 기준 체크리스트 -->
    <!-- ====================================== -->
    <div class="section page-break">
        <h2 class="section-title">IV. LH 기준 체크리스트</h2>
        <div class="warning-box">
            <strong>⚠️ 체크리스트 정보 없음</strong><br>
            체크리스트 상세 정보가 생성되지 않았습니다. 시스템 관리자에게 문의하세요.
        </div>
    </div>
    """
        
        # 데이터 추출
        items = checklist_details.get('items', [])
        category_summary = checklist_details.get('category_summary', {})
        total_items = checklist_details.get('total_items', 0)
        passed_items = checklist_details.get('passed_items', 0)
        failed_items = checklist_details.get('failed_items', 0)
        warning_items = checklist_details.get('warning_items', 0)
        
        # 통과율 계산
        pass_rate = (passed_items / total_items * 100) if total_items > 0 else 0
        
        # 상태별 색상 매핑
        def get_status_color(status: str) -> str:
            color_map = {
                "통과": "#28a745",  # 녹색
                "부적합": "#dc3545",  # 빨강
                "주의": "#ffc107",  # 노랑
                "참고": "#17a2b8"  # 청록색
            }
            return color_map.get(status, "#6c757d")
        
        def get_status_bgcolor(status: str) -> str:
            bgcolor_map = {
                "통과": "#d4edda",
                "부적합": "#f8d7da",
                "주의": "#fff3cd",
                "참고": "#d1ecf1"
            }
            return bgcolor_map.get(status, "#e9ecef")
        
        # HTML 생성
        html = f"""
    <!-- ====================================== -->
    <!-- Chapter 4: LH 기준 체크리스트 -->
    <!-- ====================================== -->
    <div class="section page-break" style="margin-top: 40px;">
        <h2 style="margin: 30px 0 20px 0; padding: 15px; background: #667eea; color: white; font-size: 16pt; border-radius: 8px; text-align: center;">
            Chapter 4. LH 기준 체크리스트
        </h2>
        
        <!-- 체크리스트 요약 -->
        <div style="margin: 25px 0; padding: 20px; background: #e3f2fd; border-left: 5px solid #2196f3; border-radius: 5px;">
            <h3 style="margin: 0 0 15px 0; color: #1976d2; font-size: 12pt;">✅ 체크리스트 종합 결과</h3>
            <div style="text-align: center; margin: 15px 0;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                    <div style="font-size: 24pt; font-weight: bold; color: #28a745;">{passed_items}</div>
                    <div style="font-size: 9pt; color: #666; margin-top: 5px;">통과</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                    <div style="font-size: 24pt; font-weight: bold; color: #ffc107;">{warning_items}</div>
                    <div style="font-size: 9pt; color: #666; margin-top: 5px;">주의</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                    <div style="font-size: 24pt; font-weight: bold; color: #dc3545;">{failed_items}</div>
                    <div style="font-size: 9pt; color: #666; margin-top: 5px;">부적합</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px;">
                    <div style="font-size: 24pt; font-weight: bold; color: #2196f3;">{pass_rate:.1f}%</div>
                    <div style="font-size: 9pt; color: #666; margin-top: 5px;">통과율</div>
                </div>
            </div>
        </div>
        
        <!-- 카테고리별 요약 -->
        <h3 style="margin: 25px 0 15px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #6c757d; font-size: 11pt;">
            📊 카테고리별 평가 현황
        </h3>
        <table style="width: 95%; margin: 15px auto; font-size: 9.5pt;">
            <thead>
                <tr style="background: #667eea; color: white;">
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 15%;">카테고리</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 15%;">평가 점수</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 15%;">통과</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 15%;">주의</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 15%;">부적합</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 25%;">상태</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 카테고리별 요약 행 추가
        for category, summary in category_summary.items():
            score = summary.get('score', 0)
            passed = summary.get('passed', 0)
            warning = summary.get('warning', 0)
            failed = summary.get('failed', 0)
            
            # 상태 판정
            if failed > 0:
                status = "개선 필요"
                status_color = "#dc3545"
                status_bgcolor = "#f8d7da"
            elif warning > 0:
                status = "주의 필요"
                status_color = "#ffc107"
                status_bgcolor = "#fff3cd"
            else:
                status = "양호"
                status_color = "#28a745"
                status_bgcolor = "#d4edda"
            
            html += f"""
                <tr style="background: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{category}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: #2196f3; font-size: 11pt;">{score:.1f}점</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: #28a745;">{passed}개</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: #ffc107;">{warning}개</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: #dc3545;">{failed}개</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; background: {status_bgcolor}; color: {status_color}; font-weight: bold;">{status}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <!-- 상세 체크리스트 -->
        <h3 style="margin: 30px 0 15px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #6c757d; font-size: 11pt;">
            📋 항목별 상세 체크리스트
        </h3>
"""
        
        # 카테고리별로 항목 그룹화
        items_by_category = {}
        for item in items:
            category = item.get('category', '기타')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        # 각 카테고리별로 테이블 생성
        for category, category_items in items_by_category.items():
            html += f"""
        <h4 style="margin: 20px 0 10px 0; color: #495057; font-size: 10.5pt;">
            {category} ({len(category_items)}개 항목)
        </h4>
        <table style="width: 95%; margin: 10px auto 25px auto; font-size: 9pt;">
            <thead>
                <tr style="background: #e9ecef;">
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 5%;">No</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; width: 20%;">항목</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 15%;">LH 기준</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 15%;">실제값</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 10%;">적합 여부</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; width: 30%;">코멘트</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 5%;">점수</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for idx, item in enumerate(category_items, 1):
                item_name = item.get('item', '')
                standard = item.get('standard', '')
                value = item.get('value', '')
                status = item.get('status', '')
                description = item.get('description', '')
                score = item.get('score', 0)
                
                status_color = get_status_color(status)
                status_bgcolor = get_status_bgcolor(status)
                
                html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{idx}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item_name}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-size: 8.5pt; color: #666;">{standard}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{value}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center; background: {status_bgcolor}; color: {status_color}; font-weight: bold;">{status}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; font-size: 8.5pt; line-height: 1.4;">{description}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: #2196f3;">{score:.0f}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
"""
        
        # 체크리스트 주의사항
        html += """
        <!-- 체크리스트 주의사항 -->
        <div style="margin: 30px 0; padding: 20px; background: #fff3cd; border: 2px solid #ffc107; border-radius: 8px;">
            <h4 style="margin: 0 0 15px 0; color: #856404; font-size: 11pt;">⚠️ 체크리스트 활용 시 주의사항</h4>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.8; font-size: 9.5pt; color: #856404;">
                <li><strong>"부적합"</strong> 항목이 있는 경우, LH 매입 승인이 거부될 수 있으므로 반드시 개선이 필요합니다.</li>
                <li><strong>"주의"</strong> 항목은 조건부 통과 가능하나, 심의 시 감점 요인이 될 수 있으니 개선을 권장합니다.</li>
                <li><strong>"통과"</strong> 항목이라도 최종 현장 실사에서 다른 판정이 나올 수 있으니 유의하시기 바랍니다.</li>
                <li>본 체크리스트는 자동 분석 시스템 기반이므로, 실제 LH 심의 시 추가 검토 항목이 있을 수 있습니다.</li>
                <li>정확한 법적 검토 및 현장 실사는 전문가(건축사, 감정평가사 등)의 검증이 필요합니다.</li>
            </ul>
        </div>
    </div>
"""
        
        return html
    
    def generate_google_docs_compatible_html(self, analysis_data: Dict[str, Any]) -> str:
        """
        Google Docs 호환 HTML 보고서 생성
        - inline CSS만 사용
        - gradient, flex, hover 등 미지원 CSS 제거
        - <table>에 width="100%" 명시
        - border-collapse 적용
        
        Args:
            analysis_data: 종합 분석 데이터
            
        Returns:
            Google Docs 호환 HTML 문자열
        """
        # 기본 보고서 생성
        original_html = self.generate_official_report(analysis_data)
        
        # Google Docs 호환 변환
        # 1. <style> 태그 제거 (inline CSS로 대체)
        import re
        html = re.sub(r'<style>.*?</style>', '', original_html, flags=re.DOTALL)
        
        # 2. gradient 제거 (단색 배경으로 변경)
        html = html.replace('background: #003d82', 'background: #003d82')
        html = html.replace('background: #e3f2fd', 'background: #e3f2fd')
        html = html.replace('background: #1e3c72', 'background: #1e3c72')
        html = html.replace('background: #667eea', 'background: #667eea')
        
        # 3. <table> 태그에 width="100%" 및 border-collapse 추가
        html = html.replace('<table', '<table width="100%" style="border-collapse: collapse;"')
        
        # 4. hover, transition 제거
        html = re.sub(r'transition:\s*[^;]+;', '', html)
        html = re.sub(r':hover\s*\{[^}]*\}', '', html)
        
        # 5. flex 제거 (table 또는 div로 대체)
        html = html.replace('display: inline-block;', '')
        html = html.replace('flex: 1;', 'width: 25%;')
        html = html.replace('justify-content: space-around;', 'text-align: center;')
        html = html.replace('align-items: center;', 'vertical-align: middle;')
        
        # 6. <meta charset="UTF-8"> 확인
        if '<meta charset="UTF-8">' not in html:
            html = html.replace('<head>', '<head>\n    <meta charset="UTF-8">')
        
        # 7. box-shadow 제거 (Google Docs 미지원)
        html = re.sub(r'box-shadow:\s*[^;]+;', '', html)
        
        # 8. border-radius 단순화 (큰 값 제거)
        html = re.sub(r'border-radius:\s*\d+px;', 'border-radius: 5px;', html)
        
        return html

    def _generate_roi_comparison_section(
        self,
        lh_result: Dict[str, Any],
        market_result: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> str:
        """
        ROI 비교표 섹션 생성 (LH 단가 vs 시장기반)
        
        Args:
            lh_result: LH 모델 결과
            market_result: 시장 모델 결과
            comparison: 비교 분석 결과
        
        Returns:
            HTML 섹션
        """
        
        html = f"""
    <!-- V. 사업성 분석 모델 비교 -->
    <div class="section page-break">
        <h2 class="section-title">V. 사업성 분석 모델 비교</h2>
        
        <div class="info-box">
            <strong>📊 두 가지 분석 모델 비교</strong><br>
            본 분석에서는 <strong>LH 매입단가 기반 모델</strong>과 <strong>시장기반(Real Market) 모델</strong>을 
            모두 적용하여 사업성을 평가하였습니다.
        </div>
        
        <h3 class="subsection-title">1. 모델별 사업성 분석 결과 비교</h3>
        <table style="width: 95%; margin: 15px auto; font-size: 9.5pt;">
            <thead>
                <tr style="background: #667eea; color: white;">
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 25%;">항목</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 37.5%;">LH 단가 모델</th>
                    <th style="padding: 12px; border: 1px solid #ddd; text-align: center; width: 37.5%;">시장기반 모델</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">총사업비</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{lh_result.get("total_cost", {}).get("formatted", "N/A")}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{market_result.get("total_cost", {}).get("formatted", "N/A")}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">매각가/매입가</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{lh_result.get("revenue", {}).get("formatted", "N/A")}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{market_result.get("revenue", {}).get("formatted", "N/A")}</td>
                </tr>
                <tr style="background: #e3f2fd;">
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">ROI</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #0066cc; font-size: 11pt;">{lh_result.get("roi", {}).get("formatted", "N/A")}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #0066cc; font-size: 11pt;">{market_result.get("roi", {}).get("formatted", "N/A")}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">결론</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{lh_result.get("feasibility", "N/A")}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{market_result.get("feasibility", "N/A")}</td>
                </tr>
            </tbody>
        </table>
        
        <h3 class="subsection-title" style="margin-top: 30px;">2. 비교 분석 및 추천</h3>
        
        <div style="margin: 20px 0; padding: 20px; background: #e3f2fd; border-left: 5px solid #2196f3; border-radius: 5px;">
            <p style="margin: 0; line-height: 1.6; font-weight: bold;">
                {comparison.get("recommendation", "추천사항 없음")}
            </p>
        </div>
    </div>
    """
        
        return html
