"""
PDF 캐싱 서비스

목적:
- RUN_ID × report_type 조합의 PDF를 로컬 파일 시스템에 캐시
- 캐시 HIT 시 즉시 반환, MISS 시에만 Playwright 실행
- TTL 24시간, 서버 재기동 후에도 유지

캐시 키 형식: pdf:{run_id}:{report_type}
저장 경로: /tmp/zerosite_pdf_cache/{run_id}_{report_type}.pdf
메타데이터: /tmp/zerosite_pdf_cache/{run_id}_{report_type}.meta
"""

import os
import time
import json
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 캐시 설정
CACHE_DIR = Path("/tmp/zerosite_pdf_cache")
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24시간


def _ensure_cache_dir():
    """캐시 디렉토리 생성 보장"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_paths(run_id: str, report_type: str) -> tuple[Path, Path]:
    """
    캐시 파일 경로 반환
    
    Returns:
        (pdf_path, meta_path)
    """
    _ensure_cache_dir()
    
    # 파일명 안전하게 구성 (특수문자 제거)
    safe_run_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in run_id)
    safe_report_type = "".join(c if c.isalnum() or c in "_-" else "_" for c in report_type)
    
    filename_base = f"{safe_run_id}_{safe_report_type}"
    
    pdf_path = CACHE_DIR / f"{filename_base}.pdf"
    meta_path = CACHE_DIR / f"{filename_base}.meta"
    
    return pdf_path, meta_path


def _is_cache_valid(meta_path: Path) -> bool:
    """
    캐시 유효성 검사 (TTL 24시간)
    
    Args:
        meta_path: 메타데이터 파일 경로
    
    Returns:
        True if valid, False if expired or missing
    """
    if not meta_path.exists():
        return False
    
    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
        
        created_at = meta.get("created_at", 0)
        now = time.time()
        
        age = now - created_at
        is_valid = age < CACHE_TTL_SECONDS
        
        if not is_valid:
            logger.info(f"Cache expired: age={age:.0f}s, TTL={CACHE_TTL_SECONDS}s")
        
        return is_valid
    
    except Exception as e:
        logger.warning(f"Failed to validate cache meta: {e}")
        return False


def get_cached_pdf(run_id: str, report_type: str) -> Optional[bytes]:
    """
    캐시에서 PDF 조회
    
    Args:
        run_id: RUN_ID (예: TEST_6REPORT)
        report_type: 보고서 타입 (예: quick-review)
    
    Returns:
        PDF bytes if cache HIT, None if MISS or expired
    """
    pdf_path, meta_path = _get_cache_paths(run_id, report_type)
    
    # 캐시 유효성 검사
    if not _is_cache_valid(meta_path):
        logger.info(f"Cache MISS: run_id={run_id}, report_type={report_type}")
        return None
    
    # PDF 파일 읽기
    if not pdf_path.exists():
        logger.warning(f"Cache meta exists but PDF missing: {pdf_path}")
        return None
    
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        logger.info(f"Cache HIT: run_id={run_id}, report_type={report_type}, size={len(pdf_bytes)} bytes")
        return pdf_bytes
    
    except Exception as e:
        logger.error(f"Failed to read cached PDF: {e}")
        return None


def set_cached_pdf(run_id: str, report_type: str, pdf_bytes: bytes) -> bool:
    """
    PDF를 캐시에 저장
    
    Args:
        run_id: RUN_ID
        report_type: 보고서 타입
        pdf_bytes: PDF 바이트 데이터
    
    Returns:
        True if success, False if failed
    """
    pdf_path, meta_path = _get_cache_paths(run_id, report_type)
    
    try:
        # PDF 저장
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        # 메타데이터 저장
        meta = {
            "run_id": run_id,
            "report_type": report_type,
            "created_at": time.time(),
            "size_bytes": len(pdf_bytes),
            "ttl_seconds": CACHE_TTL_SECONDS
        }
        
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        
        logger.info(f"Cache SET: run_id={run_id}, report_type={report_type}, size={len(pdf_bytes)} bytes")
        return True
    
    except Exception as e:
        logger.error(f"Failed to cache PDF: {e}")
        return False


def clear_expired_cache():
    """
    만료된 캐시 파일 삭제 (선택적 유틸리티)
    """
    _ensure_cache_dir()
    
    cleared_count = 0
    
    for meta_path in CACHE_DIR.glob("*.meta"):
        if not _is_cache_valid(meta_path):
            # 메타 파일 삭제
            meta_path.unlink(missing_ok=True)
            
            # 대응하는 PDF 파일 삭제
            pdf_path = meta_path.with_suffix(".pdf")
            pdf_path.unlink(missing_ok=True)
            
            cleared_count += 1
    
    if cleared_count > 0:
        logger.info(f"Cleared {cleared_count} expired cache entries")
    
    return cleared_count


def get_cache_stats() -> dict:
    """
    캐시 통계 반환 (디버깅/모니터링용)
    
    Returns:
        {
            "total_entries": int,
            "total_size_bytes": int,
            "expired_entries": int
        }
    """
    _ensure_cache_dir()
    
    total_entries = 0
    expired_entries = 0
    total_size = 0
    
    for meta_path in CACHE_DIR.glob("*.meta"):
        total_entries += 1
        
        if not _is_cache_valid(meta_path):
            expired_entries += 1
        
        pdf_path = meta_path.with_suffix(".pdf")
        if pdf_path.exists():
            total_size += pdf_path.stat().st_size
    
    return {
        "total_entries": total_entries,
        "total_size_bytes": total_size,
        "expired_entries": expired_entries,
        "cache_dir": str(CACHE_DIR)
    }
