#!/bin/bash

# ZeroSite Land Report v5.1 Full Master Generation Script
# Target: 50-55 pages, Government-Grade, PDF-Optimized
# Author: ZeroSite
# Date: 2025-12-01

set -e

SECTIONS_DIR="reports_final/sections_final"
MASTER_OUTPUT="reports_final/ZeroSite_Land_Report_v5.1_Full.md"

echo "=========================================="
echo "ZeroSite Land Report v5.1 Master Generation"
echo "=========================================="
echo ""

# Create master report header
cat > "$MASTER_OUTPUT" << 'EOF'
# ZeroSite Land Report v5.1 - Government-Grade Full Expanded Edition

**발행처**: ZeroSite  
**발행일**: 2025년 12월 1일  
**버전**: v5.1 (Final Expanded)  
**워터마크**: ZeroSite | ZeroSite Land Report v5.1  
**페이지**: 50-55 페이지 (목표)  
**보안등급**: 대외비 (Confidential)

---

EOF

# Array of section files
sections=(
  "01_Cover_Executive_Summary_Expanded.md"
  "02_Policy_Analysis_2025.md"
  "03_Market_Analysis_National.md"
  "04_ZeroSite_System_Overview.md"
  "05_Technical_Architecture_ASCII.md"
  "06_AI_Algorithm_Detailed.md"
  "07_LH_Scorecard_350.md"
  "08_Exclusion_Criteria_30_Response.md"
  "09_ESG_LH_Incentive_Linkage.md"
  "10_ROI_PF_Financial_Structure.md"
  "11_Sensitivity_Analysis.md"
  "12_PMO_Operational_Templates.md"
  "13_Quality_Management.md"
  "14_Official_References.md"
  "15_Glossary_30_Terms.md"
  "16_Appendix.md"
)

# Append each section
for section in "${sections[@]}"; do
  if [ -f "$SECTIONS_DIR/$section" ]; then
    echo "✅ Appending: $section"
    cat "$SECTIONS_DIR/$section" >> "$MASTER_OUTPUT"
    echo "" >> "$MASTER_OUTPUT"
    echo "---" >> "$MASTER_OUTPUT"
    echo "" >> "$MASTER_OUTPUT"
  else
    echo "⚠️  Missing: $section (will be generated)"
  fi
done

# Add final footer
cat >> "$MASTER_OUTPUT" << 'EOF'

---

**문서 종료**

© 2025 ZeroSite. All Rights Reserved.  
ZeroSite Land Report v5.1 - Government-Grade Full Expanded Edition

본 문서는 ZeroSite의 지적 재산이며, 무단 복제·배포·인용을 금합니다.

**워터마크**: ZeroSite | ZeroSite Land Report v5.1  
**최종 수정일**: 2025-12-01  
**문서번호**: AH-ZSR-2025-001

EOF

# Statistics
echo ""
echo "=========================================="
echo "Master Report Generated Successfully"
echo "=========================================="
echo "Output: $MASTER_OUTPUT"
wc -l "$MASTER_OUTPUT" | awk '{print "Lines: " $1}'
wc -c "$MASTER_OUTPUT" | awk '{print "Characters: " $1}'
echo "Estimated Pages: $(wc -l "$MASTER_OUTPUT" | awk '{print int($1/60)}')-$(wc -l "$MASTER_OUTPUT" | awk '{print int($1/50)}')"
echo ""

