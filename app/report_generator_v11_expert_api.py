"""
ZeroSite v11.0 EXPERT EDITION - API Wrapper
============================================
This wrapper bridges the v9.1 API with the v11.0 Expert Edition generator

Philosophy:
- Form = v7.5 (Professional Consulting Style)
- Content = v11.0 Engine (AI-Powered Data)
- Narrative = Expert Edition (Strategic/Judgmental Tone)

Author: ZeroSite Team
Date: 2025-12-05
Version: v11.0 Expert Edition API Wrapper
"""

from typing import Dict, Any
from app.report_generator_v11_expert import ReportGeneratorV11Expert


def generate_v11_expert_report(
    address: str,
    land_area: float,
    land_appraisal_price: int,
    zone_type: str,
    analysis_result: Dict[str, Any]
) -> str:
    """
    ZeroSite v11.0 EXPERT EDITION Report Generator (API Entry Point)
    
    This function serves as the bridge between the v9.1 API and the 
    v11.0 Expert Edition generator.
    
    Key Differences from v11.0 Complete:
    - Uses NarrativeGeneratorV11Expert (not NarrativeGenerator)
    - Applies v7.5 professional typography
    - Intelligent data injection (no more zeros)
    - Strategic/judgmental tone throughout
    - Full Unit-Type Analysis chapter
    
    Args:
        address: 대상 부지 주소
        land_area: 토지 면적 (㎡)
        land_appraisal_price: 토지 감정가 (원)
        zone_type: 용도지역
        analysis_result: v9.1 REAL 분석 결과
    
    Returns:
        HTML string (60+ pages, Expert Edition format)
    """
    
    print("🎯 v11.0 EXPERT EDITION Report Generation Started...")
    print("   ✓ Form: v7.5 Professional Consulting Style")
    print("   ✓ Content: v11.0 AI-Powered Data Engine")
    print("   ✓ Narrative: Expert Edition (Strategic Tone)")
    
    # Initialize Expert Edition Generator
    generator = ReportGeneratorV11Expert()
    
    # Enhance analysis_result with API-provided data
    if "basic_info" not in analysis_result:
        analysis_result["basic_info"] = {}
    
    analysis_result["basic_info"]["address"] = address
    
    if "land_info" not in analysis_result:
        analysis_result["land_info"] = {}
    
    analysis_result["land_info"]["land_area"] = land_area
    analysis_result["land_info"]["land_appraisal_price"] = land_appraisal_price
    analysis_result["land_info"]["zone_type"] = zone_type
    
    # Generate Expert Edition Report
    html_report = generator.generate_expert_report(analysis_result)
    
    print("✅ v11.0 EXPERT EDITION Report Generated Successfully!")
    print(f"   📄 Report Length: {len(html_report):,} characters")
    print("   🎨 Typography: v7.5 Professional (11pt body, 10pt tables)")
    print("   📝 Tone: Strategic/Judgmental (not explanatory)")
    print("   📊 Data: Intelligent estimates (no zero values)")
    
    return html_report


# Alias for compatibility
generate_v11_ultra_pro_report_expert = generate_v11_expert_report
