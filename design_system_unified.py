"""
Design/Font/Color Enhancement Plan
===================================

CURRENT STATE (from generated reports):
✅ Font: Noto Sans KR already used
✅ Basic CSS: Present with gradients
✅ KPI boxes: Styled with borders
⚠️ Need improvement: Consistency, spacing, colors

ENHANCEMENT AREAS:
1. Font System Standardization
2. Color Palette Unification
3. Spacing & Layout Consistency
4. Typography Hierarchy
5. KPI Box Enhancement
6. Print/PDF Optimization

TARGET: Professional, consistent, print-ready design
"""

# ============================================================================
# 1. UNIFIED FONT SYSTEM
# ============================================================================

FONT_SYSTEM = """
/* Professional Korean Font Stack */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

body.final-report {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.7;
    letter-spacing: -0.02em;
    color: #1a1a1a;
}

/* Typography Scale */
h1 { font-size: 28px; font-weight: 700; line-height: 1.3; }
h2 { font-size: 22px; font-weight: 700; line-height: 1.4; }
h3 { font-size: 18px; font-weight: 600; line-height: 1.4; }
h4 { font-size: 16px; font-weight: 600; line-height: 1.5; }
p  { font-size: 14px; font-weight: 400; line-height: 1.7; }

.small-text { font-size: 12px; }
.large-text { font-size: 16px; }
"""


# ============================================================================
# 2. UNIFIED COLOR PALETTE (Professional Theme)
# ============================================================================

COLOR_PALETTE = {
    # Primary Colors (Report Type Specific)
    "landowner": {
        "primary": "#2563EB",      # Blue - Trust, Stability
        "secondary": "#DBEAFE",
        "gradient": "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)"
    },
    "quick_check": {
        "primary": "#DC2626",      # Red - Urgency, Quick Action
        "secondary": "#FEE2E2",
        "gradient": "linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%)"
    },
    "financial": {
        "primary": "#059669",      # Green - Growth, Profit
        "secondary": "#D1FAE5",
        "gradient": "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)"
    },
    "lh_technical": {
        "primary": "#4B5563",      # Gray - Professional, Technical
        "secondary": "#F3F4F6",
        "gradient": "linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%)"
    },
    "executive": {
        "primary": "#7C3AED",      # Purple - Premium, Executive
        "secondary": "#EDE9FE",
        "gradient": "linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%)"
    },
    "all_in_one": {
        "primary": "#EA580C",      # Orange - Comprehensive, All-inclusive
        "secondary": "#FFEDD5",
        "gradient": "linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)"
    },
    
    # Neutral Colors (Universal)
    "text": {
        "primary": "#1a1a1a",
        "secondary": "#4a4a4a",
        "tertiary": "#6b6b6b",
        "disabled": "#9ca3af"
    },
    "background": {
        "white": "#ffffff",
        "light": "#f9fafb",
        "medium": "#f3f4f6",
        "dark": "#e5e7eb"
    },
    
    # Semantic Colors
    "status": {
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6"
    }
}


# ============================================================================
# 3. SPACING SYSTEM (8px base)
# ============================================================================

SPACING_SYSTEM = """
/* Consistent Spacing System (8px base) */
:root {
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;
}

/* Margins */
.m-0 { margin: 0; }
.m-sm { margin: var(--space-sm); }
.m-md { margin: var(--space-md); }
.m-lg { margin: var(--space-lg); }

.mt-md { margin-top: var(--space-md); }
.mb-md { margin-bottom: var(--space-md); }
.my-md { margin-top: var(--space-md); margin-bottom: var(--space-md); }

/* Paddings */
.p-md { padding: var(--space-md); }
.p-lg { padding: var(--space-lg); }
.p-xl { padding: var(--space-xl); }
"""


# ============================================================================
# 4. ENHANCED KPI BOX DESIGN
# ============================================================================

KPI_BOX_ENHANCED = """
/* Professional KPI Summary Box */
.kpi-summary-box {
    background: var(--report-gradient);
    border-left: 6px solid var(--report-primary);
    border-radius: 12px;
    padding: 32px;
    margin: 32px 0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    page-break-inside: avoid;
}

.kpi-summary-box h2 {
    color: var(--report-primary);
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 24px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--report-primary);
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.kpi-item {
    background: white;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;
}

.kpi-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.kpi-label {
    font-size: 13px;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--report-primary);
    line-height: 1.2;
}

.kpi-unit {
    font-size: 14px;
    font-weight: 400;
    color: #9ca3af;
    margin-left: 4px;
}
"""


# ============================================================================
# 5. TABLE DESIGN ENHANCEMENT
# ============================================================================

