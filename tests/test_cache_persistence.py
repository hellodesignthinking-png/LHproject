"""
Tests for Cache Persistence (Redis Optional)
"""

import pytest
import time
from app.core.cache_redis import (
    MemoryCacheBackend,
    CacheTTL,
    PersistentCache,
    create_cache,
    get_from_cache,
    save_to_cache,
    clear_cache,
    get_cache_stats
)


class TestMemoryCacheBackend:
    """메모리 캐시 백엔드 테스트"""
    
    @pytest.fixture
    def cache(self):
        """테스트용 메모리 캐시"""
        return MemoryCacheBackend()
    
    def test_set_and_get(self, cache):
        """저장 및 조회"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent_key(self, cache):
        """존재하지 않는 키 조회"""
        assert cache.get("nonexistent") is None
    
    def test_exists(self, cache):
        """키 존재 여부 확인"""
        cache.set("key1", "value1")
        assert cache.exists("key1") == True
        assert cache.exists("key2") == False
    
    def test_delete(self, cache):
        """키 삭제"""
        cache.set("key1", "value1")
        assert cache.exists("key1") == True
        
        cache.delete("key1")
        assert cache.exists("key1") == False
    
    def test_clear(self, cache):
        """전체 캐시 삭제"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_stats_tracking(self, cache):
        """통계 추적"""
        # Hits
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        
        # Misses
        cache.get("key2")
        cache.get("key3")
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["backend"] == "memory"
        assert "50.00%" in stats["hit_rate"]
    
    def test_complex_values(self, cache):
        """복잡한 값 저장"""
        complex_value = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3)
        }
        cache.set("complex", complex_value)
        assert cache.get("complex") == complex_value


class TestPersistentCache:
    """PersistentCache 테스트"""
    
    @pytest.fixture
    def cache(self):
        """테스트용 캐시 (메모리 백엔드)"""
        return create_cache(redis_url=None)
    
    def test_poi_cache(self, cache):
        """POI 캐시 테스트"""
        location_key = "서울특별시 강남구 역삼동 123-45"
        poi_data = {
            "schools": ["역삼초등학교", "대치중학교"],
            "hospitals": ["강남병원"],
            "distance": 300
        }
        
        cache.set_poi(location_key, poi_data)
        retrieved = cache.get_poi(location_key)
        
        assert retrieved == poi_data
        assert retrieved["distance"] == 300
    
    def test_zoning_cache(self, cache):
        """용도지역 캐시 테스트"""
        address = "서울특별시 강남구 역삼동"
        zoning_data = {
            "zone_type": "제2종일반주거지역",
            "building_coverage": 60,
            "floor_area_ratio": 200
        }
        
        cache.set_zoning(address, zoning_data)
        retrieved = cache.get_zoning(address)
        
        assert retrieved == zoning_data
        assert retrieved["zone_type"] == "제2종일반주거지역"
    
    def test_coordinates_cache(self, cache):
        """좌표 캐시 테스트"""
        address = "서울특별시 강남구 역삼동"
        coords = {"lat": 37.5013, "lng": 127.0396}
        
        cache.set_coordinates(address, coords)
        retrieved = cache.get_coordinates(address)
        
        assert retrieved == coords
    
    def test_generic_cache(self, cache):
        """범용 캐시 테스트"""
        cache.set_generic("test_service", "key1", {"data": "value"})
        retrieved = cache.get_generic("test_service", "key1")
        
        assert retrieved == {"data": "value"}
    
    def test_delete_cache(self, cache):
        """캐시 삭제 테스트"""
        cache.set_generic("test", "key1", "value1")
        assert cache.get_generic("test", "key1") == "value1"
        
        cache.delete("test", "key1")
        assert cache.get_generic("test", "key1") is None
    
    def test_clear_all(self, cache):
        """전체 캐시 삭제 테스트"""
        cache.set_poi("loc1", {"data": 1})
        cache.set_zoning("addr1", {"data": 2})
        cache.set_coordinates("addr2", {"data": 3})
        
        cache.clear_all()
        
        assert cache.get_poi("loc1") is None
        assert cache.get_zoning("addr1") is None
        assert cache.get_coordinates("addr2") is None
    
    def test_cache_key_generation(self, cache):
        """캐시 키 생성 테스트"""
        # 같은 식별자는 같은 키 생성
        key1 = cache._make_key("poi", "location1")
        key2 = cache._make_key("poi", "location1")
        assert key1 == key2
        
        # 다른 식별자는 다른 키 생성
        key3 = cache._make_key("poi", "location2")
        assert key1 != key3
        
        # 다른 서비스는 다른 키 생성
        key4 = cache._make_key("zoning", "location1")
        assert key1 != key4
    
    def test_backend_type(self, cache):
        """백엔드 타입 확인"""
        assert cache.is_redis() == False
        stats = cache.get_stats()
        assert stats["backend"] == "memory"
    
    def test_long_identifier_hashing(self, cache):
        """긴 식별자 해싱 테스트"""
        long_id = "서울특별시 강남구 역삼동 123-45 " * 100  # 매우 긴 문자열
        
        cache.set_generic("test", long_id, {"data": "value"})
        retrieved = cache.get_generic("test", long_id)
        
        assert retrieved == {"data": "value"}


