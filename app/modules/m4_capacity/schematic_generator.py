"""
M4 Capacity Module - Schematic Drawing Generator
================================================

Generates SVG/PNG schematic drawings for architectural capacity analysis:
- ground_layout: Site boundary, building footprints, setbacks
- standard_floor: Standard floor plan with unit distribution
- basement_parking: Basement parking layout with ramp
- massing_comparison: 3D massing comparison of alternatives

Features:
- Pure SVG generation (no external dependencies)
- Simple, schematic style (not detailed design)
- Parametric generation from CapacityContextV2
- Export to SVG and PNG formats

Author: ZeroSite M4 Development Team
Date: 2025-12-17
Version: 2.0
"""

import os
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# SVG Drawing Primitives
# ============================================================================

class SVGBuilder:
    """Simple SVG builder for schematic drawings"""
    
    def __init__(self, width: int, height: int, viewBox: Optional[str] = None):
        self.width = width
        self.height = height
        self.viewBox = viewBox or f"0 0 {width} {height}"
        self.elements: List[str] = []
        
    def add_rect(self, x: float, y: float, width: float, height: float, 
                 fill: str = "white", stroke: str = "black", 
                 stroke_width: float = 1, opacity: float = 1.0):
        """Add rectangle"""
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'opacity="{opacity}"/>'
        )
    
    def add_circle(self, cx: float, cy: float, r: float, 
                   fill: str = "white", stroke: str = "black", stroke_width: float = 1):
        """Add circle"""
        self.elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
    
    def add_line(self, x1: float, y1: float, x2: float, y2: float, 
                 stroke: str = "black", stroke_width: float = 1, 
                 stroke_dasharray: Optional[str] = None):
        """Add line"""
        dash = f'stroke-dasharray="{stroke_dasharray}"' if stroke_dasharray else ''
        self.elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" {dash}/>'
        )
    
    def add_text(self, x: float, y: float, text: str, 
                 font_size: int = 12, font_family: str = "Arial", 
                 fill: str = "black", anchor: str = "start", weight: str = "normal"):
        """Add text"""
        self.elements.append(
            f'<text x="{x}" y="{y}" font-size="{font_size}" '
            f'font-family="{font_family}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{text}</text>'
        )
    
    def add_polygon(self, points: List[Tuple[float, float]], 
                    fill: str = "white", stroke: str = "black", 
                    stroke_width: float = 1, opacity: float = 1.0):
        """Add polygon"""
        points_str = " ".join([f"{x},{y}" for x, y in points])
        self.elements.append(
            f'<polygon points="{points_str}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" '
            f'opacity="{opacity}"/>'
        )
    
    def add_path(self, d: str, fill: str = "none", stroke: str = "black", 
                 stroke_width: float = 1):
        """Add path"""
        self.elements.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"/>'
        )
    
    def build(self) -> str:
        """Build final SVG string"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" viewBox="{self.viewBox}" 
     xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            text {{ font-family: Arial, sans-serif; }}
            .title {{ font-size: 16px; font-weight: bold; }}
            .label {{ font-size: 12px; }}
            .small {{ font-size: 10px; fill: #666; }}
        </style>
    </defs>
    {''.join(self.elements)}
</svg>'''
        return svg


# ============================================================================
# Ground Layout Schematic
# ============================================================================

def generate_ground_layout_svg(
    site_area_sqm: float,
    building_footprints: List[Dict],
    legal_bcr: float,
    setbacks: Dict[str, float]
) -> str:
    """
    Generate ground layout schematic showing site boundary, building footprints, setbacks
    
    Args:
        site_area_sqm: Site area in square meters
        building_footprints: List of building footprint data
        legal_bcr: Legal building coverage ratio
        setbacks: Dict of setback distances (front, rear, side)
    
    Returns:
        SVG string
    """
    svg = SVGBuilder(800, 600)
    
    # Add title
    svg.add_text(400, 30, "GROUND LAYOUT - SCHEMATIC", 
                 font_size=18, anchor="middle", weight="bold")
    svg.add_text(400, 50, f"Site Area: {site_area_sqm:,.0f}㎡ | BCR: {legal_bcr*100:.0f}%", 
                 font_size=12, anchor="middle", fill="#666")
    
    # Draw site boundary (simplified rectangular site)
    site_width = math.sqrt(site_area_sqm * 1.5)  # Assume 1.5:1 aspect ratio
    site_height = site_area_sqm / site_width
    
    # Scale to fit drawing area (with margins)
    scale = min(600 / site_width, 450 / site_height)
    offset_x = 100
    offset_y = 100
    
    # Site boundary
    svg.add_rect(
        offset_x, offset_y, 
        site_width * scale, site_height * scale,
        fill="#f5f5f5", stroke="#333", stroke_width=2
    )
    
    # Setback lines (dashed)
    front_setback = setbacks.get('front', 3.0) * scale
    rear_setback = setbacks.get('rear', 3.0) * scale
    side_setback = setbacks.get('side', 2.0) * scale
    
    # Front setback
    svg.add_line(
        offset_x + front_setback, offset_y,
        offset_x + front_setback, offset_y + site_height * scale,
        stroke="#ff6b6b", stroke_width=1, stroke_dasharray="5,5"
    )
    
    # Rear setback
    svg.add_line(
        offset_x + site_width * scale - rear_setback, offset_y,
        offset_x + site_width * scale - rear_setback, offset_y + site_height * scale,
        stroke="#ff6b6b", stroke_width=1, stroke_dasharray="5,5"
    )
    
    # Side setbacks
    svg.add_line(
        offset_x, offset_y + side_setback,
        offset_x + site_width * scale, offset_y + side_setback,
        stroke="#ff6b6b", stroke_width=1, stroke_dasharray="5,5"
    )
    svg.add_line(
        offset_x, offset_y + site_height * scale - side_setback,
        offset_x + site_width * scale, offset_y + site_height * scale - side_setback,
        stroke="#ff6b6b", stroke_width=1, stroke_dasharray="5,5"
    )
    
    # Draw building footprints
    buildable_width = site_width * scale - front_setback - rear_setback
    buildable_height = site_height * scale - 2 * side_setback
    
    num_buildings = len(building_footprints)
    if num_buildings > 0:
        building_width = buildable_width / num_buildings * 0.8
        spacing = buildable_width / num_buildings * 0.2
        
        for i, footprint in enumerate(building_footprints):
            bld_x = offset_x + front_setback + i * (building_width + spacing)
            bld_y = offset_y + side_setback + (buildable_height - buildable_height * 0.6) / 2
            bld_h = buildable_height * 0.6
            
            svg.add_rect(
                bld_x, bld_y, building_width, bld_h,
                fill="#4a90e2", stroke="#2c5f8d", stroke_width=2, opacity=0.8
            )
            svg.add_text(
                bld_x + building_width/2, bld_y + bld_h/2,
                f"BLD {i+1}", font_size=14, anchor="middle", fill="white", weight="bold"
            )
    
    # Legend
    legend_y = offset_y + site_height * scale + 50
    svg.add_text(offset_x, legend_y, "LEGEND:", font_size=12, weight="bold")
    svg.add_rect(offset_x, legend_y + 10, 20, 15, fill="#4a90e2", stroke="black")
    svg.add_text(offset_x + 30, legend_y + 22, "Building Footprint", font_size=10)
    svg.add_line(offset_x + 150, legend_y + 17, offset_x + 170, legend_y + 17, 
                 stroke="#ff6b6b", stroke_dasharray="5,5")
    svg.add_text(offset_x + 180, legend_y + 22, "Setback Line", font_size=10)
    
    return svg.build()


# ============================================================================
# Standard Floor Schematic
# ============================================================================

def generate_standard_floor_svg(
    standard_floor_area: float,
    unit_count_per_floor: int,
    avg_unit_area: float
) -> str:
    """
    Generate standard floor plan schematic with unit distribution
    
    Args:
        standard_floor_area: Standard floor area (㎡)
        unit_count_per_floor: Number of units per floor
        avg_unit_area: Average unit area (㎡)
    
    Returns:
        SVG string
    """
    svg = SVGBuilder(800, 600)
    
    # Title
    svg.add_text(400, 30, "STANDARD FLOOR PLAN - SCHEMATIC", 
                 font_size=18, anchor="middle", weight="bold")
    svg.add_text(400, 50, f"Floor Area: {standard_floor_area:,.0f}㎡ | Units: {unit_count_per_floor}",
                 font_size=12, anchor="middle", fill="#666")
    
    # Draw floor plate
    floor_width = 600
    floor_height = 400
    offset_x = 100
    offset_y = 100
    
    svg.add_rect(offset_x, offset_y, floor_width, floor_height,
                 fill="#f0f0f0", stroke="#333", stroke_width=2)
    
    # Draw units
    cols = math.ceil(math.sqrt(unit_count_per_floor))
    rows = math.ceil(unit_count_per_floor / cols)
    
    unit_width = floor_width / cols
    unit_height = floor_height / rows
    
    for i in range(unit_count_per_floor):
        row = i // cols
        col = i % cols
        
        unit_x = offset_x + col * unit_width
        unit_y = offset_y + row * unit_height
        
        svg.add_rect(unit_x, unit_y, unit_width, unit_height,
                     fill="white", stroke="#666", stroke_width=1)
        svg.add_text(unit_x + unit_width/2, unit_y + unit_height/2 - 10,
                     f"UNIT {i+1}", font_size=12, anchor="middle", weight="bold")
        svg.add_text(unit_x + unit_width/2, unit_y + unit_height/2 + 10,
                     f"{avg_unit_area:.0f}㎡", font_size=10, anchor="middle", fill="#666")
    
    # Core (elevator/stairs)
    core_size = 60
    core_x = offset_x + floor_width/2 - core_size/2
    core_y = offset_y + floor_height/2 - core_size/2
    svg.add_rect(core_x, core_y, core_size, core_size,
                 fill="#ff9999", stroke="#cc0000", stroke_width=2)
    svg.add_text(core_x + core_size/2, core_y + core_size/2,
                 "CORE", font_size=10, anchor="middle", weight="bold")
    
    return svg.build()


# ============================================================================
# Basement Parking Schematic
# ============================================================================

def generate_basement_parking_svg(
    parking_spaces: int,
    basement_floors: int,
    ramp_status: str
) -> str:
    """
    Generate basement parking layout schematic with ramp
    
    Args:
        parking_spaces: Total parking spaces
        basement_floors: Number of basement floors
        ramp_status: Ramp feasibility status ('feasible', 'marginal', 'not_feasible')
    
    Returns:
        SVG string
    """
    svg = SVGBuilder(800, 600)
    
    # Title
    svg.add_text(400, 30, "BASEMENT PARKING - SCHEMATIC", 
                 font_size=18, anchor="middle", weight="bold")
    svg.add_text(400, 50, f"Total Spaces: {parking_spaces} | Basement Floors: {basement_floors}",
                 font_size=12, anchor="middle", fill="#666")
    
    # Draw parking area
    parking_width = 600
    parking_height = 350
    offset_x = 100
    offset_y = 100
    
    svg.add_rect(offset_x, offset_y, parking_width, parking_height,
                 fill="#e8e8e8", stroke="#333", stroke_width=2)
    
    # Draw parking spaces (simplified grid)
    spaces_per_floor = parking_spaces // basement_floors if basement_floors > 0 else parking_spaces
    cols = 12
    rows = math.ceil(spaces_per_floor / cols)
    
    space_width = 40
    space_height = 25
    spacing = 5
    
    for row in range(rows):
        for col in range(cols):
            space_num = row * cols + col
            if space_num >= spaces_per_floor:
                break
            
            space_x = offset_x + 50 + col * (space_width + spacing)
            space_y = offset_y + 50 + row * (space_height + spacing)
            
            svg.add_rect(space_x, space_y, space_width, space_height,
                         fill="white", stroke="#666", stroke_width=1)
    
    # Draw ramp
    ramp_color = {"feasible": "#4caf50", "marginal": "#ff9800", "not_feasible": "#f44336"}.get(ramp_status, "#666")
    ramp_x = offset_x + parking_width - 150
    ramp_y = offset_y + 50
    ramp_width = 100
    ramp_height = 200
    
    svg.add_polygon([
        (ramp_x, ramp_y),
        (ramp_x + ramp_width, ramp_y),
        (ramp_x + ramp_width, ramp_y + ramp_height),
        (ramp_x, ramp_y + ramp_height * 0.7)
    ], fill=ramp_color, stroke="#333", stroke_width=2, opacity=0.7)
    
    svg.add_text(ramp_x + ramp_width/2, ramp_y + ramp_height/2,
                 "RAMP", font_size=14, anchor="middle", weight="bold", fill="white")
    
    # Ramp status indicator
    status_y = offset_y + parking_height + 50
    svg.add_text(offset_x, status_y, f"Ramp Status: {ramp_status.upper()}", 
                 font_size=14, weight="bold", fill=ramp_color)
    
    return svg.build()


# ============================================================================
# Massing Comparison Schematic
# ============================================================================

def generate_massing_comparison_svg(
    massing_options: List[Dict]
) -> str:
    """
    Generate 3D massing comparison of alternatives
    
    Args:
        massing_options: List of massing option data with building_count, floor_count, etc.
    
    Returns:
        SVG string
    """
    svg = SVGBuilder(1000, 600)
    
    # Title
    svg.add_text(500, 30, "MASSING ALTERNATIVES COMPARISON", 
                 font_size=18, anchor="middle", weight="bold")
    svg.add_text(500, 50, f"{len(massing_options)} Options",
                 font_size=12, anchor="middle", fill="#666")
    
    # Draw each massing option
    option_width = 900 / len(massing_options) if massing_options else 200
    offset_x = 50
    offset_y = 100
    
    for i, option in enumerate(massing_options):
        opt_x = offset_x + i * option_width + option_width * 0.1
        opt_width = option_width * 0.8
        
        building_count = option.get('building_count', 1)
        floor_count = option.get('floor_count', 10)
        
        # Draw buildings (isometric view)
        building_width = opt_width / building_count * 0.7
        building_spacing = opt_width / building_count * 0.3
        
        max_height = 400
        building_height = min(floor_count * 8, max_height)  # 8px per floor
        
        for b in range(building_count):
            bld_x = opt_x + b * (building_width + building_spacing)
            bld_y = offset_y + max_height - building_height
            
            # Front face
            svg.add_rect(bld_x, bld_y, building_width, building_height,
                         fill="#4a90e2", stroke="#2c5f8d", stroke_width=2)
            
            # Top face (isometric)
            svg.add_polygon([
                (bld_x, bld_y),
                (bld_x + building_width, bld_y),
                (bld_x + building_width + 15, bld_y - 15),
                (bld_x + 15, bld_y - 15)
            ], fill="#6ba3e8", stroke="#2c5f8d", stroke_width=1)
            
            # Side face
            svg.add_polygon([
                (bld_x + building_width, bld_y),
                (bld_x + building_width + 15, bld_y - 15),
                (bld_x + building_width + 15, bld_y + building_height - 15),
                (bld_x + building_width, bld_y + building_height)
            ], fill="#3a7ec2", stroke="#2c5f8d", stroke_width=1)
        
        # Option label
        label_y = offset_y + max_height + 30
        svg.add_text(opt_x + opt_width/2, label_y, f"OPTION {i+1}",
                     font_size=14, anchor="middle", weight="bold")
        svg.add_text(opt_x + opt_width/2, label_y + 20, 
                     f"{building_count}동 × {floor_count}층",
                     font_size=11, anchor="middle", fill="#666")
        svg.add_text(opt_x + opt_width/2, label_y + 36,
                     f"FAR: {option.get('far_achieved', 0)*100:.0f}%",
                     font_size=10, anchor="middle", fill="#666")
    
    return svg.build()


# ============================================================================
# Main Generator Class
# ============================================================================

class SchematicDrawingGenerator:
    """
    Main schematic drawing generator for M4 Capacity Module
    
    Generates all 4 required schematic drawings:
    1. ground_layout
    2. standard_floor
    3. basement_parking
    4. massing_comparison
    """
    
    def __init__(self, output_dir: str = "/home/user/webapp/static/schematics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all(self, capacity_data: Dict, parcel_id: str) -> Dict[str, str]:
        """
        Generate all 4 schematic drawings
        
        Args:
            capacity_data: Data from CapacityContextV2
            parcel_id: Unique parcel identifier
        
        Returns:
            Dict with paths to generated SVG files
        """
        paths = {}
        
        # 1. Ground Layout
        ground_svg = generate_ground_layout_svg(
            site_area_sqm=capacity_data.get('site_area', 1000),
            building_footprints=capacity_data.get('massing_options', [])[:3],
            legal_bcr=capacity_data.get('legal_bcr', 0.6),
            setbacks={'front': 3.0, 'rear': 3.0, 'side': 2.0}
        )
        ground_path = self.output_dir / f"{parcel_id}_ground_layout.svg"
        ground_path.write_text(ground_svg, encoding='utf-8')
        paths['ground_layout'] = str(ground_path)
        
        # 2. Standard Floor
        massing_opt = capacity_data.get('massing_options', [{}])[0]
        standard_svg = generate_standard_floor_svg(
            standard_floor_area=massing_opt.get('standard_floor_area', 500),
            unit_count_per_floor=capacity_data.get('unit_summary', {}).get('total_units', 100) // massing_opt.get('floor_count', 10),
            avg_unit_area=capacity_data.get('avg_unit_area', 59.0)
        )
        standard_path = self.output_dir / f"{parcel_id}_standard_floor.svg"
        standard_path.write_text(standard_svg, encoding='utf-8')
        paths['standard_floor'] = str(standard_path)
        
        # 3. Basement Parking
        parking_alt_a = capacity_data.get('parking_solutions', {}).get('alternative_A', {})
        basement_svg = generate_basement_parking_svg(
            parking_spaces=parking_alt_a.get('total_spaces', 100),
            basement_floors=parking_alt_a.get('basement_floors', 2),
            ramp_status=parking_alt_a.get('ramp_conditions', {}).get('status', 'feasible')
        )
        basement_path = self.output_dir / f"{parcel_id}_basement_parking.svg"
        basement_path.write_text(basement_svg, encoding='utf-8')
        paths['basement_parking'] = str(basement_path)
        
        # 4. Massing Comparison
        massing_svg = generate_massing_comparison_svg(
            massing_options=capacity_data.get('massing_options', [])
        )
        massing_path = self.output_dir / f"{parcel_id}_massing_comparison.svg"
        massing_path.write_text(massing_svg, encoding='utf-8')
        paths['massing_comparison'] = str(massing_path)
        
        return paths


# Export main generator
__all__ = ['SchematicDrawingGenerator']