TABLE_DESIGN = """
/* Professional Table Design */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 24px 0;
    font-size: 13px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

thead {
    background: var(--report-primary);
    color: white;
}

thead th {
    padding: 14px 16px;
    font-weight: 600;
    text-align: left;
    font-size: 13px;
    letter-spacing: 0.03em;
}

tbody tr {
    border-bottom: 1px solid #e5e7eb;
    transition: background-color 0.15s ease;
}

tbody tr:hover {
    background-color: #f9fafb;
}

tbody tr:last-child {
    border-bottom: none;
}

tbody td {
    padding: 12px 16px;
    color: #374151;
}

tbody td:first-child {
    font-weight: 500;
    color: #1f2937;
}

/* Alternating row colors */
tbody tr:nth-child(even) {
    background-color: #f9fafb;
}
"""


# ============================================================================
# 6. PRINT/PDF OPTIMIZATION
# ============================================================================

PRINT_OPTIMIZATION = """
/* Print & PDF Optimization */
@media print {
    body.final-report {
        font-size: 11pt;
        line-height: 1.5;
        color: #000;
        max-width: 100%;
        padding: 0;
        margin: 0;
    }
    
    .kpi-summary-box,
    .decision-block,
    .module-section {
        page-break-inside: avoid;
        box-shadow: none;
    }
    
    h1, h2, h3 {
        page-break-after: avoid;
    }
    
    table {
        page-break-inside: avoid;
    }
    
    /* Remove unnecessary elements in print */
    .no-print {
        display: none !important;
    }
    
    /* Ensure colors print correctly */
    * {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}

@page {
    size: A4;
    margin: 20mm;
}
"""


# ============================================================================
# 7. COMPLETE UNIFIED CSS
# ============================================================================

def generate_complete_css(report_type: str) -> str:
    """Generate complete CSS for a report type"""
    
    colors = COLOR_PALETTE.get(report_type, COLOR_PALETTE["landowner"])
    
    return f"""
/* ================================================
   ZEROSITE FINAL REPORT - UNIFIED DESIGN SYSTEM
   Report Type: {report_type}
   Version: v4.3-unified
   ================================================ */

{FONT_SYSTEM}

/* Report-Specific Color Variables */
:root {{
    --report-primary: {colors['primary']};
    --report-secondary: {colors['secondary']};
    --report-gradient: {colors['gradient']};
    
    --text-primary: {COLOR_PALETTE['text']['primary']};
    --text-secondary: {COLOR_PALETTE['text']['secondary']};
    --bg-white: {COLOR_PALETTE['background']['white']};
    --bg-light: {COLOR_PALETTE['background']['light']};
}}

{SPACING_SYSTEM}

{KPI_BOX_ENHANCED}

{TABLE_DESIGN}

{PRINT_OPTIMIZATION}

/* Additional Professional Touches */
.cover-page {{
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: var(--report-gradient);
    page-break-after: always;
}}

.cover-page h1 {{
    font-size: 42px;
    font-weight: 700;
    color: var(--report-primary);
    margin-bottom: 16px;
}}

.cover-page .subtitle {{
    font-size: 18px;
    color: var(--text-secondary);
    margin-bottom: 48px;
}}

.executive-summary {{
    background: var(--report-gradient);
    border-left: 6px solid var(--report-primary);
    border-radius: 12px;
    padding: 32px;
    margin: 32px 0;
    page-break-inside: avoid;
}}

.final-judgment {{
    background: #fef3c7;
    border-left: 6px solid #f59e0b;
    border-radius: 12px;
    padding: 32px;
    margin: 32px 0;
    page-break-inside: avoid;
}}

.module-section {{
    margin: 40px 0;
    padding: 32px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    page-break-inside: avoid;
}}

.source-reference {{
    font-size: 12px;
    color: var(--text-secondary);
    font-style: italic;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
}}

/* Copyright Footer */
.copyright-footer {{
    margin-top: 80px;
    padding: 24px;
    text-align: center;
    font-size: 12px;
    color: #9ca3af;
    border-top: 1px solid #e5e7eb;
}}

/* Watermark */
body.final-report::before {{
    content: 'ZEROSITE';
    position: fixed;
    top: 20px;
    right: 30px;
    font-size: 14px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.1);
    letter-spacing: 3px;
    z-index: 9999;
    pointer-events: none;
}}
"""


if __name__ == "__main__":
    print("Design System Ready!")
    print(f"Report Types: {list(COLOR_PALETTE.keys())[:6]}")
    print(f"Font: Noto Sans KR")
    print(f"Spacing: 8px base system")
    print(f"Status: Ready for implementation")
