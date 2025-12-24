#!/usr/bin/env python3
"""
CRITICAL FIX: Block Legacy Final Report Route
==============================================

Problem: Frontend calls /api/v4/reports/final/... which is intercepted by
         the LEGACY router (pdf_download_standardized.py), NOT the new
         vABSOLUTE-FINAL-11/12/13 Phase 3 router (final_report_api.py).

Solution: Replace the legacy /final route handler to REJECT requests
          and instruct callers to use the correct new route.

Expected Behavior AFTER Fix:
- /api/v4/reports/final/... → HTTP 410 (Gone) with migration instructions
- /api/v4/final-report/... → NEW Phase 3 assemblers (vABSOLUTE-FINAL-13)

Date: 2025-12-24
Tag: vABSOLUTE-FINAL-14
"""

import re

def main():
    filepath = "app/routers/pdf_download_standardized.py"
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    with open(f"{filepath}.backup_legacy", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Backup created: {filepath}.backup_legacy")
    
    # STEP 1: Find and replace the /final/{report_type}/html endpoint
    # We'll replace the entire function body to return 410 Gone
    
    old_html_endpoint = r'''@router\.get\("/final/\{report_type\}/html", response_class=HTMLResponse\)
async def get_final_report_html\(
    report_type: str,
    context_id: str = Query\(\.\.\., description="분석 컨텍스트 ID"\)
\):
    """
    최종보고서 6종 HTML 미리보기
    
    Args:
        report_type: 최종보고서 타입 \(all_in_one, landowner_summary, etc\.\)
        context_id: 분석 컨텍스트 ID
        
    Returns:
        HTML 보고서
        
    Examples:
        GET /api/v4/reports/final/all_in_one/html\?context_id=test-001
    """
    try:
        # 보고서 타입 검증
        try:
            final_report_type = FinalReportType\(report_type\)
        except ValueError:
            raise HTTPException\(
                status_code=400,
                detail=f"Invalid report type: \{report_type\}\. Allowed: \{\[t\.value for t in FinalReportType\]\}"
            \)
        
        # ✅ STEP 1: context_id로 실제 저장된 컨텍스트 조회 \(Redis/DB\)
        frozen_context = context_storage\.get_frozen_context\(context_id\)
        
        if not frozen_context:
            raise HTTPException\(
                status_code=404,
                detail=\(
                    f"❌ 분석 데이터를 찾을 수 없습니다\.\\n\\n"
                    f"Context ID: \{context_id\}\\n\\n"
                    f"💡 해결 방법:\\n"
                    f"1\. M1 분석을 먼저 완료하세요\.\\n"
                    f"2\. '분석 시작' 버튼을 눌러 context를 저장하세요\.\\n"
                    f"3\. 분석 완료 후 최종보고서를 생성하세요\."
                \)
            \)
        
        # ✅ STEP 4: 최종보고서 데이터 조립 \(NEW: 통합 assembler 사용\)
        from app\.services\.final_report_assembler import assemble_final_report as assemble_report_data
        
        assembled_data = assemble_report_data\(
            report_type=final_report_type\.value,
            canonical_data=frozen_context,
            context_id=context_id
        \)
        
        # ✅ STEP 5: HTML 렌더링 \(NEW: 통합 renderer 사용\)
        from app\.services\.final_report_html_renderer import render_final_report_html
        
        html = render_final_report_html\(
            report_type=final_report_type\.value,
            data=assembled_data
        \)
        
        return HTMLResponse\(content=html\)
        
    except HTTPException:
        raise
    except Exception as e:
        logger\.error\(f"Failed to generate final report HTML: \{e\}"\)
        raise HTTPException\(status_code=500, detail=f"Failed to generate HTML: \{str\(e\)\}"\)'''
    
    new_html_endpoint = '''@router.get("/final/{report_type}/html", response_class=HTMLResponse)
async def get_final_report_html(
    report_type: str,
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    [vABSOLUTE-FINAL-14] LEGACY ROUTE BLOCKED
    ==========================================
    
    This endpoint has been DEPRECATED and replaced by the new Phase 3 API.
    
    ❌ OLD (DO NOT USE): /api/v4/reports/final/{report_type}/html
    ✅ NEW (USE THIS):   /api/v4/final-report/{report_type}/html
    
    Reason for deprecation:
    - This route uses OLD assemblers (final_report_assembler.py)
    - Does NOT include vABSOLUTE-FINAL-11/12/13 fixes
    - Does NOT use modules_data-based narratives
    - Does NOT include BUILD_SIGNATURE/DATA_SIGNATURE
    
    Migration Guide:
    1. Update frontend to call: /api/v4/final-report/{report_type}/html
    2. Same parameters (report_type, context_id)
    3. New route includes all Phase 3 fixes
    
    Examples:
        OLD: GET /api/v4/reports/final/all_in_one/html?context_id=test-001
        NEW: GET /api/v4/final-report/all_in_one/html?context_id=test-001
    """
    raise HTTPException(
        status_code=410,  # 410 Gone - permanently removed
        detail={
            "error": "LEGACY_ROUTE_BLOCKED",
            "message": "This endpoint has been deprecated. Please use /api/v4/final-report/{report_type}/html instead.",
            "old_path": f"/api/v4/reports/final/{report_type}/html",
            "new_path": f"/api/v4/final-report/{report_type}/html",
            "context_id": context_id,
            "migration_reason": "Phase 3 assemblers with vABSOLUTE-FINAL-11/12/13 fixes",
            "documentation": "See VABSOLUTE_FINAL_14_ROUTING_FIX.md"
        }
    )'''
    
    # Check if the pattern exists
    if re.search(old_html_endpoint, content, re.DOTALL):
        content = re.sub(old_html_endpoint, new_html_endpoint, content, flags=re.DOTALL)
        print("✅ Replaced /final/{report_type}/html endpoint with 410 Gone handler")
    else:
        print("⚠️  Could not find exact pattern for /final/{report_type}/html")
        print("    Will use simpler replacement strategy...")
        
        # Simpler strategy: Find the function and replace just the body
        pattern = r'(@router\.get\("/final/\{report_type\}/html", response_class=HTMLResponse\)\s+async def get_final_report_html\([^)]+\):\s+"""[^"]*"""\s+)try:.*?(?=\n\n\ndef |\nclass |\n@router\.)'
        
        replacement = r'''\1"""
    [vABSOLUTE-FINAL-14] LEGACY ROUTE BLOCKED
    ==========================================
    
    This endpoint has been DEPRECATED and replaced by the new Phase 3 API.
    
    ❌ OLD (DO NOT USE): /api/v4/reports/final/{report_type}/html
    ✅ NEW (USE THIS):   /api/v4/final-report/{report_type}/html
    """
    raise HTTPException(
        status_code=410,
        detail={
            "error": "LEGACY_ROUTE_BLOCKED",
            "message": "This endpoint has been deprecated. Use /api/v4/final-report/ instead.",
            "old_path": f"/api/v4/reports/final/{report_type}/html",
            "new_path": f"/api/v4/final-report/{report_type}/html",
            "context_id": context_id,
            "version": "vABSOLUTE-FINAL-14"
        }
    )


'''
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            print("✅ Applied simpler replacement for HTML endpoint")
        else:
            print("❌ Could not find HTML endpoint to replace!")
            return
    
    # STEP 2: Block /final/{report_type}/pdf endpoint if it exists
    pdf_pattern = r'@router\.get\("/final/\{report_type\}/pdf"[^)]*\)\s+async def get_final_report_pdf\([^)]+\):.*?(?=\n\n\ndef |\nclass |\n@router\.)'
    
    if re.search(pdf_pattern, content, re.DOTALL):
        pdf_replacement = '''@router.get("/final/{report_type}/pdf")
async def get_final_report_pdf(
    report_type: str,
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    [vABSOLUTE-FINAL-14] LEGACY ROUTE BLOCKED - PDF
    
    ❌ OLD: /api/v4/reports/final/{report_type}/pdf
    ✅ NEW: /api/v4/final-report/{report_type}/pdf
    """
    raise HTTPException(
        status_code=410,
        detail={
            "error": "LEGACY_ROUTE_BLOCKED",
            "message": "This PDF endpoint has been deprecated. Use /api/v4/final-report/ instead.",
            "old_path": f"/api/v4/reports/final/{report_type}/pdf",
            "new_path": f"/api/v4/final-report/{report_type}/pdf",
            "context_id": context_id,
            "version": "vABSOLUTE-FINAL-14"
        }
    )


'''
        content = re.sub(pdf_pattern, pdf_replacement, content, flags=re.DOTALL)
        print("✅ Replaced /final/{report_type}/pdf endpoint with 410 Gone handler")
    
    # Write the modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ LEGACY ROUTE BLOCKED: {filepath}")
    print("\nNext Steps:")
    print("1. Backend will auto-reload with blocked legacy routes")
    print("2. Frontend must be updated to call /api/v4/final-report/... instead")
    print("3. Any calls to old route will get HTTP 410 with migration instructions")
    print("\n🔥 THIS ENFORCES USE OF vABSOLUTE-FINAL-11/12/13 CODE!")

if __name__ == "__main__":
    main()
