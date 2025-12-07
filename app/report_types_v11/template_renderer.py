"""
ZeroSite Phase 10: Template Renderer

Jinja2-based template rendering system for 5 report types.

Key Features:
    - Unified rendering interface
    - Custom filters for Korean formatting
    - Number formatting utilities
    - Date/time formatting
    - Template caching
"""

from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import locale


class TemplateRenderer:
    """
    Template rendering engine using Jinja2
    
    Provides consistent rendering interface for all report types.
    """
    
    def __init__(self, template_dir: Path = None):
        """
        Initialize template renderer
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir or Path("./app/report_templates_v11")
        
        # Ensure template directory exists
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_filters()
    
    def _register_filters(self):
        """Register custom Jinja2 filters"""
        
        # Number formatting
        self.env.filters['format_number'] = self.format_number
        self.env.filters['format_currency'] = self.format_currency
        self.env.filters['format_percent'] = self.format_percent
        self.env.filters['format_area'] = self.format_area
        
        # Date formatting
        self.env.filters['format_date'] = self.format_date
        self.env.filters['format_datetime'] = self.format_datetime
        
        # Grade formatting
        self.env.filters['grade_color'] = self.get_grade_color
        self.env.filters['grade_text'] = self.get_grade_text
        
        # Korean helpers
        self.env.filters['josa'] = self.add_josa
    
    @staticmethod
    def format_number(value: float, decimal_places: int = 0) -> str:
        """
        Format number with thousand separators
        
        Example: 1234567 -> "1,234,567"
        """
        if value is None:
            return "N/A"
        
        if decimal_places > 0:
            return f"{value:,.{decimal_places}f}"
        return f"{int(value):,}"
    
    @staticmethod
    def format_currency(value: float, unit: str = "원") -> str:
        """
        Format currency in Korean won
        
        Example: 1234567890 -> "12억 3,457만원"
        """
        if value is None:
            return "N/A"
        
        # Convert to Korean number system
        eok = int(value // 100000000)  # 억
        man = int((value % 100000000) // 10000)  # 만
        
        if eok > 0 and man > 0:
            return f"{eok:,}억 {man:,}만{unit}"
        elif eok > 0:
            return f"{eok:,}억{unit}"
        elif man > 0:
            return f"{man:,}만{unit}"
        else:
            return f"{int(value):,}{unit}"
    
    @staticmethod
    def format_percent(value: float, decimal_places: int = 1) -> str:
        """
        Format percentage
        
        Example: 0.1234 -> "12.3%"
        """
        if value is None:
            return "N/A"
        
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def format_area(value: float, unit: str = "㎡") -> str:
        """
        Format area with unit
        
        Example: 123.45 -> "123.5㎡"
        """
        if value is None:
            return "N/A"
        
        return f"{value:,.1f}{unit}"
    
    @staticmethod
    def format_date(value: str, format: str = "%Y년 %m월 %d일") -> str:
        """Format date string"""
        if not value:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime(format)
        except:
            return value
    
    @staticmethod
    def format_datetime(value: str, format: str = "%Y년 %m월 %d일 %H:%M") -> str:
        """Format datetime string"""
        if not value:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime(format)
        except:
            return value
    
    @staticmethod
    def get_grade_color(grade: str) -> str:
        """Get color for grade"""
        colors = {
            "A": "#27AE60",  # Green
            "B": "#2ECC71",  # Light Green
            "C": "#F39C12",  # Orange
            "D": "#E67E22",  # Dark Orange
            "E": "#E74C3C",  # Red
            "F": "#C0392B"   # Dark Red
        }
        return colors.get(grade, "#95A5A6")
    
    @staticmethod
    def get_grade_text(grade: str) -> str:
        """Get Korean text for grade"""
        texts = {
            "A": "최우수",
            "B": "우수",
            "C": "양호",
            "D": "보통",
            "E": "미흡",
            "F": "부적합"
        }
        return texts.get(grade, "평가 중")
    
    @staticmethod
    def add_josa(word: str, josa_type: str = "은는") -> str:
        """
        Add Korean josa (postposition)
        
        Example: 
            "학교" + "은는" -> "학교는"
            "집" + "은는" -> "집은"
        """
        if not word:
            return word
        
        # Get last character
        last_char = word[-1]
        
        # Check if last character has final consonant
        has_final = (ord(last_char) - 0xAC00) % 28 != 0
        
        if josa_type == "은는":
            return f"{word}{'은' if has_final else '는'}"
        elif josa_type == "이가":
            return f"{word}{'이' if has_final else '가'}"
        elif josa_type == "을를":
            return f"{word}{'을' if has_final else '를'}"
        elif josa_type == "과와":
            return f"{word}{'과' if has_final else '와'}"
        else:
            return word
    
    def render(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Render template with context
        
        Args:
            template_name: Template file name (e.g., "lh_submission.html.jinja2")
            context: Template context data
        
        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"Template rendering failed for '{template_name}': {str(e)}")
    
    def render_string(
        self,
        template_string: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Render template from string
        
        Args:
            template_string: Template string
            context: Template context data
        
        Returns:
            Rendered string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)


# Template mapping
TEMPLATE_MAP = {
    "lh_submission": "lh_submission.html.jinja2",
    "investor": "investor_report.html.jinja2",
    "construction": "construction_report.html.jinja2",
    "executive": "executive_summary.html.jinja2",
    "comparative": "comparative_analysis.html.jinja2"
}


def get_template_name(report_type: str) -> str:
    """Get template file name for report type"""
    template_name = TEMPLATE_MAP.get(report_type)
    if not template_name:
        raise ValueError(f"Unknown report type: {report_type}")
    return template_name


# Convenience function
def render_report(
    report_type: str,
    context: Dict[str, Any],
    template_dir: Path = None
) -> str:
    """
    Convenience function to render report
    
    Usage:
        html = render_report("lh_submission", {"decision": decision})
    """
    renderer = TemplateRenderer(template_dir)
    template_name = get_template_name(report_type)
    return renderer.render(template_name, context)
