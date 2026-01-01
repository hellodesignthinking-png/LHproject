#!/usr/bin/env python3
"""
ZeroSite 6종 보고서 데이터 정합성 검증 스크립트
목적: "계산은 하나, 해석은 여섯" 원칙 검증
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Tuple

# 테스트 설정
BASE_URL = "http://localhost:8091"
CONTEXT_ID = "TEST_6REPORT"

# 6종 보고서 엔드포인트
ENDPOINTS = {
    "A_Master": f"{BASE_URL}/api/v4/reports/six-types/master/html?context_id={CONTEXT_ID}",
    "B_Landowner": f"{BASE_URL}/api/v4/reports/six-types/landowner/html?context_id={CONTEXT_ID}",
    "C_LH": f"{BASE_URL}/api/v4/reports/lh/technical/html?context_id={CONTEXT_ID}",
    "D_Investment": f"{BASE_URL}/api/v4/reports/six-types/investment/html?context_id={CONTEXT_ID}",
    "E_QuickReview": f"{BASE_URL}/api/v4/reports/six-types/quick-review/html?context_id={CONTEXT_ID}",
    "F_Presentation": f"{BASE_URL}/api/v4/reports/six-types/presentation/html?context_id={CONTEXT_ID}",
}


def extract_numbers(text: str) -> List[float]:
    """텍스트에서 모든 숫자를 추출 (쉼표 제거 후)"""
    # 쉼표 제거
    text = text.replace(',', '')
    # 숫자 패턴 추출 (소수점 포함)
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(n) for n in numbers if n]


def extract_site_identity(html: str) -> Dict[str, str]:
    """Site Identity Block 정보 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 일반적인 패턴으로 추출
    identity = {
        "address": "",
        "pnu": "",
        "run_id": "",
        "date": ""
    }
    
    # RUN_ID 추출
    run_id_match = re.search(r'RUN[_\s]?ID[:\s]+([A-Z0-9_]+)', html, re.IGNORECASE)
    if run_id_match:
        identity["run_id"] = run_id_match.group(1)
    
    # PNU 추출
    pnu_match = re.search(r'PNU[:\s]+(\d+)', html)
    if pnu_match:
        identity["pnu"] = pnu_match.group(1)
    
    # 주소 추출 (서울특별시 패턴)
    address_match = re.search(r'(서울특별시[^<\n]+)', html)
    if address_match:
        identity["address"] = address_match.group(1).strip()
    
    # 날짜 추출 (YYYY-MM-DD 패턴)
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', html)
    if date_match:
        identity["date"] = date_match.group(0)
    
    return identity


