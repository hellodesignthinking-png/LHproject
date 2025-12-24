#!/usr/bin/env python3
"""
Phase 3.10 - Generate 6 Final Reports with Complete Mock Data
직접 백엔드 코드 실행 (NO API, NO import from app.services)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_mock_module_html():
    """완전한 Mock Module HTML 생성 (M2, M3, M4, M5, M6)"""
    
    # M2 - Land Appraisal (토지 감정)
    m2_html = """
    <div class="module-m2" data-module="M2">
        <h2>M2 - 토지 감정 평가</h2>
        <div class="kpi-summary">
            <div class="kpi-item" data-land-value="5600000000" data-land-value-total="5600000000" data-land-value-per-pyeong="5500000">
                <span class="label">총 토지 감정가</span>
                <span class="value">5,600,000,000원</span>
            </div>
            <div class="kpi-item" data-land-area="3450.0">
                <span class="label">토지 면적</span>
                <span class="value">3,450 m²</span>
            </div>
            <div class="kpi-item" data-market-price-per-pyeong="5500000">
                <span class="label">평당 시세</span>
                <span class="value">5,500,000원</span>
            </div>
        </div>
        <table class="data-table">
            <tr>
                <th>항목</th>
                <th>값</th>
            </tr>
            <tr>
                <td>토지 면적</td>
                <td>3,450 m²</td>
            </tr>
            <tr>
                <td>평당 단가</td>
                <td>5,500,000원</td>
            </tr>
            <tr>
                <td>총 감정가</td>
                <td>56억원</td>
            </tr>
        </table>
    </div>
    """
    
    # M3 - Housing Type (주택 유형)
    m3_html = """
    <div class="module-m3" data-module="M3">
        <h2>M3 - 주택 유형 적합도 분석</h2>
        <div class="kpi-summary">
            <div class="kpi-item" data-recommended-type="공공분양주택">
                <span class="label">추천 유형</span>
                <span class="value">공공분양주택</span>
            </div>
            <div class="kpi-item" data-total-score="87.5">
                <span class="label">적합도 점수</span>
                <span class="value">87.5점 (A등급)</span>
            </div>
        </div>
        <p>분석 결과: 해당 토지는 공공분양주택 개발에 최적화되어 있으며, 높은 적합도를 보입니다.</p>
    </div>
    """
    
    # M4 - Project Scale (사업 규모)
    m4_html = """
    <div class="module-m4" data-module="M4">
        <h2>M4 - 사업 규모 산정</h2>
        <div class="kpi-summary">
            <div class="kpi-item" data-total-units="450">
                <span class="label">총 세대수</span>
                <span class="value">450세대</span>
            </div>
            <div class="kpi-item" data-floor-area="36750.5">
                <span class="label">연면적</span>
                <span class="value">36,750.5 m²</span>
            </div>
        </div>
        <table>
            <tr>
                <td>건폐율</td>
                <td>45%</td>
            </tr>
            <tr>
                <td>용적률</td>
                <td>220%</td>
            </tr>
        </table>
    </div>
    """
    
    # M5 - Feasibility (사업성)
    m5_html = """
    <div class="module-m5" data-module="M5">
        <h2>M5 - 사업성 분석</h2>
        <div class="kpi-summary">
            <div class="kpi-item" data-npv="3250000000">
                <span class="label">순현재가치(NPV)</span>
                <span class="value">32억 5천만원</span>
            </div>
            <div class="kpi-item" data-irr="15.8">
                <span class="label">내부수익률(IRR)</span>
                <span class="value">15.8%</span>
            </div>
            <div class="kpi-item" data-is-profitable="true">
                <span class="label">수익성 판단</span>
                <span class="value">양호 (사업 추진 권장)</span>
            </div>
        </div>
        <p>분석 결과: 순현재가치(NPV) 32.5억원, 내부수익률(IRR) 15.8%로 사업성이 양호합니다.</p>
    </div>
    """
    
    # M6 - LH Review (LH 검토)
    m6_html = """
    <div class="module-m6" data-module="M6">
        <h2>M6 - LH 사전 검토</h2>
        <div class="kpi-summary">
            <div class="kpi-item" data-decision="조건부 승인" data-lh-decision="조건부 승인" data-risk-summary="중위험 - 조건 이행 시 사업 추진 가능">
                <span class="label">검토 결과</span>
                <span class="value">조건부 승인</span>
            </div>
            <div class="kpi-item" data-risk-level="medium" data-risk-summary="중위험 수준, 조건 이행 시 관리 가능">
                <span class="label">리스크 수준</span>
                <span class="value">중위험 (관리 가능)</span>
            </div>
        </div>
        <p>LH 검토 의견: 기본 요건 충족, 일부 보완 조건 이행 시 승인 가능</p>
        <ul>
            <li>조건 1: 교통영향평가 완료 필요</li>
            <li>조건 2: 지역주민 설명회 개최</li>
        </ul>
        <p class="risk-summary">전체 리스크 평가: 중위험 수준으로, 조건 이행 시 사업 추진 가능</p>
    </div>
    """
    
    return {
        "M2": m2_html,
        "M3": m3_html,
        "M4": m4_html,
        "M5": m5_html,
        "M6": m6_html
    }


def test_direct_import():
    """Direct import test without running full app"""
    print("\n" + "="*80)
    print("🧪 PHASE 3.10 - DIRECT IMPORT TEST")
    print("="*80 + "\n")
    
    try:
        # Import assemblers directly
        from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler
        from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler
        from app.services.final_report_assembly.assemblers.financial_feasibility import FinancialFeasibilityAssembler
        from app.services.final_report_assembly.assemblers.lh_technical import LHTechnicalAssembler
        from app.services.final_report_assembly.assemblers.all_in_one import AllInOneAssembler
        from app.services.final_report_assembly.assemblers.executive_summary import ExecutiveSummaryAssembler
        
        print("✅ All assemblers imported successfully!\n")
        
        # Create mock context
        context_id = "test-phase-3-10-complete"
        mock_modules = create_mock_module_html()
        
        print(f"📦 Mock Context ID: {context_id}")
        print(f"📄 Mock Modules: {', '.join(mock_modules.keys())}\n")
        
        # Test each assembler
        assemblers = [
            ("Landowner Summary", LandownerSummaryAssembler),
            ("Quick Check", QuickCheckAssembler),
            ("Financial Feasibility", FinancialFeasibilityAssembler),
            ("LH Technical", LHTechnicalAssembler),
            ("All-In-One", AllInOneAssembler),
            ("Executive Summary", ExecutiveSummaryAssembler)
        ]
        
        results = {}
        
        for name, AssemblerClass in assemblers:
            print(f"🔄 Testing: {name}")
            try:
                assembler = AssemblerClass(context_id)
                
                # Mock the load_module_html method (correct method name)
                def mock_load_module_html(module_key):
                    html = mock_modules.get(module_key, "<div>Module not found</div>")
                    # Cache it like the real implementation
                    assembler._module_html_cache[module_key] = html
                    return html
                
                assembler.load_module_html = mock_load_module_html
                
                # Assemble report
                html_output = assembler.assemble()
                
                # Check if HTML is valid
                if html_output and len(html_output) > 1000:
                    print(f"   ✅ SUCCESS - Generated {len(html_output):,} bytes")
                    
                    # Check for N/A
                    na_count = html_output.count("N/A")
                    print(f"   📊 N/A occurrences: {na_count}")
                    
                    # Check for KPI values
                    has_land_value = "56억" in html_output or "5,600,000,000" in html_output
                    has_npv = "32억" in html_output or "3,250,000,000" in html_output
                    has_decision = "조건부 승인" in html_output
                    
                    print(f"   🔍 KPI Detection:")
                    print(f"      - Land Value: {'✅' if has_land_value else '❌'}")
                    print(f"      - NPV: {'✅' if has_npv else '❌'}")
                    print(f"      - LH Decision: {'✅' if has_decision else '❌'}")
                    
                    results[name] = {
                        "status": "SUCCESS",
                        "size": len(html_output),
                        "na_count": na_count,
                        "kpi_detected": has_land_value or has_npv or has_decision
                    }
                else:
                    print(f"   ❌ FAILED - Output too small or empty")
                    results[name] = {
                        "status": "FAILED",
                        "size": len(html_output) if html_output else 0
                    }
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)[:200]}")
                results[name] = {
                    "status": "ERROR",
                    "error": str(e)[:200]
                }
            
            print()
        
        # Final Summary
        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80 + "\n")
        
        success_count = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
        total_count = len(results)
        
        print(f"✅ Success: {success_count}/{total_count}")
        print(f"❌ Failed: {total_count - success_count}/{total_count}\n")
        
        for name, result in results.items():
            print(f"  {name:30} | {result.get('status', 'UNKNOWN'):10} | "
                  f"Size: {result.get('size', 0):8,} bytes | "
                  f"N/A: {result.get('na_count', 0):3}")
        
        print("\n" + "="*80 + "\n")
        
        return results
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = test_direct_import()
    
    if results:
        success_count = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
        if success_count == len(results):
            print("🎉 ALL TESTS PASSED - Phase 3.10 COMPLETE!")
            sys.exit(0)
        else:
            print(f"⚠️  PARTIAL SUCCESS - {success_count}/{len(results)} reports generated")
            sys.exit(1)
    else:
        print("❌ TEST FAILED")
        sys.exit(1)
