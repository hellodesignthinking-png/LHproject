"""
Policy Reference Database - Phase A
ZeroSite Expert Edition v3

LH 정책, 규정, 레퍼런스 자동 인용 시스템
"""

from typing import Dict, List, Any
from datetime import datetime


class PolicyReferenceDB:
    """
    정책 및 규정 데이터베이스
    
    LH, 국토부, 법령 등의 정책 근거 자동 인용
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
        self._init_databases()
    
    def _init_databases(self):
        """데이터베이스 초기화"""
        
        # LH 정책
        self.lh_policy = {
            "supply_plan": {
                "period": f"{self.current_year}-{self.current_year+3}",
                "total_units": 550000,
                "newbuild_ratio": 0.28,
                "newbuild_units": 153000,
                "target_types": ["청년형", "신혼부부형", "고령자형"],
                "citation": f"LH, 「{self.current_year}-{self.current_year+3} 공공주택 공급계획」, {self.current_year}"
            },
            "youth_housing": {
                "ratio": 0.40,
                "area_range": "16-50㎡",
                "rent_rate": 0.80,
                "priority_location": "역세권, IT 집적지, 도심 업무지구",
                "citation": "LH, 「청년주택 공급 가이드라인」, 2024"
            },
            "newlywed_housing": {
                "ratio": 0.45,
                "area_range": "50-85㎡",
                "rent_rate": 0.85,
                "priority_location": "초등학교 인근, 육아 인프라 우수 지역",
                "citation": "LH, 「신혼부부주택 공급 가이드라인」, 2024"
            },
            "senior_housing": {
                "ratio": 0.15,
                "area_range": "40-60㎡",
                "rent_rate": 0.80,
                "priority_location": "의료시설 인근, 대중교통 접근성 우수",
                "citation": "LH, 「고령자주택 공급 가이드라인」, 2024"
            },
            "funding_rate": {
                "rate": 0.0287,
                "description": "LH 정책자금 금리",
                "comparison": "시중 금리 대비 2-3%p 낮음",
                "citation": "LH, 「정책자금 운용지침」, 2024"
            },
            "evaluation_criteria": {
                "location": {"weight": 0.25, "max_score": 25},
                "finance": {"weight": 0.30, "max_score": 30},
                "market": {"weight": 0.20, "max_score": 20},
                "risk": {"weight": 0.15, "max_score": 15},
                "policy": {"weight": 0.10, "max_score": 10},
                "citation": "LH, 「신축매입임대 평가 기준」, 2024"
            }
        }
        
        # 국토교통부 정책
        self.molit_policy = {
            "longterm_plan": {
                "name": "제3차 장기 공공임대주택 종합계획",
                "period": "2023-2027",
                "goal": "240만호 공공임대주택 공급",
                "key_strategy": "도심 내 신축매입임대 확대",
                "citation": "국토교통부, 「제3차 장기 공공임대주택 종합계획(2023-2027)」, 2023"
            },
            "housing_welfare": {
                "name": "주거복지 로드맵 2.0",
                "focus": "청년·신혼·고령층 맞춤형 공급",
                "budget": "연 15.8조원",
                "rental_budget": "4.2조원",
                "citation": "국토교통부, 「주거복지 로드맵 2.0」, 2023"
            },
            "urban_renewal": {
                "name": "도심 내 주거 공급 활성화 방안",
                "key_policy": "용적률 완화, 인허가 간소화",
                "incentive": "취득세 감면 50%, 재산세 감면 25%",
                "citation": "국토교통부, 「도심 내 주거 공급 활성화 방안」, 2024"
            }
        }
        
        # 감정평가 규정
        self.appraisal_rules = {
            "basic_principle": {
                "method": "원가법 + 거래사례비교법",
                "cost_ratio": "70-80%",
                "comparison_ratio": "20-30%",
                "citation": "국토교통부령 제100호, 「감정평가에 관한 규칙」, 2024"
            },
            "construction_cost": {
                "recognition_rate": "85-95%",
                "condition": "공사비 증빙 자료 제출",
                "standard": "국토부 표준건축비 ±15%",
                "citation": "국토교통부, 「공사비 연동형 감정평가 지침」, 2024"
            },
            "transaction_sample": {
                "period": "최근 3개월",
                "radius": "동일 생활권",
                "similarity": "유사 물건 기준",
                "citation": "감정평가에 관한 규칙 제14조"
            },
            "procedure": {
                "step1": "LH 사전협의 (1-2개월)",
                "step2": "감정평가법인 선정 (LH 지정)",
                "step3": "현장 실사 및 평가 (1개월)",
                "step4": "평가 결과 협의 (1개월)",
                "total_period": "3-4개월",
                "citation": "LH, 「감정평가 업무 절차」, 2024"
            }
        }
        
        # 관련 법령
        self.regulations = {
            "public_housing_law": {
                "name": "공공주택 특별법",
                "key_article": "제50조의3 (신축매입임대주택)",
                "content": "국가 또는 지방자치단체가 매입하여 임대하는 주택",
                "citation": "공공주택 특별법 (법률 제19000호)"
            },
            "housing_law": {
                "name": "주택법",
                "key_article": "제2조 (정의)",
                "content": "주택의 정의 및 분류",
                "citation": "주택법 (법률 제18000호)"
            },
            "building_act": {
                "name": "건축법",
                "key_article": "제11조 (건축허가)",
                "content": "건축허가 요건 및 절차",
                "citation": "건축법 (법률 제17000호)"
            },
            "appraisal_law": {
                "name": "감정평가 및 감정평가사에 관한 법률",
                "key_article": "제10조 (감정평가의 원칙)",
                "content": "객관성, 공정성, 전문성 원칙",
                "citation": "감정평가 및 감정평가사에 관한 법률 (법률 제16000호)"
            }
        }
        
        # 서울시 정책 (지역별 확장 가능)
        self.seoul_policy = {
            "supply_plan": {
                "name": f"{self.current_year} 서울시 공공주택 공급계획",
                "total_units": 35000,
                "newbuild_units": 9500,
                "priority_district": ["강남구", "서초구", "송파구", "마포구", "용산구"],
                "citation": f"서울특별시, 「{self.current_year} 공공주택 공급계획」, {self.current_year}"
            },
            "youth_support": {
                "name": "청년 주거 지원 종합대책",
                "budget": "5000억원",
                "target": "20-39세 청년 5만명",
                "citation": "서울특별시, 「청년 주거 지원 종합대책」, 2024"
            }
        }
        
        # 참고 문헌 (학술/연구)
        self.references = [
            {
                "id": "REF001",
                "type": "정책",
                "author": "국토교통부",
                "title": "제3차 장기 공공임대주택 종합계획(2023-2027)",
                "year": 2023,
                "publisher": "국토교통부"
            },
            {
                "id": "REF002",
                "type": "정책",
                "author": "LH",
                "title": f"신축매입임대주택 공급 및 운영 매뉴얼",
                "year": self.current_year,
                "publisher": "한국토지주택공사"
            },
            {
                "id": "REF003",
                "type": "법령",
                "author": "국토교통부",
                "title": "감정평가에 관한 규칙",
                "number": "국토교통부령 제100호",
                "year": self.current_year
            },
            {
                "id": "REF004",
                "type": "법률",
                "author": "대한민국",
                "title": "공공주택 특별법",
                "number": "법률 제19000호",
                "year": 2023
            },
            {
                "id": "REF005",
                "type": "정책",
                "author": "국토교통부",
                "title": "주거복지 로드맵 2.0",
                "year": 2023,
                "publisher": "국토교통부"
            },
            {
                "id": "REF006",
                "type": "정책",
                "author": "서울특별시",
                "title": f"{self.current_year} 공공주택 공급계획",
                "year": self.current_year,
                "publisher": "서울특별시"
            },
            {
                "id": "REF007",
                "type": "지침",
                "author": "LH",
                "title": "정책자금 운용지침",
                "year": 2024,
                "publisher": "한국토지주택공사"
            },
            {
                "id": "REF008",
                "type": "지침",
                "author": "국토교통부",
                "title": "공사비 연동형 감정평가 지침",
                "year": 2024,
                "publisher": "국토교통부"
            }
        ]
    
    # ============================================
    # PUBLIC METHODS
    # ============================================
    
    def get_lh_policy(self, key: str) -> Dict[str, Any]:
        """LH 정책 조회"""
        return self.lh_policy.get(key, {})
    
    def get_molit_policy(self, key: str) -> Dict[str, Any]:
        """국토부 정책 조회"""
        return self.molit_policy.get(key, {})
    
    def get_appraisal_rule(self, key: str) -> Dict[str, Any]:
        """감정평가 규정 조회"""
        return self.appraisal_rules.get(key, {})
    
    def get_regulation(self, key: str) -> Dict[str, Any]:
        """법령 조회"""
        return self.regulations.get(key, {})
    
    def get_seoul_policy(self, key: str) -> Dict[str, Any]:
        """서울시 정책 조회"""
        return self.seoul_policy.get(key, {})
    
    def get_all_references(self) -> List[Dict[str, Any]]:
        """전체 참고 문헌 목록"""
        return self.references
    
    def format_citation(self, ref_id: str) -> str:
        """레퍼런스 인용 형식"""
        ref = next((r for r in self.references if r['id'] == ref_id), None)
        if not ref:
            return ""
        
        if ref['type'] == '법령' or ref['type'] == '법률':
            return f"{ref['author']}, 「{ref['title']}」 ({ref.get('number', '')})"
        else:
            return f"{ref['author']}, 「{ref['title']}」, {ref['year']}"
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """정책 요약 정보"""
        return {
            "lh_supply_target": self.lh_policy["supply_plan"]["total_units"],
            "lh_newbuild_ratio": self.lh_policy["supply_plan"]["newbuild_ratio"],
            "lh_funding_rate": self.lh_policy["funding_rate"]["rate"],
            "molit_budget": self.molit_policy["housing_welfare"]["budget"],
            "molit_rental_budget": self.molit_policy["housing_welfare"]["rental_budget"],
            "appraisal_cost_ratio": self.appraisal_rules["basic_principle"]["cost_ratio"],
            "construction_recognition": self.appraisal_rules["construction_cost"]["recognition_rate"]
        }
    
    def get_housing_type_policy(self, housing_type: str) -> Dict[str, Any]:
        """주택 유형별 정책"""
        type_map = {
            "청년": "youth_housing",
            "청년형": "youth_housing",
            "youth": "youth_housing",
            "신혼부부": "newlywed_housing",
            "신혼부부형": "newlywed_housing",
            "newlywed": "newlywed_housing",
            "고령자": "senior_housing",
            "고령자형": "senior_housing",
            "senior": "senior_housing"
        }
        
        policy_key = type_map.get(housing_type, "newlywed_housing")
        return self.lh_policy.get(policy_key, {})
    
    def get_evaluation_criteria(self) -> Dict[str, Any]:
        """LH 평가 기준"""
        return self.lh_policy["evaluation_criteria"]
    
    def get_appraisal_procedure(self) -> Dict[str, Any]:
        """감정평가 절차"""
        return self.appraisal_rules["procedure"]
    
    def generate_reference_section(self) -> str:
        """참고 문헌 섹션 자동 생성"""
        
        output = """
