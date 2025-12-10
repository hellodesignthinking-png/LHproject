"""
ZeroSite v18 Phase 4 - Real Transaction Cache System
=====================================================
실거래가 API 호출 최적화 - 파일 기반 캐싱

Features:
- JSON 파일 기반 캐싱 (SQLite 대안)
- TTL 기반 자동 만료 (기본 24시간)
- 지역/기간별 캐시 키 관리
- 통계 및 모니터링
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheMetadata:
    """캐시 메타데이터"""
    key: str
    created_at: str
    expires_at: str
    hit_count: int = 0
    data_size: int = 0


class RealTransactionCache:
    """
    실거래가 API 캐싱 시스템
    
    Cache Structure:
    - cache/real_transaction/
        - land_{region_code}_{year_month}.json
        - building_{region_code}_{year_month}.json
        - metadata.json
    """
    
    def __init__(self, cache_dir: str = "cache/real_transaction", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self.metadata_file = self.cache_dir / "metadata.json"
        self._load_metadata()
        
        logger.info("=" * 80)
        logger.info("💾 RealTransactionCache initialized")
        logger.info(f"   Cache directory: {self.cache_dir.absolute()}")
        logger.info(f"   TTL: {ttl_hours} hours")
        logger.info(f"   Cached entries: {len(self.metadata)}")
        logger.info("=" * 80)
    
    def _load_metadata(self):
        """메타데이터 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = {k: CacheMetadata(**v) for k, v in data.items()}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.metadata.items()}, 
                     f, indent=2, ensure_ascii=False)
    
    def _generate_key(self, cache_type: str, region_code: str, year_month: str) -> str:
        """캐시 키 생성"""
        raw_key = f"{cache_type}_{region_code}_{year_month}"
        return hashlib.md5(raw_key.encode()).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> Path:
        """캐시 파일 경로"""
        return self.cache_dir / f"{key}.json"
    
    def get(self, cache_type: str, region_code: str, year_month: str) -> Optional[List[Dict]]:
        """
        캐시 조회
        
        Args:
            cache_type: 'land' or 'building'
            region_code: 지역코드 (예: '11110')
            year_month: 조회 년월 (예: '202412')
        
        Returns:
            캐시된 데이터 또는 None
        """
        key = self._generate_key(cache_type, region_code, year_month)
        
        # 메타데이터 확인
        if key not in self.metadata:
            logger.debug(f"❌ Cache MISS: {cache_type}/{region_code}/{year_month}")
            return None
        
        meta = self.metadata[key]
        
        # TTL 확인
        expires_at = datetime.fromisoformat(meta.expires_at)
        if datetime.now() > expires_at:
            logger.info(f"⏰ Cache EXPIRED: {cache_type}/{region_code}/{year_month}")
            self._delete_cache(key)
            return None
        
        # 캐시 파일 읽기
        cache_file = self._get_cache_file_path(key)
        if not cache_file.exists():
            logger.warning(f"⚠️ Cache file missing: {key}")
            del self.metadata[key]
            self._save_metadata()
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Hit count 업데이트
        meta.hit_count += 1
        self._save_metadata()
        
        logger.info(f"✅ Cache HIT: {cache_type}/{region_code}/{year_month} (hit #{meta.hit_count})")
        return data
    
    def set(self, cache_type: str, region_code: str, year_month: str, data: List[Dict]):
        """
        캐시 저장
        
        Args:
            cache_type: 'land' or 'building'
            region_code: 지역코드
            year_month: 조회 년월
            data: 저장할 데이터
        """
        key = self._generate_key(cache_type, region_code, year_month)
        
        # 데이터 저장
        cache_file = self._get_cache_file_path(key)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 메타데이터 생성
        now = datetime.now()
        expires_at = now + timedelta(hours=self.ttl_hours)
        
        self.metadata[key] = CacheMetadata(
            key=key,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            hit_count=0,
            data_size=len(data)
        )
        self._save_metadata()
        
        logger.info(f"💾 Cache SAVED: {cache_type}/{region_code}/{year_month} ({len(data)} records)")
    
    def _delete_cache(self, key: str):
        """캐시 삭제"""
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            cache_file.unlink()
        
        if key in self.metadata:
            del self.metadata[key]
            self._save_metadata()
    
    def clear_expired(self):
        """만료된 캐시 정리"""
        now = datetime.now()
        expired_keys = []
        
        for key, meta in self.metadata.items():
            expires_at = datetime.fromisoformat(meta.expires_at)
            if now > expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._delete_cache(key)
        
        if expired_keys:
            logger.info(f"🗑️ Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        total_entries = len(self.metadata)
        total_hits = sum(m.hit_count for m in self.metadata.values())
        total_size = sum(m.data_size for m in self.metadata.values())
        
        # 만료 시간별 분류
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for meta in self.metadata.values():
            expires_at = datetime.fromisoformat(meta.expires_at)
            if now <= expires_at:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "total_hits": total_hits,
            "total_records": total_size,
            "cache_dir": str(self.cache_dir.absolute()),
            "ttl_hours": self.ttl_hours
        }
    
    def print_stats(self):
        """캐시 통계 출력"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("📊 Real Transaction Cache Statistics")
        print("=" * 80)
        print(f"Total Entries:    {stats['total_entries']}")
        print(f"Valid Entries:    {stats['valid_entries']}")
        print(f"Expired Entries:  {stats['expired_entries']}")
        print(f"Total Hits:       {stats['total_hits']}")
        print(f"Total Records:    {stats['total_records']}")
        print(f"Cache Directory:  {stats['cache_dir']}")
        print(f"TTL:              {stats['ttl_hours']} hours")
        print("=" * 80 + "\n")


# Singleton instance
_cache_instance = None

def get_cache(ttl_hours: int = 24) -> RealTransactionCache:
    """캐시 인스턴스 가져오기"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RealTransactionCache(ttl_hours=ttl_hours)
    return _cache_instance
