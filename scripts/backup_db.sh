#!/bin/bash

###############################################################################
# ZeroSite v7.1 데이터베이스 백업 스크립트
# 용도: 정기적인 데이터베이스 및 설정 파일 백업
###############################################################################

set -e

# 설정
BACKUP_DIR="/var/backups/zerosite"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="zerosite_backup_${TIMESTAMP}"

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

# 백업 디렉토리 생성
mkdir -p "${BACKUP_DIR}"

log_info "백업 시작: ${BACKUP_NAME}"

# 임시 백업 디렉토리 생성
TEMP_BACKUP_DIR="/tmp/${BACKUP_NAME}"
mkdir -p "${TEMP_BACKUP_DIR}"

# 1. 애플리케이션 데이터 백업
log_info "애플리케이션 데이터 백업 중..."

if [ -d "/home/user/webapp/data" ]; then
    cp -r /home/user/webapp/data "${TEMP_BACKUP_DIR}/" || log_warn "데이터 디렉토리 백업 실패"
fi

# 2. 설정 파일 백업
log_info "설정 파일 백업 중..."
if [ -f "/home/user/webapp/.env" ]; then
    cp /home/user/webapp/.env "${TEMP_BACKUP_DIR}/" || log_warn ".env 파일 백업 실패"
fi

if [ -f "/home/user/webapp/config.py" ]; then
    cp /home/user/webapp/config.py "${TEMP_BACKUP_DIR}/" || log_warn "config.py 백업 실패"
fi

# 3. Google Sheets 인증 정보 백업
log_info "인증 정보 백업 중..."
if [ -f "/home/user/webapp/credentials.json" ]; then
    cp /home/user/webapp/credentials.json "${TEMP_BACKUP_DIR}/" || log_warn "credentials.json 백업 실패"
fi

# 4. 로그 파일 백업 (최근 7일)
log_info "로그 파일 백업 중..."
if [ -d "/var/log/zerosite" ]; then
    mkdir -p "${TEMP_BACKUP_DIR}/logs"
    find /var/log/zerosite -name "*.log" -mtime -7 -exec cp {} "${TEMP_BACKUP_DIR}/logs/" \; || log_warn "로그 백업 실패"
fi

# 5. PostgreSQL 백업 (사용 시)
if command -v pg_dump &> /dev/null && [ -n "${DATABASE_URL}" ]; then
    log_info "PostgreSQL 데이터베이스 백업 중..."
    pg_dump "${DATABASE_URL}" > "${TEMP_BACKUP_DIR}/database.sql" 2>/dev/null || log_warn "DB 백업 실패"
fi

# 6. Redis 백업 (사용 시)
if command -v redis-cli &> /dev/null; then
    log_info "Redis 데이터 백업 중..."
    redis-cli --rdb "${TEMP_BACKUP_DIR}/dump.rdb" 2>/dev/null || log_warn "Redis 백업 실패"
fi

# 7. 압축
log_info "백업 파일 압축 중..."
cd /tmp
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}" || {
    log_error "압축 실패"
    rm -rf "${TEMP_BACKUP_DIR}"
    exit 1
}

# 임시 디렉토리 삭제
rm -rf "${TEMP_BACKUP_DIR}"

# 백업 파일 정보
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
log_info "백업 완료: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"

# 8. 오래된 백업 삭제
log_info "오래된 백업 정리 중 (${RETENTION_DAYS}일 이상)..."
find "${BACKUP_DIR}" -name "zerosite_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete || log_warn "백업 정리 실패"

# 9. 백업 목록 출력
log_info "현재 백업 목록:"
ls -lh "${BACKUP_DIR}" | grep "zerosite_backup_"

# 10. Slack 알림 (설정된 경우)
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{
            \"text\": \"✅ ZeroSite 백업 완료\",
            \"attachments\": [{
                \"color\": \"good\",
                \"fields\": [
                    {\"title\": \"백업 파일\", \"value\": \"${BACKUP_NAME}.tar.gz\", \"short\": true},
                    {\"title\": \"크기\", \"value\": \"${BACKUP_SIZE}\", \"short\": true}
                ]
            }]
        }" 2>/dev/null || log_warn "Slack 알림 전송 실패"
fi

log_info "백업 프로세스 완료"
