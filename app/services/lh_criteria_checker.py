"""
LH 신축매입임대 공고문 기준 심사 로직
- 입지 기준 체크
- 규모 기준 체크
- 사업성 기준 체크
- 종합 등급 산정 (A/B/C)
- 버전별 LH 규칙 적용 (2024/2025/2026)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from app.services.lh_rules import get_lh_rules, get_grade_thresholds, get_category_weights


class Grade(str, Enum):
    """사업 등급"""
    A = "A"  # 우수 - 매입 적극 권장
    B = "B"  # 양호 - 매입 검토 가능
    C = "C"  # 부적합 - 매입 부적격


class CheckStatus(str, Enum):
    """체크 상태"""
    PASS = "통과"
    FAIL = "부적합"
    WARNING = "주의"
    INFO = "참고"


@dataclass
class CheckItem:
    """체크리스트 항목"""
    category: str  # 카테고리 (입지/규모/사업성/법규)
    item: str  # 항목명
    status: CheckStatus  # 상태
    value: str  # 실제 값
    standard: str  # 기준 값
    description: str  # 상세 설명
    score: float = 0.0  # 점수 (0-100)


@dataclass
class GradeResult:
    """등급 평가 결과"""
    grade: Grade  # 최종 등급
    total_score: float  # 총점 (0-100)
    category_scores: Dict[str, float]  # 카테고리별 점수
    checklist: List[CheckItem]  # 체크리스트
    summary: str  # 종합 의견
    recommendations: List[str]  # 개선 권장사항


class LHCriteriaChecker:
    """LH 신축매입임대 기준 검증 (버전별 규칙 지원)"""
    
    def __init__(
        self,
        custom_weights: Optional[Dict[str, float]] = None,
        lh_version: str = "2024"
    ):
        """
        초기화
        
        Args:
            custom_weights: 사용자 정의 가중치 (예: {"입지": 35, "규모": 20, "사업성": 30, "법규": 15})
            lh_version: LH 기준 버전 ("2024", "2025", "2026")
        """
        self.lh_version = lh_version
        
        # 버전별 LH 규칙 로드
        self.lh_rules = get_lh_rules(lh_version)
        self.grade_thresholds = get_grade_thresholds(lh_version)
        
        # 카테고리 가중치 설정
        default_weights = get_category_weights(lh_version)
        
        if custom_weights:
            # 한글 키를 영문 키로 매핑
            key_mapping = {
                "location": "입지",
                "scale": "규모",
                "business": "사업성",
                "regulation": "법규"
            }
            self.category_weights = {}
            for eng_key, kor_key in key_mapping.items():
                if eng_key in custom_weights:
                    self.category_weights[kor_key] = custom_weights[eng_key]
                else:
                    self.category_weights[kor_key] = default_weights[kor_key]
        else:
            self.category_weights = default_weights.copy()
    
    def check_all(
        self,
        location_data: Dict[str, Any],
        building_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        zone_data: Dict[str, Any]
    ) -> GradeResult:
        """
        전체 기준 검증 및 등급 산정
        
        Args:
            location_data: 입지 정보
            building_data: 건축 정보
            financial_data: 재무 정보
            zone_data: 용도지역 정보
            
        Returns:
            GradeResult 객체
        """
        checklist = []
        
        # 1. 입지 기준 체크
        location_checks = self._check_location(location_data)
        checklist.extend(location_checks)
        
        # 2. 규모 기준 체크
        scale_checks = self._check_scale(building_data)
        checklist.extend(scale_checks)
        
        # 3. 사업성 기준 체크
        financial_checks = self._check_financial(financial_data, building_data)
        checklist.extend(financial_checks)
        
        # 4. 법규 기준 체크
        regulation_checks = self._check_regulations(zone_data, building_data)
        checklist.extend(regulation_checks)
        
        # 5. 카테고리별 점수 계산
        category_scores = self._calculate_category_scores(checklist)
        
        # 6. 총점 계산 (가중 평균)
        total_score = sum(
            score * self.category_weights[category] / 100
            for category, score in category_scores.items()
        )
        
        # 7. 등급 산정
        grade = self._determine_grade(total_score)
        
        # 8. 종합 의견 생성
        summary = self._generate_summary(grade, total_score, category_scores)
        
        # 9. 개선 권장사항
        recommendations = self._generate_recommendations(checklist)
        
        return GradeResult(
            grade=grade,
            total_score=round(total_score, 2),
            category_scores=category_scores,
            checklist=checklist,
            summary=summary,
            recommendations=recommendations
        )
    
    def _check_location(self, location_data: Dict[str, Any]) -> List[CheckItem]:
        """입지 기준 체크"""
        checks = []
        
        # 1. 역세권 접근성 (지하철역 800m 이내 우수)
        subway_distance = location_data.get('nearest_subway_distance', float('inf'))
        if subway_distance <= 800:
            status = CheckStatus.PASS
            score = 100
            desc = "역세권 입지 (도보 10분 이내)"
        elif subway_distance <= 1500:
            status = CheckStatus.WARNING
            score = 70
            desc = "역세권 인근 (도보 15~20분)"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "역세권 접근성 부족"
        
        checks.append(CheckItem(
            category="입지",
            item="지하철역 접근성",
            status=status,
            value=f"{int(subway_distance)}m",
            standard="800m 이내 우수",
            description=desc,
            score=score
        ))
        
        # 2. 생활편의시설 접근성
        accessibility_score = location_data.get('accessibility_score', 0)
        if accessibility_score >= 70:
            status = CheckStatus.PASS
            score = 100
            desc = "우수한 생활편의시설 접근성"
        elif accessibility_score >= 50:
            status = CheckStatus.WARNING
            score = 70
            desc = "보통 수준의 생활편의시설"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "생활편의시설 부족"
        
        checks.append(CheckItem(
            category="입지",
            item="생활편의시설",
            status=status,
            value=f"{accessibility_score:.0f}점",
            standard="70점 이상",
            description=desc,
            score=score
        ))
        
        # 3. 유해시설 이격거리
        harmful_facilities = location_data.get('harmful_facilities', [])
        critical_count = sum(1 for f in harmful_facilities if f.get('distance', 999) < 50)
        
        if critical_count == 0:
            status = CheckStatus.PASS
            score = 100
            desc = "유해시설 적정 이격"
        elif critical_count <= 2:
            status = CheckStatus.WARNING
            score = 60
            desc = f"유해시설 {critical_count}개 인접"
        else:
            status = CheckStatus.FAIL
            score = 30
            desc = f"유해시설 {critical_count}개 과다 인접"
        
        checks.append(CheckItem(
            category="입지",
            item="유해시설 이격",
            status=status,
            value=f"{critical_count}개 (50m 이내)",
            standard="0개",
            description=desc,
            score=score
        ))
        
        # 4. 학교/교육시설 접근성 (다자녀/신혼부부형)
        school_distance = location_data.get('nearest_school_distance', float('inf'))
        if school_distance <= 500:
            status = CheckStatus.PASS
            score = 100
            desc = "초등학교 근접 (학군 우수)"
        elif school_distance <= 1000:
            status = CheckStatus.INFO
            score = 80
            desc = "초등학교 도보 가능"
        else:
            status = CheckStatus.WARNING
            score = 50
            desc = "학교 접근성 보통"
        
        checks.append(CheckItem(
            category="입지",
            item="학교 접근성",
            status=status,
            value=f"{int(school_distance)}m",
            standard="500m 이내 우수",
            description=desc,
            score=score
        ))
        
        return checks
    
    def _check_scale(self, building_data: Dict[str, Any]) -> List[CheckItem]:
        """규모 기준 체크"""
        checks = []
        
        # 1. 세대수 기준 (LH 선호: 30세대 이상)
        units = building_data.get('units', 0)
        if units >= 50:
            status = CheckStatus.PASS
            score = 100
            desc = "적정 사업 규모 (효율적 운영)"
        elif units >= 30:
            status = CheckStatus.WARNING
            score = 80
            desc = "최소 사업 규모 충족"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "사업 규모 미달"
        
        checks.append(CheckItem(
            category="규모",
            item="세대수",
            status=status,
            value=f"{units}세대",
            standard="30세대 이상",
            description=desc,
            score=score
        ))
        
        # 2. 주차대수 기준 (세대당 0.5대 이상)
        parking_spaces = building_data.get('parking_spaces', 0)
        parking_ratio = parking_spaces / units if units > 0 else 0
        
        if parking_ratio >= 0.7:
            status = CheckStatus.PASS
            score = 100
            desc = "주차 여유 충분"
        elif parking_ratio >= 0.5:
            status = CheckStatus.WARNING
            score = 80
            desc = "주차 최소 기준 충족"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "주차 공간 부족"
        
        checks.append(CheckItem(
            category="규모",
            item="주차대수",
            status=status,
            value=f"{parking_spaces}대 (세대당 {parking_ratio:.2f}대)",
            standard="세대당 0.5대 이상",
            description=desc,
            score=score
        ))
        
        # 3. 층수 적정성 (5~15층 적정)
        floors = building_data.get('floors', 0)
        if 5 <= floors <= 15:
            status = CheckStatus.PASS
            score = 100
            desc = "적정 층수 (관리 효율적)"
        elif 3 <= floors < 5:
            status = CheckStatus.INFO
            score = 85
            desc = "저층 건물 (관리 용이)"
        elif floors > 15:
            status = CheckStatus.WARNING
            score = 70
            desc = "고층 건물 (관리비 증가)"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "층수 부적합"
        
        checks.append(CheckItem(
            category="규모",
            item="층수",
            status=status,
            value=f"{floors}층",
            standard="5~15층 적정",
            description=desc,
            score=score
        ))
        
        # 4. 세대 면적 적정성 (전용 25~45㎡)
        unit_area = building_data.get('average_unit_area', 0)
        if 25 <= unit_area <= 45:
            status = CheckStatus.PASS
            score = 100
            desc = "LH 표준 평형"
        elif 20 <= unit_area < 25 or 45 < unit_area <= 50:
            status = CheckStatus.WARNING
            score = 75
            desc = "평형 기준 근접"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "평형 부적합"
        
        checks.append(CheckItem(
            category="규모",
            item="세대 면적",
            status=status,
            value=f"{unit_area:.1f}㎡",
            standard="25~45㎡",
            description=desc,
            score=score
        ))
        
        return checks
    
    def _check_financial(
        self,
        financial_data: Dict[str, Any],
        building_data: Dict[str, Any]
    ) -> List[CheckItem]:
        """사업성 기준 체크"""
        checks = []
        
        # 1. 세대당 사업비 (LH 매입 기준: 1억 5천만원 내외)
        cost_per_unit = financial_data.get('cost_per_unit', 0)
        lh_target = 150_000_000  # 1억 5천만원
        
        if cost_per_unit <= lh_target * 0.9:
            status = CheckStatus.PASS
            score = 100
            desc = "매입 단가 우수 (LH 기준 대비 10% 절감)"
        elif cost_per_unit <= lh_target * 1.1:
            status = CheckStatus.WARNING
            score = 80
            desc = "매입 단가 적정 (LH 기준 ±10%)"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "매입 단가 초과 (LH 기준 10% 초과)"
        
        checks.append(CheckItem(
            category="사업성",
            item="세대당 사업비",
            status=status,
            value=f"{cost_per_unit/100_000_000:.2f}억원",
            standard=f"{lh_target/100_000_000:.1f}억원 내외",
            description=desc,
            score=score
        ))
        
        # 2. 예상 수익률
        profit_rate = financial_data.get('profit_rate', 0)
        if profit_rate >= 10:
            status = CheckStatus.PASS
            score = 100
            desc = "높은 수익성 (10% 이상)"
        elif profit_rate >= 5:
            status = CheckStatus.WARNING
            score = 75
            desc = "보통 수익성 (5~10%)"
        else:
            status = CheckStatus.FAIL
            score = 30
            desc = "수익성 부족 (5% 미만)"
        
        checks.append(CheckItem(
            category="사업성",
            item="예상 수익률",
            status=status,
            value=f"{profit_rate:.1f}%",
            standard="5% 이상",
            description=desc,
            score=score
        ))
        
        # 3. 평당 건축비 적정성
        construction_cost_per_pyeong = financial_data.get('cost_per_pyeong', 0) * 10000
        if construction_cost_per_pyeong <= 500 * 10000:
            status = CheckStatus.PASS
            score = 100
            desc = "건축비 적정"
        elif construction_cost_per_pyeong <= 600 * 10000:
            status = CheckStatus.WARNING
            score = 75
            desc = "건축비 보통"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "건축비 과다"
        
        checks.append(CheckItem(
            category="사업성",
            item="평당 건축비",
            status=status,
            value=f"{construction_cost_per_pyeong/10000:.0f}만원/평",
            standard="500만원/평 이하",
            description=desc,
            score=score
        ))
        
        # 4. 토지비 비중 (총 사업비 대비 30~40% 적정)
        total_cost = financial_data.get('total_project_cost', 1)
        land_cost = financial_data.get('land_cost', 0)
        land_ratio = (land_cost / total_cost * 100) if total_cost > 0 else 0
        
        if 25 <= land_ratio <= 45:
            status = CheckStatus.PASS
            score = 100
            desc = "토지비 비중 적정"
        elif 20 <= land_ratio < 25 or 45 < land_ratio <= 55:
            status = CheckStatus.WARNING
            score = 75
            desc = "토지비 비중 주의"
        else:
            status = CheckStatus.FAIL
            score = 40
            desc = "토지비 비중 부적합"
        
        checks.append(CheckItem(
            category="사업성",
            item="토지비 비중",
            status=status,
            value=f"{land_ratio:.1f}%",
            standard="25~45%",
            description=desc,
            score=score
        ))
        
        return checks
    
    def _check_regulations(
        self,
        zone_data: Dict[str, Any],
        building_data: Dict[str, Any]
    ) -> List[CheckItem]:
        """법규 기준 체크"""
        checks = []
        
        # 1. 용도지역 적합성 (주거지역 필수)
        zone_type = zone_data.get('zone_type', '')
        if '주거' in zone_type:
            status = CheckStatus.PASS
            score = 100
            desc = "주거지역 적합"
        elif '상업' in zone_type or '준공업' in zone_type:
            status = CheckStatus.WARNING
            score = 70
            desc = "주거지역 아님 (조건부 가능)"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "용도지역 부적합"
        
        checks.append(CheckItem(
            category="법규",
            item="용도지역",
            status=status,
            value=zone_type,
            standard="주거지역",
            description=desc,
            score=score
        ))
        
        # 2. 건폐율 준수
        bcr = zone_data.get('building_coverage_ratio', 0)
        building_area = building_data.get('building_area', 0)
        land_area = building_data.get('land_area', 1)
        actual_bcr = (building_area / land_area * 100) if land_area > 0 else 0
        
        if actual_bcr <= bcr:
            status = CheckStatus.PASS
            score = 100
            desc = "건폐율 준수"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "건폐율 초과"
        
        checks.append(CheckItem(
            category="법규",
            item="건폐율",
            status=status,
            value=f"{actual_bcr:.1f}% (한도 {bcr:.1f}%)",
            standard=f"{bcr:.1f}% 이하",
            description=desc,
            score=score
        ))
        
        # 3. 용적률 준수
        far = zone_data.get('floor_area_ratio', 0)
        total_floor_area = building_data.get('total_floor_area', 0)
        actual_far = (total_floor_area / land_area * 100) if land_area > 0 else 0
        
        if actual_far <= far:
            status = CheckStatus.PASS
            score = 100
            desc = "용적률 준수"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "용적률 초과"
        
        checks.append(CheckItem(
            category="법규",
            item="용적률",
            status=status,
            value=f"{actual_far:.1f}% (한도 {far:.1f}%)",
            standard=f"{far:.1f}% 이하",
            description=desc,
            score=score
        ))
        
        # 4. 높이제한 준수
        height_limit = zone_data.get('height_limit')
        floors = building_data.get('floors', 0)
        estimated_height = floors * 3.0  # 층당 3m 가정
        
        if height_limit is None or height_limit == 0:
            status = CheckStatus.INFO
            score = 100
            desc = "높이제한 없음"
        elif estimated_height <= height_limit:
            status = CheckStatus.PASS
            score = 100
            desc = "높이제한 준수"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "높이제한 초과"
        
        height_value = f"{estimated_height:.1f}m"
        if height_limit:
            height_value += f" (한도 {height_limit:.1f}m)"
        
        checks.append(CheckItem(
            category="법규",
            item="높이제한",
            status=status,
            value=height_value,
            standard=f"{height_limit:.1f}m 이하" if height_limit else "제한 없음",
            description=desc,
            score=score
        ))
        
        return checks
    
    def _calculate_category_scores(self, checklist: List[CheckItem]) -> Dict[str, float]:
        """카테고리별 평균 점수 계산"""
        category_scores = {}
        
        for category in self.category_weights.keys():
            items = [c for c in checklist if c.category == category]
            if items:
                avg_score = sum(item.score for item in items) / len(items)
                category_scores[category] = round(avg_score, 2)
            else:
                category_scores[category] = 0.0
        
        return category_scores
    
    def _determine_grade(self, total_score: float) -> Grade:
        """총점 기반 등급 산정 (버전별 기준 적용)"""
        if total_score >= self.grade_thresholds.get("A", 80):
            return Grade.A
        elif total_score >= self.grade_thresholds.get("B", 60):
            return Grade.B
        else:
            return Grade.C
    
    def _generate_summary(
        self,
        grade: Grade,
        total_score: float,
        category_scores: Dict[str, float]
    ) -> str:
        """종합 의견 생성 (버전별 메시지 적용)"""
        # 버전별 메시지 가져오기
        messages = self.lh_rules.get("messages", {})
        
        summaries = {
            Grade.A: messages.get(
                "grade_A",
                f"우수한 사업입니다 (종합 {total_score:.1f}점). LH 신축매입임대 사업으로 적극 권장합니다."
            ),
            Grade.B: messages.get(
                "grade_B",
                f"양호한 사업입니다 (종합 {total_score:.1f}점). 일부 개선사항 검토 후 LH 매입 추진 가능합니다."
            ),
            Grade.C: messages.get(
                "grade_C",
                f"부적합 사업입니다 (종합 {total_score:.1f}점). 주요 기준 미달로 LH 매입이 어렵습니다."
            )
        }
        
        # 점수 정보 추가
        for key in summaries:
            if "{total_score" not in summaries[key]:
                summaries[key] = summaries[key].format(total_score=total_score)
        
        # 취약 카테고리 파악
        weak_categories = [
            cat for cat, score in category_scores.items()
            if score < 60
        ]
        
        summary = summaries[grade]
        if weak_categories:
            summary += f" 특히 {', '.join(weak_categories)} 부문의 개선이 필요합니다."
        
        return summary
    
    def _generate_recommendations(self, checklist: List[CheckItem]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # FAIL 상태 항목
        failed_items = [c for c in checklist if c.status == CheckStatus.FAIL]
        for item in failed_items[:3]:  # 상위 3개만
            recommendations.append(
                f"[필수] {item.item}: {item.description}"
            )
        
        # WARNING 상태 항목
        warning_items = [c for c in checklist if c.status == CheckStatus.WARNING]
        for item in warning_items[:2]:  # 상위 2개만
            recommendations.append(
                f"[권장] {item.item}: {item.description}"
            )
        
        if not recommendations:
            recommendations.append("모든 기준을 충족하였습니다. 매입 진행을 권장합니다.")
        
        return recommendations
    
    def get_checklist_details(self, grade_result: GradeResult) -> Dict[str, Any]:
        """
        체크리스트 상세 정보 추출 (PDF 생성용)
        
        Args:
            grade_result: 등급 평가 결과
            
        Returns:
            체크리스트 상세 정보 딕셔너리
        """
        details = {
            "items": [],
            "category_summary": {},
            "total_items": len(grade_result.checklist),
            "passed_items": 0,
            "failed_items": 0,
            "warning_items": 0,
            "info_items": 0
        }
        
        # 카테고리별 통계
        for category in self.category_weights.keys():
            category_items = [c for c in grade_result.checklist if c.category == category]
            if category_items:
                passed = sum(1 for c in category_items if c.status == CheckStatus.PASS)
                failed = sum(1 for c in category_items if c.status == CheckStatus.FAIL)
                warning = sum(1 for c in category_items if c.status == CheckStatus.WARNING)
                info = sum(1 for c in category_items if c.status == CheckStatus.INFO)
                
                details["category_summary"][category] = {
                    "total": len(category_items),
                    "passed": passed,
                    "failed": failed,
                    "warning": warning,
                    "info": info,
                    "score": grade_result.category_scores.get(category, 0)
                }
        
        # 전체 항목 상세
        for item in grade_result.checklist:
            details["items"].append({
                "category": item.category,
                "item": item.item,
                "status": item.status.value,
                "value": item.value,
                "standard": item.standard,
                "description": item.description,
                "score": item.score
            })
            
            # 전체 통계
            if item.status == CheckStatus.PASS:
                details["passed_items"] += 1
            elif item.status == CheckStatus.FAIL:
                details["failed_items"] += 1
            elif item.status == CheckStatus.WARNING:
                details["warning_items"] += 1
            elif item.status == CheckStatus.INFO:
                details["info_items"] += 1
        
        return details
