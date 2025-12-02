"""
ROI 모델 라우터
ROI Model Router

사용자 선택에 따라 LH 단가 모델 또는 시장기반 모델로 라우팅
"""

from typing import Dict, Any, Union
import logging

from app.services.roi_lh import calculate_lh_roi, format_lh_result_for_report, LHROIResult
from app.services.roi_market import calculate_market_roi, format_market_result_for_report, MarketROIResult

logger = logging.getLogger(__name__)


def calculate_roi(
    model_type: str,  # "LH 매입단가 기반" 또는 "시장기반(Real Market) 모델"
    **kwargs
) -> Union[LHROIResult, MarketROIResult]:
    """
    모델 타입에 따라 적절한 ROI 계산 함수 호출
    
    Args:
        model_type: "LH 매입단가 기반" 또는 "시장기반(Real Market) 모델"
        **kwargs: 각 모델별 필요한 파라미터
    
    Returns:
        LHROIResult 또는 MarketROIResult 객체
    
    Raises:
        ValueError: 지원하지 않는 model_type
    """
    
    try:
        if model_type == "LH 매입단가 기반":
            logger.info("🏢 LH 매입단가 기반 ROI 계산 시작")
            result = run_lh_model(**kwargs)
            
        elif model_type == "시장기반(Real Market) 모델":
            logger.info("📊 시장기반 ROI 계산 시작")
            result = run_market_model(**kwargs)
            
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
        
        logger.info(f"✅ ROI 계산 완료: {result.roi_percentage:.2f}%")
        return result
        
    except Exception as e:
        logger.error(f"❌ ROI 계산 오류: {e}")
        raise


def run_lh_model(**kwargs) -> LHROIResult:
    """
    LH 매입단가 기반 모델 실행
    
    필수 파라미터:
        - units: 세대수
        - unit_area: 전용면적 (㎡)
        - construction_cost_per_sqm: ㎡당 공사비
        - total_floor_area: 연면적 (㎡)
    
    선택 파라미터:
        - year: LH 단가 적용 연도 (기본: "2024")
        - unit_type: 세대유형 (기본: "청년")
        - other_cost_ratio: 기타비용 비율 (기본: 0.10)
    """
    
    # 필수 파라미터 검증
    required_params = ["units", "unit_area", "construction_cost_per_sqm", "total_floor_area"]
    for param in required_params:
        if param not in kwargs:
            raise ValueError(f"LH 모델 필수 파라미터 누락: {param}")
    
    # 기본값 설정
    year = kwargs.get("year", "2024")
    unit_type = kwargs.get("unit_type", "청년")
    other_cost_ratio = kwargs.get("other_cost_ratio", 0.10)
    
    result = calculate_lh_roi(
        units=kwargs["units"],
        unit_area=kwargs["unit_area"],
        construction_cost_per_sqm=kwargs["construction_cost_per_sqm"],
        total_floor_area=kwargs["total_floor_area"],
        year=year,
        unit_type=unit_type,
        other_cost_ratio=other_cost_ratio
    )
    
    return result


def run_market_model(**kwargs) -> MarketROIResult:
    """
    시장기반(Real Market) 모델 실행
    
    필수 파라미터:
        - land_area: 대지면적 (㎡)
        - total_floor_area: 연면적 (㎡)
        - units: 세대수
        - unit_area: 전용면적 (㎡)
        - construction_cost_per_pyeong: 평당 건축비 (원/평)
    
    선택 파라미터:
        - region: 지역 (기본: "서울")
        - difficulty: 난이도 (기본: "평지")
        - other_cost_ratio: 기타비용 비율 (기본: 0.10)
        - sale_discount: 매각 할인율 (기본: 0.85)
        - custom_land_price: 사용자 지정 토지 단가 (원/㎡)
        - custom_sale_price: 사용자 지정 매각 단가 (원/㎡)
    """
    
    # 필수 파라미터 검증
    required_params = [
        "land_area", "total_floor_area", "units", 
        "unit_area", "construction_cost_per_pyeong"
    ]
    for param in required_params:
        if param not in kwargs:
            raise ValueError(f"시장 모델 필수 파라미터 누락: {param}")
    
    # 기본값 설정
    region = kwargs.get("region", "서울")
    difficulty = kwargs.get("difficulty", "평지")
    other_cost_ratio = kwargs.get("other_cost_ratio", 0.10)
    sale_discount = kwargs.get("sale_discount", 0.85)
    custom_land_price = kwargs.get("custom_land_price", None)
    custom_sale_price = kwargs.get("custom_sale_price", None)
    
    result = calculate_market_roi(
        land_area=kwargs["land_area"],
        total_floor_area=kwargs["total_floor_area"],
        units=kwargs["units"],
        unit_area=kwargs["unit_area"],
        construction_cost_per_pyeong=kwargs["construction_cost_per_pyeong"],
        region=region,
        difficulty=difficulty,
        other_cost_ratio=other_cost_ratio,
        sale_discount=sale_discount,
        custom_land_price=custom_land_price,
        custom_sale_price=custom_sale_price
    )
    
    return result


