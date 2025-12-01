"""
API Rate Limit & Failover System
- Exponential backoff retry with max 5 retries
- Adaptive retry based on API provider error rate
- Circuit breaker for Kakao → Naver → Google transitions
- Rate-limit tracking per provider
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """API 제공자"""
    KAKAO = "kakao"
    NAVER = "naver"
    GOOGLE = "google"


class CircuitState(Enum):
    """Circuit Breaker 상태"""
    CLOSED = "closed"      # 정상 작동
    OPEN = "open"          # 차단됨 (에러율 높음)
    HALF_OPEN = "half_open"  # 복구 시도 중


@dataclass
class RetryConfig:
    """재시도 설정"""
    max_retries: int = 5
    base_delay: float = 1.0  # 초기 대기 시간 (초)
    max_delay: float = 32.0  # 최대 대기 시간 (초)
    exponential_base: float = 2.0
    jitter: bool = True  # 랜덤 지터 추가


@dataclass
class ProviderStats:
    """API 제공자 통계"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    
    @property
    def error_rate(self) -> float:
        """에러율 계산"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests
    
    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        return 1.0 - self.error_rate


@dataclass
class CircuitBreaker:
    """Circuit Breaker 구현"""
    failure_threshold: int = 5  # 연속 실패 임계값
    timeout: float = 60.0  # OPEN 상태 유지 시간 (초)
    half_open_max_requests: int = 3  # HALF_OPEN 상태에서 허용할 최대 요청 수
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    half_open_requests: int = 0
    
    def record_success(self):
        """성공 기록"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker: Transitioning to CLOSED (recovery successful)")
            self.state = CircuitState.CLOSED
            self.half_open_requests = 0
    
    def record_failure(self):
        """실패 기록"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker: HALF_OPEN failed, returning to OPEN")
            self.state = CircuitState.OPEN
            self.half_open_requests = 0
        elif self.failure_count >= self.failure_threshold:
            logger.error(f"Circuit breaker: Opening circuit (failures: {self.failure_count})")
            self.state = CircuitState.OPEN
    
    def can_request(self) -> bool:
        """요청 가능 여부 확인"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # OPEN 상태에서 timeout 경과 시 HALF_OPEN으로 전환
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    logger.info("Circuit breaker: Transitioning to HALF_OPEN (timeout elapsed)")
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                    return True
            return False
        
        # HALF_OPEN 상태
        if self.half_open_requests < self.half_open_max_requests:
            self.half_open_requests += 1
            return True
        return False


