#!/usr/bin/env python3
"""
ZeroSite Report Generator v6.0
자동 보고서 생성 파이프라인: JSON → Markdown → HTML → PDF

Usage:
    python generate_report_v6.py --input analysis_result.json --output report.pdf
    python generate_report_v6.py --template custom_template.html --format html
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
import markdown
from weasyprint import HTML, CSS


class ZeroSiteReportGenerator:
    """ZeroSite 보고서 자동 생성기 v6.0"""
    
    def __init__(self, template_path: Optional[str] = None):
        """
        보고서 생성기 초기화
        
        Args:
            template_path: 커스텀 템플릿 경로 (기본값: templates/report_template_v6.html)
        """
        self.project_root = Path(__file__).parent.parent
        self.templates_dir = self.project_root / "templates"
        
        if template_path:
            self.template_path = Path(template_path)
        else:
            self.template_path = self.templates_dir / "report_template_v6.html"
        
        # Jinja2 환경 설정
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Markdown 확장 설정
        self.md_extensions = [
            'extra',           # 테이블, footnotes 등
            'codehilite',      # 코드 하이라이팅
            'toc',             # 목차 자동 생성
            'tables',          # 테이블 지원
            'fenced_code',     # 코드 블록
            'nl2br'            # 줄바꿈 처리
        ]
    
    def load_analysis_result(self, json_path: str) -> Dict[str, Any]:
        """
        JSON 분석 결과 로드
        
        Args:
            json_path: JSON 파일 경로
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ JSON 로드 성공: {json_path}")
                return data
        except Exception as e:
            print(f"❌ JSON 로드 실패: {e}")
            sys.exit(1)
    
    def generate_markdown(self, analysis_data: Dict[str, Any]) -> str:
        """
        분석 결과를 Markdown 형식으로 변환
        
        Args:
            analysis_data: 분석 결과 딕셔너리
            
        Returns:
            Markdown 문자열
        """
        md_sections = []
        
        # 1. 개요 (Executive Summary)
        md_sections.append("# 1. 개요 (Executive Summary)")
        md_sections.append(f"**프로젝트명**: {analysis_data.get('project_name', 'N/A')}")
        md_sections.append(f"**위치**: {analysis_data.get('location', 'N/A')}")
        md_sections.append(f"**분석 일자**: {analysis_data.get('analysis_date', datetime.now().strftime('%Y-%m-%d'))}")
        md_sections.append("")
        
        # 2. LH 평가 결과
        if 'lh_evaluation' in analysis_data:
            lh_eval = analysis_data['lh_evaluation']
            md_sections.append("# 2. LH 평가 결과")
            md_sections.append(f"## 종합 평가")
            md_sections.append(f"- **등급**: {lh_eval.get('grade', 'N/A')}")
            md_sections.append(f"- **총점**: {lh_eval.get('total_score', 0)}/350점")
            md_sections.append(f"- **통과 여부**: {'✅ 통과' if lh_eval.get('total_score', 0) >= 250 else '❌ 미달'}")
            md_sections.append("")
            
            # 세부 점수
            if 'category_scores' in lh_eval:
                md_sections.append("## 세부 평가 점수")
                md_sections.append("| 항목 | 점수 | 만점 | 비율 |")
                md_sections.append("|------|------|------|------|")
                for category, score in lh_eval['category_scores'].items():
                    max_score = {"location": 100, "scale": 80, "business": 100, "regulation": 70}.get(category, 100)
                    ratio = (score / max_score * 100) if max_score > 0 else 0
                    md_sections.append(f"| {category} | {score:.1f} | {max_score} | {ratio:.1f}% |")
                md_sections.append("")
        
        # 3. 입지 분석
        if 'accessibility' in analysis_data:
            access = analysis_data['accessibility']
            md_sections.append("# 3. 입지 분석")
            md_sections.append(f"## 교통 접근성")
            md_sections.append(f"- 지하철역: {access.get('nearest_subway_distance', 9999)}m")
            md_sections.append(f"- 버스정류장: {access.get('nearest_bus_distance', 9999)}m")
            md_sections.append("")
            
            md_sections.append(f"## 생활 편의시설")
            md_sections.append(f"- 학교: {access.get('nearest_school_distance', 9999)}m")
            md_sections.append(f"- 병원: {access.get('nearest_hospital_distance', 9999)}m")
            md_sections.append(f"- 대학교: {access.get('nearest_university_distance', 9999)}m")
            md_sections.append("")
        
        # 4. 수요 분석
        if 'demand_analysis' in analysis_data:
            demand = analysis_data['demand_analysis']
            md_sections.append("# 4. 수요 분석")
            md_sections.append(f"## 수요 점수: {demand.get('demand_score', 0):.1f}점")
            md_sections.append(f"**수요 수준**: {demand.get('demand_level', 'N/A')}")
            md_sections.append("")
            
            if 'household_type_scores' in demand:
                md_sections.append("## 세대유형별 수요 점수")
                md_sections.append("| 세대유형 | 점수 |")
                md_sections.append("|---------|------|")
                for htype, score in demand['household_type_scores'].items():
                    md_sections.append(f"| {htype} | {score}점 |")
                md_sections.append("")
        
        # 5. 건축 계획
        if 'building_capacity' in analysis_data:
            building = analysis_data['building_capacity']
            md_sections.append("# 5. 건축 계획")
            md_sections.append(f"- **세대수**: {building.get('units', 0)}세대")
            md_sections.append(f"- **층수**: 지상 {building.get('floors', 0)}층")
            md_sections.append(f"- **주차대수**: {building.get('parking_spaces', 0)}대")
            md_sections.append(f"- **건폐율**: {building.get('building_coverage_ratio', 0)}%")
            md_sections.append(f"- **용적률**: {building.get('floor_area_ratio', 0)}%")
            md_sections.append("")
        
        # 6. 사업성 분석
        if 'financial_analysis' in analysis_data:
            finance = analysis_data['financial_analysis']
            md_sections.append("# 6. 사업성 분석")
            md_sections.append(f"## 사업비")
            md_sections.append(f"- **총 사업비**: {finance.get('total_cost', 0):,.0f}원")
            md_sections.append(f"- **토지비**: {finance.get('land_cost', 0):,.0f}원")
            md_sections.append(f"- **건축비**: {finance.get('construction_cost', 0):,.0f}원")
            md_sections.append("")
            
            md_sections.append(f"## 수익성")
            md_sections.append(f"- **예상 ROI**: {finance.get('roi', 0):.2f}%")
            md_sections.append(f"- **예상 IRR**: {finance.get('irr', 0):.2f}%")
            md_sections.append(f"- **투자 회수 기간**: {finance.get('payback_period', 0):.1f}년")
            md_sections.append("")
        
        # 7. 추천사항
        if 'recommendations' in analysis_data:
            md_sections.append("# 7. 추천사항")
            for i, rec in enumerate(analysis_data['recommendations'], 1):
                md_sections.append(f"{i}. {rec}")
            md_sections.append("")
        
        return "\n".join(md_sections)
    
    def markdown_to_html(self, md_content: str) -> str:
        """
        Markdown을 HTML로 변환
        
        Args:
            md_content: Markdown 문자열
            
        Returns:
            HTML 문자열
        """
        html = markdown.markdown(
            md_content,
            extensions=self.md_extensions,
            output_format='html5'
        )
        print("✅ Markdown → HTML 변환 완료")
        return html
    
    def generate_toc(self, md_content: str) -> str:
        """
        목차 (TOC) 생성
        
        Args:
            md_content: Markdown 문자열
            
        Returns:
            TOC HTML 문자열
        """
        toc_items = []
        for line in md_content.split('\n'):
            if line.startswith('#'):
                level = line.count('#')
                title = line.strip('#').strip()
                
                # 페이지 번호는 임시로 '...' 처리 (실제 PDF 생성 시 weasyprint가 자동 계산)
                toc_items.append(
                    f'<div class="toc-item level-{level}">'
                    f'<span class="toc-title">{title}</span>'
                    f'<span class="toc-page">...</span>'
                    f'</div>'
                )
        
        return '\n'.join(toc_items)
    
    def apply_template(
        self,
        content_html: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        HTML 템플릿 적용
        
        Args:
            content_html: 본문 HTML
            analysis_data: 분석 결과 딕셔너리
            
        Returns:
            최종 HTML 문자열
        """
        # 목차 생성
        md_content = self.generate_markdown(analysis_data)
        toc_html = self.generate_toc(md_content)
        
        # 템플릿 로드
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 템플릿 변수 준비
        template_vars = {
            'report_title': analysis_data.get('project_name', 'ZeroSite Land Report'),
            'project_name': analysis_data.get('project_name', 'N/A'),
            'project_location': analysis_data.get('location', 'N/A'),
            'analysis_date': analysis_data.get('analysis_date', datetime.now().strftime('%Y-%m-%d')),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'lh_score': analysis_data.get('lh_evaluation', {}).get('total_score', None),
            'grade': analysis_data.get('lh_evaluation', {}).get('grade', None),
            'content': content_html,
            'toc_content': toc_html
        }
        
        # 템플릿 렌더링
        final_html = template.render(**template_vars)
        print("✅ 템플릿 적용 완료")
        return final_html
    
    def html_to_pdf(self, html_content: str, output_path: str):
        """
        HTML을 PDF로 변환
        
        Args:
            html_content: HTML 문자열
            output_path: 출력 PDF 경로
        """
        try:
            # WeasyPrint로 PDF 생성
            HTML(string=html_content, base_url=str(self.templates_dir)).write_pdf(
                output_path,
                stylesheets=None,
                presentational_hints=True
            )
            print(f"✅ PDF 생성 완료: {output_path}")
        except Exception as e:
            print(f"❌ PDF 생성 실패: {e}")
            sys.exit(1)
    
    def generate_report(
        self,
        input_json: str,
        output_path: str,
        output_format: str = 'pdf'
    ):
        """
        전체 보고서 생성 파이프라인 실행
        
        Args:
            input_json: 입력 JSON 파일 경로
            output_path: 출력 파일 경로
            output_format: 출력 형식 ('pdf', 'html', 'markdown')
        """
        print(f"🚀 ZeroSite Report Generator v6.0 시작")
        print(f"   입력: {input_json}")
        print(f"   출력: {output_path} ({output_format})")
        print("")
        
        # 1. JSON 로드
        analysis_data = self.load_analysis_result(input_json)
        
        # 2. Markdown 생성
        print("📝 Markdown 생성 중...")
        md_content = self.generate_markdown(analysis_data)
        
        if output_format == 'markdown':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"✅ Markdown 저장 완료: {output_path}")
            return
        
        # 3. HTML 변환
        print("🌐 HTML 변환 중...")
        html_content = self.markdown_to_html(md_content)
        
        # 4. 템플릿 적용
        print("🎨 템플릿 적용 중...")
        final_html = self.apply_template(html_content, analysis_data)
        
        if output_format == 'html':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            print(f"✅ HTML 저장 완료: {output_path}")
            return
        
        # 5. PDF 생성
        print("📄 PDF 생성 중...")
        self.html_to_pdf(final_html, output_path)
        
        print("")
        print("✅ 보고서 생성 완료!")
        print(f"   파일 크기: {os.path.getsize(output_path) / 1024:.1f} KB")


def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description='ZeroSite Report Generator v6.0 - 자동 보고서 생성 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # JSON → PDF 생성
  python generate_report_v6.py -i analysis.json -o report.pdf
  
  # JSON → HTML 생성 (커스텀 템플릿)
  python generate_report_v6.py -i analysis.json -o report.html -f html -t custom.html
  
  # JSON → Markdown 생성
  python generate_report_v6.py -i analysis.json -o report.md -f markdown
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='입력 JSON 파일 경로 (분석 결과)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='출력 파일 경로'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['pdf', 'html', 'markdown'],
        default='pdf',
        help='출력 형식 (기본값: pdf)'
    )
    
    parser.add_argument(
        '-t', '--template',
        default=None,
        help='커스텀 템플릿 경로 (기본값: templates/report_template_v6.html)'
    )
    
    args = parser.parse_args()
    
    # 보고서 생성기 초기화 및 실행
    generator = ZeroSiteReportGenerator(template_path=args.template)
    generator.generate_report(
        input_json=args.input,
        output_path=args.output,
        output_format=args.format
    )


if __name__ == '__main__':
    main()