def extract_key_metrics(html: str, report_type: str) -> Dict[str, any]:
    """핵심 수치 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    metrics = {}
    
    # M2 토지가치 (억원 단위)
    land_value_match = re.search(r'토지가?치[:\s]*([0-9,\.]+)\s*억', html)
    if land_value_match:
        metrics["land_value"] = float(land_value_match.group(1).replace(',', ''))
    
    # M4 세대수
    units_match = re.search(r'세대수[:\s]*([0-9,]+)\s*세대', html)
    if units_match:
        metrics["total_units"] = int(units_match.group(1).replace(',', ''))
    
    # M5 IRR (E는 제외되어야 함)
    irr_match = re.search(r'IRR[:\s]*([0-9,\.]+)\s*%', html)
    if irr_match and report_type != "E_QuickReview":
        metrics["irr"] = float(irr_match.group(1).replace(',', ''))
    
    # 용적률
    far_match = re.search(r'용적률[:\s]*([0-9,\.]+)\s*%', html)
    if far_match:
        metrics["floor_area_ratio"] = float(far_match.group(1).replace(',', ''))
    
    # 건폐율
    bcr_match = re.search(r'건폐율[:\s]*([0-9,\.]+)\s*%', html)
    if bcr_match:
        metrics["building_coverage_ratio"] = float(bcr_match.group(1).replace(',', ''))
    
    return metrics


def verify_report(report_type: str, url: str) -> Tuple[bool, str, Dict]:
    """개별 보고서 검증"""
    try:
        print(f"\n{'='*60}")
        print(f"검증 중: {report_type}")
        print(f"{'='*60}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            return False, f"❌ HTTP {response.status_code}", {}
        
        html = response.text
        
        # Site Identity 추출
        identity = extract_site_identity(html)
        print(f"📍 주소: {identity['address']}")
        print(f"📋 PNU: {identity['pnu']}")
        print(f"🆔 RUN_ID: {identity['run_id']}")
        print(f"📅 날짜: {identity['date']}")
        
        # 핵심 수치 추출
        metrics = extract_key_metrics(html, report_type)
        print(f"\n📊 핵심 수치:")
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
        # E. 사전 검토 보고서는 IRR/ROI/점수 제거 확인
        if report_type == "E_QuickReview":
            irr_found = re.search(r'IRR|ROI|종합\s*점수', html, re.IGNORECASE)
            if irr_found:
                return False, "❌ E 보고서에 IRR/ROI/점수 발견 (금지 항목)", {"identity": identity, "metrics": metrics}
            print("✅ E 보고서: IRR/ROI/점수 제거 확인")
        
        # F. 프레젠테이션 보고서는 슬라이드 구조 확인
        if report_type == "F_Presentation":
            slide_count = len(re.findall(r'<section[^>]*class="slide', html))
            print(f"📊 슬라이드 수: {slide_count}개")
            if slide_count < 10:
                return False, f"❌ F 보고서 슬라이드 수 부족 ({slide_count}개, 최소 10개 필요)", {"identity": identity, "metrics": metrics}
            
            # "결론 먼저" 확인
            if "진행 권장" not in html and "조건부" not in html and "중단" not in html:
                return False, "❌ F 보고서에 명확한 판단 (진행/조건부/중단) 없음", {"identity": identity, "metrics": metrics}
            print("✅ F 보고서: 10 슬라이드 + 명확한 판단 확인")
        
        return True, "✅ PASS", {"identity": identity, "metrics": metrics}
        
    except Exception as e:
        return False, f"❌ 오류: {str(e)}", {}


def compare_metrics(all_data: Dict[str, Dict]) -> Tuple[bool, List[str]]:
    """6종 보고서 간 수치 정합성 비교"""
    print(f"\n{'='*60}")
    print("📊 6종 보고서 수치 정합성 검증")
    print(f"{'='*60}")
    
    errors = []
    
    # Site Identity 비교
    identities = {k: v["identity"] for k, v in all_data.items()}
    
    # RUN_ID 일치 확인
    run_ids = set(d["run_id"] for d in identities.values() if d["run_id"])
    if len(run_ids) > 1:
        errors.append(f"❌ RUN_ID 불일치: {run_ids}")
    else:
        print(f"✅ RUN_ID 일치: {list(run_ids)[0] if run_ids else 'N/A'}")
    
    # PNU 일치 확인
    pnus = set(d["pnu"] for d in identities.values() if d["pnu"])
    if len(pnus) > 1:
        errors.append(f"❌ PNU 불일치: {pnus}")
    else:
        print(f"✅ PNU 일치: {list(pnus)[0] if pnus else 'N/A'}")
    
    # 주소 일치 확인
    addresses = set(d["address"] for d in identities.values() if d["address"])
    if len(addresses) > 1:
        errors.append(f"❌ 주소 불일치: {addresses}")
    else:
        print(f"✅ 주소 일치: {list(addresses)[0] if addresses else 'N/A'}")
    
    # 핵심 수치 비교
    metrics_by_report = {k: v["metrics"] for k, v in all_data.items()}
    
    # 비교 가능한 수치 목록
    comparable_keys = ["land_value", "total_units", "floor_area_ratio", "building_coverage_ratio"]
    
    for key in comparable_keys:
        values = {}
        for report, metrics in metrics_by_report.items():
            if key in metrics:
                values[report] = metrics[key]
        
        if len(values) > 1:
            unique_values = set(values.values())
            if len(unique_values) > 1:
                errors.append(f"❌ {key} 불일치: {values}")
            else:
                print(f"✅ {key} 일치: {list(unique_values)[0]}")
    
    # IRR 비교 (E 제외)
    irr_values = {}
    for report, metrics in metrics_by_report.items():
        if report != "E_QuickReview" and "irr" in metrics:
            irr_values[report] = metrics["irr"]
    
    if len(irr_values) > 1:
        unique_irrs = set(irr_values.values())
        if len(unique_irrs) > 1:
            errors.append(f"❌ IRR 불일치 (E 제외): {irr_values}")
        else:
            print(f"✅ IRR 일치 (E 제외): {list(unique_irrs)[0]}")
    
    return len(errors) == 0, errors


def main():
    """메인 검증 실행"""
    print("="*60)
    print("🧪 ZeroSite 6종 보고서 데이터 정합성 검증")
    print("="*60)
    print(f"RUN_ID: {CONTEXT_ID}")
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    
    all_data = {}
    all_pass = True
    
    # 각 보고서 검증
    for report_type, url in ENDPOINTS.items():
        success, message, data = verify_report(report_type, url)
        
        if success:
            all_data[report_type] = data
            print(f"\n{message}")
        else:
            all_pass = False
            print(f"\n{message}")
            if data:
                all_data[report_type] = data
    
    # 6종 간 수치 비교
    if len(all_data) >= 6:
        metrics_pass, errors = compare_metrics(all_data)
        if not metrics_pass:
            all_pass = False
            print("\n❌ 수치 불일치 발견:")
            for error in errors:
                print(f"  {error}")
    else:
        all_pass = False
        print(f"\n❌ 6종 보고서 중 {len(all_data)}개만 성공")
    
    # 최종 결과
    print(f"\n{'='*60}")
    print("📋 최종 검증 결과")
    print(f"{'='*60}")
    
    if all_pass:
        print("✅ ✅ ✅ PASS ✅ ✅ ✅")
        print("\n🎉 ZeroSite 6종 보고서 시스템은 제품 수준으로 완성되었습니다!")
        print("\n다음 단계: STEP 3 (PR 생성 → main 머지)")
        return 0
    else:
        print("❌ ❌ ❌ FAIL ❌ ❌ ❌")
        print("\n🔧 수정이 필요한 항목이 발견되었습니다.")
        return 1


if __name__ == "__main__":
    exit(main())
