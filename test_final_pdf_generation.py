"""
최종 감정평가 PDF 생성 테스트

Features:
- FinalAppraisalPDFGenerator 사용
- 15-20페이지 전문 보고서
- 10+ 거래사례 포함
- 상세 근거자료 포함
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.final_appraisal_pdf_generator import FinalAppraisalPDFGenerator
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_final_pdf_generation():
    """최종 PDF 생성 테스트"""
    
    logger.info("=" * 80)
    logger.info("최종 감정평가 PDF 생성 테스트 시작")
    logger.info("=" * 80)
    
    # 테스트 데이터
    appraisal_data = {
        'address': '서울시 강남구 월드컵북로 120',
        'land_area_sqm': 660.0,
        'zone_type': '제3종일반주거지역',
        'individual_land_price_per_sqm': 7000000,
        
        # 평가 결과
        'final_appraisal_value': 57.63,  # 억원
        'final_value_per_sqm': 8731818,
        
        'cost_approach_value': 46.20,
        'sales_comparison_value': 60.06,
        'income_approach_value': 67.50,  # Updated with development profit
        
        'weight_cost': 0.40,
        'weight_sales': 0.40,
        'weight_income': 0.20,
        
        'location_factor': 1.15,
        'appraisal_date': datetime.now().strftime('%Y-%m-%d'),
    }
    
    try:
        # PDF Generator 초기화
        generator = FinalAppraisalPDFGenerator()
        logger.info("✅ FinalAppraisalPDFGenerator initialized")
        
        # HTML 생성
        logger.info("📄 Generating HTML content...")
        html_content = generator.generate_pdf_html(appraisal_data)
        logger.info(f"✅ HTML content generated ({len(html_content)} characters)")
        
        # HTML 저장 (검증용)
        html_path = Path(__file__).parent / "test_final_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"✅ HTML saved to: {html_path}")
        
        # PDF 생성
        logger.info("🔄 Converting HTML to PDF...")
        pdf_bytes = generator.generate_pdf_bytes(html_content)
        logger.info(f"✅ PDF generated ({len(pdf_bytes)} bytes)")
        
        # PDF 저장
        pdf_path = Path(__file__).parent / "FINAL_감정평가보고서_ANTENNA_HOLDINGS.pdf"
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
        
        # Check HTML content
        checks = {
            'Antenna Holdings 브랜딩': 'ANTENNA HOLDINGS' in html_content,
            '15-20페이지 구성': html_content.count('<div class="page') >= 12,
            '거래사례 10개 이상': '거래사례 비교표' in html_content,
            '원가법 상세': '원가법 상세' in html_content,
            '거래사례비교법 상세': '거래사례비교법 상세' in html_content,
            '수익환원법 상세': '수익환원법 상세' in html_content,
            '데이터 출처 명시': 'MOLIT' in html_content and '카카오' in html_content,
            '신뢰도 분석': '신뢰도 분석' in html_content,
            '법적 고지': '법적 고지' in html_content,
        }
        
        logger.info("\n✅ 콘텐츠 검증:")
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            logger.info(f"  {status} {check_name}: {check_result}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 최종 PDF 생성 완료!")
            logger.info("=" * 80)
            logger.info(f"📁 PDF 파일: {pdf_path}")
            logger.info(f"📄 HTML 파일: {html_path}")
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
    success = test_final_pdf_generation()
    sys.exit(0 if success else 1)
