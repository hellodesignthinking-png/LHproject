"""
M4 V2 Schematic Drawing Generation Tests
========================================

Test schematic SVG generation for all 4 required drawings:
1. ground_layout
2. standard_floor
3. basement_parking
4. massing_comparison

Author: ZeroSite M4 Test Team
Date: 2025-12-17
"""

import pytest
import os
from pathlib import Path

from app.modules.m4_capacity.schematic_generator import (
    SchematicDrawingGenerator,
    generate_ground_layout_svg,
    generate_standard_floor_svg,
    generate_basement_parking_svg,
    generate_massing_comparison_svg
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_output_dir(tmp_path):
    """Temporary output directory for test schematics"""
    output_dir = tmp_path / "test_schematics"
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def schematic_generator(test_output_dir):
    """Schematic generator instance"""
    return SchematicDrawingGenerator(output_dir=test_output_dir)


@pytest.fixture
def sample_capacity_data():
    """Sample capacity data for schematic generation"""
    return {
        'site_area': 1000.0,
        'legal_bcr': 0.6,
        'massing_options': [
            {
                'option_id': 'OPT_A',
                'building_count': 2,
                'floor_count': 15,
                'standard_floor_area': 500.0,
                'far_achieved': 2.4
            },
            {
                'option_id': 'OPT_B',
                'building_count': 3,
                'floor_count': 10,
                'standard_floor_area': 400.0,
                'far_achieved': 2.3
            },
            {
                'option_id': 'OPT_C',
                'building_count': 1,
                'floor_count': 20,
                'standard_floor_area': 600.0,
                'far_achieved': 2.5
            }
        ],
        'unit_summary': {
            'total_units': 182
        },
        'avg_unit_area': 59.0,
        'parking_solutions': {
            'alternative_A': {
                'total_spaces': 91,
                'basement_floors': 2,
                'ramp_conditions': {
                    'status': 'feasible'
                }
            },
            'alternative_B': {
                'total_spaces': 85,
                'basement_floors': 2,
                'ramp_conditions': {
                    'status': 'feasible'
                }
            }
        }
    }


# ============================================================================
# Individual SVG Generation Tests
# ============================================================================

def test_ground_layout_svg_generation():
    """Test ground layout SVG generation"""
    svg = generate_ground_layout_svg(
        site_area_sqm=1000.0,
        building_footprints=[{'id': 1}, {'id': 2}],
        legal_bcr=0.6,
        setbacks={'front': 3.0, 'rear': 3.0, 'side': 2.0}
    )
    
    assert svg is not None
    assert '<?xml version="1.0"' in svg
    assert '<svg' in svg
    assert 'GROUND LAYOUT' in svg
    assert 'Site Area' in svg


def test_standard_floor_svg_generation():
    """Test standard floor plan SVG generation"""
    svg = generate_standard_floor_svg(
        standard_floor_area=500.0,
        unit_count_per_floor=6,
        avg_unit_area=59.0
    )
    
    assert svg is not None
    assert '<?xml version="1.0"' in svg
    assert '<svg' in svg
    assert 'STANDARD FLOOR' in svg
    assert 'UNIT' in svg


def test_basement_parking_svg_generation():
    """Test basement parking SVG generation"""
    svg = generate_basement_parking_svg(
        parking_spaces=91,
        basement_floors=2,
        ramp_status='feasible'
    )
    
    assert svg is not None
    assert '<?xml version="1.0"' in svg
    assert '<svg' in svg
    assert 'BASEMENT PARKING' in svg
    assert 'RAMP' in svg
    assert 'feasible' in svg.lower()


def test_massing_comparison_svg_generation():
    """Test massing comparison SVG generation"""
    massing_options = [
        {'option_id': 'A', 'building_count': 2, 'floor_count': 15, 'far_achieved': 2.4},
        {'option_id': 'B', 'building_count': 3, 'floor_count': 10, 'far_achieved': 2.3},
        {'option_id': 'C', 'building_count': 1, 'floor_count': 20, 'far_achieved': 2.5}
    ]
    
    svg = generate_massing_comparison_svg(massing_options)
    
    assert svg is not None
    assert '<?xml version="1.0"' in svg
    assert '<svg' in svg
    assert 'MASSING ALTERNATIVES' in svg
    assert 'OPTION' in svg


# ============================================================================
# SchematicDrawingGenerator Tests
# ============================================================================

def test_schematic_generator_initialization(test_output_dir):
    """Test schematic generator initialization"""
    generator = SchematicDrawingGenerator(output_dir=test_output_dir)
    
    assert generator is not None
    assert generator.output_dir.exists()
    assert generator.output_dir.is_dir()


def test_generate_all_schematics(schematic_generator, sample_capacity_data):
    """Test generating all 4 schematics"""
    parcel_id = "TEST_PARCEL_001"
    
    paths = schematic_generator.generate_all(
        capacity_data=sample_capacity_data,
        parcel_id=parcel_id
    )
    
    # Check that all 4 schematic paths are returned
    assert 'ground_layout' in paths
    assert 'standard_floor' in paths
    assert 'basement_parking' in paths
    assert 'massing_comparison' in paths
    
    # Check that files exist
    for key, path in paths.items():
        assert os.path.exists(path), f"File not found: {path}"
        assert path.endswith('.svg'), f"Not an SVG file: {path}"
        
        # Check file content
        with open(path, 'r') as f:
            content = f.read()
            assert '<?xml version="1.0"' in content
            assert '<svg' in content


def test_schematic_file_naming(schematic_generator, sample_capacity_data):
    """Test schematic file naming convention"""
    parcel_id = "TEST_PARCEL_002"
    
    paths = schematic_generator.generate_all(
        capacity_data=sample_capacity_data,
        parcel_id=parcel_id
    )
    
    # Check naming convention
    assert parcel_id in paths['ground_layout']
    assert 'ground_layout' in paths['ground_layout']
    
    assert parcel_id in paths['standard_floor']
    assert 'standard_floor' in paths['standard_floor']
    
    assert parcel_id in paths['basement_parking']
    assert 'basement_parking' in paths['basement_parking']
    
    assert parcel_id in paths['massing_comparison']
    assert 'massing_comparison' in paths['massing_comparison']


def test_schematic_svg_validity(schematic_generator, sample_capacity_data):
    """Test that generated SVGs are valid"""
    parcel_id = "TEST_PARCEL_003"
    
    paths = schematic_generator.generate_all(
        capacity_data=sample_capacity_data,
        parcel_id=parcel_id
    )
    
    for key, path in paths.items():
        with open(path, 'r') as f:
            content = f.read()
            
            # Basic SVG structure checks
            assert content.startswith('<?xml version="1.0"')
            assert '<svg' in content
            assert '</svg>' in content
            assert 'xmlns="http://www.w3.org/2000/svg"' in content


def test_schematic_with_minimal_data(schematic_generator):
    """Test schematic generation with minimal data"""
    minimal_data = {
        'site_area': 500.0,
        'legal_bcr': 0.5,
        'massing_options': [{'building_count': 1, 'floor_count': 5}],
        'unit_summary': {'total_units': 50},
        'avg_unit_area': 50.0,
        'parking_solutions': {
            'alternative_A': {
                'total_spaces': 25,
                'basement_floors': 1,
                'ramp_conditions': {'status': 'feasible'}
            }
        }
    }
    
    parcel_id = "TEST_MINIMAL"
    
    # Should not raise exception
    paths = schematic_generator.generate_all(
        capacity_data=minimal_data,
        parcel_id=parcel_id
    )
    
    assert len(paths) == 4


def test_schematic_overwrites_existing(schematic_generator, sample_capacity_data):
    """Test that regenerating schematics overwrites existing files"""
    parcel_id = "TEST_OVERWRITE"
    
    # Generate once
    paths_1 = schematic_generator.generate_all(
        capacity_data=sample_capacity_data,
        parcel_id=parcel_id
    )
    
    # Get initial modification time
    initial_mtime = os.path.getmtime(paths_1['ground_layout'])
    
    # Wait a moment
    import time
    time.sleep(0.1)
    
    # Generate again
    paths_2 = schematic_generator.generate_all(
        capacity_data=sample_capacity_data,
        parcel_id=parcel_id
    )
    
    # Check that file was overwritten
    new_mtime = os.path.getmtime(paths_2['ground_layout'])
    assert new_mtime > initial_mtime


# ============================================================================
# Integration Test with Full Capacity Context
# ============================================================================

@pytest.mark.skip(reason="Integration test - requires full context setup")
def test_schematic_generation_integration():
    """Integration test: Generate schematics from full capacity data"""
    from app.modules.m4_capacity.service_v2 import CapacityServiceV2
    from app.core.context.canonical_land import CanonicalLandContext
    from app.core.context.housing_type_context import HousingTypeContext
    from datetime import datetime
    
    # Create mock contexts with all required fields
    land_ctx = CanonicalLandContext(
        parcel_id="INT_TEST_001",
        address="Integration Test Address",
        road_address="Test Road Address",
        coordinates={"lat": 37.5, "lon": 127.0},
        sido="서울특별시",
        sigungu="강남구",
        dong="역삼동",
        area_sqm=1000.0,
        area_pyeong=302.5,
        land_category="대",
        land_use="주거용",
        zone_type="general_residential",
        zone_detail="제2종일반주거지역",
        far=2.0,
        bcr=0.6,
        road_width=8.0,
        road_type="local_road",
        terrain_height=0.0,
        terrain_shape="flat",
        regulations=[],
        restrictions=[],
        data_source="test",
        retrieval_date=datetime.now().strftime("%Y-%m-%d")
    )
    
    housing_ctx = HousingTypeContext(
        selected_type="newlywed_2",
        selected_type_name="신혼·신생아 II형",
        selection_confidence=0.85
    )
    
    # Run M4 service
    service = CapacityServiceV2()
    capacity_ctx = service.run(land_ctx, housing_ctx)
    
    # Check that schematic paths are populated
    assert capacity_ctx.schematic_drawing_paths is not None
    assert 'ground_layout' in capacity_ctx.schematic_drawing_paths
    assert 'standard_floor' in capacity_ctx.schematic_drawing_paths
    assert 'basement_parking' in capacity_ctx.schematic_drawing_paths
    assert 'massing_comparison' in capacity_ctx.schematic_drawing_paths
    
    # Check that files exist
    for key, path in capacity_ctx.schematic_drawing_paths.items():
        assert os.path.exists(path), f"Schematic file not found: {path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
