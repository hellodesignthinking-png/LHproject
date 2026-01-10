"""
Phase 8: 템플릿 렌더링 서비스
================================

Jinja2를 사용하여 Phase 8 템플릿을 렌더링하는 서비스

작성일: 2026-01-10
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 템플릿 디렉토리 설정
TEMPLATES_DIR = Path(__file__).parent.parent / "templates_v13"

# Jinja2 환경 설정
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)


class Phase8TemplateRenderer:
    """Phase 8 템플릿 렌더링 서비스"""
    
    def __init__(self):
        """초기화"""
        self.env = jinja_env
        logger.info("Phase8 Template Renderer initialized")
    
    def render_m6_report(self, data: Dict[str, Any]) -> str:
        """
        M6 종합 판단 보고서 렌더링
        
        Args:
            data: M6 보고서 데이터 (M6ComprehensiveDecisionReport 변환 후)
            
        Returns:
            렌더링된 HTML 문자열
        """
        try:
            template = self.env.get_template("m6_comprehensive_decision_report.html")
            html = template.render(**data)
            logger.info("M6 report rendered successfully")
            return html
        except Exception as e:
            logger.error(f"Failed to render M6 report: {str(e)}")
            raise
    
    def render_comprehensive_report(self, data: Dict[str, Any]) -> str:
        """
        종합 최종보고서(Type A) 렌더링
        
        Args:
            data: 종합 보고서 데이터
            
        Returns:
            렌더링된 HTML 문자열
        """
        try:
            template = self.env.get_template("master_comprehensive_report.html")
            html = template.render(**data)
            logger.info("Comprehensive report rendered successfully")
            return html
        except Exception as e:
            logger.error(f"Failed to render comprehensive report: {str(e)}")
            raise


# 싱글톤 인스턴스
_renderer = None

def get_template_renderer() -> Phase8TemplateRenderer:
    """템플릿 렌더러 싱글톤 가져오기"""
    global _renderer
    if _renderer is None:
        _renderer = Phase8TemplateRenderer()
    return _renderer
