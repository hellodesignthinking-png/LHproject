"""
Test PDF Generation
===================

Quick test to verify PDFGenerator works correctly
"""

from app.services.pdf_generator import PDFGenerator
from pathlib import Path

def test_pdf_generation():
    """Test basic PDF generation"""
    
    print("=" * 60)
    print("🧪 Testing PDF Generation")
    print("=" * 60)
    
    # Create PDF generator
    generator = PDFGenerator()
    print("✅ PDFGenerator initialized")
    
    # Mock Pre-Report data (simplified)
    mock_data = {
        "page_1_executive_summary": {
            "land_basic_info": {
                "address": "서울특별시 마포구 월드컵북로 120",
                "land_area_sqm": 660.0,
                "land_area_pyeong": 199.6,
                "zone_type": "제2종일반주거지역",
                "zone_type_formatted": "제2종일반주거지역 (FAR 250.0%, BCR 50.0%)"
            },
            "lh_possibility_gauge": "HIGH",
            "lh_possibility_icon": "🟢",
            "lh_possibility_color": "green",
            "lh_possibility_description": "본 토지는 LH 신축매입임대 사업에 매우 적합한 조건을 갖추고 있습니다.",
            "key_metrics": {
                "1_buildable_area": {
                    "label": "개발가능 연면적",
                    "value": 1650.0,
                    "value_pyeong": 499.1,
                    "unit": "㎡"
                },
                "2_estimated_units": {
                    "label": "예상 세대수",
                    "value": 23,
                    "range": "20~27세대",
                    "unit": "세대"
                },
                "3_recommended_supply_type": {
                    "label": "추천 공급유형",
                    "value": "행복주택",
                    "unit": ""
                }
            },
            "key_strengths": [
                "✓ 우수한 수익성 (예상 ROI 27.4%)",
                "✓ LH 공공주택 개발에 적합한 용도지역",
                "✓ 충분한 용적률로 세대수 확보 유리"
            ],
            "review_items": [
                "• 인허가 절차 사전 확인 권장"
            ]
        },
        "page_2_quick_analysis": {
            "development_overview_table": {
                "1_regulations": {
                    "item": "건폐율 / 용적률",
                    "value": "50.0% / 250.0%",
                    "note": "제2종일반주거지역"
                },
                "2_max_floors": {
                    "item": "예상 최고층수",
                    "value": "약 5층",
                    "note": "용적률 기준 추정"
                },
                "3_buildable_area": {
                    "item": "예상 연면적",
                    "value": "1,650.0㎡",
                    "note": "499.1평"
                },
                "4_estimated_units": {
                    "item": "예상 세대수",
                    "value": "약 23세대",
                    "note": "20~27세대 범위"
                },
                "5_required_parking": {
                    "item": "필요 주차대수",
                    "value": "약 23대",
                    "note": "세대당 1.0대 기준"
                }
            },
            "supply_type_visualization": {
                "chart_type": "horizontal_bar",
                "title": "공급유형별 수요 점수 (CH4 분석)",
                "data": [
                    {"type": "행복주택", "score": 15.2, "percentage": 76.0},
                    {"type": "청년", "score": 14.8, "percentage": 74.0},
                    {"type": "신혼부부", "score": 14.2, "percentage": 71.0},
                    {"type": "일반", "score": 13.5, "percentage": 67.5},
                    {"type": "공공임대", "score": 12.8, "percentage": 64.0}
                ],
                "note": "점수가 높을수록 해당 유형에 대한 지역 수요가 높음"
            },
            "next_steps_cta": {
                "title": "다음 단계: 종합보고서 계약 안내",
                "intro_text": "본 Pre-Report는 초기 검토용입니다.",
                "features": [
                    "✓ LH 매입가 적정성 분석",
                    "✓ 상세 수익성 분석 (IRR/ROI/NPV)",
                    "✓ 리스크 매트릭스 및 대응 방안"
                ],
                "report_types": [
                    "• 종합보고서 (Comprehensive Report): 15-20페이지",
                    "• Full Report: 60페이지"
                ],
                "contact_info": {
                    "title": "상담 문의",
                    "phone": "1234-5678",
                    "email": "contact@zerosite.com",
                    "note": "정식 계약 시 상세 분석 + 전문가 컨설팅 제공"
                }
            }
        }
    }
    
    metadata = {
        "report_id": "test-20251215-001",
        "created_at": "2025-12-15T12:00:00"
    }
    
    # Generate PDF
    try:
        print("\n📄 Generating Pre-Report PDF...")
        pdf_bytes = generator.generate("pre_report", mock_data, metadata)
        print(f"✅ PDF generated successfully ({len(pdf_bytes)} bytes)")
        
        # Save to file
        output_path = Path("output/test_reports")
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_file = output_path / "test_pre_report.pdf"
        generator.generate_to_file("pre_report", mock_data, str(output_file), metadata)
        print(f"✅ PDF saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    print("\n" + "=" * 60)
    if success:
        print("✅ PDF Generation Test PASSED")
    else:
        print("❌ PDF Generation Test FAILED")
    print("=" * 60)
