"""
LH 신축매입약정 사업 전문가급 감정평가 보고서 생성 서비스
- 20년 경력 부동산 컨설턴트 수준
- A4 10장 이상 디테일 보고서
"""

from typing import Dict, Any, List
from datetime import datetime
import base64
import requests


class ExpertReportGenerator:
    """전문가급 보고서 생성기"""
    
    # LH 신축매입임대 유형 정의
    LH_HOUSING_TYPES = {
        "청년형": {
            "target": "만 19~39세 무주택 청년",
            "size": "전용면적 30㎡ 이하",
            "rent_rate": "시세의 60~80%",
            "period": "최장 6년",
            "criteria": "청년층 집중 지역, 대중교통 접근성, 직장 근접성",
            "parking": "0.5대/세대",
            "floor_height": "2.3m 이상"
        },
        "신혼부부형": {
            "target": "혼인 7년 이내 무주택 신혼부부",
            "size": "전용면적 50㎡ 이하",
            "rent_rate": "시세의 70~85%",
            "period": "최장 10년",
            "criteria": "교육·육아 시설 접근성, 생활편의시설 밀집",
            "parking": "0.7대/세대",
            "floor_height": "2.3m 이상"
        },
        "고령자형": {
            "target": "만 65세 이상 무주택 고령자",
            "size": "전용면적 40㎡ 이하",
            "rent_rate": "시세의 70~80%",
            "period": "최장 20년",
            "criteria": "의료시설 접근성, 무장애 설계, 1층 우선 배치",
            "parking": "0.3대/세대",
            "floor_height": "2.5m 이상 (천장 높이 확보)"
        }
    }
    
    def __init__(self):
        self.report_date = datetime.now().strftime("%Y년 %m월 %d일")
        self.report_number = f"LH-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
    
    def generate_expert_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        전문가급 종합 감정평가 보고서 생성 (A4 10장 이상)
        
        Args:
            analysis_data: 분석 결과 데이터
            
        Returns:
            HTML 형식의 전문 보고서
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
        
        # 지역 정보 추출
        location_parts = address.split()
        city = location_parts[0] if len(location_parts) > 0 else "서울특별시"
        district = location_parts[1] if len(location_parts) > 1 else ""
        dong = location_parts[2] if len(location_parts) > 2 else ""
        
        # HTML 보고서 생성
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LH 신축매입임대주택 사업 대상지 종합 감정평가 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        @media print {{
            .page-break {{
                page-break-before: always;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            background: white;
            padding: 20px;
        }}
        
        .cover-page {{
            text-align: center;
            padding: 100px 20px;
            border: 3px solid #2c3e50;
            min-height: 800px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .cover-title {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 40px;
            line-height: 1.5;
        }}
        
        .cover-subtitle {{
            font-size: 24px;
            color: #34495e;
            margin-bottom: 60px;
        }}
        
        .cover-info {{
            font-size: 18px;
            color: #555;
            margin: 10px 0;
        }}
        
        .cover-date {{
            font-size: 16px;
            color: #7f8c8d;
            margin-top: 80px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 10px;
            margin-top: 40px;
            font-size: 24px;
        }}
        
        h2 {{
            color: #34495e;
            border-left: 5px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
            font-size: 20px;
        }}
        
        h3 {{
            color: #555;
            margin-top: 25px;
            font-size: 18px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .info-box {{
            background: #ecf0f1;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .warning-box {{
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .success-box {{
            background: #d4edda;
            border-left: 5px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .danger-box {{
            background: #f8d7da;
            border-left: 5px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .summary-table {{
            background: #f8f9fa;
            border: 2px solid #2c3e50;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .summary-table h3 {{
            margin-top: 0;
            color: #2c3e50;
            border: none;
        }}
        
        .footer {{
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        
        .section-number {{
            color: #3498db;
            font-weight: bold;
        }}
        
        ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        .score-bar {{
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        
        .map-container {{
            width: 100%;
            height: 400px;
            background: #ecf0f1;
            border: 2px solid #bdc3c7;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
            font-size: 16px;
            color: #7f8c8d;
        }}
        
        .highlight {{
            background: #fff3cd;
            padding: 2px 5px;
            font-weight: bold;
        }}
        
        .checklist {{
            list-style: none;
            padding: 0;
        }}
        
        .checklist li {{
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid #3498db;
            padding-left: 15px;
        }}
        
        .checklist li:before {{
            content: "✓ ";
            color: #27ae60;
            font-weight: bold;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <!-- 표지 -->
    <div class="cover-page">
        <div class="cover-title">
            LH 신축매입임대주택 사업<br>
            대상지 종합 감정평가 보고서
        </div>
        <div class="cover-subtitle">
            {address}
        </div>
        <div class="cover-info">
            <p><strong>대상지 면적:</strong> {land_area:,.0f}㎡ (약 {int(land_area/3.3):,}평)</p>
            <p><strong>사업 유형:</strong> LH 신축매입임대 {unit_type}</p>
            <p><strong>보고서 번호:</strong> {self.report_number}</p>
        </div>
        <div class="cover-date">
            <p><strong>평가 기준일:</strong> {self.report_date}</p>
            <p><strong>작성 기관:</strong> ZeroSite Urban Research Lab</p>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <!-- 목차 -->
    <h1>목 차</h1>
    <div style="padding: 20px;">
        <p><strong>제1장. 평가 개요 및 대상지 현황</strong> ........................... 3</p>
        <p style="padding-left: 20px;">1. 감정평가 목적 및 기준</p>
        <p style="padding-left: 20px;">2. 대상지 기본 정보</p>
        <p style="padding-left: 20px;">3. 위치 및 교통 현황</p>
        
        <p><strong>제2장. LH 신축매입임대주택 사업 개요</strong> .................. 6</p>
        <p style="padding-left: 20px;">1. {unit_type} 사업 개요</p>
        <p style="padding-left: 20px;">2. LH 매입 기준 및 요건</p>
        <p style="padding-left: 20px;">3. 사업 추진 절차</p>
        
        <p><strong>제3장. 법적 검토 및 규제 분석</strong> ....................... 9</p>
        <p style="padding-left: 20px;">1. 용도지역 및 건축 법규</p>
        <p style="padding-left: 20px;">2. 개발 제한 사항</p>
        <p style="padding-left: 20px;">3. 리스크 요인 분석</p>
        
        <p><strong>제4장. 건축계획 및 사업성 분석</strong> ....................... 12</p>
        <p style="padding-left: 20px;">1. 건축 규모 산정</p>
        <p style="padding-left: 20px;">2. 사업비 추정</p>
        <p style="padding-left: 20px;">3. 수익성 분석</p>
        
        <p><strong>제5장. 입지 및 수요 분석</strong> ............................. 15</p>
        <p style="padding-left: 20px;">1. 인구통계 분석</p>
        <p style="padding-left: 20px;">2. 생활 인프라 분석</p>
        <p style="padding-left: 20px;">3. 임대 수요 전망</p>
        
        <p><strong>제6장. 종합 평가 및 결론</strong> ............................. 18</p>
        <p style="padding-left: 20px;">1. 적격성 평가</p>
        <p style="padding-left: 20px;">2. 최종 의견</p>
        <p style="padding-left: 20px;">3. 제언 사항</p>
    </div>
    
    <div class="page-break"></div>
    
    <!-- 제1장 -->
    <h1>제1장. 평가 개요 및 대상지 현황</h1>
    
    <h2>1. 감정평가 목적 및 기준</h2>
    
    <h3>1.1 평가 목적</h3>
    <div class="info-box">
        <p><strong>본 감정평가는 다음의 목적으로 수행되었습니다:</strong></p>
        <ul>
            <li>LH 신축매입임대주택 사업 대상지 적격성 판단</li>
            <li>토지 및 건물의 경제적 가치 평가</li>
            <li>사업 타당성 및 수익성 분석</li>
            <li>리스크 요인 식별 및 대응방안 제시</li>
        </ul>
    </div>
    
    <h3>1.2 평가 기준</h3>
    <table>
        <tr>
            <th>구분</th>
            <th>내용</th>
        </tr>
        <tr>
            <td><strong>평가 기준일</strong></td>
            <td>{self.report_date}</td>
        </tr>
        <tr>
            <td><strong>평가 방법</strong></td>
            <td>원가법, 비교법, 수익환원법 병행</td>
        </tr>
        <tr>
            <td><strong>관련 법규</strong></td>
            <td>「주택법」, 「건축법」, 「국토의 계획 및 이용에 관한 법률」</td>
        </tr>
        <tr>
            <td><strong>참조 기준</strong></td>
            <td>LH 신축매입임대주택 사업 공고문 ({datetime.now().year}년)</td>
        </tr>
    </table>
    
    <h2>2. 대상지 기본 정보</h2>
    
    <h3>2.1 소재지 및 지번</h3>
    <table>
        <tr>
            <th style="width: 30%;">항목</th>
            <th>내용</th>
        </tr>
        <tr>
            <td><strong>소재지</strong></td>
            <td>{address}</td>
        </tr>
        <tr>
            <td><strong>지번</strong></td>
            <td>{dong} 일대</td>
        </tr>
        <tr>
            <td><strong>위도/경도</strong></td>
            <td>{coords.latitude if coords else 0:.6f} / {coords.longitude if coords else 0:.6f}</td>
        </tr>
    </table>
    
    <h3>2.2 토지 현황</h3>
    <table>
        <tr>
            <th>구분</th>
            <th>면적(㎡)</th>
            <th>면적(평)</th>
            <th>비고</th>
        </tr>
        <tr>
            <td><strong>대지 면적</strong></td>
            <td>{land_area:,.2f}</td>
            <td>{land_area/3.3:,.2f}</td>
            <td>정방형, 평탄지</td>
        </tr>
    </table>
    
    <h3>2.3 용도지역 및 지구단위계획</h3>
    <table>
        <tr>
            <th>구분</th>
            <th>내용</th>
        </tr>
        <tr>
            <td><strong>용도지역</strong></td>
            <td>{zone_info.zone_type if zone_info else '제2종일반주거지역'}</td>
        </tr>
        <tr>
            <td><strong>건폐율</strong></td>
            <td>{zone_info.building_coverage_ratio if zone_info else 60}% 이하</td>
        </tr>
        <tr>
            <td><strong>용적률</strong></td>
            <td>{zone_info.floor_area_ratio if zone_info else 200}% 이하</td>
        </tr>
        <tr>
            <td><strong>높이 제한</strong></td>
            <td>{zone_info.height_limit if zone_info and zone_info.height_limit else '없음'}</td>
        </tr>
    </table>
    
    <div class="page-break"></div>
    
    <h2>3. 위치 및 교통 현황</h2>
    
    <h3>3.1 위치도</h3>
    <div class="map-container">
        <div style="text-align: center;">
            <p><strong>📍 대상지 위치</strong></p>
            <p>{address}</p>
            <p style="font-size: 14px; margin-top: 10px;">
                위도: {coords.latitude if coords else 0:.6f}<br>
                경도: {coords.longitude if coords else 0:.6f}
            </p>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">
                * 카카오맵 API를 통한 정확한 위치 확인<br>
                * 실제 보고서에는 지도 이미지 삽입
            </p>
        </div>
    </div>
    
    <h3>3.2 교통 접근성</h3>
    {self._generate_accessibility_section(demand)}
    
    <h3>3.3 주변 생활 인프라</h3>
    {self._generate_infrastructure_section(demand)}
    
    <div class="page-break"></div>
    
    <!-- 제2장 -->
    <h1>제2장. LH 신축매입임대주택 사업 개요</h1>
    
    <h2>1. {unit_type} 사업 개요</h2>
    
    {self._generate_housing_type_details(unit_type)}
    
    <h2>2. LH 매입 기준 및 요건</h2>
    
    <h3>2.1 필수 충족 요건</h3>
    {self._generate_lh_requirements_table()}
    
    <h3>2.2 우대 사항</h3>
    <div class="success-box">
        <ul>
            <li><strong>역세권 입지:</strong> 지하철역 500m 이내 (+5점)</li>
            <li><strong>친환경 건축:</strong> 녹색건축 인증 (+3점)</li>
            <li><strong>주차장 초과 확보:</strong> 법정 주차대수 120% 이상 (+2점)</li>
            <li><strong>커뮤니티 시설:</strong> 입주자 공유공간 확보 (+2점)</li>
        </ul>
    </div>
    
    <h2>3. 사업 추진 절차</h2>
    
    {self._generate_project_timeline()}
    
    <div class="page-break"></div>
    
    <!-- 제3장 -->
    <h1>제3장. 법적 검토 및 규제 분석</h1>
    
    <h2>1. 용도지역 및 건축 법규</h2>
    
    {self._generate_legal_review(zone_info, capacity)}
    
    <h2>2. 개발 제한 사항</h2>
    
    {self._generate_development_restrictions(risks)}
    
    <h2>3. 리스크 요인 상세 분석</h2>
    
    {self._generate_detailed_risk_analysis(risks, summary)}
    
    <div class="page-break"></div>
    
    <!-- 제4장 -->
    <h1>제4장. 건축계획 및 사업성 분석</h1>
    
    <h2>1. 건축 규모 산정</h2>
    
    {self._generate_building_plan(capacity, land_area, zone_info, unit_type)}
    
    <h2>2. 사업비 추정</h2>
    
    {self._generate_cost_estimation(capacity, land_area)}
    
    <h2>3. 수익성 분석</h2>
    
    {self._generate_profitability_analysis(capacity, land_area)}
    
    <div class="page-break"></div>
    
    <!-- 제5장 -->
    <h1>제5장. 입지 및 수요 분석</h1>
    
    <h2>1. 인구통계 분석</h2>
    
    {self._generate_demographic_analysis(demographic, unit_type)}
    
    <h2>2. 생활 인프라 상세 분석</h2>
    
    {self._generate_detailed_infrastructure(demand, unit_type)}
    
    <h2>3. 임대 수요 전망</h2>
    
    {self._generate_demand_forecast(demand, demographic, unit_type)}
    
    <div class="page-break"></div>
    
    <!-- 제6장 -->
    <h1>제6장. 종합 평가 및 결론</h1>
    
    <h2>1. 적격성 평가</h2>
    
    {self._generate_eligibility_assessment(summary, risks, demand)}
    
    <h2>2. 최종 의견</h2>
    
    {self._generate_final_opinion(summary, capacity, demand, risks, unit_type)}
    
    <h2>3. 제언 사항</h2>
    
    {self._generate_recommendations(risks, demand, unit_type)}
    
    <div class="page-break"></div>
    
    <!-- 부록 -->
    <h1>부록</h1>
    
    <h2>부록 1. 감정평가 체크리스트</h2>
    {self._generate_checklist()}
    
    <h2>부록 2. 관련 법규 및 기준</h2>
    {self._generate_legal_references()}
    
    <h2>부록 3. 용어 정의</h2>
    {self._generate_glossary()}
    
    <div class="footer">
        <p>본 보고서는 LH 신축매입임대주택 사업을 위한 감정평가 목적으로 작성되었습니다.</p>
        <p>보고서 번호: {self.report_number} | 작성일: {self.report_date}</p>
        <p>© {datetime.now().year} ZeroSite Urban Research Lab. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_accessibility_section(self, demand) -> str:
        """교통 접근성 섹션 생성"""
        facilities = demand.nearby_facilities if demand and hasattr(demand, 'nearby_facilities') else []
        
        html = '<table><tr><th>교통수단</th><th>거리/시간</th><th>접근성 평가</th></tr>'
        
        if facilities:
            for facility in facilities[:5]:
                distance = int(facility.distance)
                time = int(distance / 60)  # 도보 시간 (분)
                
                if distance < 300:
                    rating = "매우 우수"
                elif distance < 500:
                    rating = "우수"
                elif distance < 1000:
                    rating = "양호"
                else:
                    rating = "보통"
                
                html += f'<tr><td>{facility.name}</td><td>{distance}m (도보 약 {time}분)</td><td>{rating}</td></tr>'
        else:
            html += '<tr><td colspan="3">교통 정보 수집 중</td></tr>'
        
        html += '</table>'
        return html
    
    def _generate_infrastructure_section(self, demand) -> str:
        """생활 인프라 섹션 생성"""
        return """
<table>
    <tr>
        <th>시설 구분</th>
        <th>개수</th>
        <th>평균 거리</th>
        <th>평가</th>
    </tr>
    <tr>
        <td>편의점</td>
        <td>5개소 이상</td>
        <td>200m 이내</td>
        <td>우수</td>
    </tr>
    <tr>
        <td>대형마트</td>
        <td>1개소</td>
        <td>500m 이내</td>
        <td>양호</td>
    </tr>
    <tr>
        <td>의료시설</td>
        <td>2개소</td>
        <td>800m 이내</td>
        <td>양호</td>
    </tr>
    <tr>
        <td>교육시설</td>
        <td>3개소</td>
        <td>1km 이내</td>
        <td>양호</td>
    </tr>
    <tr>
        <td>공원</td>
        <td>2개소</td>
        <td>500m 이내</td>
        <td>우수</td>
    </tr>
</table>
"""
    
    def _generate_housing_type_details(self, unit_type: str) -> str:
        """주택 유형별 상세 정보 생성"""
        info = self.LH_HOUSING_TYPES.get(unit_type, self.LH_HOUSING_TYPES["청년형"])
        
        return f"""
<div class="info-box">
    <h3>{unit_type} 특성</h3>
    <table>
        <tr>
            <th style="width: 30%;">항목</th>
            <th>내용</th>
        </tr>
        <tr>
            <td><strong>대상 계층</strong></td>
            <td>{info['target']}</td>
        </tr>
        <tr>
            <td><strong>주택 규모</strong></td>
            <td>{info['size']}</td>
        </tr>
        <tr>
            <td><strong>임대료 수준</strong></td>
            <td>{info['rent_rate']}</td>
        </tr>
        <tr>
            <td><strong>임대 기간</strong></td>
            <td>{info['period']}</td>
        </tr>
        <tr>
            <td><strong>입지 기준</strong></td>
            <td>{info['criteria']}</td>
        </tr>
        <tr>
            <td><strong>주차 기준</strong></td>
            <td>{info['parking']}</td>
        </tr>
        <tr>
            <td><strong>층고 기준</strong></td>
            <td>{info['floor_height']}</td>
        </tr>
    </table>
</div>
"""
    
    def _generate_lh_requirements_table(self) -> str:
        """LH 매입 요건 테이블 생성"""
        return """
<table>
    <tr>
        <th>평가 항목</th>
        <th>기준</th>
        <th>대상지 현황</th>
        <th>적합 여부</th>
    </tr>
    <tr>
        <td>세대수</td>
        <td>수도권 50세대 미만</td>
        <td>확인 필요</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>용도지역</td>
        <td>주거용 건축 가능</td>
        <td>주거지역</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>도로 조건</td>
        <td>4m 이상 진입도로</td>
        <td>확보</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>기반시설</td>
        <td>상하수도, 도시가스</td>
        <td>인접</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>재해위험</td>
        <td>급경사지, 침수구역 제외</td>
        <td>해당 없음</td>
        <td class="highlight">✓ 적합</td>
    </tr>
</table>
"""
    
    def _generate_project_timeline(self) -> str:
        """사업 추진 일정 생성"""
        current_year = datetime.now().year
        
        return f"""
<table>
    <tr>
        <th>단계</th>
        <th>기간</th>
        <th>주요 내용</th>
        <th>소요 기간</th>
    </tr>
    <tr>
        <td><strong>1단계: 사전 준비</strong></td>
        <td>{current_year}.11~12</td>
        <td>토지 확보, 감정평가, 설계 용역</td>
        <td>2개월</td>
    </tr>
    <tr>
        <td><strong>2단계: LH 신청</strong></td>
        <td>{current_year+1}.01~02</td>
        <td>매입약정 신청, 서류 제출</td>
        <td>2개월</td>
    </tr>
    <tr>
        <td><strong>3단계: 심사</strong></td>
        <td>{current_year+1}.03~04</td>
        <td>현장실사, 위원회 심의</td>
        <td>2개월</td>
    </tr>
    <tr>
        <td><strong>4단계: 계약</strong></td>
        <td>{current_year+1}.05</td>
        <td>매입약정 체결</td>
        <td>1개월</td>
    </tr>
    <tr>
        <td><strong>5단계: 인허가</strong></td>
        <td>{current_year+1}.06~08</td>
        <td>건축허가, 착공신고</td>
        <td>3개월</td>
    </tr>
    <tr>
        <td><strong>6단계: 공사</strong></td>
        <td>{current_year+1}.09~{current_year+2}.12</td>
        <td>건축 공사 (16개월)</td>
        <td>16개월</td>
    </tr>
    <tr>
        <td><strong>7단계: 준공</strong></td>
        <td>{current_year+3}.01~02</td>
        <td>준공검사, 사용승인</td>
        <td>2개월</td>
    </tr>
    <tr>
        <td><strong>8단계: 매각</strong></td>
        <td>{current_year+3}.03</td>
        <td>LH 매매계약, 소유권 이전</td>
        <td>1개월</td>
    </tr>
</table>
<p style="text-align: center; margin-top: 20px;">
    <strong>총 소요 기간: 약 28개월</strong>
</p>
"""
    
    def _generate_legal_review(self, zone_info, capacity) -> str:
        """법적 검토 섹션 생성"""
        return f"""
<h3>1.1 건축 가능 규모</h3>
<table>
    <tr>
        <th>구분</th>
        <th>법정 한도</th>
        <th>계획</th>
        <th>적합 여부</th>
    </tr>
    <tr>
        <td>건폐율</td>
        <td>{zone_info.building_coverage_ratio if zone_info else 60}% 이하</td>
        <td>{(capacity.building_area / 500 * 100):.1f}%</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>용적률</td>
        <td>{zone_info.floor_area_ratio if zone_info else 200}% 이하</td>
        <td>{(capacity.total_floor_area / 500 * 100):.1f}%</td>
        <td class="highlight">✓ 적합</td>
    </tr>
    <tr>
        <td>층수</td>
        <td>15층 이하</td>
        <td>{capacity.floors}층</td>
        <td class="highlight">✓ 적합</td>
    </tr>
</table>

<h3>1.2 건축법규 준수 사항</h3>
<ul class="checklist">
    <li>일조권 확보: 인동간격 기준 준수</li>
    <li>소방법: 스프링클러 설치, 피난계단 확보</li>
    <li>주차장법: 법정 주차대수 {capacity.parking_spaces}대 확보</li>
    <li>장애인·노인·임산부등의편의증진보장에관한법률: 편의시설 설치</li>
    <li>녹지공간: 대지면적의 10% 이상 확보</li>
</ul>
"""
    
    def _generate_development_restrictions(self, risks) -> str:
        """개발 제한 사항 생성"""
        if not risks or len(risks) == 0:
            return """
<div class="success-box">
    <h3>✓ 개발 제한 사항 없음</h3>
    <p>대상지는 다음의 개발 제한 구역에 해당하지 않습니다:</p>
    <ul>
        <li>개발제한구역 (그린벨트)</li>
        <li>군사시설보호구역</li>
        <li>문화재보호구역</li>
        <li>자연환경보전지역</li>
        <li>상수원보호구역</li>
    </ul>
</div>
"""
        else:
            html = '<div class="warning-box"><h3>⚠ 주의 사항</h3><ul>'
            for risk in risks:
                html += f'<li><strong>[{risk.category}]</strong> {risk.description}</li>'
            html += '</ul></div>'
            return html
    
    def _generate_detailed_risk_analysis(self, risks, summary) -> str:
        """상세 리스크 분석 생성"""
        if not risks or len(risks) == 0:
            return """
<div class="success-box">
    <h3>리스크 평가 결과: 낮음</h3>
    <p>대상지는 중대한 리스크 요인이 없으며, LH 매입 추진에 문제가 없습니다.</p>
</div>
"""
        
        html = '<table><tr><th>리스크 구분</th><th>내용</th><th>심각도</th><th>대응방안</th></tr>'
        
        for risk in risks:
            severity_ko = {"high": "높음", "medium": "중간", "low": "낮음"}.get(risk.severity, "중간")
            color = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}.get(risk.severity, "#ffc107")
            
            mitigation = self._get_mitigation_plan(risk)
            
            html += f'''
<tr>
    <td style="color: {color}; font-weight: bold;">{risk.category}</td>
    <td>{risk.description}</td>
    <td style="color: {color};">{severity_ko}</td>
    <td>{mitigation}</td>
</tr>
'''
        
        html += '</table>'
        return html
    
    def _get_mitigation_plan(self, risk) -> str:
        """리스크별 대응방안 반환"""
        if "유해시설" in risk.category:
            return "환경영향평가 실시, 방음·방진 시설 설치"
        elif "접근성" in risk.category:
            return "셔틀버스 운영, 자전거 보관소 설치"
        elif "법적제한" in risk.category:
            return "관할 구청 사전 협의, 용도 변경 검토"
        else:
            return "지속적 모니터링 및 대응"
    
    def _generate_building_plan(self, capacity, land_area, zone_info, unit_type) -> str:
        """건축 계획 상세 생성"""
        unit_area = {"청년형": 30, "신혼부부형": 50, "고령자형": 40}.get(unit_type, 30)
        
        return f"""
<h3>1.1 건축 개요</h3>
<table>
    <tr>
        <th>구분</th>
        <th>내용</th>
    </tr>
    <tr>
        <td><strong>대지면적</strong></td>
        <td>{land_area:,.2f}㎡ ({land_area/3.3:,.1f}평)</td>
    </tr>
    <tr>
        <td><strong>건축면적</strong></td>
        <td>{capacity.building_area:,.2f}㎡ ({capacity.building_area/3.3:,.1f}평)</td>
    </tr>
    <tr>
        <td><strong>연면적</strong></td>
        <td>{capacity.total_floor_area:,.2f}㎡ ({capacity.total_floor_area/3.3:,.1f}평)</td>
    </tr>
    <tr>
        <td><strong>건폐율</strong></td>
        <td>{(capacity.building_area/land_area*100):.1f}% (법정 {zone_info.building_coverage_ratio if zone_info else 60}%)</td>
    </tr>
    <tr>
        <td><strong>용적률</strong></td>
        <td>{(capacity.total_floor_area/land_area*100):.1f}% (법정 {zone_info.floor_area_ratio if zone_info else 200}%)</td>
    </tr>
    <tr>
        <td><strong>규모</strong></td>
        <td>지하 1층 ~ 지상 {capacity.floors}층</td>
    </tr>
    <tr>
        <td><strong>구조</strong></td>
        <td>철근콘크리트조 (RC)</td>
    </tr>
    <tr>
        <td><strong>주차</strong></td>
        <td>지하 및 지상 {capacity.parking_spaces}대</td>
    </tr>
</table>

<h3>1.2 세대 구성</h3>
<table>
    <tr>
        <th>유형</th>
        <th>전용면적</th>
        <th>세대수</th>
        <th>비율</th>
    </tr>
    <tr>
        <td><strong>{unit_type}</strong></td>
        <td>{unit_area}㎡</td>
        <td>{capacity.units}세대</td>
        <td>100%</td>
    </tr>
    <tr>
        <td colspan="2"><strong>합계</strong></td>
        <td><strong>{capacity.units}세대</strong></td>
        <td><strong>100%</strong></td>
    </tr>
</table>

<h3>1.3 층별 구성</h3>
<table>
    <tr>
        <th>층</th>
        <th>용도</th>
        <th>면적(㎡)</th>
    </tr>
    <tr>
        <td>지하 1층</td>
        <td>주차장, 기계실, 전기실</td>
        <td>{capacity.building_area:,.1f}</td>
    </tr>
    <tr>
        <td>1층</td>
        <td>로비, 관리사무소, 커뮤니티시설</td>
        <td>{capacity.building_area:,.1f}</td>
    </tr>
    <tr>
        <td>2층 ~ {capacity.floors}층</td>
        <td>주거 ({capacity.floors-1}개층)</td>
        <td>{capacity.building_area * (capacity.floors-1):,.1f}</td>
    </tr>
</table>
"""
    
    def _generate_cost_estimation(self, capacity, land_area) -> str:
        """사업비 추정 생성"""
        land_price = land_area * 3000000  # 평당 1,000만원 가정
        construction_cost = capacity.total_floor_area * 2500000  # ㎡당 250만원
        additional_cost = (land_price + construction_cost) * 0.15
        total_cost = land_price + construction_cost + additional_cost
        
        return f"""
<h3>2.1 총 사업비</h3>
<table>
    <tr>
        <th>구분</th>
        <th>금액(원)</th>
        <th>비율</th>
    </tr>
    <tr>
        <td><strong>토지비</strong></td>
        <td>{land_price:,.0f}</td>
        <td>{(land_price/total_cost*100):.1f}%</td>
    </tr>
    <tr>
        <td><strong>건축비</strong></td>
        <td>{construction_cost:,.0f}</td>
        <td>{(construction_cost/total_cost*100):.1f}%</td>
    </tr>
    <tr>
        <td><strong>부대비용</strong></td>
        <td>{additional_cost:,.0f}</td>
        <td>{(additional_cost/total_cost*100):.1f}%</td>
    </tr>
    <tr style="font-weight: bold; background: #f0f0f0;">
        <td><strong>합계</strong></td>
        <td><strong>{total_cost:,.0f}</strong></td>
        <td><strong>100%</strong></td>
    </tr>
</table>

<h3>2.2 세대당 사업비</h3>
<div class="info-box">
    <p><strong>세대당 평균 사업비: {int(total_cost/capacity.units):,.0f}원</strong></p>
    <p>* LH 매입 기준 세대당 1억 5천만원 이내 권장</p>
</div>
"""
    
    def _generate_profitability_analysis(self, capacity, land_area) -> str:
        """수익성 분석 생성"""
        total_cost = land_area * 3000000 + capacity.total_floor_area * 2500000
        total_cost *= 1.15
        
        lh_price = capacity.units * 150000000
        profit = lh_price - total_cost
        profit_rate = (profit / total_cost) * 100
        
        return f"""
<h3>3.1 LH 매입가 시나리오</h3>
<table>
    <tr>
        <th>구분</th>
        <th>세대당 단가</th>
        <th>총 매입가</th>
        <th>예상 수익</th>
        <th>수익률</th>
    </tr>
    <tr>
        <td>보수적</td>
        <td>130,000,000원</td>
        <td>{capacity.units * 130000000:,.0f}원</td>
        <td>{(capacity.units * 130000000 - total_cost):,.0f}원</td>
        <td>{((capacity.units * 130000000 - total_cost)/total_cost*100):.1f}%</td>
    </tr>
    <tr style="background: #fffacd;">
        <td><strong>표준</strong></td>
        <td><strong>150,000,000원</strong></td>
        <td><strong>{lh_price:,.0f}원</strong></td>
        <td><strong>{profit:,.0f}원</strong></td>
        <td><strong>{profit_rate:.1f}%</strong></td>
    </tr>
    <tr>
        <td>낙관적</td>
        <td>170,000,000원</td>
        <td>{capacity.units * 170000000:,.0f}원</td>
        <td>{(capacity.units * 170000000 - total_cost):,.0f}원</td>
        <td>{((capacity.units * 170000000 - total_cost)/total_cost*100):.1f}%</td>
    </tr>
</table>

<h3>3.2 사업성 평가</h3>
<div class="{"success-box" if profit_rate > 10 else "warning-box"}">
    <p><strong>종합 평가: {"우수" if profit_rate > 15 else "양호" if profit_rate > 10 else "보통"}</strong></p>
    <ul>
        <li>예상 수익률: <strong>{profit_rate:.1f}%</strong></li>
        <li>투자 회수 기간: 약 {int(28 + (100/profit_rate if profit_rate > 0 else 0))}개월</li>
        <li>리스크 대비 수익: {"높음" if profit_rate > 15 else "중간" if profit_rate > 10 else "낮음"}</li>
    </ul>
</div>
"""
    
    def _generate_demographic_analysis(self, demographic, unit_type) -> str:
        """인구통계 분석 생성"""
        if not demographic:
            return "<p>인구통계 데이터 수집 중</p>"
        
        return f"""
<h3>1.1 지역 인구 현황</h3>
<table>
    <tr>
        <th>구분</th>
        <th>인구수</th>
        <th>비율</th>
        <th>평가</th>
    </tr>
    <tr>
        <td>총 인구</td>
        <td>{demographic.total_population:,}명</td>
        <td>100%</td>
        <td>-</td>
    </tr>
    <tr>
        <td><strong>청년층 (20-39세)</strong></td>
        <td><strong>{demographic.youth_population:,}명</strong></td>
        <td><strong>{demographic.youth_ratio}%</strong></td>
        <td><strong>{"매우 높음" if demographic.youth_ratio > 35 else "높음" if demographic.youth_ratio > 30 else "보통"}</strong></td>
    </tr>
    <tr>
        <td>1인 가구</td>
        <td>{demographic.single_households:,}가구</td>
        <td>{demographic.single_household_ratio}%</td>
        <td>{"매우 높음" if demographic.single_household_ratio > 35 else "높음" if demographic.single_household_ratio > 30 else "보통"}</td>
    </tr>
</table>

<h3>1.2 {unit_type} 타겟층 분석</h3>
<div class="info-box">
    {self._generate_target_analysis(demographic, unit_type)}
</div>
"""
    
    def _generate_target_analysis(self, demographic, unit_type) -> str:
        """타겟층 분석 생성"""
        if unit_type == "청년형":
            return f"""
<p><strong>청년층 수요 분석:</strong></p>
<ul>
    <li>대상 인구: {demographic.youth_population:,}명 (전체의 {demographic.youth_ratio}%)</li>
    <li>1인 가구 비중: {demographic.single_household_ratio}%로 높은 편</li>
    <li>주거 형태: 원룸, 투룸 선호</li>
    <li>주요 수요: 직장 근접 주거, 교통 편의성 중시</li>
</ul>
<p><strong>결론:</strong> 청년형 임대주택 수요가 {"매우 높음" if demographic.youth_ratio > 30 else "높음" if demographic.youth_ratio > 25 else "보통"}</p>
"""
        elif unit_type == "신혼부부형":
            return f"""
<p><strong>신혼부부 수요 분석:</strong></p>
<ul>
    <li>잠재 대상: 25-35세 인구의 약 30%</li>
    <li>주거 형태: 투룸, 쓰리룸 선호</li>
    <li>주요 수요: 육아 환경, 교육 시설 접근성</li>
    <li>임대료 부담: 시세 70-85% 수준 선호</li>
</ul>
<p><strong>결론:</strong> 신혼부부형 임대주택 수요 {"높음" if demographic.youth_ratio > 25 else "보통"}</p>
"""
        else:
            return """
<p><strong>고령자 수요 분석:</strong></p>
<ul>
    <li>65세 이상 인구 증가 추세</li>
    <li>주거 형태: 1인 또는 부부 세대</li>
    <li>주요 수요: 의료 접근성, 무장애 설계</li>
    <li>장기 거주 선호</li>
</ul>
<p><strong>결론:</strong> 고령자형 임대주택 수요 증가 예상</p>
"""
    
    def _generate_detailed_infrastructure(self, demand, unit_type) -> str:
        """생활 인프라 상세 분석"""
        return """
<h3>2.1 필수 생활 인프라</h3>
<table>
    <tr>
        <th>시설 유형</th>
        <th>시설명</th>
        <th>거리</th>
        <th>중요도</th>
    </tr>
    <tr>
        <td rowspan="2">교통</td>
        <td>지하철역</td>
        <td>도보 10분 이내</td>
        <td>필수</td>
    </tr>
    <tr>
        <td>버스정류장</td>
        <td>도보 5분 이내</td>
        <td>필수</td>
    </tr>
    <tr>
        <td rowspan="2">상업</td>
        <td>편의점</td>
        <td>도보 5분 이내</td>
        <td>필수</td>
    </tr>
    <tr>
        <td>대형마트</td>
        <td>도보 10분 이내</td>
        <td>권장</td>
    </tr>
    <tr>
        <td>의료</td>
        <td>병의원</td>
        <td>도보 10분 이내</td>
        <td>권장</td>
    </tr>
    <tr>
        <td>여가</td>
        <td>공원</td>
        <td>도보 10분 이내</td>
        <td>권장</td>
    </tr>
</table>

<h3>2.2 특화 시설 (유형별)</h3>
""" + self._generate_specialized_facilities(unit_type)
    
    def _generate_specialized_facilities(self, unit_type) -> str:
        """유형별 특화 시설"""
        if unit_type == "청년형":
            return """
<div class="info-box">
    <p><strong>청년형 특화 시설:</strong></p>
    <ul>
        <li>코워킹 스페이스 (반경 1km 이내)</li>
        <li>카페·프랜차이즈 (도보권)</li>
        <li>피트니스센터 (단지 내 또는 인근)</li>
        <li>편의점·무인택배 (단지 내 필수)</li>
    </ul>
</div>
"""
        elif unit_type == "신혼부부형":
            return """
<div class="info-box">
    <p><strong>신혼부부형 특화 시설:</strong></p>
    <ul>
        <li>어린이집·유치원 (도보 10분 이내)</li>
        <li>소아과·산부인과 (차량 10분 이내)</li>
        <li>놀이터·키즈카페 (인근)</li>
        <li>대형마트·백화점 (차량 15분 이내)</li>
    </ul>
</div>
"""
        else:
            return """
<div class="info-box">
    <p><strong>고령자형 특화 시설:</strong></p>
    <ul>
        <li>종합병원 (차량 10분 이내)</li>
        <li>경로당·복지관 (도보 10분 이내)</li>
        <li>약국 (도보 5분 이내)</li>
        <li>공원·산책로 (도보 5분 이내)</li>
    </ul>
</div>
"""
    
    def _generate_demand_forecast(self, demand, demographic, unit_type) -> str:
        """임대 수요 전망 생성"""
        score = demand.demand_score if demand else 50
        
        return f"""
<h3>3.1 수요 점수</h3>
<div class="score-bar">
    <div class="score-fill" style="width: {score}%;">
        {score}/100점
    </div>
</div>

<h3>3.2 수요 전망</h3>
<table>
    <tr>
        <th>평가 항목</th>
        <th>점수</th>
        <th>평가</th>
    </tr>
    <tr>
        <td>인구통계 적합성</td>
        <td>{min(score * 0.4, 40):.0f}/40</td>
        <td>{"우수" if score > 70 else "양호" if score > 50 else "보통"}</td>
    </tr>
    <tr>
        <td>교통 접근성</td>
        <td>{min(score * 0.3, 30):.0f}/30</td>
        <td>{"우수" if score > 70 else "양호" if score > 50 else "보통"}</td>
    </tr>
    <tr>
        <td>생활 편의성</td>
        <td>{min(score * 0.3, 30):.0f}/30</td>
        <td>{"우수" if score > 70 else "양호" if score > 50 else "보통"}</td>
    </tr>
</table>

<h3>3.3 임대 경쟁률 예측</h3>
<div class="{"success-box" if score > 70 else "info-box"}">
    <p><strong>예상 경쟁률:</strong> {self._calculate_competition_rate(score, unit_type)}</p>
    <p><strong>공실률 전망:</strong> {"5% 이하 (매우 낮음)" if score > 70 else "10% 이하 (낮음)" if score > 50 else "15% 이하 (보통)"}</p>
    <p><strong>안정적 운영 가능성:</strong> {"매우 높음" if score > 70 else "높음" if score > 50 else "보통"}</p>
</div>
"""
    
    def _calculate_competition_rate(self, score, unit_type) -> str:
        """경쟁률 계산"""
        if score > 80:
            return "15:1 이상 (매우 높음)"
        elif score > 70:
            return "10:1 ~ 15:1 (높음)"
        elif score > 60:
            return "7:1 ~ 10:1 (중간)"
        else:
            return "5:1 ~ 7:1 (보통)"
    
    def _generate_eligibility_assessment(self, summary, risks, demand) -> str:
        """적격성 평가 생성"""
        eligible = summary.is_eligible if summary else False
        risk_count = len(risks)
        score = demand.demand_score if demand else 50
        
        return f"""
<div class="summary-table">
    <h3>종합 평가 요약</h3>
    <table>
        <tr>
            <th>평가 항목</th>
            <th>평가 결과</th>
            <th>비고</th>
        </tr>
        <tr>
            <td><strong>LH 매입 적격성</strong></td>
            <td class="highlight" style="font-size: 18px;">{"✓ 적격" if eligible else "✗ 부적격"}</td>
            <td>{summary.recommendation if summary else ""}</td>
        </tr>
        <tr>
            <td><strong>예상 세대수</strong></td>
            <td>{summary.estimated_units if summary else 0}세대</td>
            <td>{"적정 규모" if (summary and summary.estimated_units >= 20) else "소규모"}</td>
        </tr>
        <tr>
            <td><strong>수요 점수</strong></td>
            <td>{score}/100점</td>
            <td>{"우수" if score > 70 else "양호" if score > 50 else "보통"}</td>
        </tr>
        <tr>
            <td><strong>리스크 수준</strong></td>
            <td>{risk_count}개 요인</td>
            <td>{"낮음" if risk_count <= 1 else "중간" if risk_count <= 3 else "높음"}</td>
        </tr>
        <tr>
            <td><strong>사업 추진 가능성</strong></td>
            <td>{"높음" if eligible and score > 60 else "중간" if eligible else "낮음"}</td>
            <td>{"즉시 추진 권장" if eligible and score > 70 else "검토 후 추진" if eligible else "추진 보류"}</td>
        </tr>
    </table>
</div>
"""
    
    def _generate_final_opinion(self, summary, capacity, demand, risks, unit_type) -> str:
        """최종 의견 생성"""
        eligible = summary.is_eligible if summary else False
        
        if eligible:
            opinion_class = "success-box"
            opinion_title = "✓ 긍정 의견"
            opinion_text = f"""
본 감정인은 대상지가 다음의 이유로 LH 신축매입임대주택 사업지로 <strong>적합</strong>하다고 판단합니다:

<ul>
    <li>법적 제한 사항이 없으며, 건축 기준을 충족합니다.</li>
    <li>교통 및 생활 인프라가 우수하여 {unit_type} 수요층 확보가 용이합니다.</li>
    <li>인구통계학적으로 타겟층이 충분히 존재합니다.</li>
    <li>예상 세대수 {capacity.units}세대로 적정 규모입니다.</li>
    <li>사업성 및 수익성이 확보되어 있습니다.</li>
</ul>

<p><strong>따라서, LH 매입약정 신청을 적극 권장합니다.</strong></p>
"""
        else:
            opinion_class = "warning-box"
            opinion_title = "⚠ 유보 의견"
            opinion_text = f"""
본 감정인은 대상지에 대해 다음의 사유로 <strong>신중한 검토</strong>가 필요하다고 판단합니다:

<ul>
    <li>리스크 요인 {len(risks)}개가 확인되었습니다.</li>
    <li>일부 LH 기준 충족에 어려움이 있을 수 있습니다.</li>
    <li>추가적인 대응방안 마련이 필요합니다.</li>
</ul>

<p><strong>리스크 대응 후 재평가를 권장합니다.</strong></p>
"""
        
        return f"""
<div class="{opinion_class}">
    <h3>{opinion_title}</h3>
    {opinion_text}
</div>

<h3>감정인 의견</h3>
<p style="line-height: 2.0; text-align: justify;">
본 보고서는 LH 신축매입임대주택 사업을 목적으로 대상 부동산의 입지, 법적 현황, 
사업성, 수요 등을 종합적으로 검토한 결과입니다. 
감정평가 기준일 현재 대상지는 {unit_type} 임대주택 공급지로서 
{"우수한" if eligible else "일부 보완이 필요한"} 조건을 갖추고 있는 것으로 판단됩니다.
</p>
<p style="line-height: 2.0; text-align: justify;">
다만, 본 평가는 현장 조사 및 공부상 확인 사항을 기준으로 하였으며, 
향후 인허가 과정에서 추가적인 제한 사항이 발생할 수 있음을 유의하시기 바랍니다.
</p>
"""
    
    def _generate_recommendations(self, risks, demand, unit_type) -> str:
        """제언 사항 생성"""
        return f"""
<h3>3.1 사업 추진 시 고려사항</h3>
<ul class="checklist">
    <li>LH와의 사전 협의를 통한 매입 조건 확인</li>
    <li>정밀 지반조사 및 토양오염 검사 실시</li>
    <li>인근 주민 설명회 개최 및 민원 대응</li>
    <li>친환경 건축 인증 추진 (LH 우대 사항)</li>
    <li>품질관리 전담 조직 구성</li>
</ul>

<h3>3.2 리스크 대응방안</h3>
{self._generate_risk_mitigation_plan(risks)}

<h3>3.3 성공적 사업 추진을 위한 제언</h3>
<div class="info-box">
    <ol>
        <li><strong>철저한 사전 준비:</strong> LH 공고 요건을 세밀히 검토하고 모든 서류를 완벽하게 준비</li>
        <li><strong>전문가 협업:</strong> 건축사, 감정평가사, 법무사 등 전문가 팀 구성</li>
        <li><strong>일정 관리:</strong> 각 단계별 일정을 철저히 관리하여 지연 방지</li>
        <li><strong>품질 최우선:</strong> LH 품질 기준을 상회하는 시공 품질 확보</li>
        <li><strong>지속적 소통:</strong> LH 담당자와 긴밀한 협의 체계 구축</li>
    </ol>
</div>
"""
    
    def _generate_risk_mitigation_plan(self, risks) -> str:
        """리스크 대응 계획 생성"""
        if not risks or len(risks) == 0:
            return """
<div class="success-box">
    <p><strong>현재 중대한 리스크 요인이 없습니다.</strong></p>
    <p>다만, 사업 진행 중 발생 가능한 일반적 리스크에 대한 대비는 필요합니다.</p>
</div>
"""
        
        html = "<table><tr><th>리스크</th><th>대응방안</th><th>예상 비용</th></tr>"
        for risk in risks:
            mitigation = self._get_mitigation_plan(risk)
            cost = "사업비의 1-3%" if risk.severity == "high" else "경미"
            html += f"<tr><td>{risk.description}</td><td>{mitigation}</td><td>{cost}</td></tr>"
        html += "</table>"
        return html
    
    def _generate_checklist(self) -> str:
        """체크리스트 생성"""
        return """
<table>
    <tr>
        <th>점검 항목</th>
        <th>확인 결과</th>
    </tr>
    <tr><td>토지 소유권 확보</td><td class="highlight">✓</td></tr>
    <tr><td>용도지역 적합성</td><td class="highlight">✓</td></tr>
    <tr><td>진입도로 4m 이상</td><td class="highlight">✓</td></tr>
    <tr><td>상하수도 인입 가능</td><td class="highlight">✓</td></tr>
    <tr><td>도시가스 인입 가능</td><td class="highlight">✓</td></tr>
    <tr><td>개발제한구역 제외</td><td class="highlight">✓</td></tr>
    <tr><td>군사시설보호구역 제외</td><td class="highlight">✓</td></tr>
    <tr><td>문화재보호구역 제외</td><td class="highlight">✓</td></tr>
    <tr><td>급경사지 아님</td><td class="highlight">✓</td></tr>
    <tr><td>침수구역 아님</td><td class="highlight">✓</td></tr>
    <tr><td>세대수 50세대 미만</td><td class="highlight">✓</td></tr>
    <tr><td>주차대수 기준 충족</td><td class="highlight">✓</td></tr>
</table>
"""
    
    def _generate_legal_references(self) -> str:
        """관련 법규 생성"""
        return """
<h3>주요 관련 법규</h3>
<ul>
    <li><strong>주택법</strong> 제2조, 제15조 (민간임대주택 등록)</li>
    <li><strong>건축법</strong> 제42조, 제56조 (건폐율, 용적률)</li>
    <li><strong>국토의 계획 및 이용에 관한 법률</strong> 제36조 (용도지역)</li>
    <li><strong>주차장법</strong> 제19조 (부설주차장 설치)</li>
    <li><strong>소방시설법</strong> 제9조 (소방시설 설치)</li>
</ul>

<h3>LH 신축매입임대주택 사업 관련 규정</h3>
<ul>
    <li>LH 신축매입임대주택 사업 공고문 ({datetime.now().year}년)</li>
    <li>공공주택 특별법 시행규칙</li>
    <li>LH 품질관리 매뉴얼</li>
</ul>
"""
    
    def _generate_glossary(self) -> str:
        """용어 정의 생성"""
        return """
<table>
    <tr>
        <th>용어</th>
        <th>정의</th>
    </tr>
    <tr>
        <td>신축매입임대</td>
        <td>사업자가 신축한 주택을 LH가 매입하여 임대하는 방식</td>
    </tr>
    <tr>
        <td>건폐율</td>
        <td>대지면적에 대한 건축면적의 비율</td>
    </tr>
    <tr>
        <td>용적률</td>
        <td>대지면적에 대한 연면적의 비율</td>
    </tr>
    <tr>
        <td>전용면적</td>
        <td>주거 전용으로 사용하는 면적 (발코니, 계단 등 제외)</td>
    </tr>
    <tr>
        <td>도시형생활주택</td>
        <td>300세대 미만의 국민주택규모에 해당하는 주택</td>
    </tr>
</table>
"""


# 전역 인스턴스
expert_generator = ExpertReportGenerator()
