"""
Phase 4.0 - Unified Design System for Final Reports
디자인/폰트/색상 통합 시스템

This module provides:
- Unified CSS with CSS variables
- Font system (Pretendard + JetBrains Mono)
- Color palette with brand colors per report type
- Typography scale (8 levels)
- Spacing system
- Improved KPI box design
"""

from typing import Dict


class DesignSystem:
    """통합 디자인 시스템 - Phase 4.0"""
    
    @staticmethod
    def get_font_imports() -> str:
        """웹 폰트 임포트 (Pretendard + JetBrains Mono)"""
        return """
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
        """
    
    @staticmethod
    def get_css_variables() -> str:
        """CSS 변수 정의 (색상, 폰트, 간격)"""
        return """
        :root {
            /* === 폰트 시스템 === */
            --font-primary: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            --font-mono: 'JetBrains Mono', 'Courier New', monospace;
            --font-fallback: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            
            /* === 타이포그래피 스케일 === */
            --text-xs: 11px;
            --text-sm: 12px;
            --text-base: 14px;
            --text-lg: 16px;
            --text-xl: 18px;
            --text-2xl: 20px;
            --text-3xl: 24px;
            --text-4xl: 28px;
            
            /* === 간격 시스템 === */
            --space-xs: 8px;
            --space-sm: 12px;
            --space-md: 16px;
            --space-lg: 24px;
            --space-xl: 32px;
            --space-2xl: 48px;
            --space-3xl: 64px;
            
            /* === 공통 색상 === */
            --color-primary: #2563EB;
            --color-success: #10B981;
            --color-warning: #F59E0B;
            --color-danger: #EF4444;
            --color-neutral: #64748B;
            
            /* === 텍스트 색상 === */
            --color-text-primary: #1F2937;
            --color-text-secondary: #64748B;
            --color-text-muted: #9CA3AF;
            
            /* === 배경 색상 === */
            --color-bg-primary: #FFFFFF;
            --color-bg-secondary: #F9FAFB;
            --color-bg-accent: #EFF6FF;
            --color-bg-muted: #F3F4F6;
            
            /* === 테두리 === */
            --border-color: #E5E7EB;
            --border-radius-sm: 4px;
            --border-radius-md: 6px;
            --border-radius-lg: 8px;
            
            /* === 그림자 === */
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* === 보고서별 브랜드 색상 === */
        .report-color-landowner {
            --report-brand-color: #2563EB;
            --report-bg-light: #EFF6FF;
            --report-bg-lighter: #DBEAFE;
        }
        
        .report-color-quick_check {
            --report-brand-color: #F59E0B;
            --report-bg-light: #FFFBEB;
            --report-bg-lighter: #FEF3C7;
        }
        
        .report-color-financial_feasibility {
            --report-brand-color: #10B981;
            --report-bg-light: #ECFDF5;
            --report-bg-lighter: #D1FAE5;
        }
        
        .report-color-lh_technical {
            --report-brand-color: #374151;
            --report-bg-light: #F9FAFB;
            --report-bg-lighter: #F3F4F6;
        }
        
        .report-color-all_in_one {
            --report-brand-color: #6B7280;
            --report-bg-light: #F9FAFB;
            --report-bg-lighter: #F3F4F6;
        }
        
        .report-color-executive_summary {
            --report-brand-color: #8B5CF6;
            --report-bg-light: #F5F3FF;
            --report-bg-lighter: #EDE9FE;
        }
        """
    
    @staticmethod
    def get_base_typography() -> str:
        """기본 타이포그래피 스타일"""
        return """
        /* === 기본 타이포그래피 === */
        body.final-report {
            font-family: var(--font-primary);
            font-size: var(--text-base);
            line-height: 1.6;
            color: var(--color-text-primary);
            max-width: 1200px;
            margin: 0 auto;
            padding: var(--space-2xl);
        }
        
        body.final-report h1 {
            font-size: var(--text-3xl);
            font-weight: 700;
            margin: 0 0 var(--space-lg) 0;
            color: var(--color-text-primary);
        }
        
        body.final-report h2 {
            font-size: var(--text-2xl);
            font-weight: 700;
            margin: var(--space-2xl) 0 var(--space-md) 0;
            padding-bottom: var(--space-sm);
            border-bottom: 2px solid var(--report-brand-color, var(--color-primary));
            color: var(--color-text-primary);
        }
        
        body.final-report h3 {
            font-size: var(--text-xl);
            font-weight: 700;
            margin: var(--space-xl) 0 var(--space-sm) 0;
            color: var(--color-text-primary);
        }
        
        body.final-report h4 {
            font-size: var(--text-lg);
            font-weight: 600;
            margin: var(--space-lg) 0 var(--space-sm) 0;
            color: var(--color-text-secondary);
        }
        
        body.final-report p {
            font-size: var(--text-base);
            line-height: 1.7;
            margin: var(--space-md) 0;
            color: var(--color-text-primary);
        }
        
        body.final-report .text-muted {
            color: var(--color-text-muted);
            font-size: var(--text-sm);
        }
        
        body.final-report .text-caption {
            font-size: var(--text-xs);
            color: var(--color-text-muted);
            font-style: italic;
        }
        """
    
    @staticmethod
    def get_layout_styles() -> str:
        """레이아웃 스타일"""
        return """
        /* === 레이아웃 === */
        body.final-report .section {
            margin: var(--space-2xl) 0;
        }
        
        body.final-report .module-section {
            page-break-before: auto;
            page-break-inside: avoid;
            margin: var(--space-2xl) 0;
            padding: var(--space-xl);
            background: var(--color-bg-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-lg);
        }
        
        body.final-report .cover-page {
            text-align: center;
            padding: 100px var(--space-lg);
            border-bottom: 2px solid var(--report-brand-color, var(--color-primary));
            page-break-after: always;
        }
        
        body.final-report .executive-summary {
            background: var(--report-bg-light);
            padding: var(--space-xl);
            border-left: 4px solid var(--report-brand-color, var(--color-primary));
            margin: var(--space-xl) 0;
            border-radius: var(--border-radius-md);
            page-break-after: always;
        }
        
        body.final-report .final-judgment {
            background: var(--report-bg-lighter);
            padding: var(--space-xl);
            border-left: 4px solid var(--color-warning);
            margin: var(--space-xl) 0;
            border-radius: var(--border-radius-md);
        }
        """
    
    @staticmethod
    def get_kpi_styles() -> str:
        """KPI 박스 & 카드 스타일 (개선된 디자인)"""
        return """
        /* === KPI 박스 (개선) === */
        .kpi-summary-box {
            background: var(--color-bg-primary);
            border: 2px solid var(--report-brand-color, var(--color-primary));
            border-left: 6px solid var(--report-brand-color, var(--color-primary));
            border-radius: var(--border-radius-lg);
            padding: var(--space-xl);
            margin: var(--space-xl) 0;
            page-break-inside: avoid !important;
        }
        
        .kpi-summary-box h3 {
            margin: 0 0 var(--space-lg) 0;
            color: var(--report-brand-color, var(--color-primary));
            font-size: var(--text-2xl);
            font-weight: 700;
        }
        
        .kpi-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--space-lg);
        }
        
        .kpi-card {
            background: var(--color-bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-md);
            padding: var(--space-lg);
            text-align: center;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
        }
        
        .kpi-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .kpi-label {
            font-size: var(--text-sm);
            color: var(--color-text-secondary);
            margin-bottom: var(--space-sm);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .kpi-value {
            font-size: var(--text-3xl);
            font-weight: 700;
            color: var(--report-brand-color, var(--color-primary));
            font-family: var(--font-mono);
            margin: var(--space-sm) 0;
        }
        
        .kpi-description {
            font-size: var(--text-xs);
            color: var(--color-text-muted);
            margin-top: var(--space-xs);
        }
        
        /* === Decision Block === */
        .decision-block {
            background: var(--report-bg-light);
            border-left: 4px solid var(--report-brand-color, var(--color-primary));
            padding: var(--space-xl);
            margin: var(--space-xl) 0;
            border-radius: var(--border-radius-md);
            page-break-inside: avoid;
        }
        
        .decision-block h3 {
            color: var(--report-brand-color, var(--color-primary));
            margin: 0 0 var(--space-md) 0;
        }
        """
    
    @staticmethod
    def get_table_styles() -> str:
        """테이블 스타일"""
        return """
        /* === 테이블 === */
        body.final-report table {
            width: 100%;
            border-collapse: collapse;
            margin: var(--space-lg) 0;
            font-size: var(--text-sm);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-md);
            overflow: hidden;
        }
        
        body.final-report table thead {
            background: var(--color-bg-secondary);
        }
        
        body.final-report table thead th {
            font-weight: 700;
            color: var(--color-text-primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: var(--text-xs);
        }
        
        body.final-report table th,
        body.final-report table td {
            padding: var(--space-md);
            text-align: left;
            border: 1px solid var(--border-color);
        }
        
        body.final-report table tbody tr:hover {
            background: var(--color-bg-accent);
        }
        
        body.final-report table td.numeric {
            text-align: right;
            font-family: var(--font-mono);
            font-weight: 600;
        }
        
        body.final-report table td.highlight {
            font-weight: 700;
            color: var(--report-brand-color, var(--color-primary));
        }
        """
    
    @staticmethod
    def get_print_styles() -> str:
        """인쇄 스타일"""
        return """
        /* === 인쇄 스타일 === */
        @media print {
            body.final-report {
                padding: 20mm;
                max-width: 100%;
            }
            
            .module-section,
            .kpi-summary-box,
            .decision-block {
                page-break-inside: avoid;
            }
            
            .kpi-card {
                box-shadow: none !important;
                transform: none !important;
            }
            
            body.final-report table {
                page-break-inside: auto;
            }
            
            body.final-report tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }
        }
        """
    
    @staticmethod
    def get_complete_css() -> str:
        """완전한 통합 CSS 반환"""
        return "\n".join([
            DesignSystem.get_font_imports(),
            DesignSystem.get_css_variables(),
            DesignSystem.get_base_typography(),
            DesignSystem.get_layout_styles(),
            DesignSystem.get_kpi_styles(),
            DesignSystem.get_table_styles(),
            DesignSystem.get_print_styles(),
        ])


def get_report_brand_class(report_type: str) -> str:
    """보고서 타입에 맞는 브랜드 색상 클래스 반환"""
    mapping = {
        "landowner_summary": "report-color-landowner",
        "quick_check": "report-color-quick_check",
        "financial_feasibility": "report-color-financial_feasibility",
        "lh_technical": "report-color-lh_technical",
        "all_in_one": "report-color-all_in_one",
        "executive_summary": "report-color-executive_summary",
    }
    return mapping.get(report_type, "report-color-landowner")
