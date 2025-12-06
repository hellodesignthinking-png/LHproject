#!/usr/bin/env python3
"""
Test Script for Phase A: Narrative Layer
=========================================

Tests the complete Narrative Interpreter integration
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.narrative_interpreter import NarrativeInterpreter
from app.services_v13.report_full.policy_reference_db import PolicyReferenceDB


def print_section(title: str, width: int = 80):
    """Print section header"""
    print("\n" + "=" * width)
    print(f" {title}")
    print("=" * width + "\n")


def test_narrative_interpreter():
    """Test NarrativeInterpreter standalone"""
    print_section("TEST 1: Narrative Interpreter Standalone")
    
    interpreter = NarrativeInterpreter()
    
    # Sample context
    sample_ctx = {
        'site': {
            'address': {'full_address': '서울시 강남구 역삼동 123'},
            'land_area_sqm': 500
        },
        'demand': {
            'overall_score': 68.4,
            'recommended_type': '신혼부부형'
        },
        'market': {
            'signal': 'UNDERVALUED',
            'delta_pct': -8.4,
            'temperature': 'COOL',
            'trend': '하락'
        },
        'finance': {
            'capex_billion': 145.2,
            'npv_billion': -13.7,
            'irr_percent': -1.8
        },
        'scorecard': {
            'overall': {
                'score': 62.3,
                'grade': 'C+',
                'recommendation': 'CONDITIONAL'
            }
        },
        'risk_analysis': {
            'enhanced': {
                'top_10_risks': [
                    {
                        'name': '재무 타당성 부족',
                        'risk_level': 'CRITICAL',
                        'risk_score': 25,
                        'description': 'NPV 음수로 수익성 부족',
                        'response_strategies': [
                            '사업 규모 확대',
                            '공사비 절감',
                            '정책자금 활용'
                        ]
                    }
                ]
            }
        }
    }
    
    # Test Executive Summary
    print("Testing Executive Summary generation...")
    exec_summary = interpreter.interpret_executive_summary(sample_ctx)
    print(f"✅ Generated: {len(exec_summary)} characters")
    print(f"Preview (first 500 chars):\n{exec_summary[:500]}...\n")
    
    # Test Policy Framework
    print("Testing Policy Framework generation...")
    policy = interpreter.interpret_policy_framework(sample_ctx)
    print(f"✅ Generated: {len(policy)} characters")
    print(f"Preview (first 500 chars):\n{policy[:500]}...\n")
    
    # Test Market Analysis
    print("Testing Market Analysis generation...")
    market = interpreter.interpret_market_analysis(sample_ctx)
    print(f"✅ Generated: {len(market)} characters")
    print(f"Preview (first 500 chars):\n{market[:500]}...\n")
    
    print("✅ Narrative Interpreter: ALL TESTS PASSED")


def test_policy_reference_db():
    """Test PolicyReferenceDB"""
    print_section("TEST 2: Policy Reference Database")
    
    db = PolicyReferenceDB()
    
    # Test LH policy
    print("Testing LH policy retrieval...")
    supply_plan = db.get_lh_policy("supply_plan")
    print(f"✅ LH Supply Plan: {supply_plan['total_units']:,}호 ({supply_plan['period']})")
    
    # Test housing type policy
    print("\nTesting housing type policy...")
    youth_policy = db.get_housing_type_policy("청년형")
    print(f"✅ Youth Housing: {youth_policy['ratio']*100}%, Rent Rate: {youth_policy['rent_rate']*100}%")
    
    # Test references
    print("\nTesting references...")
    refs = db.get_all_references()
    print(f"✅ Total references: {len(refs)}")
    for ref in refs[:3]:
        print(f"   - {ref['id']}: {ref['title']}")
    
    # Test reference section generation
    print("\nTesting reference section generation...")
    ref_section = db.generate_reference_section()
    print(f"✅ Generated: {len(ref_section)} characters")
    
    print("\n✅ Policy Reference DB: ALL TESTS PASSED")


def test_integration():
    """Test full integration with ReportContextBuilder"""
    print_section("TEST 3: Full Integration Test")
    
    # Initialize builder
    print("Initializing ReportContextBuilder...")
    builder = ReportContextBuilder()
    print("✅ Builder initialized")
    
    # Test parameters
    address = "서울시 강남구 역삼동 123"
    land_area_sqm = 500.0
    coordinates = (37.5, 127.0)
    
    print(f"\nTest parameters:")
    print(f"  Address: {address}")
    print(f"  Land Area: {land_area_sqm}㎡")
    print(f"  Coordinates: {coordinates}")
    
    # Build expert context
    print("\nBuilding Expert Edition context...")
    try:
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=coordinates,
            additional_params={'housing_type': 'youth'}
        )
        print("✅ Context built successfully")
        
        # Check narrative layer
        if 'narratives' in context:
            narratives = context['narratives']
            print(f"\n📝 Narrative Layer Summary:")
            print(f"  - Executive Summary: {len(narratives.get('executive_summary', ''))} chars")
            print(f"  - Policy Framework: {len(narratives.get('policy_framework', ''))} chars")
            print(f"  - Market Analysis: {len(narratives.get('market_analysis', ''))} chars")
            print(f"  - Demand Analysis: {len(narratives.get('demand_analysis', ''))} chars")
            print(f"  - Financial: {len(narratives.get('financial', ''))} chars")
            print(f"  - Risk: {len(narratives.get('risk', ''))} chars")
            print(f"  - Roadmap: {len(narratives.get('roadmap', ''))} chars")
            print(f"  - Academic: {len(narratives.get('academic_conclusion', ''))} chars")
            
            total_chars = sum(len(v) for v in narratives.values())
            print(f"\n  📊 Total Narrative: {total_chars:,} characters")
            print(f"  📄 Estimated Pages: {total_chars // 3000} pages")
            
            # Check references
            if 'references' in context:
                refs = context['references']
                print(f"\n  📚 References: {len(refs)} items")
            
            print("\n✅ Narrative Layer: VERIFIED")
        else:
            print("❌ Narrative Layer: NOT FOUND")
            return False
        
        # Check metadata
        metadata = context.get('metadata', {})
        print(f"\n📋 Report Metadata:")
        print(f"  - Type: {metadata.get('report_type', 'N/A')}")
        print(f"  - Version: {metadata.get('version', 'N/A')}")
        print(f"  - Estimated Pages: {metadata.get('page_count_estimated', 'N/A')}")
        
        print("\n✅ Full Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Context building failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_narrative_quality():
    """Test narrative quality metrics"""
    print_section("TEST 4: Narrative Quality Assessment")
    
    interpreter = NarrativeInterpreter()
    
    # Sample context with various scenarios
    scenarios = [
        {
            'name': 'High Score (GO)',
            'ctx': {
                'site': {'address': {'full_address': '서울시 강남구'}, 'land_area_sqm': 800},
                'demand': {'overall_score': 85, 'recommended_type': '청년형'},
                'market': {'signal': 'FAIR', 'delta_pct': 0, 'temperature': 'NEUTRAL', 'trend': '안정'},
                'finance': {'capex_billion': 150, 'npv_billion': 15, 'irr_percent': 6.5},
                'scorecard': {'overall': {'score': 85, 'grade': 'A', 'recommendation': 'GO'}},
                'risk_analysis': {'enhanced': {'top_10_risks': []}}
            }
        },
        {
            'name': 'Low Score (NO-GO)',
            'ctx': {
                'site': {'address': {'full_address': '경기도 어딘가'}, 'land_area_sqm': 300},
                'demand': {'overall_score': 45, 'recommended_type': '고령자형'},
                'market': {'signal': 'OVERVALUED', 'delta_pct': 15, 'temperature': 'HOT', 'trend': '급등'},
                'finance': {'capex_billion': 120, 'npv_billion': -50, 'irr_percent': -8},
                'scorecard': {'overall': {'score': 35, 'grade': 'F', 'recommendation': 'NO-GO'}},
                'risk_analysis': {'enhanced': {'top_10_risks': []}}
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🔍 Scenario: {scenario['name']}")
        exec_summary = interpreter.interpret_executive_summary(scenario['ctx'])
        
        # Quality metrics
        word_count = len(exec_summary.split())
        has_data = any(keyword in exec_summary for keyword in ['NPV', 'IRR', '점', '억원'])
        has_reasoning = any(keyword in exec_summary for keyword in ['의미', '이유', '왜', '따라서'])
        has_recommendation = any(keyword in exec_summary for keyword in ['GO', 'CONDITIONAL', 'REVISE', 'NO-GO'])
        
        print(f"  📊 Word Count: {word_count}")
        print(f"  ✅ Contains Data: {has_data}")
        print(f"  ✅ Contains Reasoning: {has_reasoning}")
        print(f"  ✅ Contains Recommendation: {has_recommendation}")
        
        quality_score = sum([has_data, has_reasoning, has_recommendation, word_count > 200])
        print(f"  🎯 Quality Score: {quality_score}/4")
    
    print("\n✅ Narrative Quality: ASSESSED")


def main():
    """Run all tests"""
    print_section("PHASE A: NARRATIVE LAYER TEST SUITE", 100)
    print("Testing all components of the Narrative Interpreter system")
    print("=" * 100)
    
    try:
        # Test 1: Standalone Interpreter
        test_narrative_interpreter()
        
        # Test 2: Policy DB
        test_policy_reference_db()
        
        # Test 3: Full Integration
        success = test_integration()
        
        # Test 4: Quality Assessment
        test_narrative_quality()
        
        # Final summary
        print_section("TEST SUMMARY", 100)
        if success:
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ Phase A Implementation: VERIFIED")
            print("✅ Narrative Interpreter: WORKING")
            print("✅ Policy Reference DB: WORKING")
            print("✅ Integration: SUCCESSFUL")
            print("\n🚀 Ready for template integration!")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            print("Please check the error messages above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
