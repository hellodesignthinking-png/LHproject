#!/usr/bin/env python3
"""
ZeroSite CLI v1.0
Command-Line Interface for ZeroSite Land Analysis Platform

Commands:
  analyze              토지 분석 수행
  generate-report      보고서 생성
  sync-lh-notices      LH 공고 동기화
  multi-parcel         다필지 통합 분석
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ZeroSiteCLI:
    """ZeroSite CLI v1.0"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.project_root = Path(__file__).parent.parent
    
    async def analyze_land(
        self,
        address: str,
        land_area: float,
        unit_type: str = "청년",
        lh_version: str = "2024",
        output: Optional[str] = None
    ):
        """
        토지 분석 수행
        
        Args:
            address: 분석할 토지 주소
            land_area: 토지 면적 (㎡)
            unit_type: 세대 유형
            lh_version: LH 기준 버전
            output: 출력 JSON 파일 경로
        """
        from app.services.analysis_engine import AnalysisEngine
        from app.schemas import LandAnalysisRequest
        
        print(f"🔍 ZeroSite 토지 분석 시작")
        print(f"   주소: {address}")
        print(f"   면적: {land_area}㎡")
        print(f"   유형: {unit_type}")
        print(f"   LH 버전: {lh_version}")
        print("")
        
        # 분석 요청 생성
        request = LandAnalysisRequest(
            address=address,
            land_area=land_area,
            unit_type=unit_type,
            lh_version=lh_version
        )
        
        # 분석 엔진 초기화 및 실행
        engine = AnalysisEngine()
        
        try:
            result = await engine.analyze_land(request)
            
            # 결과 출력
            print("✅ 분석 완료!")
            print(f"   LH 점수: {result.grade.total_score:.1f}/350점")
            print(f"   등급: {result.grade.grade}")
            print(f"   세대수: {result.building.units}세대")
            print(f"   수요 수준: {result.demand.demand_level}")
            
            # JSON 출력
            if output:
                result_dict = result.dict()
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(result_dict, f, ensure_ascii=False, indent=2)
                print(f"   결과 저장: {output}")
            else:
                # stdout로 JSON 출력
                print("\n" + "="*60)
                print(json.dumps(result.dict(), ensure_ascii=False, indent=2))
        
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
            sys.exit(1)
    
    def generate_report(
        self,
        input_json: str,
        output: str,
        format: str = 'pdf',
        template: Optional[str] = None
    ):
        """
        보고서 생성
        
        Args:
            input_json: 입력 JSON 파일 (분석 결과)
            output: 출력 파일 경로
            format: 출력 형식 (pdf/html/markdown)
            template: 커스텀 템플릿 경로
        """
        from scripts.generate_report_v6 import ZeroSiteReportGenerator
        
        print(f"📄 ZeroSite 보고서 생성")
        print(f"   입력: {input_json}")
        print(f"   출력: {output}")
        print(f"   형식: {format}")
        print("")
        
        # 보고서 생성기 초기화 및 실행
        generator = ZeroSiteReportGenerator(template_path=template)
        generator.generate_report(
            input_json=input_json,
            output_path=output,
            output_format=format
        )
    
    async def sync_lh_notices(
        self,
        year: int,
        region: Optional[str] = None,
        output: Optional[str] = None
    ):
        """
        LH 공고 동기화
        
        Args:
            year: 연도
            region: 지역 필터 (선택)
            output: 출력 JSON 파일 경로
        """
        print(f"🔄 LH 공고 동기화")
        print(f"   연도: {year}")
        print(f"   지역: {region if region else '전체'}")
        print("")
        
        # LH 공고 스크래핑 로직 (예시)
        notices = [
            {
                "id": "LH2024001",
                "title": "서울 강남구 역삼동 신축매입임대 공고",
                "region": "서울",
                "units": 50,
                "posted_date": "2024-03-15",
                "deadline": "2024-04-30"
            },
            {
                "id": "LH2024002",
                "title": "경기 광명시 신혼·신생아 공고",
                "region": "경기",
                "units": 60,
                "posted_date": "2024-03-20",
                "deadline": "2024-05-15"
            }
        ]
        
        # 지역 필터 적용
        if region:
            notices = [n for n in notices if region in n['region']]
        
        print(f"✅ {len(notices)}개 공고 동기화 완료")
        for notice in notices:
            print(f"   - [{notice['id']}] {notice['title']} ({notice['units']}세대)")
        
        # JSON 출력
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(notices, f, ensure_ascii=False, indent=2)
            print(f"   결과 저장: {output}")
    
    async def multi_parcel_analysis(
        self,
        parcel_file: str,
        unit_type: str = "청년",
        output: Optional[str] = None
    ):
        """
        다필지 통합 분석
        
        Args:
            parcel_file: 필지 정보 JSON 파일
            unit_type: 세대 유형
            output: 출력 JSON 파일 경로
        """
        print(f"🏘️ 다필지 통합 분석")
        print(f"   입력: {parcel_file}")
        print(f"   유형: {unit_type}")
        print("")
        
        # 필지 정보 로드
        try:
            with open(parcel_file, 'r', encoding='utf-8') as f:
                parcels = json.load(f)
        except Exception as e:
            print(f"❌ 필지 파일 로드 실패: {e}")
            sys.exit(1)
        
        print(f"   필지 수: {len(parcels)}개")
        
        # 각 필지 분석
        results = []
        for i, parcel in enumerate(parcels, 1):
            print(f"   [{i}/{len(parcels)}] 분석 중: {parcel.get('address', 'N/A')}")
            
            # 분석 수행 (실제 엔진 호출)
            try:
                result = await self.analyze_land(
                    address=parcel['address'],
                    land_area=parcel['land_area'],
                    unit_type=unit_type,
                    output=None
                )
                results.append(result)
            except Exception as e:
                print(f"      ⚠️ 분석 실패: {e}")
        
        print(f"✅ {len(results)}/{len(parcels)}개 필지 분석 완료")
        
        # 통합 분석 결과
        combined_result = {
            "total_parcels": len(parcels),
            "analyzed_parcels": len(results),
            "analysis_date": datetime.now().isoformat(),
            "results": results
        }
        
        # JSON 출력
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(combined_result, f, ensure_ascii=False, indent=2)
            print(f"   결과 저장: {output}")