class RateLimitManager:
    """Rate Limit 및 Failover 관리자"""
    
    def __init__(self, retry_config: Optional[RetryConfig] = None):
        self.retry_config = retry_config or RetryConfig()
        self.provider_stats: Dict[APIProvider, ProviderStats] = {
            provider: ProviderStats() for provider in APIProvider
        }
        self.circuit_breakers: Dict[APIProvider, CircuitBreaker] = {
            provider: CircuitBreaker() for provider in APIProvider
        }
        self.provider_priority: List[APIProvider] = [
            APIProvider.KAKAO,
            APIProvider.NAVER,
            APIProvider.GOOGLE
        ]
    
    def _calculate_delay(self, retry_count: int) -> float:
        """재시도 지연 시간 계산 (exponential backoff)"""
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** retry_count),
            self.retry_config.max_delay
        )
        
        # 지터 추가 (±25%)
        if self.retry_config.jitter:
            import random
            jitter = delay * 0.25 * (random.random() * 2 - 1)
            delay += jitter
        
        return max(0, delay)
    
    def _record_success(self, provider: APIProvider):
        """성공 기록"""
        stats = self.provider_stats[provider]
        stats.total_requests += 1
        stats.successful_requests += 1
        stats.last_success_time = datetime.now()
        stats.consecutive_failures = 0
        
        self.circuit_breakers[provider].record_success()
    
    def _record_failure(self, provider: APIProvider):
        """실패 기록"""
        stats = self.provider_stats[provider]
        stats.total_requests += 1
        stats.failed_requests += 1
        stats.last_failure_time = datetime.now()
        stats.consecutive_failures += 1
        
        self.circuit_breakers[provider].record_failure()
    
    def get_available_provider(self) -> Optional[APIProvider]:
        """사용 가능한 제공자 반환 (우선순위 기반)"""
        for provider in self.provider_priority:
            circuit_breaker = self.circuit_breakers[provider]
            if circuit_breaker.can_request():
                return provider
        
        # 모든 제공자가 차단된 경우 에러율이 가장 낮은 것 반환
        available = [
            (provider, self.provider_stats[provider].error_rate)
            for provider in self.provider_priority
        ]
        available.sort(key=lambda x: x[1])
        
        if available:
            logger.warning(f"All circuits open, forcing provider: {available[0][0].value}")
            return available[0][0]
        
        return None
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        provider: Optional[APIProvider] = None,
        **kwargs
    ) -> Any:
        """재시도 로직이 포함된 함수 실행"""
        
        # 제공자 선택
        if provider is None:
            provider = self.get_available_provider()
        
        if provider is None:
            raise Exception("No API provider available")
        
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.retry_config.max_retries:
            try:
                # Circuit breaker 확인
                circuit_breaker = self.circuit_breakers[provider]
                if not circuit_breaker.can_request():
                    logger.warning(f"Circuit breaker OPEN for {provider.value}, trying next provider")
                    # 다음 제공자로 전환
                    next_provider = self.get_available_provider()
                    if next_provider and next_provider != provider:
                        provider = next_provider
                        retry_count = 0  # 새 제공자로 재시도 카운트 리셋
                    else:
                        raise Exception(f"Circuit breaker OPEN for {provider.value}")
                
                # 함수 실행
                logger.info(f"Executing API call with {provider.value} (attempt {retry_count + 1})")
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 성공 기록
                self._record_success(provider)
                logger.info(f"API call successful with {provider.value}")
                return result
            
            except Exception as e:
                last_exception = e
                self._record_failure(provider)
                
                retry_count += 1
                logger.error(
                    f"API call failed with {provider.value} (attempt {retry_count}): {str(e)}"
                )
                
                if retry_count > self.retry_config.max_retries:
                    logger.error(f"Max retries ({self.retry_config.max_retries}) exceeded")
                    break
                
                # Adaptive retry: 에러율이 높으면 다른 제공자로 전환
                stats = self.provider_stats[provider]
                if stats.error_rate > 0.5 and retry_count > 2:
                    logger.warning(
                        f"High error rate ({stats.error_rate:.2%}) for {provider.value}, "
                        f"switching provider"
                    )
                    next_provider = self.get_available_provider()
                    if next_provider and next_provider != provider:
                        provider = next_provider
                        retry_count = 0  # 새 제공자로 재시도 카운트 리셋
                
                # Exponential backoff
                delay = self._calculate_delay(retry_count - 1)
                logger.info(f"Waiting {delay:.2f}s before retry...")
                await asyncio.sleep(delay)
        
        # 모든 재시도 실패
        raise Exception(
            f"Failed after {self.retry_config.max_retries} retries: {str(last_exception)}"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        return {
            "providers": {
                provider.value: {
                    "total_requests": stats.total_requests,
                    "successful_requests": stats.successful_requests,
                    "failed_requests": stats.failed_requests,
                    "success_rate": f"{stats.success_rate:.2%}",
                    "error_rate": f"{stats.error_rate:.2%}",
                    "consecutive_failures": stats.consecutive_failures,
                    "circuit_state": self.circuit_breakers[provider].state.value
                }
                for provider, stats in self.provider_stats.items()
            }
        }
    
    def reset_stats(self):
        """통계 초기화"""
        self.provider_stats = {
            provider: ProviderStats() for provider in APIProvider
        }
        self.circuit_breakers = {
            provider: CircuitBreaker() for provider in APIProvider
        }


# 전역 인스턴스
rate_limit_manager = RateLimitManager()


# 편의 함수
async def execute_with_failover(
    func: Callable,
    *args,
    provider: Optional[APIProvider] = None,
    **kwargs
) -> Any:
    """Failover가 포함된 API 호출"""
    return await rate_limit_manager.execute_with_retry(func, *args, provider=provider, **kwargs)


def get_rate_limit_stats() -> Dict[str, Any]:
    """Rate limit 통계 조회"""
    return rate_limit_manager.get_stats()
