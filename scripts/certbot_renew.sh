#!/bin/bash

###############################################################################
# ZeroSite v7.1 SSL 인증서 자동 갱신 스크립트
# 용도: Let's Encrypt SSL 인증서 자동 갱신 및 서비스 재시작
###############################################################################

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 설정
DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

log_info "SSL 인증서 갱신 시작: ${DOMAIN}"

# Certbot 설치 확인
if ! command -v certbot &> /dev/null; then
    log_error "Certbot이 설치되지 않았습니다."
    log_info "설치: sudo apt-get install certbot python3-certbot-nginx"
    exit 1
fi

# 인증서 갱신 시도
log_info "인증서 갱신 중..."
if sudo certbot renew --quiet --deploy-hook "systemctl reload nginx"; then
    log_info "✅ 인증서 갱신 성공"
    
    # 인증서 정보 출력
    CERT_INFO=$(sudo certbot certificates -d "${DOMAIN}" 2>/dev/null | grep "Expiry Date" || echo "정보 없음")
    log_info "인증서 정보: ${CERT_INFO}"
    
    # Nginx 재시작
    log_info "Nginx 재시작 중..."
    if sudo systemctl reload nginx; then
        log_info "✅ Nginx 재시작 성공"
    else
        log_error "❌ Nginx 재시작 실패"
    fi
    
    # Slack 알림 (성공)
    if [ -n "${SLACK_WEBHOOK_URL}" ]; then
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"✅ SSL 인증서 갱신 성공\",
                \"attachments\": [{
                    \"color\": \"good\",
                    \"fields\": [
                        {\"title\": \"도메인\", \"value\": \"${DOMAIN}\", \"short\": true},
                        {\"title\": \"상태\", \"value\": \"갱신 완료\", \"short\": true}
                    ]
                }]
            }" 2>/dev/null || log_warn "Slack 알림 전송 실패"
    fi
    
else
    log_error "❌ 인증서 갱신 실패"
    
    # Slack 알림 (실패)
    if [ -n "${SLACK_WEBHOOK_URL}" ]; then
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"❌ SSL 인증서 갱신 실패\",
                \"attachments\": [{
                    \"color\": \"danger\",
                    \"fields\": [
                        {\"title\": \"도메인\", \"value\": \"${DOMAIN}\", \"short\": true},
                        {\"title\": \"상태\", \"value\": \"갱신 실패\", \"short\": true}
                    ]
                }]
            }" 2>/dev/null || log_warn "Slack 알림 전송 실패"
    fi
    
    exit 1
fi

# 인증서 만료일 확인
log_info "인증서 만료일 확인 중..."
EXPIRY_DATE=$(sudo certbot certificates -d "${DOMAIN}" 2>/dev/null | grep "Expiry Date" | awk '{print $3, $4, $5}')

if [ -n "${EXPIRY_DATE}" ]; then
    log_info "만료 예정일: ${EXPIRY_DATE}"
    
    # 만료일까지 남은 일수 계산
    EXPIRY_TIMESTAMP=$(date -d "${EXPIRY_DATE}" +%s 2>/dev/null || echo "0")
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_REMAINING=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    log_info "만료까지 남은 일수: ${DAYS_REMAINING}일"
    
    # 경고 알림 (30일 미만)
    if [ ${DAYS_REMAINING} -lt 30 ] && [ -n "${SLACK_WEBHOOK_URL}" ]; then
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"⚠️ SSL 인증서 만료 임박\",
                \"attachments\": [{
                    \"color\": \"warning\",
                    \"fields\": [
                        {\"title\": \"도메인\", \"value\": \"${DOMAIN}\", \"short\": true},
                        {\"title\": \"남은 일수\", \"value\": \"${DAYS_REMAINING}일\", \"short\": true}
                    ]
                }]
            }" 2>/dev/null
    fi
fi

log_info "SSL 인증서 갱신 프로세스 완료"
