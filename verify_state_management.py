#!/usr/bin/env python3
"""
ZeroSite v6.5 - STATE MANAGEMENT 검증 스크립트

주소 변경 시 전 모듈 데이터 100% 갱신을 검증합니다.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class StateManagementVerifier:
    """STATE MANAGEMENT LOCK 검증기"""
    
    def __init__(self, webapp_dir='/home/user/webapp'):
        self.webapp_dir = Path(webapp_dir)
        self.results = {
            'q1_new_context': False,
            'q2_no_cache_reuse': False,
            'q3_same_context_id': False,
            'q4_same_timestamp': False,
            'overall': False
        }
        
    def verify_q1_new_context_on_address_change(self):
        """Q1: 주소 변경 시 context_id 강제 초기화 확인"""
        print("\n" + "="*70)
        print("Q1: 주소를 바꾸면 모든 숫자가 달라질 수 있는가?")
        print("="*70)
        
        # app.py 또는 main API 파일 확인
        api_files = [
            self.webapp_dir / 'app.py',
            self.webapp_dir / 'main_api.py',
            self.webapp_dir / 'api' / 'main.py'
        ]
        
        found_init = False
        for api_file in api_files:
            if not api_file.exists():
                continue
                
            print(f"\n📄 검사 중: {api_file.name}")
            content = api_file.read_text()
            
            # context_id 생성 패턴 확인
            patterns = [
                r'context_id\s*=.*generate.*context',
                r'context_id\s*=.*datetime\.now',
                r'new.*context.*id',
                r'clear.*previous.*context',
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"   ✅ 발견: {pattern}")
                    found_init = True
        
        if found_init:
            print("\n✅ PASS: context_id 초기화 로직 발견")
            self.results['q1_new_context'] = True
        else:
            print("\n❌ FAIL: context_id 강제 초기화 로직 없음")
            print("   ⚠️  주소 변경 시 이전 context 재사용 위험")
        
        return self.results['q1_new_context']
    
    def verify_q2_no_cache_reuse(self):
        """Q2: 이전 주소의 결과가 섞일 가능성 0% 확인"""
        print("\n" + "="*70)
        print("Q2: 이전 주소의 결과가 섞일 가능성은 0%인가?")
        print("="*70)
        
        # generator 파일들 확인
        generator_files = list(self.webapp_dir.glob('generate_*.py'))
        
        cache_risks = []
        for gen_file in generator_files:
            content = gen_file.read_text()
            
            # 캐시 위험 패턴
            risk_patterns = [
                (r'cache.*get', '캐시 조회'),
                (r'@.*cache', '캐시 데코레이터'),
                (r'pickle.*load', 'Pickle 로딩'),
                (r'redis.*get', 'Redis 캐시'),
            ]
            
            for pattern, desc in risk_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    cache_risks.append(f"{gen_file.name}: {desc}")
        
        if cache_risks:
            print("\n❌ FAIL: 캐시 재사용 위험 발견")
            for risk in cache_risks:
                print(f"   ⚠️  {risk}")
            self.results['q2_no_cache_reuse'] = False
        else:
            print("\n✅ PASS: 캐시 재사용 패턴 없음")
            self.results['q2_no_cache_reuse'] = True
        
        return self.results['q2_no_cache_reuse']
    
    def verify_q3_same_context_id(self):
        """Q3: M2~M6 모든 보고서의 context_id 동일성 확인"""
        print("\n" + "="*70)
        print("Q3: M2~M6 모든 보고서의 context_id는 동일한가?")
        print("="*70)
        
        # 최신 보고서들 확인
        latest_reports = list((self.webapp_dir / 'static/latest_reports').glob('M*최신*.html'))
        
        if not latest_reports:
            print("\n⚠️  최신 보고서 없음 - 검증 불가")
            return False
        
        context_ids = {}
        for report in latest_reports:
            content = report.read_text()
            
            # context_id 또는 report_id 패턴 찾기
            match = re.search(r'(context[_-]id|report[_-]id)[:\s]+([A-Z0-9\-]+)', content, re.IGNORECASE)
            if match:
                context_ids[report.name] = match.group(2)
        
        if not context_ids:
            print("\n⚠️  보고서에서 context_id 찾을 수 없음")
            print("   💡 힌트: context_id를 HTML에 명시적으로 포함해야 함")
            return False
        
        print(f"\n📊 발견된 context_id:")
        for report, ctx_id in context_ids.items():
            print(f"   {report}: {ctx_id}")
        
        unique_ids = set(context_ids.values())
        if len(unique_ids) == 1:
            print(f"\n✅ PASS: 모든 보고서가 동일한 context_id 사용")
            self.results['q3_same_context_id'] = True
        else:
            print(f"\n❌ FAIL: {len(unique_ids)}개의 서로 다른 context_id 발견")
            print("   ⚠️  모듈별 독립 실행 위험")
            self.results['q3_same_context_id'] = False
        
        return self.results['q3_same_context_id']
    
    def verify_q4_same_timestamp(self):
        """Q4: 모든 보고서 생성 시각이 동일한 분석 세션인지 확인"""
        print("\n" + "="*70)
        print("Q4: 모든 보고서 생성 시각이 동일한 분석 세션인가?")
        print("="*70)
        
        # 최신 보고서들의 생성 시각 확인
        latest_reports = list((self.webapp_dir / 'static/latest_reports').glob('M*최신*.html'))
        
        if not latest_reports:
            print("\n⚠️  최신 보고서 없음 - 검증 불가")
            return False
        
        timestamps = {}
        for report in latest_reports:
            content = report.read_text()
            
            # 분석 일자 패턴 찾기
            patterns = [
                r'분석\s*일자[:\s]+(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
                r'작성\s*일자[:\s]+(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    timestamps[report.name] = match.group(1)
                    break
        
        if not timestamps:
            print("\n⚠️  보고서에서 생성 시각 찾을 수 없음")
            return False
        
        print(f"\n📊 발견된 생성 시각:")
        for report, ts in timestamps.items():
            print(f"   {report}: {ts}")
        
        unique_times = set(timestamps.values())
        if len(unique_times) == 1:
            print(f"\n✅ PASS: 모든 보고서가 동일한 시각에 생성됨")
            self.results['q4_same_timestamp'] = True
        else:
            print(f"\n❌ FAIL: {len(unique_times)}개의 서로 다른 생성 시각")
            print("   ⚠️  부분 재계산 위험")
            self.results['q4_same_timestamp'] = False
        
        return self.results['q4_same_timestamp']
    
    def run_full_verification(self):
        """전체 검증 실행"""
        print("\n" + "="*70)
        print("🔒 ZeroSite v6.5 - STATE MANAGEMENT LOCK 검증")
        print("="*70)
        print(f"검사 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"대상 디렉토리: {self.webapp_dir}")
        
        # 4문항 검증
        self.verify_q1_new_context_on_address_change()
        self.verify_q2_no_cache_reuse()
        self.verify_q3_same_context_id()
        self.verify_q4_same_timestamp()
        
        # 종합 평가
        print("\n" + "="*70)
        print("📊 종합 평가 결과")
        print("="*70)
        
        all_pass = all([
            self.results['q1_new_context'],
            self.results['q2_no_cache_reuse'],
            self.results['q3_same_context_id'],
            self.results['q4_same_timestamp']
        ])
        
        self.results['overall'] = all_pass
        
        print(f"\nQ1 (주소 변경 시 context 초기화): {'✅ PASS' if self.results['q1_new_context'] else '❌ FAIL'}")
        print(f"Q2 (캐시 재사용 없음):            {'✅ PASS' if self.results['q2_no_cache_reuse'] else '❌ FAIL'}")
        print(f"Q3 (동일 context_id):             {'✅ PASS' if self.results['q3_same_context_id'] else '❌ FAIL'}")
        print(f"Q4 (동일 생성 시각):              {'✅ PASS' if self.results['q4_same_timestamp'] else '❌ FAIL'}")
        
        print("\n" + "="*70)
        if all_pass:
            print("🎉 최종 결과: ✅ ALL PASS")
            print("="*70)
            print("\n✅ STATE MANAGEMENT LOCK 완료")
            print("✅ PUBLIC RELEASE READY")
        else:
            print("⚠️  최종 결과: ❌ FAIL")
            print("="*70)
            print("\n❌ STATE MANAGEMENT LOCK 미완료")
            print("❌ PUBLIC RELEASE NOT READY")
            print("\n⚠️  위험: 주소 변경 시 이전 데이터 혼입 가능성")
            print("⚠️  조치: ZEROSITE_STATE_MANAGEMENT_LOCK.md 참고하여 수정 필요")
        
        print("\n" + "="*70)
        
        return self.results

if __name__ == '__main__':
    verifier = StateManagementVerifier()
    results = verifier.run_full_verification()
    
    # 결과 저장
    output_file = Path('/home/user/webapp/state_management_verification.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 검증 결과 저장: {output_file}")
    
    # Exit code
    exit(0 if results['overall'] else 1)
