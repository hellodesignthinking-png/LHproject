"""
교통 접근성 점수 계산 모듈
Transport Accessibility Score Calculator

지하철 우선, 버스 후순위 평가 시스템
"""

from typing import Tuple, Dict, Any


def get_transport_score(
    subway_distance: float,
    bus_distance: float
) -> Tuple[float, str, Dict[str, Any]]:
    """
    교통 점수 계산 (지하철 최우선, 버스 후순위)
    
    Args:
        subway_distance: 가장 가까운 지하철역까지 거리 (m)
        bus_distance: 가장 가까운 버스 정류장까지 거리 (m)
    
    Returns:
        (점수, 등급, 상세정보) 튜플
        - 점수: 0.0 ~ 5.0
        - 등급: "S", "A", "B", "C", "D"
        - 상세정보: {"mode": "지하철/버스", "distance": ..., "comment": ...}
    """
    
    # Safe float conversion helper
    def safe_float(value):
        """None/0/"0"/"" 등 edge case를 안전하게 처리"""
        try:
            converted = float(value)
            # 0.0은 None으로 처리 (거리 정보 없음)
            return None if converted == 0.0 else converted
        except (TypeError, ValueError):
            return None
    
    subway = safe_float(subway_distance)
    bus = safe_float(bus_distance)
    
    # 1단계: 지하철역 거리 평가 (최우선)
    # subway가 유효한 값(None이 아니고 0보다 큼)일 때만 평가
    if subway is not None and subway > 0:
        if subway <= 500:
            score = 5.0
            grade = "S"
            mode = "지하철"
            comment = f"역세권 (지하철역 {subway:.0f}m) - 최우수 교통입지"
            
        elif subway <= 1000:
            score = 3.0
            grade = "A"
            mode = "지하철"
            comment = f"준역세권 (지하철역 {subway:.0f}m) - 우수한 교통입지"
            
        else:
            # 2단계: 지하철이 1000m 초과일 경우 버스 정류장 평가
            if bus is not None and bus > 0:
                if bus <= 50:
                    score = 3.5
                    grade = "A"
                    mode = "버스"
                    comment = f"버스 정류장 초근접 ({bus:.0f}m) - 양호한 교통입지"
                    
                elif bus <= 100:
                    score = 2.0
                    grade = "B"
                    mode = "버스"
                    comment = f"버스 정류장 근접 ({bus:.0f}m) - 보통 교통입지"
                    
                else:
                    score = 0.0
                    grade = "D"
                    mode = "도보"
                    comment = f"대중교통 접근 불량 (지하철 {subway:.0f}m, 버스 {bus:.0f}m)"
            else:
                # 버스 정보도 없음
                score = 0.0
                grade = "D"
                mode = "도보"
                comment = f"대중교통 접근 불량 (지하철 {subway:.0f}m, 버스 정보 없음)"
    else:
        # 지하철 정보가 없을 때 → 버스로 평가
        if bus is not None and bus > 0:
            if bus <= 50:
                score = 3.5
                grade = "A"
                mode = "버스"
                comment = f"버스 정류장 초근접 ({bus:.0f}m) - 양호한 교통입지"
                
            elif bus <= 100:
                score = 2.0
                grade = "B"
                mode = "버스"
                comment = f"버스 정류장 근접 ({bus:.0f}m) - 보통 교통입지"
                
            else:
                score = 0.0
                grade = "D"
                mode = "도보"
                comment = f"대중교통 접근 불량 (지하철 정보 없음, 버스 {bus:.0f}m)"
        else:
            # 지하철도 버스도 정보 없음
            score = 0.0
            grade = "D"
            mode = "도보"
            comment = "대중교통 정보 없음"
    
    details = {
        "mode": mode,
        "score": score,
        "grade": grade,
        "subway_distance": subway,
        "bus_distance": bus,
        "comment": comment
    }
    
    return score, grade, details


def calculate_5point_transport_score(subway_distance: float, bus_distance: float) -> float:
    """
    5.0 만점 기준 교통 점수 반환 (기존 시스템 호환용)
    
    Args:
        subway_distance: 지하철역 거리 (m)
        bus_distance: 버스 정류장 거리 (m)
    
    Returns:
        0.0 ~ 5.0 점수
    """
    score, _, _ = get_transport_score(subway_distance, bus_distance)
    return score


def get_transport_grade(score: float) -> str:
    """
    점수를 등급으로 변환
    
    Args:
        score: 교통 점수 (0.0 ~ 5.0)
    
    Returns:
        등급 문자열 ("S", "A", "B", "C", "D")
    """
    if score >= 5.0:
        return "S"
    elif score >= 3.5:
        return "A"
    elif score >= 2.0:
        return "B"
    elif score >= 1.0:
        return "C"
    else:
        return "D"


def get_transport_recommendations(
    subway_distance: float,
    bus_distance: float
) -> list:
    """
    교통 점수 기반 추천사항 생성
    
    Args:
        subway_distance: 지하철역 거리 (m)
        bus_distance: 버스 정류장 거리 (m)
    
    Returns:
        추천사항 리스트
    """
    recommendations = []
    
    if subway_distance <= 500:
        recommendations.append("✅ 역세권 강점을 마케팅 포인트로 적극 활용")
        recommendations.append("✅ 프리미엄 임대료 책정 가능")
        
    elif subway_distance <= 1000:
        recommendations.append("✅ 준역세권 입지, 도보 접근성 양호")
        recommendations.append("⚠️ 지하철역 방향 보행환경 개선 검토")
        
    elif subway_distance <= 1500:
        if bus_distance <= 100:
            recommendations.append("⚠️ 버스-지하철 환승 편의성 강조")
            recommendations.append("⚠️ 통근 셔틀버스 운영 검토")
        else:
            recommendations.append("❌ 교통 접근성 열위, 가격 경쟁력 확보 필요")
            recommendations.append("❌ 커뮤니티 버스 또는 셔틀 운영 필수 검토")
    else:
        recommendations.append("❌ 대중교통 접근 매우 불량, 대안 교통수단 필수")
        recommendations.append("❌ 자가용 이용자 타겟 전략 필요")
        
        if bus_distance <= 50:
            recommendations.append("⚠️ 버스 노선 및 배차간격 정밀 조사 필요")
    
    return recommendations


# 등급별 설명
GRADE_DESCRIPTIONS = {
    "S": "최우수 - 역세권 입지 (지하철역 500m 이내)",
    "A": "우수 - 준역세권 또는 버스 정류장 초근접",
    "B": "보통 - 버스 정류장 도보권",
    "C": "미흡 - 대중교통 접근 제한적",
    "D": "불량 - 대중교통 접근 매우 불량"
}


def get_grade_description(grade: str) -> str:
    """등급 설명 반환"""
    return GRADE_DESCRIPTIONS.get(grade, "등급 정보 없음")
