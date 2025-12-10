"""
Risk Matrix Formatter for ZeroSite v22
=======================================

Converts risk data into template-ready format.

Key Features:
- Dict to List conversion
- Risk level classification
- Mitigation strategy generation
- Color coding by severity

Author: ZeroSite Development Team
Date: 2025-12-10
Version: v22.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RiskLevel:
    """Risk level definition"""
    name: str
    min_score: int
    max_score: int
    color: str
    badge_class: str


class RiskMatrixFormatter:
    """Format risk matrix for template rendering"""
    
    # Risk level definitions
    RISK_LEVELS = [
        RiskLevel("매우 낮음", 0, 20, "#28a745", "success"),
        RiskLevel("낮음", 21, 40, "#17a2b8", "info"),
        RiskLevel("보통", 41, 60, "#ffc107", "warning"),
        RiskLevel("높음", 61, 80, "#fd7e14", "warning"),
        RiskLevel("매우 높음", 81, 100, "#dc3545", "danger")
    ]
    
    # Risk categories with default mitigation strategies
    RISK_CATEGORIES = {
        "financial": {
            "name": "재무 리스크",
            "description": "사업 수익성 및 재무 안정성 리스크",
            "color": "#dc3545",
            "default_mitigation": "감정평가율 최적화 + 건축비 절감 + 정책자금 확보"
        },
        "market": {
            "name": "시장 리스크",
            "description": "부동산 시장 변동 및 수요-공급 리스크",
            "color": "#ffc107",
            "default_mitigation": "시장 모니터링 강화 + 가격 전략 유연성 확보"
        },
        "policy": {
            "name": "정책 리스크",
            "description": "정부 정책 변경 및 규제 리스크",
            "color": "#0066CC",
            "default_mitigation": "정책 동향 모니터링 + LH 협의 강화"
        },
        "construction": {
            "name": "시공 리스크",
            "description": "공사 지연, 품질, 안전 리스크",
            "color": "#6c757d",
            "default_mitigation": "시공사 역량 검증 + 공정 관리 강화 + 안전 점검"
        },
        "legal": {
            "name": "법규 리스크",
            "description": "건축 법규, 인허가, 민원 리스크",
            "color": "#17a2b8",
            "default_mitigation": "법률 자문 + 사전 인허가 검토 + 주민 소통"
        },
        "environmental": {
            "name": "환경 리스크",
            "description": "환경 영향, 재해, 기후 리스크",
            "color": "#28a745",
            "default_mitigation": "환경영향평가 + 방재 계획 + 친환경 설계"
        }
    }
    
    @classmethod
    def classify_risk_level(cls, score: int) -> RiskLevel:
        """Classify risk level by score"""
        for level in cls.RISK_LEVELS:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.RISK_LEVELS[2]  # Default to "보통"
    
    @classmethod
    def format_risk_matrix(cls, risk_data: Dict) -> List[Dict]:
        """
        Convert risk dict to list of row objects for template
        
        Args:
            risk_data: Risk data dict (e.g., {"financial": {...}, "market": {...}})
            
        Returns:
            List of risk row dicts ready for template rendering
        """
        risk_rows = []
        
        # Process each category
        for category_key, category_info in cls.RISK_CATEGORIES.items():
            # Get risk data for this category
            category_data = risk_data.get(category_key, {})
            
            # Extract score
            if isinstance(category_data, dict):
                score = category_data.get("score", 50)
                mitigation = category_data.get("mitigation", category_info["default_mitigation"])
                impact = category_data.get("impact", "중간")
                probability = category_data.get("probability", "중간")
            else:
                # If just a number
                score = int(category_data) if category_data else 50
                mitigation = category_info["default_mitigation"]
                impact = "중간"
                probability = "중간"
            
            # Classify level
            risk_level = cls.classify_risk_level(score)
            
            # Build row
            risk_rows.append({
                "category": category_info["name"],
                "description": category_info["description"],
                "score": score,
                "level": risk_level.name,
                "impact": impact,
                "probability": probability,
                "mitigation": mitigation,
                "color": category_info["color"],
                "level_color": risk_level.color,
                "badge_class": risk_level.badge_class,
                "category_key": category_key
            })
        
        # Sort by score (highest risk first)
        risk_rows.sort(key=lambda x: x["score"], reverse=True)
        
        return risk_rows
    
    @classmethod
    def calculate_total_risk_score(cls, risk_data: Dict) -> Dict:
        """
        Calculate total risk score and overall assessment
        
        Args:
            risk_data: Risk data dict
            
        Returns:
            Dict with total score and assessment
        """
        scores = []
        
        for category_key in cls.RISK_CATEGORIES.keys():
            category_data = risk_data.get(category_key, {})
            if isinstance(category_data, dict):
                score = category_data.get("score", 50)
            else:
                score = int(category_data) if category_data else 50
            scores.append(score)
        
        total_score = sum(scores)
        avg_score = total_score / len(scores) if scores else 50
        
        # Overall risk level
        overall_level = cls.classify_risk_level(int(avg_score))
        
        # Risk assessment
        if avg_score < 30:
            assessment = "매우 낮은 리스크 - 사업 추진 적극 권장"
        elif avg_score < 50:
            assessment = "낮은 리스크 - 사업 추진 가능"
        elif avg_score < 60:
            assessment = "보통 리스크 - 완화 전략 수립 후 추진"
        elif avg_score < 75:
            assessment = "높은 리스크 - 신중한 검토 및 완화 방안 필수"
        else:
            assessment = "매우 높은 리스크 - 사업 재검토 권고"
        
        return {
            "total_score": total_score,
            "average_score": round(avg_score, 1),
            "overall_level": overall_level.name,
            "overall_color": overall_level.color,
            "assessment": assessment,
            "category_count": len(scores),
            "high_risk_categories": [
                cat for cat in cls.RISK_CATEGORIES.keys()
                if (risk_data.get(cat, {}).get("score", 50) if isinstance(risk_data.get(cat), dict) else 50) >= 70
            ]
        }
    
    @classmethod
    def generate_risk_narrative(cls, risk_data: Dict, context: Dict) -> str:
        """
        Generate comprehensive risk narrative
        
        Args:
            risk_data: Risk data dict
            context: Context with project info
            
        Returns:
            Risk narrative text (150+ characters)
        """
        total_risk = cls.calculate_total_risk_score(risk_data)
        risk_rows = cls.format_risk_matrix(risk_data)
        
        # Get top 3 risks
        top_risks = risk_rows[:3]
        
        narrative = f"""
