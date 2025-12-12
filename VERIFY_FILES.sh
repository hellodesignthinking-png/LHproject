#!/bin/bash
echo "================================"
echo "File Verification Script"
echo "================================"
echo ""

echo "1. Backend Engine Files:"
ls -lh /home/user/webapp/backend/services_v9/*.py 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "2. Test File:"
ls -lh /home/user/webapp/tests/test_v32_complete.py 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "3. HTML Template:"
ls -lh /home/user/webapp/app/services_v13/report_full/section_03_1*.html 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "4. Sample Report:"
ls -lh /home/user/webapp/test_expert_v3_2_output.html 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "5. Run Test:"
echo "  Running tests..."
cd /home/user/webapp && python3 tests/test_v32_complete.py 2>&1 | grep -A 5 "TEST SUMMARY"

echo ""
echo "================================"
echo "Verification Complete"
echo "================================"
