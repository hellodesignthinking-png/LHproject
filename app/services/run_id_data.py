"""
v1.6.0: RUN_ID Data Integration Service
실제 RUN_ID 데이터 조회 및 관리
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.services.context_storage import context_storage
from app.models.context_snapshot import ContextSnapshot
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class RunIdInfo(BaseModel):
    """RUN_ID 정보 모델"""
    run_id: str
    address: Optional[str] = None
    pnu: Optional[str] = None
    land_area: Optional[float] = None
    zone: Optional[str] = None
    created_at: datetime
    status: str = "ACTIVE"
    has_data: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "RUN_20260101_ABC123",
                "address": "서울시 강남구 테헤란로 123",
                "pnu": "1168010100",
                "land_area": 500.0,
                "zone": "제2종일반주거지역",
                "created_at": "2026-01-01T12:00:00",
                "status": "ACTIVE",
                "has_data": True
            }
        }


class RunIdDataService:
    """
    RUN_ID 데이터 통합 서비스
    
    데이터 소스:
    1. Context Storage (Redis/Memory)
    2. Database Snapshots
    3. 테스트 데이터 (DEV 모드)
    """
    
    def __init__(self):
        self.test_run_ids = self._generate_test_run_ids()
    
    def _generate_test_run_ids(self) -> List[RunIdInfo]:
        """테스트용 RUN_ID 생성 (DEV 모드)"""
        base_time = datetime.now()
        
        return [
            RunIdInfo(
                run_id="TEST_6REPORT",
                address="서울시 강남구 테헤란로 123",
                pnu="1168010100",
                land_area=500.0,
                zone="제2종일반주거지역",
                created_at=base_time - timedelta(hours=2),
                status="ACTIVE",
                has_data=True
            ),
            RunIdInfo(
                run_id="RUN_20260101_SAMPLE_A",
                address="서울시 서초구 반포대로 58",
                pnu="1165010100",
                land_area=800.0,
                zone="제3종일반주거지역",
                created_at=base_time - timedelta(days=1),
                status="ACTIVE",
                has_data=True
            ),
            RunIdInfo(
                run_id="RUN_20260101_SAMPLE_B",
                address="경기도 성남시 분당구 판교역로 235",
                pnu="4113510100",
                land_area=1200.0,
                zone="준주거지역",
                created_at=base_time - timedelta(days=2),
                status="ACTIVE",
                has_data=True
            ),
            RunIdInfo(
                run_id="RUN_20260101_SAMPLE_C",
                address="인천시 연수구 송도동 123",
                pnu="2871510100",
                land_area=600.0,
                zone="제2종일반주거지역",
                created_at=base_time - timedelta(days=3),
                status="ACTIVE",
                has_data=True
            ),
            RunIdInfo(
                run_id="RUN_20260101_SAMPLE_D",
                address="대전시 유성구 대학로 99",
                pnu="3023010100",
                land_area=450.0,
                zone="준주거지역",
                created_at=base_time - timedelta(days=5),
                status="ACTIVE",
                has_data=True
            )
        ]
    
    def get_all_run_ids(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[RunIdInfo]:
        """
        모든 RUN_ID 조회
        
        Args:
            status: 상태 필터 (ACTIVE, EXPIRED, etc.)
            limit: 최대 조회 개수
            
        Returns:
            RUN_ID 정보 리스트
        """
        run_ids = []
        
        # 1. Database에서 조회
        try:
            db_run_ids = self._get_from_database(limit=limit)
            run_ids.extend(db_run_ids)
        except Exception as e:
            logger.warning(f"Failed to load RUN_IDs from database: {e}")
        
        # 2. 테스트 데이터 추가 (개발 모드)
        import os
        if os.getenv("ZEROSITE_ENV", "dev").lower() == "dev":
            run_ids.extend(self.test_run_ids)
        
        # 3. 상태 필터링
        if status:
            run_ids = [r for r in run_ids if r.status == status]
        
        # 4. 생성일 기준 정렬 (최신순)
        run_ids.sort(key=lambda x: x.created_at, reverse=True)
        
        # 5. 중복 제거 (run_id 기준)
        seen = set()
        unique_run_ids = []
        for r in run_ids:
            if r.run_id not in seen:
                seen.add(r.run_id)
                unique_run_ids.append(r)
        
        return unique_run_ids[:limit]
    
    def _get_from_database(self, limit: int = 100) -> List[RunIdInfo]:
        """데이터베이스에서 RUN_ID 조회"""
        run_ids = []
        
        try:
            with SessionLocal() as db:
                # ContextSnapshot에서 조회
                snapshots = db.query(ContextSnapshot).order_by(
                    ContextSnapshot.created_at.desc()
                ).limit(limit).all()
                
                for snapshot in snapshots:
                    # JSON 데이터에서 정보 추출
                    try:
                        context_data = snapshot.context_data
                        
                        run_ids.append(RunIdInfo(
                            run_id=snapshot.context_id,
                            address=context_data.get('address'),
                            pnu=context_data.get('pnu'),
                            land_area=context_data.get('land_area'),
                            zone=context_data.get('zone'),
                            created_at=snapshot.created_at,
                            status="ACTIVE",
                            has_data=True
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse snapshot {snapshot.context_id}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Database query failed: {e}")
        
        return run_ids
    
    def get_run_id_info(self, run_id: str) -> Optional[RunIdInfo]:
        """
        특정 RUN_ID 정보 조회
        
        Args:
            run_id: RUN_ID
            
        Returns:
            RUN_ID 정보 또는 None
        """
        # 1. Database 조회
        try:
            with SessionLocal() as db:
                snapshot = db.query(ContextSnapshot).filter(
                    ContextSnapshot.context_id == run_id
                ).first()
                
                if snapshot:
                    context_data = snapshot.context_data
                    return RunIdInfo(
                        run_id=snapshot.context_id,
                        address=context_data.get('address'),
                        pnu=context_data.get('pnu'),
                        land_area=context_data.get('land_area'),
                        zone=context_data.get('zone'),
                        created_at=snapshot.created_at,
                        status="ACTIVE",
                        has_data=True
                    )
        except Exception as e:
            logger.warning(f"Failed to query database for {run_id}: {e}")
        
        # 2. 테스트 데이터에서 조회
        for test_run in self.test_run_ids:
            if test_run.run_id == run_id:
                return test_run
        
        return None
    
    def search_run_ids(
        self,
        query: str,
        limit: int = 20
    ) -> List[RunIdInfo]:
        """
        RUN_ID 검색 (주소, PNU, RUN_ID로 검색)
        
        Args:
            query: 검색어
            limit: 최대 결과 개수
            
        Returns:
            검색 결과 리스트
        """
        all_run_ids = self.get_all_run_ids(limit=100)
        
        # 검색어 정규화 (공백 제거만, lower는 한글에 문제 없음)
        query_normalized = query.strip()
        
        logger.info(f"🔍 Searching for: '{query_normalized}' (total RUN_IDs: {len(all_run_ids)})")
        
        # 필터링
        results = []
        for run_id_info in all_run_ids:
            # RUN_ID 매칭 (대소문자 무시)
            if query_normalized.lower() in run_id_info.run_id.lower():
                results.append(run_id_info)
                logger.debug(f"  ✓ Matched RUN_ID: {run_id_info.run_id}")
                continue
            
            # 주소 매칭 (한글은 대소문자 없으므로 그대로 비교)
            if run_id_info.address and query_normalized in run_id_info.address:
                results.append(run_id_info)
                logger.debug(f"  ✓ Matched Address: {run_id_info.address}")
                continue
            
            # PNU 매칭
            if run_id_info.pnu and query_normalized in run_id_info.pnu:
                results.append(run_id_info)
                logger.debug(f"  ✓ Matched PNU: {run_id_info.pnu}")
                continue
        
        logger.info(f"🔍 Search results: {len(results)} items found")
        return results[:limit]
    
    def get_run_id_statistics(self) -> Dict[str, Any]:
        """
        RUN_ID 통계 조회
        
        Returns:
            통계 정보 딕셔너리
        """
        all_run_ids = self.get_all_run_ids(limit=1000)
        
        # 상태별 카운트
        status_count = {}
        for r in all_run_ids:
            status_count[r.status] = status_count.get(r.status, 0) + 1
        
        # 지역별 카운트 (주소 기준)
        region_count = {}
        for r in all_run_ids:
            if r.address:
                # 첫 단어 추출 (예: "서울시", "경기도")
                region = r.address.split()[0] if r.address.split() else "기타"
                region_count[region] = region_count.get(region, 0) + 1
        
        # 최근 생성된 RUN_ID
        recent = sorted(all_run_ids, key=lambda x: x.created_at, reverse=True)[:5]
        
        return {
            "total_count": len(all_run_ids),
            "active_count": status_count.get("ACTIVE", 0),
            "by_status": status_count,
            "by_region": region_count,
            "recent": [r.run_id for r in recent]
        }


# Singleton instance
_service_instance: Optional[RunIdDataService] = None


def get_run_id_service() -> RunIdDataService:
    """RUN_ID 데이터 서비스 싱글톤 인스턴스"""
    global _service_instance
    if _service_instance is None:
        _service_instance = RunIdDataService()
    return _service_instance