def calculate_both_models(**kwargs) -> Dict[str, Any]:
    """
    두 모델을 모두 실행하고 결과 비교
    
    Args:
        **kwargs: 두 모델에 필요한 모든 파라미터
    
    Returns:
        두 모델의 결과를 포함한 딕셔너리
        {
            "lh_model": {...},
            "market_model": {...},
            "comparison": {...}
        }
    """
    
    results = {
        "lh_model": None,
        "market_model": None,
        "comparison": None
    }
    
    # LH 모델 실행
    try:
        lh_result = run_lh_model(**kwargs)
        results["lh_model"] = format_lh_result_for_report(lh_result)
    except Exception as e:
        logger.warning(f"⚠️ LH 모델 계산 실패: {e}")
        results["lh_model"] = {
            "error": str(e),
            "model_type": "LH 매입단가 기반",
            "total_cost": {"formatted": "N/A"},
            "revenue": {"formatted": "N/A"},
            "roi": {"formatted": "N/A"},
            "feasibility": "계산 불가"
        }
    
    # 시장 모델 실행
    try:
        market_result = run_market_model(**kwargs)
        results["market_model"] = format_market_result_for_report(market_result)
    except Exception as e:
        logger.warning(f"⚠️ 시장 모델 계산 실패: {e}")
        results["market_model"] = {
            "error": str(e),
            "model_type": "시장기반(Real Market)",
            "total_cost": {"formatted": "N/A"},
            "revenue": {"formatted": "N/A"},
            "roi": {"formatted": "N/A"},
            "feasibility": "계산 불가"
        }
    
    # 비교 분석
    results["comparison"] = _generate_comparison(
        results["lh_model"],
        results["market_model"]
    )
    
    return results


def _generate_comparison(lh_result: Dict, market_result: Dict) -> Dict[str, Any]:
    """
    두 모델 결과 비교 분석
    
    Args:
        lh_result: LH 모델 결과
        market_result: 시장 모델 결과
    
    Returns:
        비교 분석 결과
    """
    
    comparison = {
        "roi_difference": "N/A",
        "better_model": "판단 불가",
        "comment": "",
        "recommendation": ""
    }
    
    # 오류 체크
    if "error" in lh_result or "error" in market_result:
        comparison["comment"] = "일부 모델 계산 실패로 비교 불가"
        return comparison
    
    # ROI 차이 계산
    lh_roi = lh_result["roi"]["value"]
    market_roi = market_result["roi"]["value"]
    roi_diff = abs(lh_roi - market_roi)
    
    comparison["roi_difference"] = f"{roi_diff:.2f}%p"
    
    # 더 나은 모델 판단
    if lh_roi > market_roi:
        comparison["better_model"] = "LH 매입단가 기반"
        comparison["comment"] = f"LH 모델이 {roi_diff:.2f}%p 더 높은 수익률"
    elif market_roi > lh_roi:
        comparison["better_model"] = "시장기반(Real Market)"
        comparison["comment"] = f"시장 모델이 {roi_diff:.2f}%p 더 높은 수익률"
    else:
        comparison["better_model"] = "동일"
        comparison["comment"] = "두 모델의 수익률이 동일"
    
    # 추천사항 생성
    if lh_roi >= 10 and market_roi >= 15:
        comparison["recommendation"] = "✅ 두 모델 모두 수익성 확보 - 사업 추진 권장"
    elif lh_roi >= 10:
        comparison["recommendation"] = "⚠️ LH 매입 방식 추천 - 안정적 수익 확보"
    elif market_roi >= 15:
        comparison["recommendation"] = "⚠️ 시장 매각 방식 추천 - 높은 수익 잠재력"
    else:
        comparison["recommendation"] = "❌ 두 모델 모두 수익성 미흡 - 사업 재검토 필요"
    
    return comparison


def format_comparison_for_pdf(lh_result: Dict, market_result: Dict) -> str:
    """
    PDF 보고서용 비교표 HTML 생성
    
    Args:
        lh_result: LH 모델 결과
        market_result: 시장 모델 결과
    
    Returns:
        HTML 테이블 문자열
    """
    
    html = f"""
    <h3 style="margin-top: 30px; color: #0066cc;">사업성 분석 모델 비교</h3>
    <table style="width: 95%; margin: 15px auto; font-size: 9.5pt;">
        <thead>
            <tr style="background: #667eea; color: white;">
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">항목</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">LH 단가 모델</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">시장기반 모델</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">총사업비</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{lh_result["total_cost"]["formatted"]}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{market_result["total_cost"]["formatted"]}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">매각가/매입가</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{lh_result["revenue"]["formatted"]}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{market_result["revenue"]["formatted"]}</td>
            </tr>
            <tr style="background: #e3f2fd;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">ROI</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #0066cc;">{lh_result["roi"]["formatted"]}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; color: #0066cc;">{market_result["roi"]["formatted"]}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">결론</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{lh_result["feasibility"]}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{market_result["feasibility"]}</td>
            </tr>
        </tbody>
    </table>
    """
    
    return html
