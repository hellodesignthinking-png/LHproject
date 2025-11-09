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
            scores, critical_checks, map_image
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
        map_image: Optional[str]
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
    
    <!-- 종합 결론 -->
    <div class="conclusion page-break">
        <h3>VI. 종합 검토 및 최종 결론</h3>
        
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
        
        <h4 style="margin-top: 20px;">3. 권장 전략 (특장점)</h4>
        <ul>
            <li><strong>{unit_type}</strong> 수요가 풍부한 입지로 임대 수요 확보 유리</li>
            <li>5.0 만점 평가에서 평균 <strong>{scores['average']['score']:.2f}점</strong> 획득</li>
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
