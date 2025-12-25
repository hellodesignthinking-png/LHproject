#!/usr/bin/env python3
"""
Generate Sample Reports for LH Review
LH 검토용 샘플 보고서 생성
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, '.')

from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

# Mock production data
MOCK_PRODUCTION_CONTEXT = {
    "context_id": "prod-sample-lh-001",
    "created_at": datetime.now().isoformat(),
    
    # M2: Land Appraisal
    "m2_result": {
        "calculation": {
            "final_appraised_total": 7500000000,
            "premium_adjusted_per_sqm": 49587000,
            "base_price_per_sqm": 12000000,
        },
        "confidence": {"overall_score": 0.82},
        "transaction_cases": [
            {"price": 5000000000, "date": "2024-06-15"},
            {"price": 6200000000, "date": "2024-08-20"},
            {"price": 7100000000, "date": "2024-10-10"},
            {"price": 7800000000, "date": "2024-11-25"},
            {"price": 8000000000, "date": "2024-12-05"},
        ]
    },
    
    # M3: Housing Type
    "m3_result": {
        "selected": {"name": "청년형", "total_score": 85, "confidence": 0.82},
        "alternatives": [
            {"name": "신혼부부형", "score": 78},
            {"name": "고령자형", "score": 62}
        ],
        "scores": {
            "청년형": {"total": 85},
            "신혼부부형": {"total": 78},
            "고령자형": {"total": 62}
        }
    },
    
    # M4: Capacity
    "m4_result": {
        "legal_capacity": {"total_units": 150, "parking_spaces": 180},
        "incentive_capacity": {"total_units": 180, "parking_spaces": 210},
        "recommended": {"scenario": "incentive", "total_units": 180}
    },
    
    # M5: Financial
    "m5_result": {
        "financials": {
            "npv_public": 1850000000,
            "npv_market": 2100000000,
            "irr_public": 0.185,
            "irr_market": 0.21,
            "roi": 0.263
        },
        "profitability": {"grade": "B", "score": 78.5, "is_profitable": True},
        "costs": {
            "total_cost": 5200000000,
            "land_acquisition": 7500000000,
            "construction": 3800000000
        }
    },
    
    # M6: LH Review
    "m6_result": {
        "decision": {
            "type": "CONDITIONAL",
            "rationale": "조건부 추진 권장 - 위치 우수, 사업성 양호, 일부 보완 필요"
        },
        "approval": {"probability": 0.72},
        "scores": {"total": 78.5},
        "grade": "B",
        "max_score": 100,
        "key_factors": ["위치 우수", "수요 적합", "사업성 양호"],
        "risks": ["주차 여건 검토 필요", "인근 경쟁 프로젝트 모니터링"]
    }
}

def generate_sample_reports(output_dir="sample_reports"):
    """샘플 보고서 생성"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"📄 GENERATING SAMPLE REPORTS FOR LH REVIEW")
    print(f"{'='*80}\n")
    print(f"Output directory: {output_dir}/")
    print(f"Context ID: {MOCK_PRODUCTION_CONTEXT['context_id']}\n")
    
    report_types = [
        ("all_in_one", "All-in-One Report", "🎯 PRIMARY - LH 제출용"),
        ("financial_feasibility", "Financial Feasibility", "💰 재무 상세 분석"),
        ("executive_summary", "Executive Summary", "📊 경영진 요약"),
    ]
    
    results = []
    
    for report_type, report_name, description in report_types:
        print(f"🔄 Generating: {report_name}...")
        print(f"   {description}")
        
        try:
            # Assemble
            assembled = assemble_final_report(
                report_type=report_type,
                canonical_data=MOCK_PRODUCTION_CONTEXT,
                context_id=MOCK_PRODUCTION_CONTEXT["context_id"]
            )
            
            # Render
            html = render_final_report_html(report_type, assembled)
            
            # Save
            filename = f"{report_type}_{MOCK_PRODUCTION_CONTEXT['context_id']}.html"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            file_size = os.path.getsize(filepath)
            
            print(f"   ✅ Saved: {filename}")
            print(f"   Size: {file_size:,} bytes ({len(html):,} characters)")
            print(f"   Path: {filepath}\n")
            
            results.append({
                "report_type": report_type,
                "filename": filename,
                "filepath": filepath,
                "size": file_size,
                "status": "success"
            })
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}\n")
            results.append({
                "report_type": report_type,
                "filename": None,
                "filepath": None,
                "size": 0,
                "status": "failed",
                "error": str(e)
            })
    
    # Summary
    print(f"{'='*80}")
    print(f"📋 SUMMARY")
    print(f"{'='*80}\n")
    
    successful = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    
    print(f"Total reports: {total}")
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total-successful}/{total}\n")
    
    if successful > 0:
        print(f"✅ Generated Files:")
        total_size = 0
        for r in results:
            if r["status"] == "success":
                print(f"   - {r['filename']:45} {r['size']:10,} bytes")
                total_size += r['size']
        print(f"\n   Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)\n")
    
    print(f"{'='*80}")
    print(f"🎯 NEXT STEPS")
    print(f"{'='*80}\n")
    print(f"1. Review generated HTML files in '{output_dir}/' directory")
    print(f"2. Open in browser to verify visual quality")
    print(f"3. Send to LH reviewers with feedback template")
    print(f"4. Template: LH_REVIEWER_FEEDBACK_TEMPLATE.md\n")
    
    return results


if __name__ == "__main__":
    results = generate_sample_reports()
    
    # Exit code
    successful = sum(1 for r in results if r["status"] == "success")
    if successful == len(results):
        sys.exit(0)
    else:
        sys.exit(1)