def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description='ZeroSite CLI v1.0 - LH 토지 분석 플랫폼',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  analyze              토지 분석 수행
  generate-report      보고서 생성
  sync-lh-notices      LH 공고 동기화
  multi-parcel         다필지 통합 분석

Examples:
  # 토지 분석
  zerosite analyze --address "서울 강남구 역삼동 123" --area 1500 --type 청년
  
  # 보고서 생성
  zerosite generate-report -i analysis.json -o report.pdf
  
  # LH 공고 동기화
  zerosite sync-lh-notices --year 2024 --region 서울
  
  # 다필지 분석
  zerosite multi-parcel -i parcels.json -t 신혼·신생아I -o results.json
        """
    )
    
    # 버전 정보
    parser.add_argument('--version', action='version', version='ZeroSite CLI v1.0.0')
    
    # 서브커맨드 파서
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # 1. analyze 명령어
    analyze_parser = subparsers.add_parser('analyze', help='토지 분석 수행')
    analyze_parser.add_argument('--address', '-a', required=True, help='토지 주소')
    analyze_parser.add_argument('--area', '-s', type=float, required=True, help='토지 면적 (㎡)')
    analyze_parser.add_argument('--type', '-t', default='청년', help='세대 유형 (기본값: 청년)')
    analyze_parser.add_argument('--lh-version', '-v', default='2024', help='LH 기준 버전 (기본값: 2024)')
    analyze_parser.add_argument('--output', '-o', help='출력 JSON 파일 경로')
    
    # 2. generate-report 명령어
    report_parser = subparsers.add_parser('generate-report', help='보고서 생성')
    report_parser.add_argument('--input', '-i', required=True, help='입력 JSON 파일')
    report_parser.add_argument('--output', '-o', required=True, help='출력 파일 경로')
    report_parser.add_argument('--format', '-f', choices=['pdf', 'html', 'markdown'], default='pdf', help='출력 형식')
    report_parser.add_argument('--template', '-t', help='커스텀 템플릿 경로')
    
    # 3. sync-lh-notices 명령어
    sync_parser = subparsers.add_parser('sync-lh-notices', help='LH 공고 동기화')
    sync_parser.add_argument('--year', '-y', type=int, required=True, help='연도')
    sync_parser.add_argument('--region', '-r', help='지역 필터')
    sync_parser.add_argument('--output', '-o', help='출력 JSON 파일 경로')
    
    # 4. multi-parcel 명령어
    multi_parser = subparsers.add_parser('multi-parcel', help='다필지 통합 분석')
    multi_parser.add_argument('--input', '-i', required=True, help='필지 정보 JSON 파일')
    multi_parser.add_argument('--type', '-t', default='청년', help='세대 유형')
    multi_parser.add_argument('--output', '-o', help='출력 JSON 파일 경로')
    
    # 인자 파싱
    args = parser.parse_args()
    
    # 명령어가 없으면 help 출력
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # CLI 인스턴스 생성
    cli = ZeroSiteCLI()
    
    # 명령어 실행
    try:
        if args.command == 'analyze':
            asyncio.run(cli.analyze_land(
                address=args.address,
                land_area=args.area,
                unit_type=args.type,
                lh_version=args.lh_version,
                output=args.output
            ))
        
        elif args.command == 'generate-report':
            cli.generate_report(
                input_json=args.input,
                output=args.output,
                format=args.format,
                template=args.template
            )
        
        elif args.command == 'sync-lh-notices':
            asyncio.run(cli.sync_lh_notices(
                year=args.year,
                region=args.region,
                output=args.output
            ))
        
        elif args.command == 'multi-parcel':
            asyncio.run(cli.multi_parcel_analysis(
                parcel_file=args.input,
                unit_type=args.type,
                output=args.output
            ))
    
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
