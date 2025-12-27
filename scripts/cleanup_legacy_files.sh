#!/bin/bash
# ZeroSite 4.0 Legacy Files Cleanup
# Phase 3+ - Remove unused legacy report generators

echo "🧹 Cleaning up legacy files..."

# Legacy report generators (v7, v8, v10, v11, etc.)
LEGACY_FILES=(
    "app/lh_decision_engine_v11.py"
    "app/lh_score_mapper_v11.py"
    "app/report_generator_v10_ultra_pro.py"
    "app/services/lh_report_generator_v7_2_extended.py"
    "app/services/lh_report_generator_v7_5_final.py"
    "app/services/narrative_templates_v7_3.py"
    "app/services/report_generator_v8_8.py"
    "app/services_v13/report_full/v21_narrative_engine_pro.py"
    "app/services_v13/report_full/v21_narrative_generator.py"
)

# Backup before removal
BACKUP_DIR="backup_legacy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  🗑️  Removing: $file"
        cp "$file" "$BACKUP_DIR/"
        git rm "$file" 2>/dev/null || rm "$file"
    else
        echo "  ⏭️  Not found: $file (already removed?)"
    fi
done

echo ""
echo "✅ Legacy cleanup complete"
echo "   Backup saved to: $BACKUP_DIR"
