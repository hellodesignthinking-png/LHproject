"""
Multi-Language Support for ZeroSite v11.0
==========================================
Provides English translation for reports and analysis
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReportTranslator:
    """
    Translates Korean report content to English
    Maintains professional consulting tone
    """
    
    def __init__(self):
        self.translations = self._load_translations()
        logger.info("✅ Report Translator initialized (Korean ↔ English)")
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Load translation dictionaries
        """
        return {
            # Section Headers
            "headers": {
                "1.1 프로젝트 개요": "1.1 Project Overview",
                "1.2 핵심 분석 결과": "1.2 Key Analysis Results",
                "1.3 최종 권고사항": "1.3 Final Recommendations",
                "2.1 대지 특성 분석": "2.1 Site Characteristics Analysis",
                "2.2 10분 생활권 분석": "2.2 10-Minute Living Sphere Analysis",
                "2.3 교통 접근성 분석": "2.3 Transportation Accessibility",
                "3.1 법규 및 용도지역": "3.1 Regulations and Zoning",
                "3.2 건축 기준 분석": "3.2 Building Standards Analysis",
                "3.3 개발 계획 수립": "3.3 Development Plan Formulation",
                "4.1 시장 환경 분석": "4.1 Market Environment Analysis",
                "4.2 수요 예측": "4.2 Demand Forecast",
                "4.3 경쟁 현황": "4.3 Competition Analysis",
                "5.1 투자 규모 및 재원 조달": "5.1 Investment Scale & Financing",
                "5.2 수익성 분석": "5.2 Profitability Analysis",
                "5.3 시나리오 분석": "5.3 Scenario Analysis",
                "6.1 LH 평가 체계": "6.1 LH Evaluation System",
                "6.2 세부 평가 결과": "6.2 Detailed Evaluation Results",
                "6.3 등급 판정 및 해석": "6.3 Grade Assessment & Interpretation",
                "7.1 리스크 매트릭스": "7.1 Risk Matrix",
                "7.2 리스크 완화 전략": "7.2 Risk Mitigation Strategy",
                "8.1 종합 의견": "8.1 Comprehensive Opinion",
                "8.2 실행 로드맵": "8.2 Implementation Roadmap",
            },
            
            # Zone Types
            "zones": {
                "제1종일반주거지역": "Class 1 General Residential Zone",
                "제2종일반주거지역": "Class 2 General Residential Zone",
                "제3종일반주거지역": "Class 3 General Residential Zone",
                "준주거지역": "Semi-Residential Zone",
                "중심상업지역": "Central Commercial Zone",
                "일반상업지역": "General Commercial Zone",
                "근린상업지역": "Neighborhood Commercial Zone",
            },
            
            # Unit Types
            "unit_types": {
                "청년": "Youth",
                "신혼부부": "Newlywed",
                "고령자": "Senior",
                "일반": "General",
                "취약계층": "Vulnerable Group",
            },
            
            # Decisions
            "decisions": {
                "GO": "PROCEED",
                "REVIEW": "REVIEW",
                "NO-GO": "REJECT",
                "NO_GO": "REJECT",
                "사업 추진 권장": "Project Recommended",
                "조건부 추진": "Conditional Approval",
                "사업 중단 권장": "Project Not Recommended",
            },
            
            # Common Terms
            "terms": {
                "대지면적": "Land Area",
                "건폐율": "Building Coverage Ratio (BCR)",
                "용적률": "Floor Area Ratio (FAR)",
                "세대수": "Number of Units",
                "층수": "Number of Floors",
                "주차대수": "Parking Spaces",
                "건축비": "Construction Cost",
                "토지비": "Land Cost",
                "총 공사비": "Total Project Cost",
                "LH 매입가": "LH Purchase Price",
                "수익률": "Return Rate",
                "내부수익률": "Internal Rate of Return (IRR)",
                "자본환원율": "Capitalization Rate",
                "투자회수기간": "Payback Period",
                "순현재가치": "Net Present Value (NPV)",
                "점수": "Score",
                "등급": "Grade",
                "신뢰도": "Confidence",
                "리스크": "Risk",
                "추천": "Recommended",
                "세대유형": "Unit Type",
                "입지": "Location",
                "교통": "Transportation",
                "시장성": "Marketability",
                "재무": "Financial",
                "법규": "Regulation",
                "사업성": "Feasibility",
            },
            
            # Descriptive Phrases
            "phrases": {
                "분석 결과": "Analysis Results",
                "종합 평가": "Comprehensive Evaluation",
                "주요 특징": "Key Features",
                "강점": "Strengths",
                "약점": "Weaknesses",
                "기회": "Opportunities",
                "위협": "Threats",
                "전략적 제언": "Strategic Recommendations",
                "실행 방안": "Implementation Plan",
                "예상 효과": "Expected Outcomes",
                "주의사항": "Precautions",
                "다음 단계": "Next Steps",
            },
            
            # Report Metadata
            "metadata": {
                "보고서": "Report",
                "작성일": "Date",
                "대상지": "Site",
                "분석 버전": "Analysis Version",
                "컨설팅 리포트": "Consulting Report",
                "전문가 에디션": "Expert Edition",
            }
        }
    
    def translate_text(self, korean_text: str, category: str = "terms") -> str:
        """
        Translate Korean text to English
        
        Args:
            korean_text: Korean text to translate
            category: Translation category (headers, zones, terms, etc.)
        
        Returns:
            English translation or original text if not found
        """
        if category in self.translations:
            return self.translations[category].get(korean_text, korean_text)
        
        # Try all categories
        for cat_translations in self.translations.values():
            if korean_text in cat_translations:
                return cat_translations[korean_text]
        
        return korean_text
    
    def translate_section_header(self, korean_header: str) -> str:
        """Translate section header"""
        return self.translate_text(korean_header, "headers")
    
    def translate_zone_type(self, korean_zone: str) -> str:
        """Translate zone type"""
        return self.translate_text(korean_zone, "zones")
    
    def translate_unit_type(self, korean_unit: str) -> str:
        """Translate unit type"""
        return self.translate_text(korean_unit, "unit_types")
    
    def translate_decision(self, korean_decision: str) -> str:
        """Translate decision"""
        return self.translate_text(korean_decision, "decisions")
    
    def translate_report_html(self, html_content: str, language: str = "en") -> str:
        """
        Translate entire HTML report
        
        Args:
            html_content: Korean HTML report
            language: Target language (currently only 'en' supported)
        
        Returns:
            Translated HTML content
        """
        if language != "en":
            return html_content
        
        translated = html_content
        
        # Translate all categories
        for category, translations in self.translations.items():
            for korean, english in translations.items():
                # Use word boundaries to avoid partial matches
                # But be careful with HTML tags
                translated = translated.replace(korean, english)
        
        # Update version indicator
        translated = translated.replace(
            "ZeroSite v11.0",
            "ZeroSite v11.0 (English Edition)"
        )
        
        # Update language meta tag
        translated = translated.replace(
            'lang="ko"',
            'lang="en"'
        )
        
        return translated
    
    def translate_analysis_result(self, result: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """
        Translate analysis result dictionary
        
        Args:
            result: Analysis result dictionary
            language: Target language
        
        Returns:
            Translated result dictionary
        """
        if language != "en":
            return result
        
        translated = result.copy()
        
        # Translate zone type
        if "zone_type" in translated:
            translated["zone_type"] = self.translate_zone_type(translated["zone_type"])
        
        # Translate unit type
        if "recommended_unit_type" in translated:
            translated["recommended_unit_type"] = self.translate_unit_type(
                translated["recommended_unit_type"]
            )
        
        # Translate decision
        if "decision" in translated:
            translated["decision"] = self.translate_decision(translated["decision"])
        
        # Translate nested dictionaries
        if "unit_analysis" in translated and isinstance(translated["unit_analysis"], dict):
            for key in list(translated["unit_analysis"].keys()):
                english_key = self.translate_unit_type(key)
                if english_key != key:
                    translated["unit_analysis"][english_key] = translated["unit_analysis"].pop(key)
        
        return translated


# Global translator instance
translator = ReportTranslator()


def translate(text: str, category: str = "terms", language: str = "en") -> str:
    """
    Quick translation function
    
    Usage:
        translated = translate("세대수", category="terms")
    """
    if language == "ko":
        return text
    return translator.translate_text(text, category)


def get_language_config(language: str = "ko") -> Dict[str, str]:
    """
    Get language-specific configuration
    
    Returns:
        Dictionary with language-specific strings
    """
    if language == "en":
        return {
            "report_title": "ZeroSite v11.0 HYBRID - Expert Land Analysis Report",
            "generated_by": "Generated by ZeroSite AI Engine",
            "confidential": "CONFIDENTIAL - For Internal Use Only",
            "page": "Page",
            "of": "of",
            "table_of_contents": "Table of Contents",
            "executive_summary": "Executive Summary",
            "analysis_date": "Analysis Date",
            "report_version": "Report Version",
        }
    else:  # Korean (default)
        return {
            "report_title": "ZeroSite v11.0 HYBRID - 전문가급 토지 분석 리포트",
            "generated_by": "ZeroSite AI 엔진으로 생성",
            "confidential": "대외비 - 내부용",
            "page": "페이지",
            "of": "중",
            "table_of_contents": "목차",
            "executive_summary": "경영진 요약",
            "analysis_date": "분석일",
            "report_version": "리포트 버전",
        }
