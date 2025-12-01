"""
차트 생성 서비스
수요 점수 시각화를 위한 레이더 차트 생성
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 백그라운드 렌더링
import numpy as np
from typing import Dict, List, Any
import base64
from io import BytesIO


class ChartService:
    """차트 생성 서비스"""
    
    def __init__(self):
        """초기화"""
        # 한글 폰트 설정 (시스템에 따라 다를 수 있음)
        try:
            plt.rcParams['font.family'] = 'NanumGothic'
        except:
            try:
                plt.rcParams['font.family'] = 'Malgun Gothic'
            except:
                # 한글 폰트가 없으면 기본 폰트 사용
                plt.rcParams['font.family'] = 'DejaVu Sans'
        
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    
    def create_demand_radar_chart(
        self,
        demographic_score: float,
        accessibility_score: float,
        market_score: float,
        regulation_score: float,
        environment_score: float,
        title: str = "수요 분석 레이더 차트"
    ) -> str:
        """
        수요 점수 5각형 레이더 차트 생성
        
        Args:
            demographic_score: 인구통계 점수 (0-40)
            accessibility_score: 접근성 점수 (0-30)
            market_score: 시장 규모 점수 (0-30)
            regulation_score: 규제 환경 점수 (0-20, 추가 계산 필요)
            environment_score: 주변 환경 점수 (0-20, 추가 계산 필요)
            title: 차트 제목
            
        Returns:
            Base64 인코딩된 PNG 이미지
        """
        # 카테고리 및 점수
        categories = ['인구통계\n(40점)', '접근성\n(30점)', '시장규모\n(30점)', '규제환경\n(20점)', '주변환경\n(20점)']
        scores = [demographic_score, accessibility_score, market_score, regulation_score, environment_score]
        max_scores = [40, 30, 30, 20, 20]
        
        # 정규화된 점수 (0-1 범위로)
        normalized_scores = [score / max_score for score, max_score in zip(scores, max_scores)]
        
        # 각도 계산 (5각형)
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        # 차트를 닫기 위해 첫 값을 끝에 추가
        scores_closed = scores + [scores[0]]
        normalized_closed = normalized_scores + [normalized_scores[0]]
        angles_closed = angles + [angles[0]]
        
        # 그래프 생성
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
        
        # 배경 그리드 설정
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9, color='gray')
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=11, weight='bold')
        
        # 그리드 스타일
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7, color='gray')
        
        # 레이더 차트 그리기
        ax.plot(angles_closed, normalized_closed, 'o-', linewidth=2, color='#667eea', label='현재 점수')
        ax.fill(angles_closed, normalized_closed, alpha=0.25, color='#667eea')
        
        # 각 카테고리별 점수 텍스트 표시
        for angle, score, max_score, category in zip(angles, scores, max_scores, categories):
            # 레이더 차트 끝 위치에 점수 표시
            x = angle
            y = (score / max_score) + 0.1  # 약간 바깥쪽
            
            ax.text(x, y, f'{score:.1f}점', 
                   ha='center', va='center',
                   fontsize=10, weight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#667eea', linewidth=1.5))
        
        # 제목
        plt.title(title, fontsize=15, weight='bold', pad=20)
        
        # 범례
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        
        # 이미지를 Base64로 인코딩
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def create_simple_bar_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str = "점수 비교",
        ylabel: str = "점수"
    ) -> str:
        """
        간단한 막대 차트 생성
        
        Args:
            categories: 카테고리 리스트
            values: 값 리스트
            title: 차트 제목
            ylabel: Y축 레이블
            
        Returns:
            Base64 인코딩된 PNG 이미지
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 색상 그라데이션
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(categories)))
        
        bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.2)
        
        # 값 표시
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold')
        
        ax.set_ylabel(ylabel, fontsize=12, weight='bold')
        ax.set_title(title, fontsize=14, weight='bold', pad=15)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        
        # Base64 인코딩
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def create_unit_type_comparison_chart(
        self,
        unit_types: List[str],
        scores: List[float],
        recommended_type: str = None
    ) -> str:
        """
        세대 유형별 수요 점수 비교 차트
        
        Args:
            unit_types: 세대 유형 리스트
            scores: 점수 리스트
            recommended_type: 추천 유형 (강조 표시)
            
        Returns:
            Base64 인코딩된 PNG 이미지
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 색상 설정 (추천 유형은 다른 색으로)
        colors = []
        for unit_type in unit_types:
            if unit_type == recommended_type:
                colors.append('#667eea')  # 추천 유형: 보라색
            else:
                colors.append('#e0e0e0')  # 일반: 회색
        
        bars = ax.barh(unit_types, scores, color=colors, edgecolor='black', linewidth=1.5)
        
        # 값 표시
        for i, (bar, score) in enumerate(zip(bars, scores)):
            width = bar.get_width()
            is_recommended = unit_types[i] == recommended_type
            
            ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                   f'{score:.1f}점' + (' ⭐ 추천' if is_recommended else ''),
                   ha='left', va='center', fontsize=11, 
                   weight='bold' if is_recommended else 'normal',
                   color='#667eea' if is_recommended else 'black')
        
        ax.set_xlabel('수요 점수 (0-100)', fontsize=12, weight='bold')
        ax.set_title('LH 7개 유형 수요 점수 비교', fontsize=14, weight='bold', pad=15)
        ax.set_xlim(0, max(scores) + 10)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Base64 인코딩
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"


# 싱글톤 인스턴스
_chart_service = None


def get_chart_service() -> ChartService:
    """ChartService 싱글톤 인스턴스 반환"""
    global _chart_service
    if _chart_service is None:
        _chart_service = ChartService()
    return _chart_service
