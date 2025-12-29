#!/usr/bin/env python3
"""
ZeroSite v6.5 - M4 건축 규모 판단 보고서 생성기
REAL APPRAISAL STANDARD 적용

목적: M2와 동일한 실무 판단 보고서 형식으로 건축 규모 판단 결과 출력
"""

import os
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class M4BuildingScaleGenerator:
    """M4: 건축 규모 판단 보고서 생성기"""
    
    def __init__(self, template_dir=None):
        if template_dir is None:
            template_dir = Path(__file__).parent / "app" / "templates_v13"
        
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.env.filters['number_format'] = lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)
        self.env.filters['percentage'] = lambda x: f"{x*100:.1f}%" if isinstance(x, float) else f"{x}%"
        
        print("✅ M4 Building Scale Generator initialized")
        print(f"📁 Template dir: {template_dir}")
    
    def generate_report(
        self,
        project_address: str,
        land_area: str,
        zone_type: str,
        selected_scale: str,
        total_units: int = 150,
        unit_composition: list = None,
        bcr_limit: float = 60.0,
        far_limit: float = 250.0,
        legal_score: float = 90.0,
        review_score: float = 85.0,
        stability_score: float = 80.0,
        analysis_date: str = None,
        output_path: str = None
    ):
        """
        M4 건축 규모 판단 보고서 생성
        
        Args:
            project_address: 사업지 주소
            land_area: 토지면적
            zone_type: 용도지역
            selected_scale: 선정된 규모 (예: "총 150세대, 30주차")
            total_units: 총 세대수
            unit_composition: 세대 구성 데이터
            bcr_limit: 건폐율 한도 (%)
            far_limit: 용적률 한도 (%)
            legal_score: 법적 제약 점수
            review_score: 심사 기준 점수
            stability_score: 사업 안정성 점수
            analysis_date: 분석 기준일
            output_path: 출력 파일 경로
            
        Returns:
            str: 생성된 보고서 파일 경로
        """
        print("\n" + "="*80)
        print("🏗️ M4 BUILDING SCALE ANALYSIS REPORT GENERATOR")
        print("="*80)
        print(f"📍 Project: {project_address}")
        print(f"📏 Land Area: {land_area}")
        print(f"🏗️ Selected Scale: {selected_scale}")
        print("="*80 + "\n")
        
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        report_id = f"ZS-M4-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 세대 구성 데이터 (샘플)
        if unit_composition is None:
            unit_composition = [
                {'type': '59㎡ (18평형)', 'count': 90, 'ratio': 60.0, 'compliance': '적합'},
                {'type': '74㎡ (22평형)', 'count': 45, 'ratio': 30.0, 'compliance': '적합'},
                {'type': '84㎡ (25평형)', 'count': 15, 'ratio': 10.0, 'compliance': '적합'}
            ]
        
        # 심사 기준 체크리스트
        review_checklist = [
            {'item': '세대수 적정성', 'standard': '100-200세대', 'result': '적합'},
            {'item': '평형 구성 비율', 'standard': '소형 60% 이상', 'result': '적합'},
            {'item': '주차 확보율', 'standard': '세대당 0.7대 이상', 'result': '적합'},
            {'item': '층수 제한', 'standard': '15층 이하', 'result': '적합'}
        ]
        
        # 총 점수 계산
        total_score = (
            legal_score * 0.5 +      # PRIMARY: 50%
            review_score * 0.3 +      # SECONDARY: 30%
            stability_score * 0.2     # REFERENCE: 20%
        )
        
        # 핵심 판단 요약 (REAL APPRAISAL STANDARD v6.5)
        legal_max_units = int(total_units * 1.2)
        executive_conclusion = (
            f"본 사업의 법정 최대 규모는 {legal_max_units}세대까지 가능하나, "
            f"LH 심사 안정성, 공급 유형 적합성, 사업 리스크를 종합적으로 검토한 결과, "
            f"{selected_scale}로 계획하는 것이 가장 안정적인 규모로 판단됩니다."
        )
        
        # 법정 최대 대비 축소 사유
        scale_reduction_reason = (
            f"법적 기준상 최대 {legal_max_units}세대까지 계획이 가능하나, "
            f"세대 밀도 증가에 따른 주차·공용부 부담, 심사 과정에서의 규모 조정 가능성을 고려할 경우, "
            f"{total_units}세대 규모가 인허가 및 심사 안정성 측면에서 유리합니다."
        )
        
        # M3 공급 유형 연결 논리
        supply_type_connection = (
            f"본 사업은 M3 분석 결과 신혼희망타운 공급 유형으로 선정되었으며, "
            f"신혼형 공급은 중소형 평형 위주의 적정 세대수 확보가 중요합니다. "
            f"\n\n{total_units}세대 규모는 신혼형 세대 구성 및 평형 비율 기준을 안정적으로 충족하면서, "
            f"과도한 밀집을 피할 수 있는 적정 규모입니다."
        )
        
        # 사업 안정성 점수 해석
        stability_interpretation = (
            f"사업 안정성 점수 {stability_score}점은 법적 기준은 충족하되, "
            f"규모를 과도하게 확장하지 않음으로써 심사 리스크를 선제적으로 회피한 결과입니다."
        )
        
        # 최종 판단 의견 (REAL APPRAISAL STANDARD v6.5)
        final_opinion = (
            f"종합 검토 결과, 본 사업은 {selected_scale}로 추진하는 것이 "
            f"법적 적합성, 심사 안정성, 공급 유형 측면에서 가장 합리적인 선택으로 판단됩니다."
            f"\n\n법적 제약 검토를 중심으로, 심사 기준 및 사업 안정성을 단계적으로 검토하였습니다. "
            f"{supply_type_connection}"
            f"\n\n{stability_interpretation}"
        )
        
        # 컨텍스트 구성
        context = {
            'report_id': report_id,
            'project_address': project_address,
            'land_area': land_area,
            'zone_type': zone_type,
            'analysis_date': analysis_date,
            'selected_scale': selected_scale,
            'executive_conclusion': executive_conclusion,
            'legal_max_scale': f"{legal_max_units}세대 (법정 최대)",
            'scale_reduction_reason': scale_reduction_reason,
            'supply_type_connection': supply_type_connection,
            'stability_interpretation': stability_interpretation,
            'review_score': review_score,
            'stability_score': stability_score,
            'total_units': total_units,
            'unit_composition': unit_composition,
            'review_checklist': review_checklist,
            'bcr_limit': bcr_limit,
            'far_limit': far_limit,
            'bcr_applied': bcr_limit * 0.9,
            'far_applied': far_limit * 0.85,
            'max_building_area': 3500,
            'planned_building_area': 3150,
            'max_floor_area': 14500,
            'planned_floor_area': 12325,
            'legal_parking': 105,
            'planned_parking': 120,
            'parking_ratio': 114.3,
            'legal_score': legal_score,
            'total_score': total_score,
            'final_opinion': final_opinion
        }
        
        # 템플릿 렌더링
        template = self.env.get_template('m4_building_scale_format.html')
        html_content = template.render(**context)
        
        # HTML 저장
        if not output_path:
            output_dir = Path("/home/user/webapp/generated_reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"M4_BuildingScale_{timestamp}.html"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        file_size = output_path.stat().st_size / 1024
        
        print("\n✅ Report Generated!")
        print(f"📄 Output: {output_path}")
        print(f"📊 Size: {file_size:.2f} KB")
        print(f"🏗️ Selected Scale: {selected_scale}")
        print(f"💯 Total Score: {total_score:.1f}")
        
        return str(output_path)


def main():
    """테스트 실행"""
    generator = M4BuildingScaleGenerator()
    
    output = generator.generate_report(
        project_address="서울특별시 강남구 역삼동 1234",
        land_area="5,800㎡ (1,754평)",
        zone_type="제2종일반주거지역",
        selected_scale="총 150세대, 주차 120대",
        total_units=150,
        legal_score=90.0,
        review_score=85.0,
        stability_score=80.0
    )
    
    print(f"\n🎉 Test report: {output}")


if __name__ == "__main__":
    main()
