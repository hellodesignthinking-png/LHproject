#!/bin/bash

# PDF 생성 종합 테스트

echo "📄 PDF 생성 테스트"
echo "=================="
echo ""

BASE_URL="http://localhost:8000"
OUTPUT_DIR="pdf_tests"

mkdir -p "$OUTPUT_DIR"

# 테스트 케이스
test_pdf() {
    local name=$1
    local address=$2
    local area=$3
    
    echo "🧪 테스트: $name"
    echo "   주소: $address"
    
    output_file="$OUTPUT_DIR/${name// /_}.pdf"
    
    curl -s -X POST "$BASE_URL/api/v24.1/appraisal/pdf" \
        -H "Content-Type: application/json" \
        -d "{\"address\":\"$address\",\"land_area_sqm\":$area}" \
        -o "$output_file"
    
    if [ -f "$output_file" ]; then
        size=$(stat -c%s "$output_file" 2>/dev/null || stat -f%z "$output_file" 2>/dev/null)
        
        if [ "$size" -gt 10000 ]; then
            # PDF 정보 확인
            pages=$(pdfinfo "$output_file" 2>/dev/null | grep "Pages:" | awk '{print $2}')
            
            echo "   ✅ 생성 성공"
            echo "   크기: $((size / 1024))KB"
            
            if [ -n "$pages" ]; then
                echo "   페이지: $pages"
                
                # 36페이지 확인
                if [ "$pages" = "36" ]; then
                    echo "   ✅ 36페이지 확인"
                else
                    echo "   ⚠️  페이지 수: $pages (예상: 36)"
                fi
            else
                echo "   페이지: ? (pdfinfo 없음)"
            fi
        else
            echo "   ❌ 파일 크기 이상 (${size}B)"
            cat "$output_file" | head -5
        fi
    else
        echo "   ❌ 생성 실패"
    fi
    
    echo ""
}

# 테스트 실행
test_pdf "서울_강남" "서울 강남구 역삼동 680-11" 400
test_pdf "서울_관악" "서울 관악구 신림동 1524-8" 435
test_pdf "부산_해운대" "부산 해운대구 우동 1234" 500
test_pdf "경기_성남" "경기도 성남시 분당구 정자동 600" 350
test_pdf "제주_제주" "제주특별자치도 제주시 연동 1400" 450

echo "=================="
echo "✅ 테스트 완료"
echo ""
echo "생성된 PDF:"
ls -lh "$OUTPUT_DIR"