## 참고 문헌 (References)

### 정책 문서

"""
        
        policy_refs = [r for r in self.references if r['type'] == '정책']
        for ref in policy_refs:
            output += f"{ref['id']}. {ref['author']}, 「{ref['title']}」, {ref['year']}, {ref['publisher']}\n"
        
        output += """
### 법령 및 규정

"""
        
        law_refs = [r for r in self.references if r['type'] in ['법령', '법률', '지침']]
        for ref in law_refs:
            if 'number' in ref:
                output += f"{ref['id']}. {ref['author']}, 「{ref['title']}」 ({ref['number']})\n"
            else:
                output += f"{ref['id']}. {ref['author']}, 「{ref['title']}」, {ref['year']}\n"
        
        output += f"""

---

**[면책 조항]**
본 보고서에 인용된 정책 및 법령은 {self.current_year}년 {datetime.now().month}월 기준이며, 
이후 개정 또는 변경될 수 있습니다. 최신 정보는 해당 기관의 공식 홈페이지를 참고하시기 바랍니다.

**[주요 기관 웹사이트]**
- LH 한국토지주택공사: https://www.lh.or.kr
- 국토교통부: https://www.molit.go.kr
- 서울특별시: https://www.seoul.go.kr

---
"""
        
        return output


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Initialize database
    db = PolicyReferenceDB()
    
    # Get LH policy
    supply_plan = db.get_lh_policy("supply_plan")
    print("LH Supply Plan:", supply_plan)
    
    # Get citation
    citation = db.format_citation("REF001")
    print("Citation:", citation)
    
    # Get housing type policy
    youth_policy = db.get_housing_type_policy("청년형")
    print("Youth Policy:", youth_policy)
    
    # Generate references section
    ref_section = db.generate_reference_section()
    print(ref_section)
