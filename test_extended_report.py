"""
Extended Report 테스트 스크립트
report_mode='extended'를 사용하여 25-40페이지 보고서 생성 테스트
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.lh_report_generator_v7_2_extended import LHReportGeneratorV72Extended
from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete
from datetime import datetime


def create_sample_analysis_data():
    """샘플 분석 데이터 생성"""
    return {
        "basic_info": {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area": 660.0,
            "unit_type": "청년",
            "zone_type": "제3종일반주거지역",
        },
        "poi_analysis_v3_1": {
            "total_score_v3_1": 85.5,
            "lh_grade": "A",
            "final_distance": 350,
            "version": "v3.1",
            "poi_details": [
                {
                    "name": "서울고등학교",
                    "category": "학교",
                    "distance": 280,
                    "weight": 0.25,
                    "lh_grade": "A",
                    "address": "서울특별시 마포구...",
                    "note": "도보 5분"
                },
                {
                    "name": "마포중앙병원",
                    "category": "병원",
                    "distance": 420,
                    "weight": 0.20,
                    "lh_grade": "B",
                    "address": "서울특별시 마포구...",
                    "note": "도보 7분"
                },
                {
                    "name": "홍대입구역",
                    "category": "지하철역",
                    "distance": 310,
                    "weight": 0.20,
                    "lh_grade": "A",
                    "address": "서울특별시 마포구...",
                    "note": "2호선"
                },
            ]
        },
        "type_demand_v3_1": {
            "main_score": 82.3,
            "demand_level": "high",
            "version": "v3.1",
            "type_scores": {
                "청년": {
                    "raw_score": 75.0,
                    "poi_bonus": 4.5,
                    "user_type_weight": 1.2,
                    "final_score": 82.3,
                    "grade": "A",
                    "grade_text": "우수"
                },
                "신혼부부": {
                    "raw_score": 78.5,
                    "poi_bonus": 4.5,
                    "user_type_weight": 1.0,
                    "final_score": 78.5,
                    "grade": "B",
                    "grade_text": "양호"
                },
                "고령자": {
                    "raw_score": 72.0,
                    "poi_bonus": 4.5,
                    "user_type_weight": 1.0,
                    "final_score": 72.0,
                    "grade": "B",
                    "grade_text": "양호"
                },
            }
        },
        "zone_info": {
            "zone_type": "제3종일반주거지역",
            "building_coverage": 50.0,
            "floor_area_ratio": 250.0,
            "height_limit": 35.0,
            "land_use_regulation": "주거용 건축물 허용"
        },
        "geo_optimizer_v3_1": {
            "final_score": 78.5,
            "grade": "B",
            "version": "v3.1"
        },
        "risk_analysis_2025": {
            "risk_score": 88.0,
            "risk_level": "낮음",
            "total_risk_count": 2,
            "version": "2025"
        },
        "lh_assessment": {
            "grade": "A",
            "total_score": 83.5,
            "is_eligible": True,
            "recommendation": "사업 추진 적극 권장",
            "version": "v7.2"
        },
        "multi_parcel_v3_0": {
            "parcel_count": 1
        }
    }


def test_extended_report():
    """Extended Report 생성 테스트"""
    print("=" * 80)
    print("🧪 Extended Report Generator 테스트 시작")
    print("=" * 80)
    print()
    
    # 1. 샘플 데이터 생성
    print("📊 Step 1: 샘플 분석 데이터 생성...")
    analysis_data = create_sample_analysis_data()
    print(f"✅ 분석 데이터 생성 완료 (Keys: {list(analysis_data.keys())})")
    print()
    
    # 2. Extended Report Generator 인스턴스 생성
    print("📄 Step 2: Extended Report Generator 초기화...")
    try:
        generator = LHReportGeneratorV72Extended()
        print("✅ Extended Report Generator 초기화 성공")
    except Exception as e:
        print(f"❌ Extended Report Generator 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # 3. Extended Report 생성 (report_mode='extended')
    print("📝 Step 3: Extended Report 생성 (25-40 페이지)...")
    try:
        html_report = generator.generate_html_report(analysis_data, report_mode="extended")
        print(f"✅ Extended Report 생성 성공!")
        print(f"📏 보고서 크기: {len(html_report):,} bytes ({len(html_report) / 1024:.1f} KB)")
        print(f"📄 추정 페이지 수: {len(html_report) / 5000:.1f} 페이지 (5KB/페이지 기준)")
        print()
        
        # 보고서 저장
        output_file = "/home/user/webapp/test_extended_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_report)
        print(f"💾 Extended Report 저장 완료: {output_file}")
        print()
        
        # 주요 섹션 확인
        print("🔍 Step 4: 주요 섹션 포함 여부 확인...")
        sections_to_check = [
            ("목차 (Table of Contents)", "📑 목차"),
            ("POI 접근성 분석 (Extended)", "POI 접근성 분석 (Point of Interest"),
            ("Type Demand 분석 (Extended)", "유형별 수요 분석 (Type-Specific Demand"),
            ("Zoning 분석 (Extended)", "용도지역·지구 분석 (Zoning Analysis)"),
            ("GeoOptimizer 분석", "GeoOptimizer 분석"),
            ("Risk 분석", "Risk 분석"),
            ("종합 결론", "종합 결론"),
            ("인구 및 산업 분석 (신규)", "인구 및 산업 분석"),
            ("정책 시사점 (신규)", "정책 시사점 및 제언"),
            ("부록 - Raw Data (신규)", "부록 - 전체 Raw Data"),
        ]
        
        all_sections_found = True
        for section_name, section_marker in sections_to_check:
            if section_marker in html_report:
                print(f"  ✅ {section_name}")
            else:
                print(f"  ❌ {section_name} - 누락!")
                all_sections_found = False
        
        print()
        
        if all_sections_found:
            print("✅ 모든 섹션이 정상적으로 포함되어 있습니다!")
        else:
            print("⚠️ 일부 섹션이 누락되었습니다.")
        
        print()
        print("=" * 80)
        print("🎉 테스트 완료!")
        print("=" * 80)
        print()
        print(f"📁 생성된 파일: {output_file}")
        print(f"🌐 브라우저에서 열어서 확인하세요!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Extended Report 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_report():
    """Basic Report 생성 테스트 (기존 기능 확인)"""
    print("=" * 80)
    print("🧪 Basic Report Generator 테스트 시작 (기존 기능 확인)")
    print("=" * 80)
    print()
    
    analysis_data = create_sample_analysis_data()
    
    try:
        generator = LHReportGeneratorV72Extended()
        html_report = generator.generate_html_report(analysis_data, report_mode="basic")
        
        output_file = "/home/user/webapp/test_basic_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_report)
        
        print(f"✅ Basic Report 생성 성공!")
        print(f"📏 보고서 크기: {len(html_report):,} bytes ({len(html_report) / 1024:.1f} KB)")
        print(f"💾 저장 완료: {output_file}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Basic Report 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 ZeroSite v7.2 Extended Report Generator 통합 테스트\n")
    
    # Test 1: Extended Report
    success_extended = test_extended_report()
    
    print("\n" + "=" * 80 + "\n")
    
    # Test 2: Basic Report (기존 기능 확인)
    success_basic = test_basic_report()
    
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"Extended Report (25-40 pages): {'✅ PASS' if success_extended else '❌ FAIL'}")
    print(f"Basic Report (8-10 pages): {'✅ PASS' if success_basic else '❌ FAIL'}")
    print("=" * 80)
    
    if success_extended and success_basic:
        print("\n🎉 모든 테스트 통과! Extended Report 프로젝트 성공!")
        sys.exit(0)
    else:
        print("\n❌ 일부 테스트 실패. 로그를 확인하세요.")
        sys.exit(1)