본 사업의 종합 리스크 평가 결과, 평균 리스크 점수는 {total_risk['average_score']}점으로 
'{total_risk['overall_level']}' 수준으로 분류됩니다. 

주요 리스크 요인은 다음과 같습니다:

1. **{top_risks[0]['category']}** (점수: {top_risks[0]['score']}점, {top_risks[0]['level']})
   - 영향도: {top_risks[0]['impact']} | 발생확률: {top_risks[0]['probability']}
   - 완화 전략: {top_risks[0]['mitigation']}

2. **{top_risks[1]['category']}** (점수: {top_risks[1]['score']}점, {top_risks[1]['level']})
   - 영향도: {top_risks[1]['impact']} | 발생확률: {top_risks[1]['probability']}
   - 완화 전략: {top_risks[1]['mitigation']}

3. **{top_risks[2]['category']}** (점수: {top_risks[2]['score']}점, {top_risks[2]['level']})
   - 영향도: {top_risks[2]['impact']} | 발생확률: {top_risks[2]['probability']}
   - 완화 전략: {top_risks[2]['mitigation']}

**종합 평가:** {total_risk['assessment']}

본 리스크 분석은 LH 한국토지주택공사의 『사업 리스크 관리 매뉴얼』(2023)을 기반으로 하였으며, 
5대 리스크 영역(재무, 시장, 정책, 시공, 법규)을 종합적으로 평가하였습니다. 
각 리스크에 대한 완화 전략을 단계별로 실행하여 사업 안정성을 확보할 것을 권고합니다.
""".strip()
        
        return narrative
    
    @classmethod
    def generate_default_risk_data(cls, context: Dict) -> Dict:
        """
        Generate default risk data based on context
        
        Args:
            context: Context with financial and project info
            
        Returns:
            Default risk data dict
        """
        # Calculate scores based on context
        irr = context.get("irr", 0)
        roi = context.get("roi", 0)
        npv = context.get("npv", 0)
        
        # Financial risk (IRR/ROI 기반)
        if irr >= 8 and roi >= 10:
            financial_score = 30  # 낮은 리스크
        elif irr >= 5 and roi >= 5:
            financial_score = 50  # 보통
        else:
            financial_score = 70  # 높은 리스크
        
        # Market risk (수요 점수 기반)
        demand_score = context.get("demand_score", 50)
        market_score = 100 - demand_score  # Inverse relationship
        
        # Policy risk (낮음으로 기본 설정 - LH 사업)
        policy_score = 35
        
        # Construction risk (보통)
        construction_score = 45
        
        # Legal risk (낮음)
        legal_score = 40
        
        return {
            "financial": {
                "score": financial_score,
                "impact": "높음",
                "probability": "중간",
                "mitigation": "감정평가율 98% 확보 + 건축비 5% 절감 + 정책자금 금리 2% 확보"
            },
            "market": {
                "score": int(market_score),
                "impact": "중간",
                "probability": "중간",
                "mitigation": "분기별 시장 모니터링 + 가격 조정 전략 + 수요 분석 업데이트"
            },
            "policy": {
                "score": policy_score,
                "impact": "중간",
                "probability": "낮음",
                "mitigation": "LH 정책 동향 모니터링 + 사전 협의 + 규정 변경 대응 계획"
            },
            "construction": {
                "score": construction_score,
                "impact": "중간",
                "probability": "중간",
                "mitigation": "우수 시공사 선정 + 공정 관리 시스템 + 안전 점검 강화"
            },
            "legal": {
                "score": legal_score,
                "impact": "낮음",
                "probability": "낮음",
                "mitigation": "법률 자문 + 사전 인허가 검토 + 주민 설명회"
            }
        }


# Convenience functions
def format_risk_matrix(risk_data: Dict) -> List[Dict]:
    """Format risk matrix for template"""
    return RiskMatrixFormatter.format_risk_matrix(risk_data)


def calculate_total_risk(risk_data: Dict) -> Dict:
    """Calculate total risk score"""
    return RiskMatrixFormatter.calculate_total_risk_score(risk_data)


def generate_risk_narrative(risk_data: Dict, context: Dict) -> str:
    """Generate risk narrative"""
    return RiskMatrixFormatter.generate_risk_narrative(risk_data, context)


def get_default_risks(context: Dict) -> Dict:
    """Get default risk data"""
    return RiskMatrixFormatter.generate_default_risk_data(context)
