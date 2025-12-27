#!/usr/bin/env python3
"""
ZeroSite 4.0 Kill-Switch 상시 감시 시스템
==========================================

Purpose: 운영 환경에서 Kill-Switch를 주기적으로 실행하여
         금지된 판단 로직 패턴이 추가되지 않았는지 감시

Usage:
    # 한 번 실행
    python scripts/kill_switch_monitor.py

    # Cron으로 매시간 실행
    0 * * * * cd /app && python scripts/kill_switch_monitor.py

    # Systemd 서비스로 실행
    systemctl start kill-switch-monitor

Author: ZeroSite 4.0 Team
Date: 2025-12-27
Version: 1.0
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# 설정
# ============================================================================

# 알림 설정
ENABLE_EMAIL_ALERT = os.getenv('KILL_SWITCH_EMAIL_ALERT', 'false').lower() == 'true'
EMAIL_FROM = os.getenv('KILL_SWITCH_EMAIL_FROM', 'alert@zerosite.com')
EMAIL_TO = os.getenv('KILL_SWITCH_EMAIL_TO', 'admin@zerosite.com').split(',')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# Slack 알림 설정
ENABLE_SLACK_ALERT = os.getenv('KILL_SWITCH_SLACK_ALERT', 'false').lower() == 'true'
SLACK_WEBHOOK_URL = os.getenv('KILL_SWITCH_SLACK_WEBHOOK', '')

# 로그 설정
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'kill_switch_monitor.log'

# Kill-Switch 스크립트 경로
KILL_SWITCH_SCRIPT = Path(__file__).parent / 'kill_switch_checker.py'


# ============================================================================
# 로깅
# ============================================================================

def log_message(level: str, message: str):
    """로그 메시지 기록"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # 파일에 기록
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # 콘솔에도 출력
    print(log_entry.strip())


# ============================================================================
# Kill-Switch 실행
# ============================================================================

def run_kill_switch() -> Dict[str, Any]:
    """Kill-Switch 체커 실행"""
    log_message('INFO', 'Running Kill-Switch checker...')
    
    try:
        result = subprocess.run(
            [sys.executable, str(KILL_SWITCH_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        # 결과 파싱
        passed = result.returncode == 0
        critical_count = 0
        warning_count = 0
        
        # 출력에서 위반 건수 추출
        for line in output.split('\n'):
            if 'Summary:' in line:
                # "Summary: 43 CRITICAL, 0 WARNING" 형식
                parts = line.split(':')[-1].strip()
                if 'CRITICAL' in parts:
                    critical_count = int(parts.split()[0])
                if 'WARNING' in parts:
                    warning_count = int(parts.split(',')[-1].split()[0])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'critical_count': critical_count,
            'warning_count': warning_count,
            'output': output,
            'exit_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        log_message('ERROR', 'Kill-Switch checker timed out!')
        return {
            'timestamp': datetime.now().isoformat(),
            'passed': False,
            'critical_count': -1,
            'warning_count': -1,
            'output': 'TIMEOUT',
            'exit_code': -1
        }
    except Exception as e:
        log_message('ERROR', f'Failed to run Kill-Switch checker: {e}')
        return {
            'timestamp': datetime.now().isoformat(),
            'passed': False,
            'critical_count': -1,
            'warning_count': -1,
            'output': str(e),
            'exit_code': -1
        }


# ============================================================================
# 알림
# ============================================================================

def send_email_alert(result: Dict[str, Any]):
    """이메일 알림 발송"""
    if not ENABLE_EMAIL_ALERT or not SMTP_USER:
        return
    
    try:
        subject = '🔴 [ZeroSite 4.0] Kill-Switch 위반 감지!'
        
        body = f"""
ZeroSite 4.0 Kill-Switch 감시 시스템에서 위반을 감지했습니다.

시각: {result['timestamp']}
결과: {'PASSED' if result['passed'] else 'FAILED'}
CRITICAL: {result['critical_count']}건
WARNING: {result['warning_count']}건

상세 내용:
{result['output'][:1000]}

즉시 확인 필요:
1. 최근 커밋 확인
2. 위반 패턴 제거
3. Kill-Switch 재실행 및 검증

자동 롤백 절차:
git revert HEAD
python scripts/kill_switch_checker.py
"""
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ', '.join(EMAIL_TO)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        log_message('INFO', f'Email alert sent to {EMAIL_TO}')
        
    except Exception as e:
        log_message('ERROR', f'Failed to send email alert: {e}')


def send_slack_alert(result: Dict[str, Any]):
    """Slack 알림 발송"""
    if not ENABLE_SLACK_ALERT or not SLACK_WEBHOOK_URL:
        return
    
    try:
        import requests
        
        color = 'danger' if not result['passed'] else 'good'
        
        payload = {
            'attachments': [{
                'color': color,
                'title': '🔴 Kill-Switch 위반 감지!' if not result['passed'] else '✅ Kill-Switch 정상',
                'fields': [
                    {'title': '시각', 'value': result['timestamp'], 'short': True},
                    {'title': '결과', 'value': 'FAILED' if not result['passed'] else 'PASSED', 'short': True},
                    {'title': 'CRITICAL', 'value': str(result['critical_count']), 'short': True},
                    {'title': 'WARNING', 'value': str(result['warning_count']), 'short': True},
                ],
                'footer': 'ZeroSite 4.0 Kill-Switch Monitor'
            }]
        }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        log_message('INFO', 'Slack alert sent')
        
    except Exception as e:
        log_message('ERROR', f'Failed to send Slack alert: {e}')


# ============================================================================
# 메인
# ============================================================================

def main():
    """메인 실행 함수"""
    log_message('INFO', '=' * 80)
    log_message('INFO', 'ZeroSite 4.0 Kill-Switch Monitor - Starting')
    
    # Kill-Switch 실행
    result = run_kill_switch()
    
    # 결과 기록
    result_file = LOG_DIR / f"kill_switch_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    log_message('INFO', f"Result saved to {result_file}")
    
    # 결과 로깅
    if result['passed']:
        log_message('INFO', '✅ Kill-Switch: PASSED')
        log_message('INFO', f"CRITICAL: {result['critical_count']}, WARNING: {result['warning_count']}")
    else:
        log_message('ERROR', '❌ Kill-Switch: FAILED')
        log_message('ERROR', f"CRITICAL: {result['critical_count']}, WARNING: {result['warning_count']}")
        
        # 알림 발송
        send_email_alert(result)
        send_slack_alert(result)
    
    log_message('INFO', 'ZeroSite 4.0 Kill-Switch Monitor - Finished')
    log_message('INFO', '=' * 80)
    
    # 실패 시 exit code 1
    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
