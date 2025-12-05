"""
Tests for API Rate Limit & Failover System
"""

import pytest
import asyncio
from datetime import datetime
from app.core.rate_limit import (
    RateLimitManager,
    APIProvider,
    CircuitState,
    RetryConfig,
    CircuitBreaker,
    rate_limit_manager,
    execute_with_failover
)


class TestCircuitBreaker:
    """Circuit Breaker 테스트"""
    
    def test_initial_state_closed(self):
        """초기 상태는 CLOSED"""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_request() == True
    
    def test_transition_to_open_on_failures(self):
        """연속 실패 시 OPEN으로 전환"""
        cb = CircuitBreaker(failure_threshold=3)
        
        for i in range(3):
            cb.record_failure()
        
        assert cb.state == CircuitState.OPEN
        assert cb.can_request() == False
    
    def test_transition_to_half_open_after_timeout(self):
        """Timeout 후 HALF_OPEN으로 전환"""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        # OPEN 상태로 전환
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        
        # Timeout 대기
        import time
        time.sleep(0.2)
        
        # HALF_OPEN으로 전환 확인
        assert cb.can_request() == True
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_recovery_to_closed_on_success(self):
        """성공 시 CLOSED로 복구"""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        # OPEN 상태로 전환
        cb.record_failure()
        cb.record_failure()
        
        # Timeout 후 HALF_OPEN
        import time
        time.sleep(0.2)
        cb.can_request()
        
        # 성공으로 CLOSED 복구
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestRateLimitManager:
    """Rate Limit Manager 테스트"""
    
    @pytest.fixture
    def manager(self):
        """테스트용 매니저"""
        config = RetryConfig(max_retries=3, base_delay=0.1, max_delay=1.0)
        return RateLimitManager(retry_config=config)
    
    def test_initial_stats(self, manager):
        """초기 통계 확인"""
        stats = manager.get_stats()
        assert "providers" in stats
        assert APIProvider.KAKAO.value in stats["providers"]
        assert APIProvider.NAVER.value in stats["providers"]
        assert APIProvider.GOOGLE.value in stats["providers"]
    
    def test_record_success(self, manager):
        """성공 기록 테스트"""
        manager._record_success(APIProvider.KAKAO)
        
        stats = manager.provider_stats[APIProvider.KAKAO]
        assert stats.total_requests == 1
        assert stats.successful_requests == 1
        assert stats.failed_requests == 0
        assert stats.consecutive_failures == 0
    
    def test_record_failure(self, manager):
        """실패 기록 테스트"""
        manager._record_failure(APIProvider.KAKAO)
        
        stats = manager.provider_stats[APIProvider.KAKAO]
        assert stats.total_requests == 1
        assert stats.successful_requests == 0
        assert stats.failed_requests == 1
        assert stats.consecutive_failures == 1
    
    def test_error_rate_calculation(self, manager):
        """에러율 계산 테스트"""
        # 5번 성공, 5번 실패
        for _ in range(5):
            manager._record_success(APIProvider.KAKAO)
        for _ in range(5):
            manager._record_failure(APIProvider.KAKAO)
        
        stats = manager.provider_stats[APIProvider.KAKAO]
        assert stats.error_rate == 0.5
        assert stats.success_rate == 0.5
    
    def test_get_available_provider_priority(self, manager):
        """제공자 우선순위 테스트"""
        provider = manager.get_available_provider()
        assert provider == APIProvider.KAKAO  # 첫 번째 우선순위
    
    def test_provider_failover(self, manager):
        """Circuit breaker OPEN 시 다음 제공자로 전환"""
        # Kakao circuit breaker OPEN
        kakao_cb = manager.circuit_breakers[APIProvider.KAKAO]
        kakao_cb.state = CircuitState.OPEN
        
        provider = manager.get_available_provider()
        assert provider == APIProvider.NAVER  # 두 번째 우선순위
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, manager):
        """재시도 성공 테스트"""
        call_count = 0
        
        async def mock_api_call():
            nonlocal call_count
            call_count += 1
            return {"result": "success"}
        
        result = await manager.execute_with_retry(
            mock_api_call,
            provider=APIProvider.KAKAO
        )
        
        assert result == {"result": "success"}
        assert call_count == 1
        
        stats = manager.provider_stats[APIProvider.KAKAO]
        assert stats.successful_requests == 1
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_failure_then_success(self, manager):
        """재시도 후 성공 테스트"""
        call_count = 0
        
        async def mock_api_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"result": "success"}
        
        result = await manager.execute_with_retry(
            mock_api_call,
            provider=APIProvider.KAKAO
        )
        
        assert result == {"result": "success"}
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_with_retry_max_retries_exceeded(self, manager):
        """최대 재시도 초과 테스트"""
        async def mock_api_call():
            raise Exception("Permanent failure")
        
        with pytest.raises(Exception) as exc_info:
            await manager.execute_with_retry(
                mock_api_call,
                provider=APIProvider.KAKAO
            )
        
        assert "Failed after" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self, manager):
        """Exponential backoff 타이밍 테스트"""
        call_times = []
        
        async def mock_api_call():
            call_times.append(datetime.now())
            raise Exception("Failure")
        
        try:
            await manager.execute_with_retry(
                mock_api_call,
                provider=APIProvider.KAKAO
            )
        except Exception:
            pass
        
        # 최소 4번 호출 (초기 + 3번 재시도)
        assert len(call_times) >= 4
        
        # 각 재시도 간 간격이 증가하는지 확인
        intervals = []
        for i in range(1, len(call_times)):
            interval = (call_times[i] - call_times[i-1]).total_seconds()
            intervals.append(interval)
        
        # 간격이 대체로 증가해야 함 (지터로 인해 완벽하진 않음)
        # 첫 간격 < 마지막 간격
        if len(intervals) >= 2:
            assert intervals[0] < intervals[-1]
    
    @pytest.mark.asyncio
    async def test_adaptive_retry_provider_switch(self, manager):
        """Adaptive retry: 에러율 높을 때 제공자 전환 테스트"""
        # Kakao에 높은 에러율 설정
        for _ in range(10):
            manager._record_failure(APIProvider.KAKAO)
        
        call_count = 0
        
        async def mock_api_call():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise Exception("Kakao failure")
            return {"result": "success"}
        
        result = await manager.execute_with_retry(
            mock_api_call,
            provider=APIProvider.KAKAO
        )
        
        assert result == {"result": "success"}


