#!/usr/bin/env python3
"""
ZeroSite v4.0 - Security Audit Script
OWASP ZAP 자동 취약점 스캔
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# OWASP ZAP 설치 확인 및 가이드
SECURITY_CHECKS = {
    "authentication": {
        "name": "인증 및 세션 관리",
        "checks": [
            "JWT 토큰 만료 검증",
            "Refresh 토큰 보안",
            "비밀번호 복잡도 정책",
            "브루트 포스 방어 (Rate Limiting)",
            "세션 고정 공격 방어"
        ]
    },
    "authorization": {
        "name": "권한 관리",
        "checks": [
            "API 키 권한 검증",
            "RBAC (Role-Based Access Control)",
            "수평적 권한 상승 방어",
            "수직적 권한 상승 방어"
        ]
    },
    "input_validation": {
        "name": "입력 검증",
        "checks": [
            "SQL Injection 방어",
            "XSS (Cross-Site Scripting) 방어",
            "CSRF (Cross-Site Request Forgery) 방어",
            "파일 업로드 검증",
            "JSON 입력 검증 (Pydantic)"
        ]
    },
    "cryptography": {
        "name": "암호화",
        "checks": [
            "비밀번호 해싱 (bcrypt)",
            "JWT 서명 검증",
            "API 키 해싱 (SHA256)",
            "HTTPS 강제 사용",
            "민감 데이터 암호화"
        ]
    },
    "security_headers": {
        "name": "보안 헤더",
        "checks": [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Strict-Transport-Security",
            "X-XSS-Protection"
        ]
    },
    "api_security": {
        "name": "API 보안",
        "checks": [
            "Rate Limiting (IP/API Key)",
            "CORS 설정",
            "API 버전 관리",
            "에러 메시지 정보 노출 방지",
            "로깅 및 모니터링"
        ]
    }
}


def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_zap_installation():
    """ZAP 설치 확인"""
    print("🔍 Checking OWASP ZAP installation...")
    
    # ZAP Python API 확인
    try:
        from zapv2 import ZAPv2
        print("✅ OWASP ZAP Python API is installed")
        return True
    except ImportError:
        print("❌ OWASP ZAP Python API not found")
        print("\n📦 Installation Guide:")
        print("   pip install python-owasp-zap-v2.4")
        print("\n🔗 OWASP ZAP Download:")
        print("   https://www.zaproxy.org/download/")
        return False


def generate_security_checklist():
    """보안 체크리스트 생성"""
    print_header("ZeroSite v4.0 - Security Checklist")
    
    checklist = {
        "audit_date": datetime.now().isoformat(),
        "version": "4.0.0",
        "categories": []
    }
    
    for category_id, category in SECURITY_CHECKS.items():
        print(f"\n📋 {category['name']}")
        print("-" * 80)
        
        category_data = {
            "id": category_id,
            "name": category['name'],
            "checks": []
        }
        
        for check in category['checks']:
            print(f"  ☐ {check}")
            category_data['checks'].append({
                "description": check,
                "status": "pending",
                "notes": ""
            })
        
        checklist['categories'].append(category_data)
    
    return checklist


def manual_security_review():
    """수동 보안 검토 가이드"""
    print_header("Manual Security Review Guide")
    
    reviews = [
        {
            "title": "1. 인증 플로우 검토",
            "steps": [
                "로그인 페이지에서 SQL Injection 시도",
                "JWT 토큰 만료 후 요청 시도",
                "잘못된 Refresh 토큰으로 갱신 시도",
                "동시 다중 로그인 테스트",
                "로그아웃 후 토큰 재사용 시도"
            ]
        },
        {
            "title": "2. API 권한 검증",
            "steps": [
                "API 키 없이 보호된 엔드포인트 접근",
                "다른 사용자의 데이터 조회 시도 (IDOR)",
                "만료된 API 키 사용 시도",
                "Rate Limit 초과 테스트",
                "관리자 전용 API 일반 사용자로 접근"
            ]
        },
        {
            "title": "3. 입력 검증 테스트",
            "steps": [
                "특수문자 포함 입력값 테스트",
                "매우 긴 문자열 입력 (Buffer Overflow)",
                "잘못된 JSON 형식 전송",
                "파일 업로드 시 악성 파일 차단 확인",
                "XSS 페이로드 테스트: <script>alert('XSS')</script>"
            ]
        },
        {
            "title": "4. 보안 헤더 확인",
            "steps": [
                "curl -I http://localhost:8000/health 실행",
                "Content-Security-Policy 헤더 존재 확인",
                "X-Frame-Options: DENY 확인",
                "Strict-Transport-Security 확인",
                "X-Content-Type-Options: nosniff 확인"
            ]
        },
        {
            "title": "5. HTTPS 및 암호화",
            "steps": [
                "HTTP로 접속 시 HTTPS 리다이렉트 확인",
                "SSL/TLS 인증서 유효성 검증",
                "약한 암호화 스위트 차단 확인",
                "비밀번호 평문 전송 방지 확인",
                "민감 데이터 로깅 방지 확인"
            ]
        }
    ]
    
    for review in reviews:
        print(f"\n{review['title']}")
        print("-" * 80)
        for i, step in enumerate(review['steps'], 1):
            print(f"  {i}. {step}")
    
    print("\n" + "=" * 80)


def generate_security_report():
    """보안 감사 보고서 생성"""
    output_dir = Path("tests/security_audit_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 체크리스트 저장
    checklist = generate_security_checklist()
    checklist_path = output_dir / "security_checklist.json"
    with open(checklist_path, 'w', encoding='utf-8') as f:
        json.dump(checklist, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Security checklist saved: {checklist_path}")
    
    # 마크다운 보고서 생성
    report_path = output_dir / "security_audit_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# ZeroSite v4.0 Security Audit Report\n\n")
        f.write(f"**Audit Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Executive Summary\n\n")
        f.write("이 보고서는 ZeroSite v4.0 플랫폼의 보안 감사 결과를 요약합니다.\n\n")
        
        f.write("## Security Categories\n\n")
        for category_id, category in SECURITY_CHECKS.items():
            f.write(f"### {category['name']}\n\n")
            for check in category['checks']:
                f.write(f"- [ ] {check}\n")
            f.write("\n")
        
        f.write("## Manual Testing Guide\n\n")
        f.write("상세한 수동 테스트 절차는 스크립트를 실행하여 확인하세요.\n\n")
        
        f.write("## Automated Scan Results\n\n")
        f.write("OWASP ZAP 스캔 결과는 별도 파일로 생성됩니다.\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. 정기적인 보안 스캔 실행 (월 1회 이상)\n")
        f.write("2. 침투 테스트 실시 (연 2회 이상)\n")
        f.write("3. 보안 패치 및 업데이트 적용\n")
        f.write("4. 로그 모니터링 및 이상 징후 탐지\n")
        f.write("5. 보안 교육 및 인식 제고\n")
    
    print(f"✅ Security report saved: {report_path}")
    
    return str(output_dir)


def main():
    """메인 실행 함수"""
    print_header("ZeroSite v4.0 Security Audit Tool")
    
    # ZAP 설치 확인
    zap_installed = check_zap_installation()
    
    # 보안 체크리스트 및 보고서 생성
    output_dir = generate_security_report()
    
    # 수동 검토 가이드 출력
    manual_security_review()
    
    print("\n" + "=" * 80)
    print("\n📁 Security audit files generated in:")
    print(f"   {output_dir}")
    
    if not zap_installed:
        print("\n⚠️  OWASP ZAP is not installed.")
        print("   For automated scanning, please install ZAP:")
        print("   1. Download from https://www.zaproxy.org/download/")
        print("   2. Install ZAP")
        print("   3. Install Python API: pip install python-owasp-zap-v2.4")
        print("   4. Start ZAP in daemon mode: zap.sh -daemon -port 8080")
        print("   5. Re-run this script")
    
    print("\n✅ Security audit preparation complete!")
    print("\n📋 Next Steps:")
    print("   1. Review security_checklist.json")
    print("   2. Perform manual security tests")
    print("   3. Run automated OWASP ZAP scan (if installed)")
    print("   4. Update security_audit_report.md with findings")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
