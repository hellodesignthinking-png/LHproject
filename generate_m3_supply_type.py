#!/usr/bin/env python3
"""
ZeroSite v6.5 - M3 공급 유형 판단 보고서 생성기
REAL APPRAISAL STANDARD 적용

목적: M2와 동일한 실무 판단 보고서 형식으로 공급 유형 선정 결과 출력
"""

import os
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class M3SupplyTypeGenerator:
    """M3: 공급 유형 판단 보고서 생성기"""
    
    def __init__(self, template_dir=None):
        """
        Args:
            template_dir: 템플릿 디렉토리 경로 (기본값: app/templates_v13)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "app" / "templates_v13"
        
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Jinja2 필터 등록
        self.env.filters['number_format'] = lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)
        self.env.filters['percentage'] = lambda x: f"{x*100:.1f}%" if isinstance(x, float) else f"{x}%"
        
        print("✅ M3 Supply Type Generator initialized")
        print(f"📁 Template dir: {template_dir}")
    
    def generate_report(
        self,
        project_address: str,
        project_scale: str,
        selected_supply_type: str,
        supply_type_analysis: list = None,
        demographic_analysis: list = None,
        policy_target_score: float = 85.0,
        demand_score: float = 75.0,
        supply_feasibility_score: float = 70.0,
        analysis_date: str = None,
        output_path: str = None
    ):
        """
        M3 공급 유형 판단 보고서 생성
        
        Args:
            project_address: 사업지 주소
            project_scale: 사업 규모 (예: "총 150세대, 30주차")
            selected_supply_type: 선정된 공급 유형 (예: "신혼희망타운")
            supply_type_analysis: 공급 유형별 분석 데이터
            demographic_analysis: 인구 구성 분석 데이터
            policy_target_score: 정책 대상 적합성 점수
            demand_score: 입지 수요 분석 점수
            supply_feasibility_score: 공급 가능성 점수
            analysis_date: 분석 기준일
            output_path: 출력 파일 경로
            
        Returns:
            str: 생성된 보고서 파일 경로
        """
        print("\n" + "="*80)
        print("🏗️ M3 SUPPLY TYPE ANALYSIS REPORT GENERATOR")
        print("="*80)
        print(f"📍 Project: {project_address}")
        print(f"📏 Scale: {project_scale}")
        print(f"🏘️ Selected Type: {selected_supply_type}")
        print("="*80 + "\n")
        
        # 기본값 설정
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        report_id = f"ZS-M3-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 공급 유형별 분석 데이터 (샘플)
        if supply_type_analysis is None:
            supply_type_analysis = [
                {
                    'supply_type': '신혼희망타운',
                    'policy_priority': '최우선',
                    'regional_demand': '높음',
                    'location_fit': '적합',
                    'total_score': 85,
                    'is_selected': selected_supply_type == '신혼희망타운'
                },
                {
                    'supply_type': '청년주택',
                    'policy_priority': '우선',
                    'regional_demand': '보통',
                    'location_fit': '보통',
                    'total_score': 70,
                    'is_selected': selected_supply_type == '청년주택'
                },
                {
                    'supply_type': '행복주택',
                    'policy_priority': '보통',
                    'regional_demand': '낮음',
                    'location_fit': '부적합',
                    'total_score': 55,
                    'is_selected': selected_supply_type == '행복주택'
                }
            ]
        
        # 인구 구성 분석 데이터 (샘플)
        if demographic_analysis is None:
            demographic_analysis = [
                {
                    'category': '20-30대 미혼',
                    'percentage': 35.5,
                    'analysis': '청년층 비중이 높아 청년주택 수요 예상'
                },
                {
                    'category': '신혼부부 (결혼 7년 이내)',
                    'percentage': 28.3,
                    'analysis': '신혼희망타운 주요 수요층으로 판단'
                },
                {
                    'category': '자녀 1명 이하 가구',
                    'percentage': 22.1,
                    'analysis': '소형 평형 선호층 다수'
                },
                {
                    'category': '기타',
                    'percentage': 14.1,
                    'analysis': '일반 수요층'
                }
            ]
        
        # 총 점수 계산
        total_score = (
            policy_target_score * 0.5 +  # PRIMARY: 50%
            demand_score * 0.3 +           # SECONDARY: 30%
            supply_feasibility_score * 0.2  # REFERENCE: 20%
        )
        
        # 핵심 판단 요약 (REAL APPRAISAL STANDARD v6.5)
        executive_conclusion = (
            f"본 사업지는 정책 대상 적합성, 입지 수요 구조, 심사 안정성을 종합적으로 검토한 결과, "
            f"{selected_supply_type} 공급 유형으로 선정하는 것이 가장 타당합니다. "
            f"다른 유형 대비 정책 적합성과 심사 안정성이 가장 높게 확보됩니다."
        )
        
        # 최종 판단 의견 (REAL APPRAISAL STANDARD v6.5)
        final_opinion = (
            f"종합 검토 결과, 본 사업은 {selected_supply_type} 공급 유형으로 추진하는 것이 가장 합리적이며, "
            f"정책·심사·수요 측면에서 안정성이 확보됩니다. "
            f"\n\n정책 대상 적합성을 중심으로 판단하였으며, 입지 수요 및 공급 가능성을 보조적으로 검토하였습니다. "
            f"본 사업지 주변의 가구 구성은 신혼부부 및 자녀 1명 이하 가구 비중이 높아, "
            f"전용 59㎡ 내외의 중소형 평형 수요가 중심을 이룹니다. "
            f"이는 {selected_supply_type}의 세대 구성 및 평형 기준과 직접적으로 부합합니다. "
            f"\n\n{selected_supply_type}은 LH 정책상 일괄매입 구조가 명확하고 유사 사례 축적으로 심사 안정성이 높습니다."
        )
        
        # 타 유형 배제 사유 데이터
        exclusion_reasons = [
            {
                'supply_type': '청년주택',
                'exclusion_reason': '청년 단일 수요 대비 신혼·소형가구 비중이 높아 정책 효율성 낮음'
            },
            {
                'supply_type': '행복주택',
                'exclusion_reason': '소득·가구 특성상 대상 범위 과다, 정책 우선순위 낮음'
            },
            {
                'supply_type': selected_supply_type,
                'exclusion_reason': '정책 우선순위 및 지역 수요 구조와 가장 부합'
            }
        ]
        
        # 심사 안정성 분석 데이터
        review_stability_analysis = [
            {
                'supply_type': selected_supply_type,
                'stability_level': '높음',
                'reason': 'LH 정책상 일괄매입 구조가 명확하고 유사 사례 축적으로 안정성 높음'
            },
            {
                'supply_type': '청년주택',
                'stability_level': '보통',
                'reason': '지역 수요 대비 대상 범위가 커 조정 가능성 존재'
            },
            {
                'supply_type': '행복주택',
                'stability_level': '낮음',
                'reason': '대상 범위가 광범위하여 심사 기준 적용 시 불확실성 높음'
            }
        ]
        
        # 컨텍스트 구성
        context = {
            'report_id': report_id,
            'project_address': project_address,
            'project_scale': project_scale,
            'analysis_date': analysis_date,
            'selected_supply_type': selected_supply_type,
            'executive_conclusion': executive_conclusion,
            'policy_target_score': policy_target_score,
            'demand_score': demand_score,
            'supply_feasibility_score': supply_feasibility_score,
            'total_score': total_score,
            'supply_type_analysis': supply_type_analysis,
            'demographic_analysis': demographic_analysis,
            'exclusion_reasons': exclusion_reasons,
            'review_stability_analysis': review_stability_analysis,
            'final_opinion': final_opinion,
            # 추가 정보
            'target_demographic': '20-30대 신혼부부, 결혼 7년 이내',
            'income_level': '도시근로자 가구 월평균 소득 100% 이하',
            'household_type': '무주택 세대구성원, 1-2인 가구',
            'policy_support': 'LH 일괄매입, 장기저리 융자 지원',
            'transport_access': '지하철 2호선 역세권 (도보 5분), 버스 정류장 3개소',
            'education_facilities': '초등학교 1개소 (도보 10분), 어린이집 5개소',
            'commercial_facilities': '대형마트 1개소 (1km), 편의점 8개소',
            'medical_facilities': '종합병원 1개소 (2km), 의원 12개소'
        }
        
        # 템플릿 렌더링
        template = self.env.get_template('m3_supply_type_format.html')
        html_content = template.render(**context)
        
        # HTML 저장
        if not output_path:
            output_dir = Path("/home/user/webapp/generated_reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"M3_SupplyType_{timestamp}.html"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        file_size = output_path.stat().st_size / 1024  # KB
        
        print("\n✅ Report Generated!")
        print(f"📄 Output: {output_path}")
        print(f"📊 Size: {file_size:.2f} KB")
        print(f"🏘️ Selected Type: {selected_supply_type}")
        print(f"💯 Total Score: {total_score:.1f}")
        
        return str(output_path)


def main():
    """테스트 실행"""
    generator = M3SupplyTypeGenerator()
    
    output = generator.generate_report(
        project_address="서울특별시 마포구 상암동 1234",
        project_scale="총 150세대 (전용면적 59㎡ 기준), 30주차",
        selected_supply_type="신혼희망타운",
        policy_target_score=85.0,
        demand_score=78.0,
        supply_feasibility_score=72.0
    )
    
    print(f"\n🎉 Test report: {output}")


if __name__ == "__main__":
    main()