class TestGlobalFunctions:
    """전역 함수 테스트"""
    
    @pytest.mark.asyncio
    async def test_execute_with_failover(self):
        """execute_with_failover 함수 테스트"""
        async def mock_api_call(value):
            return {"result": value}
        
        result = await execute_with_failover(mock_api_call, "test")
        assert result == {"result": "test"}
    
    def test_get_rate_limit_stats(self):
        """get_rate_limit_stats 함수 테스트"""
        from app.core.rate_limit import get_rate_limit_stats
        
        stats = get_rate_limit_stats()
        assert "providers" in stats
        assert isinstance(stats["providers"], dict)


class TestRetryConfig:
    """RetryConfig 테스트"""
    
    def test_default_config(self):
        """기본 설정 확인"""
        config = RetryConfig()
        assert config.max_retries == 5
        assert config.base_delay == 1.0
        assert config.max_delay == 32.0
        assert config.exponential_base == 2.0
        assert config.jitter == True
    
    def test_custom_config(self):
        """커스텀 설정 확인"""
        config = RetryConfig(
            max_retries=3,
            base_delay=0.5,
            max_delay=10.0,
            jitter=False
        )
        assert config.max_retries == 3
        assert config.base_delay == 0.5
        assert config.max_delay == 10.0
        assert config.jitter == False


class TestIntegrationScenarios:
    """통합 시나리오 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_failover_scenario(self):
        """전체 Failover 시나리오"""
        manager = RateLimitManager(RetryConfig(max_retries=5, base_delay=0.1))
        
        call_count = 0
        
        async def mock_api_call_with_failover():
            nonlocal call_count
            call_count += 1
            
            # 처음 3번은 실패
            if call_count <= 3:
                raise Exception("API Error")
            
            return {"result": "success", "attempt": call_count}
        
        result = await manager.execute_with_retry(
            mock_api_call_with_failover,
            provider=APIProvider.KAKAO
        )
        
        assert result["result"] == "success"
        assert result["attempt"] == 4
        
        # 통계 확인
        stats = manager.get_stats()
        kakao_stats = stats["providers"][APIProvider.KAKAO.value]
        assert kakao_stats["successful_requests"] == 1
        assert kakao_stats["failed_requests"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
