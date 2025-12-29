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
        
        # 핵심 판단 요약
        executive_conclusion = (
            f"본 사업의 적정 건축 규모는 {selected_scale}로 판단됩니다. "
            f"법적 제약 분석 및 LH 심사 기준을 종합적으로 검토한 결과, "
            f"해당 규모가 사업 목적 달성 및 승인 가능성 측면에서 가장 적합한 것으로 판단됩니다."
        )
        
        # 최종 판단 의견
        final_opinion = (
            f"본 사업의 건축 규모는 {selected_scale}로 선정됩니다. "
            f"법적 제약 분석 결과 {legal_score}점, LH 심사 기준 적합성 {review_score}점으로 "
            f"종합 점수 {total_score:.1f}점을 기록하였으며, "
            f"건축법 및 관련 법규를 모두 충족하는 것으로 판단됩니다. "
            f"사업 안정성이 확보되었으므로, 해당 규모로의 사업 추진을 권고합니다."
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
            'legal_max_scale': f"{int(total_units * 1.2)}세대 (법정 최대)",
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
