#!/bin/bash

###############################################################################
# ZeroSite v7.1 데이터베이스 복원 스크립트
# 용도: 백업 파일로부터 시스템 복원
###############################################################################

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_question() {
    echo -e "${BLUE}[?]${NC} $1"
}

# 사용법
usage() {
    echo "사용법: $0 <backup_file.tar.gz>"
    echo "예시: $0 /var/backups/zerosite/zerosite_backup_20250101_120000.tar.gz"
    exit 1
}

# 인자 확인
if [ $# -eq 0 ]; then
    usage
fi

BACKUP_FILE=$1

# 백업 파일 존재 확인
if [ ! -f "${BACKUP_FILE}" ]; then
    log_error "백업 파일을 찾을 수 없습니다: ${BACKUP_FILE}"
    exit 1
fi

log_info "백업 파일: ${BACKUP_FILE}"

# 확인 메시지
log_warn "⚠️  경고: 이 작업은 기존 데이터를 덮어씁니다."
log_question "계속하시겠습니까? (yes/no)"
read -r CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    log_info "복원이 취소되었습니다."
    exit 0
fi

# 서비스 중지
log_info "서비스 중지 중..."
if systemctl is-active --quiet zerosite; then
    sudo systemctl stop zerosite || log_warn "서비스 중지 실패"
fi

# 임시 디렉토리 생성
TEMP_RESTORE_DIR="/tmp/zerosite_restore_$$"
mkdir -p "${TEMP_RESTORE_DIR}"

# 압축 해제
log_info "백업 파일 압축 해제 중..."
tar -xzf "${BACKUP_FILE}" -C "${TEMP_RESTORE_DIR}" || {
    log_error "압축 해제 실패"
    rm -rf "${TEMP_RESTORE_DIR}"
    exit 1
}

# 백업 디렉토리 찾기
BACKUP_DIR=$(find "${TEMP_RESTORE_DIR}" -maxdepth 1 -type d -name "zerosite_backup_*" | head -n 1)

if [ -z "${BACKUP_DIR}" ]; then
    log_error "백업 디렉토리를 찾을 수 없습니다"
    rm -rf "${TEMP_RESTORE_DIR}"
    exit 1
fi

log_info "백업 디렉토리: ${BACKUP_DIR}"

# 1. 애플리케이션 데이터 복원
if [ -d "${BACKUP_DIR}/data" ]; then
    log_info "애플리케이션 데이터 복원 중..."
    rm -rf /home/user/webapp/data
    cp -r "${BACKUP_DIR}/data" /home/user/webapp/ || log_warn "데이터 복원 실패"
fi

# 2. 설정 파일 복원
log_info "설정 파일 복원 중..."
if [ -f "${BACKUP_DIR}/.env" ]; then
    cp "${BACKUP_DIR}/.env" /home/user/webapp/ || log_warn ".env 복원 실패"
fi

if [ -f "${BACKUP_DIR}/config.py" ]; then
    cp "${BACKUP_DIR}/config.py" /home/user/webapp/ || log_warn "config.py 복원 실패"
fi

# 3. 인증 정보 복원
if [ -f "${BACKUP_DIR}/credentials.json" ]; then
    log_info "인증 정보 복원 중..."
    cp "${BACKUP_DIR}/credentials.json" /home/user/webapp/ || log_warn "credentials.json 복원 실패"
fi

# 4. PostgreSQL 복원
if [ -f "${BACKUP_DIR}/database.sql" ] && command -v psql &> /dev/null && [ -n "${DATABASE_URL}" ]; then
    log_info "PostgreSQL 데이터베이스 복원 중..."
    
    log_warn "기존 데이터베이스가 삭제됩니다!"
    log_question "계속하시겠습니까? (yes/no)"
    read -r DB_CONFIRM
    
    if [ "${DB_CONFIRM}" = "yes" ]; then
        psql "${DATABASE_URL}" < "${BACKUP_DIR}/database.sql" || log_warn "DB 복원 실패"
    fi
fi

# 5. Redis 복원
if [ -f "${BACKUP_DIR}/dump.rdb" ] && command -v redis-cli &> /dev/null; then
    log_info "Redis 데이터 복원 중..."
    
    # Redis 중지
    sudo systemctl stop redis || log_warn "Redis 중지 실패"
    
    # dump.rdb 복원
    sudo cp "${BACKUP_DIR}/dump.rdb" /var/lib/redis/dump.rdb || log_warn "Redis dump 복사 실패"
    sudo chown redis:redis /var/lib/redis/dump.rdb
    
    # Redis 재시작
    sudo systemctl start redis || log_warn "Redis 시작 실패"
fi

# 6. 로그 파일 복원 (선택적)
if [ -d "${BACKUP_DIR}/logs" ]; then
    log_info "로그 파일 복원 중..."
    mkdir -p /var/log/zerosite
    cp -r "${BACKUP_DIR}/logs/"* /var/log/zerosite/ 2>/dev/null || log_warn "로그 복원 실패"
fi

# 임시 디렉토리 정리
rm -rf "${TEMP_RESTORE_DIR}"

# 권한 설정
log_info "권한 설정 중..."
sudo chown -R $USER:$USER /home/user/webapp/ || log_warn "권한 설정 실패"

# 서비스 재시작
log_info "서비스 시작 중..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start zerosite || log_warn "서비스 시작 실패"
    sleep 2
    sudo systemctl status zerosite --no-pager || log_warn "서비스 상태 확인 실패"
fi

# Slack 알림
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{
            \"text\": \"✅ ZeroSite 복원 완료\",
            \"attachments\": [{
                \"color\": \"good\",
                \"fields\": [
                    {\"title\": \"백업 파일\", \"value\": \"$(basename ${BACKUP_FILE})\", \"short\": true}
                ]
            }]
        }" 2>/dev/null || log_warn "Slack 알림 전송 실패"
fi

log_info "복원 프로세스 완료!"
log_info "서비스 상태를 확인하세요: sudo systemctl status zerosite"