class TestCacheTTL:
    """TTL 설정 테스트"""
    
    def test_ttl_constants(self):
        """TTL 상수 확인"""
        assert CacheTTL.POI == 24 * 60 * 60  # 24시간
        assert CacheTTL.ZONING == 72 * 60 * 60  # 72시간
        assert CacheTTL.COORDINATES == 24 * 60 * 60  # 24시간
        assert CacheTTL.DEFAULT == 60 * 60  # 1시간


class TestLegacyCompatibility:
    """v7.1 호환성 테스트"""
    
    def test_get_from_cache(self):
        """get_from_cache 함수"""
        save_to_cache("test_key", "test_value")
        assert get_from_cache("test_key") == "test_value"
    
    def test_save_to_cache(self):
        """save_to_cache 함수"""
        save_to_cache("key1", {"data": "value"})
        assert get_from_cache("key1") == {"data": "value"}
    
    def test_clear_cache(self):
        """clear_cache 함수"""
        save_to_cache("key1", "value1")
        save_to_cache("key2", "value2")
        
        clear_cache()
        
        assert get_from_cache("key1") is None
        assert get_from_cache("key2") is None
    
    def test_get_cache_stats(self):
        """get_cache_stats 함수"""
        stats = get_cache_stats()
        assert "backend" in stats
        assert "hits" in stats
        assert "misses" in stats


class TestRedisIntegration:
    """Redis 통합 테스트 (Redis 설치 시에만 실행)"""
    
    @pytest.fixture
    def redis_cache(self):
        """Redis 캐시 (사용 가능 시)"""
        try:
            cache = create_cache(redis_url="redis://localhost:6379/15")  # 테스트 DB 15 사용
            if cache.is_redis():
                cache.clear_all()  # 테스트 전 정리
                return cache
        except Exception:
            pass
        pytest.skip("Redis not available")
    
    def test_redis_connection(self, redis_cache):
        """Redis 연결 테스트"""
        assert redis_cache.is_redis() == True
        stats = redis_cache.get_stats()
        assert stats["backend"] == "redis"
    
    def test_redis_set_get(self, redis_cache):
        """Redis 저장 및 조회"""
        redis_cache.set_poi("test_location", {"data": "value"})
        retrieved = redis_cache.get_poi("test_location")
        assert retrieved == {"data": "value"}
    
    def test_redis_complex_data(self, redis_cache):
        """Redis 복잡한 데이터 저장"""
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": {"deep": "value"}},
            "set": {1, 2, 3},  # set은 list로 변환됨
            "tuple": (1, 2, 3)  # tuple은 유지됨
        }
        redis_cache.set_generic("test", "complex", complex_data)
        retrieved = redis_cache.get_generic("test", "complex")
        
        assert retrieved["list"] == [1, 2, 3]
        assert retrieved["dict"]["nested"]["deep"] == "value"


class TestPerformance:
    """성능 테스트"""
    
    @pytest.fixture
    def cache(self):
        """테스트용 캐시"""
        return create_cache(redis_url=None)
    
    def test_memory_cache_performance(self, cache):
        """메모리 캐시 성능 테스트"""
        import time
        
        # 1000개 항목 저장
        start = time.time()
        for i in range(1000):
            cache.set_generic("perf_test", f"key_{i}", {"value": i})
        write_time = time.time() - start
        
        # 1000개 항목 조회
        start = time.time()
        for i in range(1000):
            cache.get_generic("perf_test", f"key_{i}")
        read_time = time.time() - start
        
        print(f"\n메모리 캐시 성능:")
        print(f"  쓰기 (1000개): {write_time:.3f}s")
        print(f"  읽기 (1000개): {read_time:.3f}s")
        
        # 성능 검증 (메모리 캐시는 매우 빨라야 함)
        assert write_time < 1.0  # 1초 이내
        assert read_time < 1.0  # 1초 이내
    
    def test_cache_hit_rate(self, cache):
        """캐시 히트율 테스트"""
        # 데이터 저장
        for i in range(100):
            cache.set_generic("hit_test", f"key_{i}", f"value_{i}")
        
        # 50% 히트, 50% 미스
        for i in range(100):
            cache.get_generic("hit_test", f"key_{i}")  # Hit
        for i in range(100, 200):
            cache.get_generic("hit_test", f"key_{i}")  # Miss
        
        stats = cache.get_stats()
        print(f"\n캐시 통계: {stats}")
        
        # 히트율 확인
        assert stats["hits"] >= 100
        assert stats["misses"] >= 100


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    @pytest.fixture
    def cache(self):
        """테스트용 캐시"""
        return create_cache(redis_url=None)
    
    def test_none_value(self, cache):
        """None 값 저장"""
        cache.set_generic("test", "none_key", None)
        # None은 저장되지만 조회 시 None 반환 (캐시 미스와 구분 불가)
        retrieved = cache.get_generic("test", "none_key")
        assert retrieved is None
    
    def test_empty_string(self, cache):
        """빈 문자열 저장"""
        cache.set_generic("test", "empty", "")
        assert cache.get_generic("test", "empty") == ""
    
    def test_unicode_characters(self, cache):
        """유니코드 문자 저장"""
        korean_text = "한글 테스트 🎉"
        cache.set_generic("test", "unicode", korean_text)
        assert cache.get_generic("test", "unicode") == korean_text
    
    def test_large_data(self, cache):
        """대용량 데이터 저장"""
        large_list = list(range(10000))
        cache.set_generic("test", "large", large_list)
        retrieved = cache.get_generic("test", "large")
        assert len(retrieved) == 10000
        assert retrieved[0] == 0
        assert retrieved[-1] == 9999


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
