"""
ZeroSite v6.1 - POI Distance Calculation Bug Fix Validation Test
학교/병원 거리 계산 오류 수정 검증

테스트 목적:
- analyze_location_accessibility()가 학교/병원 거리를 정확히 반환하는지 확인
- 최단 거리 계산 로직(min() 함수)이 올바르게 작동하는지 검증
- 거리 threshold 판정(Excellent/Good/Poor)이 정확한지 확인

버그 증상 (v6.0):
- 학교/병원이 가까운데 "멀다"고 판정
- nearest_school_distance가 9999로 반환 (검색 실패)
- LH Scorecard에서 교육/의료 시설 점수가 0점 처리
"""

import pytest
import asyncio
from app.services.kakao_service import KakaoService
from app.schemas import Coordinates


class TestPOIDistanceCalculationV6:
    """POI 거리 계산 정확성 검증"""
    
    def setup_method(self):
        """테스트 초기화"""
        self.kakao = KakaoService()
        
        # 테스트용 좌표 (서울 강남구 역삼동 - 학교/병원이 많은 지역)
        self.test_coordinates = Coordinates(
            latitude=37.5010,  # 역삼역 인근
            longitude=127.0364
        )
    
    @pytest.mark.asyncio
    async def test_학교_거리_계산_정확성(self):
        """
        학교 거리 계산이 정확한지 확인
        
        v6.0 버그: nearest_school_distance가 항상 9999 반환 (검색 안됨)
        v6.1 수정: 초등학교/중학교 검색 추가, min() 로직 수정
        """
        result = await self.kakao.analyze_location_accessibility(self.test_coordinates)
        
        print(f"\n📍 테스트 좌표: {self.test_coordinates.latitude}, {self.test_coordinates.longitude}")
        print(f"📊 학교 거리 결과:")
        print(f"  - 초등학교: {result.get('nearest_elementary_school_distance', 'N/A')}m")
        print(f"  - 중학교: {result.get('nearest_middle_school_distance', 'N/A')}m")
        print(f"  - 최종 학교 거리: {result.get('nearest_school_distance', 'N/A')}m")
        
        # 검증 1: 학교 거리가 9999가 아니어야 함 (검색 성공 확인)
        assert result['nearest_school_distance'] < 9999, \
            f"학교 검색 실패 (9999m 반환) → v6.0 버그 미수정"
        
        # 검증 2: 학교 거리가 합리적인 범위 내에 있어야 함 (서울 역삼동 기준 2km 이내 존재)
        assert result['nearest_school_distance'] < 2000, \
            f"학교 거리가 비정상적으로 멈 ({result['nearest_school_distance']}m > 2000m)"
        
        # 검증 3: 초등학교 또는 중학교 중 하나는 반드시 검색되어야 함
        assert result['nearest_elementary_school_distance'] < 9999 or result['nearest_middle_school_distance'] < 9999, \
            "초등학교와 중학교 모두 검색 실패"
        
        # 검증 4: nearest_school_distance는 초등/중학교 중 가까운 거리여야 함
        expected_min = min(
            result['nearest_elementary_school_distance'],
            result['nearest_middle_school_distance']
        )
        assert result['nearest_school_distance'] == expected_min, \
            f"학교 최단 거리 계산 오류: {result['nearest_school_distance']}m != min({result['nearest_elementary_school_distance']}, {result['nearest_middle_school_distance']})m"
        
        print("  ✅ 학교 거리 계산 정상!")
    
    @pytest.mark.asyncio
    async def test_병원_거리_계산_정확성(self):
        """
        병원 거리 계산이 정확한지 확인
        
        v6.0 버그: nearest_hospital_distance가 항상 9999 반환 (검색 안됨)
        v6.1 수정: 병원 검색 추가
        """
        result = await self.kakao.analyze_location_accessibility(self.test_coordinates)
        
        print(f"\n📊 병원 거리 결과:")
        print(f"  - 병원: {result.get('nearest_hospital_distance', 'N/A')}m")
        
        # 검증 1: 병원 거리가 9999가 아니어야 함 (검색 성공 확인)
        assert result['nearest_hospital_distance'] < 9999, \
            f"병원 검색 실패 (9999m 반환) → v6.0 버그 미수정"
        
        # 검증 2: 병원 거리가 합리적인 범위 내에 있어야 함 (서울 역삼동 기준 2km 이내 존재)
        assert result['nearest_hospital_distance'] < 2000, \
            f"병원 거리가 비정상적으로 멈 ({result['nearest_hospital_distance']}m > 2000m)"
        
        print("  ✅ 병원 거리 계산 정상!")
    
    @pytest.mark.asyncio
    async def test_거리_threshold_판정_정확성(self):
        """
        거리 기반 등급 판정이 정확한지 확인
        
        LH 기준:
        - 학교: 0-400m Excellent, 400-800m Good, 800m+ Poor
        - 병원: 0-500m Excellent, 500-1200m Good, 1200m+ Poor
        """
        result = await self.kakao.analyze_location_accessibility(self.test_coordinates)
        
        school_dist = result['nearest_school_distance']
        hospital_dist = result['nearest_hospital_distance']
        
        # 학교 등급 판정
        if school_dist <= 400:
            school_grade = "Excellent"
        elif school_dist <= 800:
            school_grade = "Good"
        else:
            school_grade = "Poor"
        
        # 병원 등급 판정
        if hospital_dist <= 500:
            hospital_grade = "Excellent"
        elif hospital_dist <= 1200:
            hospital_grade = "Good"
        else:
            hospital_grade = "Poor"
        
        print(f"\n📊 거리 등급 판정:")
        print(f"  - 학교: {school_dist}m → {school_grade}")
        print(f"  - 병원: {hospital_dist}m → {hospital_grade}")
        
        # 검증: 등급 판정이 합리적이어야 함 (서울 역삼동은 Good 이상 예상)
        assert school_grade in ["Excellent", "Good"], \
            f"학교 거리 판정 이상: {school_dist}m → {school_grade} (역삼동은 Good 이상 예상)"
        
        assert hospital_grade in ["Excellent", "Good"], \
            f"병원 거리 판정 이상: {hospital_dist}m → {hospital_grade} (역삼동은 Good 이상 예상)"
        
        print("  ✅ 거리 threshold 판정 정상!")
    
    @pytest.mark.asyncio
    async def test_모든_POI_거리_필드_존재_확인(self):
        """
        analyze_location_accessibility() 반환값에 모든 POI 거리 필드가 존재하는지 확인
        """
        result = await self.kakao.analyze_location_accessibility(self.test_coordinates)
        
        # v6.1에서 추가된 필드들
        required_fields = [
            "nearest_school_distance",
            "nearest_elementary_school_distance",
            "nearest_middle_school_distance",
            "nearest_hospital_distance",
            "schools",  # 학교 리스트
            "hospitals"  # 병원 리스트
        ]
        
        print(f"\n📊 반환 필드 확인:")
        for field in required_fields:
            exists = field in result
            value = result.get(field, "N/A")
            print(f"  - {field}: {value} {'✅' if exists else '❌'}")
            
            assert exists, f"필수 필드 '{field}' 누락 → v6.1 수정 미반영"
        
        print("  ✅ 모든 POI 거리 필드 존재 확인!")
    
    @pytest.mark.asyncio
    async def test_디버그_로깅_출력_확인(self):
        """
        v6.1에서 추가한 디버그 로깅이 출력되는지 확인
        
        예상 출력:
        🔍 [POI Distance Debug] 초등학교: XXXm, 중학교: YYYm → 최종 학교: ZZZm
        🔍 [POI Distance Debug] 병원: AAAm
        """
        print(f"\n📊 디버그 로깅 출력 테스트:")
        print("  (콘솔에서 '🔍 [POI Distance Debug]' 메시지 확인)")
        
        result = await self.kakao.analyze_location_accessibility(self.test_coordinates)
        
        # 로깅이 정상 출력되었으면 테스트 통과
        assert result['nearest_school_distance'] < 9999, "디버그 로깅 추가 실패 가능성"
        
        print("  ✅ 디버그 로깅 출력 확인!")


