"""
ZeroSite v7.1 Performance Tests
- 응답 시간 검증
- 동시성 테스트
- 부하 테스트
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from statistics import mean, median
import aiohttp


class TestPerformanceV7:
    """성능 테스트 스위트"""
    
    @pytest.fixture
    def base_url(self):
        """테스트 대상 URL"""
        return "http://localhost:8000"
    
    @pytest.fixture
    def sample_request(self):
        """샘플 분석 요청"""
        return {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000.0,
            "unit_type": "youth",
            "zone_type": "residential",
            "land_status": "vacant",
            "land_appraisal_price": 5000000000,
            "consultant": {
                "name": "테스트담당자",
                "phone": "010-1234-5678",
                "department": "영업팀",
                "email": "test@example.com"
            }
        }
    
    async def measure_response_time(
        self,
        session: aiohttp.ClientSession,
        url: str,
        data: Dict[str, Any]
    ) -> float:
        """단일 요청 응답 시간 측정"""
        start_time = time.time()
        try:
            async with session.post(url, json=data) as response:
                await response.json()
                return time.time() - start_time
        except Exception as e:
            print(f"Request failed: {e}")
            return -1
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self, base_url, sample_request):
        """단일 요청 성능 테스트"""
        url = f"{base_url}/api/analyze"
        
        async with aiohttp.ClientSession() as session:
            response_times = []
            
            # 10회 측정
            for _ in range(10):
                response_time = await self.measure_response_time(session, url, sample_request)
                if response_time > 0:
                    response_times.append(response_time)
            
            if response_times:
                avg_time = mean(response_times)
                median_time = median(response_times)
                max_time = max(response_times)
                
                print(f"\n단일 요청 성능:")
                print(f"  평균: {avg_time:.3f}s")
                print(f"  중앙값: {median_time:.3f}s")
                print(f"  최대: {max_time:.3f}s")
                
                # 검증: 평균 < 0.7초
                assert avg_time < 0.7, f"평균 응답 시간이 목표를 초과했습니다: {avg_time:.3f}s > 0.7s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, base_url, sample_request):
        """동시 요청 성능 테스트 (20 concurrent)"""
        url = f"{base_url}/api/analyze"
        concurrent_requests = 20
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            # 동시 요청 실행
            tasks = [
                self.measure_response_time(session, url, sample_request)
                for _ in range(concurrent_requests)
            ]
            
            response_times = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # 실패한 요청 제외
            valid_times = [t for t in response_times if t > 0]
            
            if valid_times:
                avg_time = mean(valid_times)
                p95_time = sorted(valid_times)[int(len(valid_times) * 0.95)]
                success_rate = len(valid_times) / len(response_times)
                
                print(f"\n동시 요청 성능 ({concurrent_requests}개):")
                print(f"  총 시간: {total_time:.3f}s")
                print(f"  평균 응답: {avg_time:.3f}s")
                print(f"  P95 응답: {p95_time:.3f}s")
                print(f"  성공률: {success_rate*100:.1f}%")
                
                # 검증
                assert success_rate >= 0.95, f"성공률이 95% 미만입니다: {success_rate*100:.1f}%"
                assert p95_time < 1.2, f"P95 응답 시간이 목표를 초과했습니다: {p95_time:.3f}s > 1.2s"
    
    @pytest.mark.asyncio
    async def test_load_test_sustained(self, base_url, sample_request):
        """지속 부하 테스트 (30초)"""
        url = f"{base_url}/api/analyze"
        duration = 30  # 30초
        request_rate = 2  # 초당 2개 요청
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            response_times = []
            errors = 0
            
            while time.time() - start_time < duration:
                batch_start = time.time()
                
                # 배치 요청
                tasks = [
                    self.measure_response_time(session, url, sample_request)
                    for _ in range(request_rate)
                ]
                
                batch_times = await asyncio.gather(*tasks)
                
                for t in batch_times:
                    if t > 0:
                        response_times.append(t)
                    else:
                        errors += 1
                
                # 요청 간격 조정
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
            
            total_requests = len(response_times) + errors
            
            if response_times:
                avg_time = mean(response_times)
                p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
                error_rate = errors / total_requests
                
                print(f"\n지속 부하 테스트 ({duration}초):")
                print(f"  총 요청: {total_requests}개")
                print(f"  성공: {len(response_times)}개")
                print(f"  실패: {errors}개")
                print(f"  평균 응답: {avg_time:.3f}s")
                print(f"  P95 응답: {p95_time:.3f}s")
                print(f"  에러율: {error_rate*100:.2f}%")
                
                # 검증
                assert error_rate < 0.05, f"에러율이 5%를 초과했습니다: {error_rate*100:.2f}%"
                assert avg_time < 0.8, f"평균 응답 시간이 목표를 초과했습니다: {avg_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_multi_parcel_performance(self, base_url):
        """다필지 분석 성능 테스트"""
        url = f"{base_url}/api/analyze-multi"
        
        # 5개 필지 요청
        request_data = {
            "parcels": [
                {
                    "address": f"서울특별시 강남구 역삼동 {100+i}-{i+1}",
                    "land_area": 1000.0 + (i * 100),
                    "land_appraisal_price": 5000000000 + (i * 100000000)
                }
                for i in range(5)
            ],
            "unit_type": "youth",
            "zone_type": "residential",
            "land_status": "vacant",
            "consultant": {
                "name": "테스트담당자",
                "phone": "010-1234-5678",
                "department": "영업팀",
                "email": "test@example.com"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            response_times = []
            
            # 5회 측정
            for _ in range(5):
                response_time = await self.measure_response_time(session, url, request_data)
                if response_time > 0:
                    response_times.append(response_time)
            
            if response_times:
                avg_time = mean(response_times)
                
                print(f"\n다필지 분석 성능 (5개 필지):")
                print(f"  평균: {avg_time:.3f}s")
                print(f"  최대: {max(response_times):.3f}s")
                
                # 검증: 다필지는 단일 필지의 1.5배 이내
                assert avg_time < 1.5, f"다필지 응답 시간이 목표를 초과했습니다: {avg_time:.3f}s > 1.5s"
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, base_url, sample_request):
        """캐시 효과성 테스트"""
        url = f"{base_url}/api/analyze"
        
        async with aiohttp.ClientSession() as session:
            # 첫 요청 (캐시 없음)
            first_time = await self.measure_response_time(session, url, sample_request)
            
            # 두 번째 요청 (캐시 적중)
            second_time = await self.measure_response_time(session, url, sample_request)
            
            print(f"\n캐시 효과성:")
            print(f"  첫 요청: {first_time:.3f}s")
            print(f"  캐시 요청: {second_time:.3f}s")
            print(f"  개선율: {(1 - second_time/first_time)*100:.1f}%")
            
            # 캐시로 인한 성능 개선 확인
            # 두 번째 요청이 첫 번째보다 빠르거나 비슷해야 함
            assert second_time <= first_time * 1.2, "캐시가 제대로 작동하지 않습니다"


class TestAPIEndpointsPerformance:
    """각 API 엔드포인트별 성능 테스트"""
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """헬스 체크 성능"""
        url = "http://localhost:8000/health"
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url) as response:
                await response.json()
                response_time = time.time() - start_time
            
            print(f"\n헬스 체크 응답 시간: {response_time:.3f}s")
            assert response_time < 0.1, "헬스 체크가 100ms를 초과했습니다"
    
    @pytest.mark.asyncio
    async def test_lh_notice_list_performance(self):
        """LH 공고문 목록 조회 성능"""
        url = "http://localhost:8000/api/lh-notices"
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url) as response:
                await response.json()
                response_time = time.time() - start_time
            
            print(f"\nLH 공고문 목록 응답 시간: {response_time:.3f}s")
            assert response_time < 0.5, "공고문 목록 조회가 500ms를 초과했습니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
