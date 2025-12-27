"""
ZeroSite v4.0 - Locust Load Testing Suite
성능 테스트 시나리오:
1. 인증 API (로그인, 토큰 갱신)
2. 분석 API (단일 부지 분석)
3. 대시보드 페이지 로드
4. 차트 생성 및 조회
"""

import json
import random
from locust import HttpUser, task, between, SequentialTaskSet


class AuthenticationTasks(SequentialTaskSet):
    """인증 관련 태스크"""
    
    def on_start(self):
        """테스트 시작 시 로그인"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "demo",
            "password": "demo123"
        })
        if response.status_code == 200:
            self.user.access_token = response.json().get("access_token")
            self.user.refresh_token = response.json().get("refresh_token")
    
    @task(5)
    def get_current_user(self):
        """현재 사용자 정보 조회"""
        if hasattr(self.user, 'access_token'):
            self.client.get("/api/v1/auth/me", headers={
                "Authorization": f"Bearer {self.user.access_token}"
            })
    
    @task(2)
    def refresh_token(self):
        """토큰 갱신"""
        if hasattr(self.user, 'refresh_token'):
            response = self.client.post("/api/v1/auth/refresh", headers={
                "Authorization": f"Bearer {self.user.refresh_token}"
            })
            if response.status_code == 200:
                self.user.access_token = response.json().get("access_token")


class AnalysisTasks(SequentialTaskSet):
    """분석 관련 태스크"""
    
    def on_start(self):
        """API 키로 인증"""
        # 실제 환경에서는 환경 변수에서 API 키를 가져와야 함
        self.api_key = "zerosite_test_key_12345"
    
    @task(10)
    def analyze_land(self):
        """단일 부지 분석"""
        land_data = {
            "parcel_id": f"TEST-{random.randint(1000, 9999)}",
            "address": "서울특별시 강남구 테스트동",
            "area_pyeong": random.randint(100, 500),
            "area_sqm": random.randint(330, 1650),
            "zone": random.choice(["제2종일반주거지역", "제3종일반주거지역", "준주거지역"]),
            "far_percent": random.randint(180, 300),
            "bcr_percent": random.randint(50, 70),
            "asking_price_million": random.randint(5000, 20000)
        }
        
        response = self.client.post("/api/v1/analyze", 
            json=land_data,
            headers={"X-API-Key": self.api_key}
        )
        
        if response.status_code == 200:
            job_id = response.json().get("job_id")
            self.user.last_job_id = job_id
    
    @task(8)
    def check_status(self):
        """분석 상태 확인"""
        if hasattr(self.user, 'last_job_id'):
            self.client.get(f"/api/v1/status/{self.user.last_job_id}", 
                headers={"X-API-Key": self.api_key}
            )
    
    @task(5)
    def get_result(self):
        """분석 결과 조회"""
        if hasattr(self.user, 'last_job_id'):
            self.client.get(f"/api/v1/result/{self.user.last_job_id}",
                headers={"X-API-Key": self.api_key}
            )
    
    @task(3)
    def get_chart(self):
        """차트 조회"""
        if hasattr(self.user, 'last_job_id'):
            chart_types = ["lh_score", "financial", "capacity"]
            chart_type = random.choice(chart_types)
            self.client.get(f"/api/v1/chart/{self.user.last_job_id}/{chart_type}",
                headers={"X-API-Key": self.api_key}
            )


class DashboardTasks(SequentialTaskSet):
    """대시보드 관련 태스크"""
    
    @task(10)
    def view_dashboard(self):
        """대시보드 페이지 로드"""
        self.client.get("/")
    
    @task(5)
    def view_analysis_page(self):
        """분석 페이지 로드"""
        self.client.get("/analysis")
    
    @task(3)
    def view_comparison_page(self):
        """비교 페이지 로드"""
        self.client.get("/comparison")
    
    @task(2)
    def view_map_page(self):
        """지도 페이지 로드"""
        self.client.get("/map")
    
    @task(7)
    def get_all_jobs(self):
        """전체 작업 목록 조회"""
        self.client.get("/api/v1/jobs")


class ZeroSiteUser(HttpUser):
    """ZeroSite 사용자 시뮬레이션"""
    
    # 요청 간 대기 시간: 1~5초
    wait_time = between(1, 5)
    
    # 태스크 가중치 설정
    tasks = {
        DashboardTasks: 3,      # 30% - 대시보드 조회
        AnalysisTasks: 5,       # 50% - 분석 API
        AuthenticationTasks: 2  # 20% - 인증
    }
    
    def on_start(self):
        """테스트 시작 시 헬스 체크"""
        self.client.get("/health")


# 추가 시나리오: 스파이크 테스트
class SpikeTestUser(HttpUser):
    """급격한 트래픽 증가 시뮬레이션"""
    
    wait_time = between(0.1, 0.5)  # 매우 짧은 대기 시간
    
    @task
    def rapid_fire_requests(self):
        """연속 요청"""
        endpoints = ["/", "/health", "/api/v1/jobs"]
        for endpoint in endpoints:
            self.client.get(endpoint)


# 추가 시나리오: 스트레스 테스트
class StressTestUser(HttpUser):
    """시스템 한계 테스트"""
    
    wait_time = between(0.1, 1.0)
    
    @task(5)
    def heavy_analysis(self):
        """대량 분석 요청"""
        for i in range(5):  # 동시에 5개 분석 요청
            land_data = {
                "parcel_id": f"STRESS-{random.randint(1000, 9999)}-{i}",
                "address": f"스트레스테스트 {i}번지",
                "area_pyeong": 200,
                "area_sqm": 660,
                "zone": "제2종일반주거지역",
                "far_percent": 200,
                "bcr_percent": 60,
                "asking_price_million": 10000
            }
            self.client.post("/api/v1/analyze", json=land_data)
    
    @task(3)
    def polling_storm(self):
        """폴링 폭주"""
        for i in range(10):  # 동시에 10번 상태 확인
            self.client.get(f"/api/v1/status/test-job-{i}")
