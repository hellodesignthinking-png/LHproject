"""
ZeroSite v4.0 Chart Generator
==============================

matplotlib/plotly 기반 차트 생성

Author: ZeroSite Visualization Team
Date: 2025-12-26
Version: 1.0
"""

import os
import io
from typing import Dict, Any, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np


class ChartGenerator:
    """차트 생성 엔진"""
    
    def __init__(self, output_dir: str = "output/charts"):
        """초기화"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 한글 폰트 설정
        self._setup_korean_font()
        
        # 기본 스타일
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            # 나눔고딕 폰트 경로
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_prop = fm.FontProperties(fname=font_path)
                    plt.rcParams['font.family'] = font_prop.get_name()
                    plt.rcParams['axes.unicode_minus'] = False
                    print(f"✓ 한글 폰트 설정: {font_prop.get_name()}")
                    return
            
            print("⚠ 한글 폰트 없음 - 기본 폰트 사용")
            
        except Exception as e:
            print(f"⚠ 폰트 설정 실패: {e}")
    
    def generate_lh_scorecard_chart(
        self,
        section_scores: Dict[str, float],
        total_score: float,
        file_name: str = "lh_scorecard.png"
    ) -> str:
        """LH 점수표 차트 생성"""
        
        # 섹션 정보
        section_names = {
            "A": "정책·유형",
            "B": "입지·환경",
            "C": "건축가능성",
            "D": "가격·매입",
            "E": "사업성"
        }
        
        max_scores = {"A": 25, "B": 20, "C": 20, "D": 15, "E": 20}
        
        # 데이터 준비
        sections = []
        scores = []
        max_vals = []
        percentages = []
        
        for section_id in ["A", "B", "C", "D", "E"]:
            score = section_scores.get(section_id, 0.0)
            max_score = max_scores[section_id]
            pct = (score / max_score * 100) if max_score > 0 else 0
            
            sections.append(section_names[section_id])
            scores.append(score)
            max_vals.append(max_score)
            percentages.append(pct)
        
        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 왼쪽: 섹션별 점수 바 차트
        y_pos = np.arange(len(sections))
        colors = ['#0070C0' if p >= 80 else '#FFA500' if p >= 60 else '#FF6B6B' 
                  for p in percentages]
        
        bars = ax1.barh(y_pos, scores, color=colors, alpha=0.8)
        
        # 최대값 표시
        for i, (score, max_val) in enumerate(zip(scores, max_vals)):
            ax1.plot([max_val, max_val], [i - 0.4, i + 0.4], 
                    'k--', alpha=0.3, linewidth=1)
            ax1.text(max_val + 0.5, i, f'{max_val}점', 
                    va='center', ha='left', fontsize=9, alpha=0.6)
            # 점수 표시
            ax1.text(score + 0.5, i, f'{score:.1f}점', 
                    va='center', ha='left', fontsize=10, fontweight='bold')
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(sections, fontsize=11)
        ax1.set_xlabel('점수', fontsize=11)
        ax1.set_title('섹션별 득점 현황', fontsize=13, fontweight='bold', pad=15)
        ax1.grid(axis='x', alpha=0.3)
        ax1.set_xlim(0, max(max_vals) + 5)
        
        # 오른쪽: 득점률 도넛 차트
        total_max = sum(max_vals)
        total_pct = (total_score / total_max * 100)
        
        # 도넛 차트 데이터
        wedges, texts, autotexts = ax2.pie(
            [total_score, total_max - total_score],
            labels=['득점', '미득점'],
            autopct='',
            startangle=90,
            colors=['#0070C0', '#E0E0E0'],
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        
        # 중앙에 총점 표시
        ax2.text(0, 0.1, f'{total_score:.1f}', 
                ha='center', va='center', fontsize=32, fontweight='bold', color='#0070C0')
        ax2.text(0, -0.15, f'/ {total_max}점', 
                ha='center', va='center', fontsize=14, color='#666')
        ax2.text(0, -0.35, f'{total_pct:.1f}%', 
                ha='center', va='center', fontsize=16, fontweight='bold', color='#333')
        
        ax2.set_title('종합 득점률', fontsize=13, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.output_dir, file_name)
        plt.savefig(file_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ LH 점수표 차트 생성: {file_path}")
        return file_path
    
    def generate_financial_chart(
        self,
        cost_breakdown: Dict[str, float],
        revenue_projection: Dict[str, float],
        npv: float,
        irr: float,
        file_name: str = "financial_chart.png"
    ) -> str:
        """재무 분석 차트 생성"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 비용 구조 파이 차트
        cost_labels = []
        cost_values = []
        for key, value in cost_breakdown.items():
            if value > 0:
                cost_labels.append(key)
                cost_values.append(value)
        
        colors1 = plt.cm.Blues(np.linspace(0.4, 0.8, len(cost_values)))
        wedges, texts, autotexts = ax1.pie(
            cost_values,
            labels=cost_labels,
            autopct='%1.1f%%',
            colors=colors1,
            startangle=90
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax1.set_title('비용 구조', fontsize=12, fontweight='bold', pad=15)
        
        # 2. 수익 구조 파이 차트
        revenue_labels = []
        revenue_values = []
        for key, value in revenue_projection.items():
            if value > 0:
                revenue_labels.append(key)
                revenue_values.append(value)
        
        colors2 = plt.cm.Greens(np.linspace(0.4, 0.8, len(revenue_values)))
        wedges, texts, autotexts = ax2.pie(
            revenue_values,
            labels=revenue_labels,
            autopct='%1.1f%%',
            colors=colors2,
            startangle=90
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        ax2.set_title('수익 구조', fontsize=12, fontweight='bold', pad=15)
        
        # 3. 비용 vs 수익 비교
        total_cost = sum(cost_values)
        total_revenue = sum(revenue_values)
        
        categories = ['총 비용', '총 수익']
        values = [total_cost, total_revenue]
        colors3 = ['#FF6B6B', '#4ECDC4']
        
        bars = ax3.bar(categories, values, color=colors3, alpha=0.8, width=0.5)
        
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'₩{value/1e8:.1f}억',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax3.set_ylabel('금액 (원)', fontsize=10)
        ax3.set_title('비용 vs 수익 비교', fontsize=12, fontweight='bold', pad=15)
        ax3.ticklabel_format(style='plain', axis='y')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. 수익성 지표
        ax4.axis('off')
        
        # NPV 표시
        npv_color = '#4ECDC4' if npv > 0 else '#FF6B6B'
        npv_text = f'₩{abs(npv)/1e8:.1f}억'
        npv_sign = '+' if npv > 0 else '-'
        
        ax4.text(0.5, 0.75, 'NPV (순현재가치)', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax4.text(0.5, 0.60, f'{npv_sign}{npv_text}', 
                ha='center', va='center', fontsize=22, fontweight='bold', color=npv_color)
        
        # IRR 표시
        irr_color = '#4ECDC4' if irr > 8 else '#FFA500' if irr > 5 else '#FF6B6B'
        
        ax4.text(0.5, 0.40, 'IRR (내부수익률)', 
                ha='center', va='center', fontsize=14, fontweight='bold')
        ax4.text(0.5, 0.25, f'{irr:.2f}%', 
                ha='center', va='center', fontsize=22, fontweight='bold', color=irr_color)
        
        # 판정
        if npv > 0 and irr > 8:
            verdict = '수익성 우수'
            verdict_color = '#4ECDC4'
        elif npv > -500000000 and irr > 5:
            verdict = '수익성 양호'
            verdict_color = '#FFA500'
        else:
            verdict = '수익성 개선 필요'
            verdict_color = '#FF6B6B'
        
        ax4.text(0.5, 0.05, verdict, 
                ha='center', va='center', fontsize=12, fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor=verdict_color, alpha=0.3))
        
        ax4.set_title('수익성 지표', fontsize=12, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.output_dir, file_name)
        plt.savefig(file_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 재무 분석 차트 생성: {file_path}")
        return file_path
    
    def generate_capacity_comparison_chart(
        self,
        legal_capacity: Dict[str, Any],
        incentive_capacity: Dict[str, Any],
        file_name: str = "capacity_comparison.png"
    ) -> str:
        """건축 규모 비교 차트"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. 용적률/건폐율 비교
        categories = ['용적률', '건폐율']
        legal_vals = [
            legal_capacity.get('applied_far', 0),
            legal_capacity.get('applied_bcr', 0)
        ]
        incentive_vals = [
            incentive_capacity.get('applied_far', 0),
            incentive_capacity.get('applied_bcr', 0)
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, legal_vals, width, label='법정', 
                       color='#95B8D1', alpha=0.8)
        bars2 = ax1.bar(x + width/2, incentive_vals, width, label='인센티브', 
                       color='#0070C0', alpha=0.8)
        
        # 값 표시
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}%',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax1.set_ylabel('비율 (%)', fontsize=11)
        ax1.set_title('용적률/건폐율 비교', fontsize=13, fontweight='bold', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontsize=11)
        ax1.legend(fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. 세대수/주차 비교
        categories2 = ['세대수', '주차대수']
        legal_vals2 = [
            legal_capacity.get('total_units', 0),
            legal_capacity.get('required_parking_spaces', 0)
        ]
        incentive_vals2 = [
            incentive_capacity.get('total_units', 0),
            incentive_capacity.get('required_parking_spaces', 0)
        ]
        
        x2 = np.arange(len(categories2))
        
        bars3 = ax2.bar(x2 - width/2, legal_vals2, width, label='법정', 
                       color='#95B8D1', alpha=0.8)
        bars4 = ax2.bar(x2 + width/2, incentive_vals2, width, label='인센티브', 
                       color='#0070C0', alpha=0.8)
        
        # 값 표시
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax2.set_ylabel('개수', fontsize=11)
        ax2.set_title('세대수/주차 비교', fontsize=13, fontweight='bold', pad=15)
        ax2.set_xticks(x2)
        ax2.set_xticklabels(categories2, fontsize=11)
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.output_dir, file_name)
        plt.savefig(file_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 건축 규모 비교 차트 생성: {file_path}")
        return file_path
    
    def generate_multi_site_comparison_chart(
        self,
        sites: List[Dict[str, Any]],
        file_name: str = "multi_site_comparison.png"
    ) -> str:
        """다중 부지 비교 차트"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 데이터 추출
        site_names = [site['site_name'] for site in sites]
        lh_scores = [site['lh_score_total'] for site in sites]
        npvs = [site['npv_public'] / 1e8 for site in sites]  # 억 단위
        irrs = [site['irr_public'] for site in sites]
        land_values = [site['land_value'] / 1e8 for site in sites]  # 억 단위
        
        # 색상 (점수 기준)
        colors = ['#4ECDC4' if score >= 85 else '#FFA500' if score >= 70 else '#FF6B6B' 
                  for score in lh_scores]
        
        # 1. LH 점수 비교
        bars1 = ax1.barh(site_names, lh_scores, color=colors, alpha=0.8)
        
        for i, (bar, score) in enumerate(zip(bars1, lh_scores)):
            width = bar.get_width()
            ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                    f'{score:.1f}점',
                    ha='left', va='center', fontsize=10, fontweight='bold')
        
        ax1.set_xlabel('LH 점수', fontsize=11)
        ax1.set_title('LH 종합 점수 비교', fontsize=13, fontweight='bold', pad=15)
        ax1.axvline(x=85, color='green', linestyle='--', alpha=0.5, label='GO (85점)')
        ax1.axvline(x=70, color='orange', linestyle='--', alpha=0.5, label='CONDITIONAL (70점)')
        ax1.legend(fontsize=9)
        ax1.grid(axis='x', alpha=0.3)
        ax1.set_xlim(0, 100)
        
        # 2. NPV 비교
        colors2 = ['#4ECDC4' if npv > 0 else '#FF6B6B' for npv in npvs]
        bars2 = ax2.bar(range(len(site_names)), npvs, color=colors2, alpha=0.8)
        
        for bar, npv in zip(bars2, npvs):
            height = bar.get_height()
            label = f'{npv:.1f}억'
            y_pos = height if height > 0 else height - 2
            va = 'bottom' if height > 0 else 'top'
            ax2.text(bar.get_x() + bar.get_width()/2., y_pos,
                    label, ha='center', va=va, fontsize=9, fontweight='bold')
        
        ax2.set_ylabel('NPV (억원)', fontsize=11)
        ax2.set_title('순현재가치 (NPV) 비교', fontsize=13, fontweight='bold', pad=15)
        ax2.set_xticks(range(len(site_names)))
        ax2.set_xticklabels([f'부지{i+1}' for i in range(len(site_names))], fontsize=9)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. IRR 비교
        colors3 = ['#4ECDC4' if irr > 8 else '#FFA500' if irr > 5 else '#FF6B6B' 
                   for irr in irrs]
        bars3 = ax3.bar(range(len(site_names)), irrs, color=colors3, alpha=0.8)
        
        for bar, irr in zip(bars3, irrs):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{irr:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax3.set_ylabel('IRR (%)', fontsize=11)
        ax3.set_title('내부수익률 (IRR) 비교', fontsize=13, fontweight='bold', pad=15)
        ax3.set_xticks(range(len(site_names)))
        ax3.set_xticklabels([f'부지{i+1}' for i in range(len(site_names))], fontsize=9)
        ax3.axhline(y=8, color='green', linestyle='--', alpha=0.5, label='우수 (8%)')
        ax3.axhline(y=5, color='orange', linestyle='--', alpha=0.5, label='양호 (5%)')
        ax3.legend(fontsize=9)
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. 토지가 vs LH점수 산점도
        scatter = ax4.scatter(land_values, lh_scores, c=lh_scores, 
                             cmap='RdYlGn', s=200, alpha=0.7, edgecolors='black')
        
        for i, name in enumerate(site_names):
            ax4.annotate(f'부지{i+1}', 
                        (land_values[i], lh_scores[i]),
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=9, fontweight='bold')
        
        ax4.set_xlabel('토지가 (억원)', fontsize=11)
        ax4.set_ylabel('LH 점수', fontsize=11)
        ax4.set_title('토지가 vs LH 점수', fontsize=13, fontweight='bold', pad=15)
        ax4.grid(alpha=0.3)
        
        # 컬러바
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('LH 점수', fontsize=10)
        
        plt.tight_layout()
        
        # 저장
        file_path = os.path.join(self.output_dir, file_name)
        plt.savefig(file_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 다중 부지 비교 차트 생성: {file_path}")
        return file_path


__all__ = ['ChartGenerator']
