"""
ZeroSite v11.0 - Unit-Type Suitability Analyzer
================================================
세대유형 적합성 분석 엔진

5가지 세대유형:
1. 청년형 (Youth Type) - 19-34세 대상
2. 신혼형 (Newlywed Type) - 신혼부부 대상
3. 고령자형 (Senior Type) - 65세 이상 대상
4. 일반형 (General Type) - 일반 가구 대상
5. 취약계층형 (Vulnerable Type) - 저소득층 대상

평가 기준 (6개 요소):
- 인구구조 (Demographics)
- 교통 접근성 (Transportation)
- 생활 인프라 (Living Infrastructure)
- 정책 정합성 (Policy Alignment)
- 경제적 적정성 (Economic Suitability)
- 사회적 수요 (Social Demand)
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime


class DemographicIntelligence:
    """인구통계 분석 엔진"""
    
    @staticmethod
    def analyze_age_structure(address: str) -> Dict[str, float]:
        """
        주소 기반 연령대별 인구 비율 분석
        실제로는 통계청 API 연동 필요
        """
        # 지역별 특성 반영 (임시 데이터)
        if "강남" in address or "서초" in address:
            return {
                "youth_ratio": 28.5,  # 19-34세
                "newlywed_ratio": 22.3,  # 신혼부부 추정
                "senior_ratio": 12.8,  # 65세 이상
                "general_ratio": 36.4   # 기타
            }
        elif "마포" in address or "용산" in address:
            return {
                "youth_ratio": 32.1,
                "newlywed_ratio": 24.7,
                "senior_ratio": 10.2,
                "general_ratio": 33.0
            }
        elif "노원" in address or "강북" in address:
            return {
                "youth_ratio": 18.5,
                "newlywed_ratio": 16.2,
                "senior_ratio": 22.8,
                "general_ratio": 42.5
            }
        else:
            return {
                "youth_ratio": 23.0,
                "newlywed_ratio": 19.5,
                "senior_ratio": 16.8,
                "general_ratio": 40.7
            }
    
    @staticmethod
    def analyze_household_structure(address: str) -> Dict[str, Any]:
        """가구 구조 분석"""
        return {
            "single_household_ratio": 35.2,
            "couple_household_ratio": 18.5,
            "nuclear_family_ratio": 28.3,
            "extended_family_ratio": 18.0,
            "avg_household_size": 2.3
        }


class InfrastructureScoring:
    """인프라 점수화 엔진"""
    
    @staticmethod
    def score_youth_infrastructure(address: str, coord: Dict[str, float]) -> Dict[str, Any]:
        """청년형 인프라 평가"""
        # 실제로는 카카오맵/네이버맵 API 활용
        return {
            "universities": {
                "count": 3,
                "names": ["홍익대학교", "서강대학교", "연세대학교"],
                "avg_distance": "2.5km",
                "score": 92
            },
            "youth_centers": {
                "count": 2,
                "names": ["서울청년센터", "마포청년허브"],
                "avg_distance": "1.8km",
                "score": 88
            },
            "job_centers": {
                "count": 5,
                "major_companies": ["IT 스타트업 밸리", "디지털미디어시티"],
                "score": 85
            },
            "cultural_facilities": {
                "theaters": 8,
                "cafes": 156,
                "gyms": 12,
                "score": 90
            },
            "public_transport": {
                "subway_lines": 3,
                "bus_routes": 42,
                "nightbus_available": True,
                "score": 95
            },
            "overall_score": 90
        }
    
    @staticmethod
    def score_senior_infrastructure(address: str, coord: Dict[str, float]) -> Dict[str, Any]:
        """고령자형 인프라 평가"""
        return {
            "hospitals": {
                "count": 8,
                "major_hospitals": ["서울대병원", "연세세브란스병원", "서울아산병원"],
                "specialized_clinics": 25,
                "avg_distance": "1.2km",
                "score": 94
            },
            "senior_centers": {
                "count": 4,
                "names": ["마포노인복지관", "서울시니어클럽"],
                "score": 86
            },
            "parks": {
                "count": 6,
                "walking_trails": 3,
                "score": 88
            },
            "barrier_free": {
                "sidewalk_quality": "우수",
                "elevator_availability": "높음",
                "score": 82
            },
            "medical_access": {
                "emergency_response_time": "5분",
                "pharmacy_count": 18,
                "score": 92
            },
            "overall_score": 88
        }
    
    @staticmethod
    def score_newlywed_infrastructure(address: str, coord: Dict[str, float]) -> Dict[str, Any]:
        """신혼형 인프라 평가"""
        return {
            "childcare": {
                "daycare_centers": 12,
                "kindergartens": 8,
                "avg_distance": "500m",
                "score": 89
            },
            "education": {
                "elementary_schools": 5,
                "middle_schools": 3,
                "high_schools": 2,
                "score": 92
            },
            "shopping": {
                "large_marts": 4,
                "convenience_stores": 38,
                "score": 90
            },
            "parks_recreation": {
                "family_parks": 3,
                "playgrounds": 15,
                "score": 86
            },
            "overall_score": 89
        }


class UnitTypeSuitabilityAnalyzer:
    """세대유형 적합성 분석기"""
    
    def __init__(self):
        self.demo_intel = DemographicIntelligence()
        self.infra_scoring = InfrastructureScoring()
    
    def analyze_all_types(
        self, 
        address: str, 
        coord: Dict[str, float],
        zone_type: str,
        land_area: float
    ) -> Dict[str, Any]:
        """
        5가지 세대유형 종합 평가
        
        Returns:
            {
                "youth": {...},
                "newlywed": {...},
                "senior": {...},
                "general": {...},
                "vulnerable": {...},
                "recommended_type": "youth",
                "confidence": 0.92
            }
        """
        
        # 인구통계 분석
        age_structure = self.demo_intel.analyze_age_structure(address)
        household_structure = self.demo_intel.analyze_household_structure(address)
        
        # 각 세대유형별 평가
        youth_analysis = self._analyze_youth_type(address, coord, age_structure)
        newlywed_analysis = self._analyze_newlywed_type(address, coord, age_structure)
        senior_analysis = self._analyze_senior_type(address, coord, age_structure)
        general_analysis = self._analyze_general_type(address, coord, age_structure)
        vulnerable_analysis = self._analyze_vulnerable_type(address, coord, age_structure)
        
        # 최적 세대유형 선정
        all_scores = {
            "youth": youth_analysis["total_score"],
            "newlywed": newlywed_analysis["total_score"],
            "senior": senior_analysis["total_score"],
            "general": general_analysis["total_score"],
            "vulnerable": vulnerable_analysis["total_score"]
        }
        
        recommended_type = max(all_scores, key=all_scores.get)
        confidence = all_scores[recommended_type] / 100.0
        
        return {
            "youth": youth_analysis,
            "newlywed": newlywed_analysis,
            "senior": senior_analysis,
            "general": general_analysis,
            "vulnerable": vulnerable_analysis,
            "recommended_type": recommended_type,
            "confidence": confidence,
            "age_structure": age_structure,
            "household_structure": household_structure
        }
    
    def _analyze_youth_type(
        self, 
        address: str, 
        coord: Dict[str, float],
        age_structure: Dict[str, float]
    ) -> Dict[str, Any]:
        """청년형 세대 평가"""
        
        infra = self.infra_scoring.score_youth_infrastructure(address, coord)
        
        scores = {
            "demographics": min(age_structure["youth_ratio"] * 3, 100),  # 청년 비율
            "transportation": infra["public_transport"]["score"],
            "infrastructure": infra["overall_score"],
            "policy_alignment": 88,  # LH 청년정책 정합성
            "economic_suitability": 85,  # 임대료 적정성
            "social_demand": 90  # 청년 주거 수요
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "type_name": "청년형 (Youth Type)",
            "target_age": "19-34세",
            "scores": scores,
            "total_score": total_score,
            "infrastructure": infra,
            "strengths": [
                f"청년 인구 비율 {age_structure['youth_ratio']:.1f}% (높은 수준)",
                f"대학 {infra['universities']['count']}개 인접 (평균 {infra['universities']['avg_distance']})",
                f"대중교통 {infra['public_transport']['subway_lines']}개 노선 접근",
                "청년센터 및 일자리 인프라 우수"
            ],
            "considerations": [
                "청년 맞춤형 커뮤니티 시설 필요",
                "소형 평형(20-40㎡) 위주 설계 권장",
                "공유 오피스/스터디 공간 계획"
            ]
        }
    
    def _analyze_newlywed_type(
        self, 
        address: str, 
        coord: Dict[str, float],
        age_structure: Dict[str, float]
    ) -> Dict[str, Any]:
        """신혼형 세대 평가"""
        
        infra = self.infra_scoring.score_newlywed_infrastructure(address, coord)
        
        scores = {
            "demographics": min(age_structure["newlywed_ratio"] * 4, 100),
            "transportation": 88,
            "infrastructure": infra["overall_score"],
            "policy_alignment": 92,  # LH 신혼부부 정책
            "economic_suitability": 87,
            "social_demand": 89
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "type_name": "신혼형 (Newlywed Type)",
            "target_age": "신혼부부 (결혼 7년 이내)",
            "scores": scores,
            "total_score": total_score,
            "infrastructure": infra,
            "strengths": [
                f"신혼 가구 비율 {age_structure['newlywed_ratio']:.1f}%",
                f"어린이집 {infra['childcare']['daycare_centers']}개 (평균 {infra['childcare']['avg_distance']})",
                f"초등학교 {infra['education']['elementary_schools']}개 도보권",
                "가족 친화형 생활 인프라 완비"
            ],
            "considerations": [
                "중소형 평형(40-60㎡) 위주 설계",
                "육아 지원 시설 필수",
                "공동 육아방/키즈카페 계획"
            ]
        }
    
    def _analyze_senior_type(
        self, 
        address: str, 
        coord: Dict[str, float],
        age_structure: Dict[str, float]
    ) -> Dict[str, Any]:
        """고령자형 세대 평가"""
        
        infra = self.infra_scoring.score_senior_infrastructure(address, coord)
        
        scores = {
            "demographics": min(age_structure["senior_ratio"] * 4, 100),
            "transportation": 85,
            "infrastructure": infra["overall_score"],
            "policy_alignment": 86,
            "economic_suitability": 90,
            "social_demand": 88
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "type_name": "고령자형 (Senior Type)",
            "target_age": "65세 이상",
            "scores": scores,
            "total_score": total_score,
            "infrastructure": infra,
            "strengths": [
                f"고령 인구 비율 {age_structure['senior_ratio']:.1f}%",
                f"종합병원 {infra['hospitals']['count']}개 인접 (평균 {infra['hospitals']['avg_distance']})",
                f"노인복지관 {infra['senior_centers']['count']}개",
                "의료 접근성 우수 (응급 5분 이내)"
            ],
            "considerations": [
                "배리어프리 설계 필수",
                "응급 호출 시스템 설치",
                "건강 관리 프로그램 운영"
            ]
        }
    
    def _analyze_general_type(
        self, 
        address: str, 
        coord: Dict[str, float],
        age_structure: Dict[str, float]
    ) -> Dict[str, Any]:
        """일반형 세대 평가"""
        
        scores = {
            "demographics": 85,
            "transportation": 88,
            "infrastructure": 87,
            "policy_alignment": 82,
            "economic_suitability": 86,
            "social_demand": 84
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "type_name": "일반형 (General Type)",
            "target_age": "전 연령층",
            "scores": scores,
            "total_score": total_score,
            "infrastructure": {},
            "strengths": [
                "다양한 가구 유형 수용 가능",
                "범용적 생활 인프라",
                "안정적 수요 기반"
            ],
            "considerations": [
                "다양한 평형 구성 (30-85㎡)",
                "범용 커뮤니티 시설",
                "전 연령층 배려 설계"
            ]
        }
    
    def _analyze_vulnerable_type(
        self, 
        address: str, 
        coord: Dict[str, float],
        age_structure: Dict[str, float]
    ) -> Dict[str, Any]:
        """취약계층형 세대 평가"""
        
        scores = {
            "demographics": 78,
            "transportation": 90,  # 대중교통 중요
            "infrastructure": 82,
            "policy_alignment": 94,  # LH 사회적 배려
            "economic_suitability": 95,  # 저렴한 임대료
            "social_demand": 88
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "type_name": "취약계층형 (Vulnerable Type)",
            "target_age": "저소득층, 한부모가정, 장애인 등",
            "scores": scores,
            "total_score": total_score,
            "infrastructure": {},
            "strengths": [
                "대중교통 접근성 우수",
                "저렴한 임대료 설정 가능",
                "사회복지 시설 인접"
            ],
            "considerations": [
                "소형 평형 위주",
                "복지 연계 프로그램",
                "생활 지원 서비스"
            ]
        }
    
    def generate_unit_type_narrative(
        self,
        analysis_result: Dict[str, Any],
        address: str
    ) -> str:
        """세대유형 분석 서술문 생성"""
        
        recommended = analysis_result["recommended_type"]
        recommended_data = analysis_result[recommended]
        confidence = analysis_result["confidence"]
        
        type_names = {
            "youth": "청년형",
            "newlywed": "신혼형",
            "senior": "고령자형",
            "general": "일반형",
            "vulnerable": "취약계층형"
        }
        
        narrative = f"""
        <h3>🎯 권장 세대유형: {type_names[recommended]}</h3>
        <p><strong>분석 신뢰도: {confidence*100:.1f}%</strong></p>
        
        <p>대상 지역인 <strong>{address}</strong>에 대한 종합적인 세대유형 적합성 분석 결과,
        <strong>{recommended_data['type_name']}</strong>이 가장 적합한 것으로 평가되었습니다.</p>
        
        <h4>📊 평가 근거</h4>
        <ul>
        """
        
        for strength in recommended_data["strengths"]:
            narrative += f"<li>{strength}</li>\n"
        
        narrative += f"""
        </ul>
        
        <h4>🏗️ 개발 권장사항</h4>
        <ul>
        """
        
        for consideration in recommended_data["considerations"]:
            narrative += f"<li>{consideration}</li>\n"
        
        narrative += """
        </ul>
        
        <p>이러한 분석 결과를 바탕으로 LH 신축매입임대 사업 추진 시 
        세대유형 특화 전략을 수립하여 입주율 제고 및 사회적 가치 실현이 가능할 것으로 판단됩니다.</p>
        """
        
        return narrative
    
    def generate_comparison_table(
        self,
        analysis_result: Dict[str, Any]
    ) -> str:
        """5가지 세대유형 비교표 생성"""
        
        html = """
        <table class="unit-type-comparison">
            <thead>
                <tr>
                    <th>세대유형</th>
                    <th>인구구조</th>
                    <th>교통</th>
                    <th>인프라</th>
                    <th>정책</th>
                    <th>경제성</th>
                    <th>수요</th>
                    <th>종합점수</th>
                </tr>
            </thead>
            <tbody>
        """
        
        types = ["youth", "newlywed", "senior", "general", "vulnerable"]
        type_names = {
            "youth": "청년형",
            "newlywed": "신혼형",
            "senior": "고령자형",
            "general": "일반형",
            "vulnerable": "취약계층형"
        }
        
        for t in types:
            data = analysis_result[t]
            scores = data["scores"]
            total = data["total_score"]
            
            row_class = "recommended" if t == analysis_result["recommended_type"] else ""
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>{type_names[t]}</strong></td>
                    <td>{scores['demographics']:.0f}</td>
                    <td>{scores['transportation']:.0f}</td>
                    <td>{scores['infrastructure']:.0f}</td>
                    <td>{scores['policy_alignment']:.0f}</td>
                    <td>{scores['economic_suitability']:.0f}</td>
                    <td>{scores['social_demand']:.0f}</td>
                    <td class="total-score"><strong>{total:.1f}</strong></td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        
        <style>
        .unit-type-comparison {
            font-size: 13px;
        }
        
        .unit-type-comparison tr.recommended {
            background: #e8f5e9;
            font-weight: bold;
        }
        
        .unit-type-comparison td.total-score {
            background: #fff3e0;
            font-size: 16px;
        }
        </style>
        
        <div class="table-note">
            <p>* 각 항목은 100점 만점으로 평가되었으며, 종합점수는 6개 항목의 평균값입니다.</p>
            <p>* <span style="background: #e8f5e9; padding: 2px 8px;">녹색 배경</span>은 권장 세대유형을 나타냅니다.</p>
        </div>
        """
        
        return html


# 모듈 테스트
if __name__ == "__main__":
    analyzer = UnitTypeSuitabilityAnalyzer()
    
    result = analyzer.analyze_all_types(
        address="서울특별시 마포구 월드컵북로 120",
        coord={"latitude": 37.563945, "longitude": 126.913344},
        zone_type="제3종일반주거지역",
        land_area=1000.0
    )
    
    print(f"✅ 권장 세대유형: {result['recommended_type']}")
    print(f"✅ 신뢰도: {result['confidence']*100:.1f}%")
    print(f"✅ 청년형 점수: {result['youth']['total_score']:.1f}")
    print(f"✅ 신혼형 점수: {result['newlywed']['total_score']:.1f}")
    print(f"✅ 고령자형 점수: {result['senior']['total_score']:.1f}")
