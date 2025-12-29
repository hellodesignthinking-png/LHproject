#!/bin/bash
# Add user guarantee footer to M3/M4/M5 templates

for file in app/templates_v13/m3_supply_type_format.html \
            app/templates_v13/m4_building_scale_format.html \
            app/templates_v13/m5_feasibility_format.html; do
    
    echo "Processing $file..."
    
    # Find the last </div> before </body>
    # Insert footer before that closing div
    sed -i '/<\/body>/i\        <!-- 🔒 USER GUARANTEE FOOTER -->\n        {% include '"'"'_user_guarantee_footer.html'"'"' %}' "$file"
    
    echo "✅ Footer added to $file"
done

echo ""
echo "🎉 All templates updated!"