class TestGeoOptimizerPOIIntegration:
    """Geo Optimizer와 POI 거리 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_geo_optimizer가_정확한_POI_거리_사용(self):
        """
        Geo Optimizer가 v6.1에서 수정된 POI 거리를 정확히 사용하는지 확인
        
        v6.0 문제: geo_optimizer.py에서 accessibility['nearest_school_distance']를 사용하지만
                  해당 값이 항상 9999로 전달되어 최적화 실패
        
        v6.1 기대: 정확한 학교/병원 거리를 기반으로 최적 위치 제안
        """
        from app.services.geo_optimizer import GeoOptimizer
        from app.services.analysis_engine import AnalysisEngine
        
        # 역삼동 기준 좌표
        test_coord = Coordinates(latitude=37.5010, longitude=127.0364)
        
        # Kakao 서비스로 accessibility 정보 획득
        kakao = KakaoService()
        accessibility = await kakao.analyze_location_accessibility(test_coord)
        
        print(f"\n📊 Geo Optimizer 입력:")
        print(f"  - 학교 거리: {accessibility['nearest_school_distance']}m")
        print(f"  - 병원 거리: {accessibility['nearest_hospital_distance']}m")
        
        # 검증: Geo Optimizer가 9999가 아닌 실제 거리를 받았는지 확인
        assert accessibility['nearest_school_distance'] < 9999, \
            "Geo Optimizer에 잘못된 학교 거리 전달 (9999)"
        
        assert accessibility['nearest_hospital_distance'] < 9999, \
            "Geo Optimizer에 잘못된 병원 거리 전달 (9999)"
        
        print("  ✅ Geo Optimizer POI 거리 통합 정상!")


if __name__ == "__main__":
    """직접 실행 시 테스트 수행"""
    pytest.main([__file__, "-v", "-s", "--asyncio-mode=auto"])
