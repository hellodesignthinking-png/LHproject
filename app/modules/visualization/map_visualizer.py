"""
ZeroSite v4.0 Map Visualization Module
=======================================

Folium 기반 지도 시각화

Author: ZeroSite Visualization Team
Date: 2025-12-27
Version: 1.0
"""

import folium
from folium import plugins
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json


class MapVisualizer:
    """지도 기반 시각화 클래스"""
    
    def __init__(self, output_dir: str = "output/maps"):
        """
        Args:
            output_dir: 지도 HTML 파일 저장 디렉터리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 서울 중심 좌표
        self.default_center = (37.5665, 126.9780)
        self.default_zoom = 11
    
    def create_single_site_map(
        self,
        site_info: Dict[str, Any],
        lh_result: Dict[str, Any],
        file_name: str = "single_site_map.html"
    ) -> str:
        """
        단일 부지 지도 생성
        
        Args:
            site_info: 부지 정보 (address, coordinates, etc.)
            lh_result: LH 평가 결과
            file_name: 저장 파일명
            
        Returns:
            저장된 파일 경로
        """
        # 지도 생성
        coords = site_info.get("coordinates", self.default_center)
        m = folium.Map(
            location=coords,
            zoom_start=16,
            tiles="OpenStreetMap"
        )
        
        # 마커 색상 결정 (판정 기준)
        judgement = lh_result.get("judgement", "NO_GO")
        
        if judgement == "GO":
            marker_color = "green"
            icon_name = "check-circle"
        elif judgement == "CONDITIONAL_GO":
            marker_color = "orange"
            icon_name = "exclamation-circle"
        else:
            marker_color = "red"
            icon_name = "times-circle"
        
        # 팝업 내용
        popup_html = f"""
        <div style="font-family: Arial; width: 300px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{site_info.get('address', 'N/A')}</h4>
            <hr style="margin: 10px 0;">
            <table style="width: 100%; font-size: 14px;">
                <tr>
                    <td><b>판정:</b></td>
                    <td><span style="color: {marker_color}; font-weight: bold;">{judgement}</span></td>
                </tr>
                <tr>
                    <td><b>LH 점수:</b></td>
                    <td>{lh_result.get('lh_score_total', 0):.1f}/100</td>
                </tr>
                <tr>
                    <td><b>등급:</b></td>
                    <td>{lh_result.get('grade', 'N/A')}</td>
                </tr>
                <tr>
                    <td><b>면적:</b></td>
                    <td>{site_info.get('area_sqm', 0):.1f}㎡</td>
                </tr>
                <tr>
                    <td><b>용도지역:</b></td>
                    <td>{site_info.get('zone_type', 'N/A')}</td>
                </tr>
                <tr>
                    <td><b>NPV:</b></td>
                    <td>₩{self._format_currency(lh_result.get('npv', 0))}</td>
                </tr>
                <tr>
                    <td><b>IRR:</b></td>
                    <td>{lh_result.get('irr', 0):.2f}%</td>
                </tr>
            </table>
        </div>
        """
        
        # 마커 추가
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix='fa'),
            tooltip=site_info.get('address', 'N/A')
        ).add_to(m)
        
        # 반경 500m 원 추가
        folium.Circle(
            location=coords,
            radius=500,
            color=marker_color,
            fill=True,
            fillColor=marker_color,
            fillOpacity=0.1,
            popup="500m 반경"
        ).add_to(m)
        
        # 저장
        output_path = self.output_dir / file_name
        m.save(str(output_path))
        
        return str(output_path)
    
    def create_comparison_map(
        self,
        sites: List[Dict[str, Any]],
        file_name: str = "comparison_map.html"
    ) -> str:
        """
        다중 부지 비교 지도 생성
        
        Args:
            sites: 부지 리스트 (각각 site_info, lh_result 포함)
            file_name: 저장 파일명
            
        Returns:
            저장된 파일 경로
        """
        # 중심 좌표 계산 (모든 부지의 평균)
        if sites:
            avg_lat = sum(site["site_info"]["coordinates"][0] for site in sites) / len(sites)
            avg_lon = sum(site["site_info"]["coordinates"][1] for site in sites) / len(sites)
            center = (avg_lat, avg_lon)
        else:
            center = self.default_center
        
        # 지도 생성
        m = folium.Map(
            location=center,
            zoom_start=12,
            tiles="OpenStreetMap"
        )
        
        # 마커 클러스터 추가
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # 각 부지에 마커 추가
        for idx, site in enumerate(sites, 1):
            site_info = site["site_info"]
            lh_result = site["lh_result"]
            
            coords = site_info.get("coordinates", self.default_center)
            judgement = lh_result.get("judgement", "NO_GO")
            
            # 마커 색상
            if judgement == "GO":
                marker_color = "green"
                icon_name = "check-circle"
            elif judgement == "CONDITIONAL_GO":
                marker_color = "orange"
                icon_name = "exclamation-circle"
            else:
                marker_color = "red"
                icon_name = "times-circle"
            
            # 팝업 내용
            popup_html = f"""
            <div style="font-family: Arial; width: 320px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">
                    부지 #{idx}: {site_info.get('address', 'N/A')}
                </h4>
                <hr style="margin: 10px 0;">
                <table style="width: 100%; font-size: 14px;">
                    <tr>
                        <td><b>판정:</b></td>
                        <td><span style="color: {marker_color}; font-weight: bold;">{judgement}</span></td>
                    </tr>
                    <tr>
                        <td><b>LH 점수:</b></td>
                        <td>{lh_result.get('lh_score_total', 0):.1f}/100</td>
                    </tr>
                    <tr>
                        <td><b>등급:</b></td>
                        <td>{lh_result.get('grade', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><b>순위:</b></td>
                        <td>{site.get('rank', 'N/A')}위</td>
                    </tr>
                    <tr>
                        <td><b>면적:</b></td>
                        <td>{site_info.get('area_sqm', 0):.1f}㎡</td>
                    </tr>
                    <tr>
                        <td><b>NPV:</b></td>
                        <td>₩{self._format_currency(lh_result.get('npv', 0))}</td>
                    </tr>
                    <tr>
                        <td><b>IRR:</b></td>
                        <td>{lh_result.get('irr', 0):.2f}%</td>
                    </tr>
                </table>
            </div>
            """
            
            # 마커 추가
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=370),
                icon=folium.Icon(color=marker_color, icon=icon_name, prefix='fa'),
                tooltip=f"부지 #{idx}"
            ).add_to(marker_cluster)
        
        # 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    width: 200px; height: auto; 
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 9999; 
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0;">범례</h4>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker fa-2x" style="color:green"></i> GO</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker fa-2x" style="color:orange"></i> 조건부 GO</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker fa-2x" style="color:red"></i> NO_GO</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 미니맵 추가
        minimap = plugins.MiniMap(toggle_display=True)
        m.add_child(minimap)
        
        # 전체 화면 버튼
        plugins.Fullscreen(
            position="topleft",
            title="전체 화면",
            title_cancel="전체 화면 종료",
            force_separate_button=True
        ).add_to(m)
        
        # 저장
        output_path = self.output_dir / file_name
        m.save(str(output_path))
        
        return str(output_path)
    
    def create_heatmap(
        self,
        locations: List[Tuple[float, float, float]],
        file_name: str = "heatmap.html"
    ) -> str:
        """
        히트맵 생성 (LH 점수 기준)
        
        Args:
            locations: [(lat, lon, score), ...] 형태의 위치와 점수 리스트
            file_name: 저장 파일명
            
        Returns:
            저장된 파일 경로
        """
        # 중심 좌표 계산
        if locations:
            avg_lat = sum(loc[0] for loc in locations) / len(locations)
            avg_lon = sum(loc[1] for loc in locations) / len(locations)
            center = (avg_lat, avg_lon)
        else:
            center = self.default_center
        
        # 지도 생성
        m = folium.Map(
            location=center,
            zoom_start=11,
            tiles="CartoDB positron"
        )
        
        # 히트맵 데이터 준비
        heat_data = [[loc[0], loc[1], loc[2]/100] for loc in locations]
        
        # 히트맵 레이어 추가
        plugins.HeatMap(
            heat_data,
            min_opacity=0.2,
            radius=25,
            blur=15,
            gradient={
                0.0: 'red',
                0.5: 'yellow',
                1.0: 'green'
            }
        ).add_to(m)
        
        # 저장
        output_path = self.output_dir / file_name
        m.save(str(output_path))
        
        return str(output_path)
    
    def _format_currency(self, value: float) -> str:
        """통화 포맷팅"""
        if value >= 1e8:
            return f"{value/1e8:.1f}억"
        elif value >= 1e4:
            return f"{value/1e4:.0f}만"
        else:
            return f"{value:,.0f}"


# 테스트 코드
if __name__ == "__main__":
    visualizer = MapVisualizer()
    
    # 예제 단일 부지
    site_info = {
        "address": "서울 강남구 역삼동 648-23",
        "coordinates": (37.498, 127.028),
        "area_sqm": 500.0,
        "zone_type": "제2종일반주거지역"
    }
    
    lh_result = {
        "judgement": "NO_GO",
        "lh_score_total": 61.0,
        "grade": "D",
        "npv": 792999999,
        "irr": 7.15
    }
    
    map_path = visualizer.create_single_site_map(site_info, lh_result)
    print(f"단일 부지 지도 생성: {map_path}")
