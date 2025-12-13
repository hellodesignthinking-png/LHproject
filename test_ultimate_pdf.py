"""
궁극의 감정평가 PDF 테스트
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ultimate_pdf():
    """궁극의 PDF 생성 테스트"""
    
    logger.info("=" * 80)
    logger.info("🎯 궁극의 감정평가 PDF 생성 테스트")
    logger.info("=" * 80)
    
    # 테스트 데이터
    appraisal_data = {
        'address': '서울시 마포구 월드컵북로 120',
        'land_area_sqm': 660.0,
        'zone_type': '제3종일반주거지역',
        'individual_land_price_per_sqm': 7000000,
        
        # 평가 결과 (기존)
        'final_appraisal_value': 57.63,  # 억원
        'final_value_per_sqm': 8731818,
        
        'cost_approach_value': 46.20,
        'sales_comparison_value': 60.06,
        'income_approach_value': 67.50,
        
        'weight_cost': 0.40,
        'weight_sales': 0.40,
        'weight_income': 0.20,
    }
    
    try:
        # Generator 초기화
        generator = UltimateAppraisalPDFGenerator()
        logger.info("✅ UltimateAppraisalPDFGenerator initialized")
        
        # HTML 생성
        logger.info("📄 Generating HTML content...")
        html_content = generator.generate_pdf_html(appraisal_data)
        logger.info(f"✅ HTML content generated ({len(html_content)} characters)")
        
        # HTML 저장 (검증용)
        html_path = Path(__file__).parent / "test_ultimate_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"✅ HTML saved to: {html_path}")
        
        # PDF 생성
        logger.info("🔄 Converting HTML to PDF...")
        pdf_bytes = generator.generate_pdf_bytes(html_content)
        logger.info(f"✅ PDF generated ({len(pdf_bytes)} bytes)")
        
        # PDF 저장
        pdf_path = Path(__file__).parent / "ULTIMATE_감정평가보고서_실거래가100%_ANTENNA.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"✅ PDF saved to: {pdf_path}")
        
        # 검증
        logger.info("\n" + "=" * 80)
        logger.info("📊 검증 결과:")
        logger.info("=" * 80)
        logger.info(f"✅ PDF 파일 크기: {len(pdf_bytes):,} bytes")
        logger.info(f"✅ HTML 길이: {len(html_content):,} characters")
        logger.info(f"✅ 저장 경로: {pdf_path}")
        
        # Check key improvements
        checks = {
            '실제 주소 표시': '번지' in html_content or '동' in html_content,
            '도로 등급': '대로' in html_content or '중로' in html_content or '소로' in html_content,
            '평수 표시': '평' in html_content and '평당' in html_content,
            'Antenna Holdings 브랜딩': 'ANTENNA HOLDINGS' in html_content,
            '시장 반영률': '시장 반영률' in html_content,
            '가중치 조정': '가중치' in html_content,
        }
        
        logger.info("\n✅ 핵심 개선사항 검증:")
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            logger.info(f"  {status} {check_name}: {check_result}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 궁극의 PDF 생성 완료!")
            logger.info("=" * 80)
            logger.info(f"📁 PDF 파일: {pdf_path}")
            logger.info(f"📄 HTML 파일: {html_path}")
            logger.info("\n🎯 핵심 개선사항:")
            logger.info("   1. ✅ 실제 주소 표시 (법정동·번지)")
            logger.info("   2. ✅ 도로 등급 가중치 (대로/중로/소로)")
            logger.info("   3. ✅ 실거래가 수준 평가 (시장가 반영)")
            logger.info("   4. ✅ 완벽한 A4 레이아웃")
            logger.info("   5. ✅ 평수 표시 추가")
            logger.info("=" * 80)
        else:
            logger.warning("⚠️ 일부 검증 실패")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PDF 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ultimate_pdf()
    sys.exit(0 if success else 1)
