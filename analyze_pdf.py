#!/usr/bin/env python3
"""Analyze uploaded PDF for issues"""
import PyPDF2
import sys

pdf_path = '/home/user/uploaded_files/감정평가보고서 (8).pdf'

print("=" * 80)
print("PDF Analysis Report")
print("=" * 80)

try:
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        print(f"\n📄 Basic Info:")
        print(f"   Total Pages: {len(reader.pages)}")
        
        if reader.metadata:
            print(f"\n📋 Metadata:")
            for key, value in reader.metadata.items():
                print(f"   {key}: {value}")
        
        # Check page sizes (A4 should be 595 x 842 points)
        print(f"\n📐 Page Sizes:")
        for i, page in enumerate(reader.pages[:5], 1):
            box = page.mediabox
            width = float(box.width)
            height = float(box.height)
            
            # Convert points to mm (1 point = 0.352778 mm)
            width_mm = width * 0.352778
            height_mm = height * 0.352778
            
            a4_check = "✅ A4" if abs(width_mm - 210) < 5 and abs(height_mm - 297) < 5 else "❌ NOT A4"
            
            print(f"   Page {i}: {width:.1f} x {height:.1f} pt ({width_mm:.1f} x {height_mm:.1f} mm) {a4_check}")
        
        # Extract text from key pages
        print(f"\n📝 Content Sample (Page 2 - Final Value):")
        if len(reader.pages) >= 2:
            text = reader.pages[1].extract_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()][:20]
            for line in lines:
                print(f"   {line}")
        
        print(f"\n📝 Content Sample (Page 8 - Transaction Cases):")
        if len(reader.pages) >= 8:
            text = reader.pages[7].extract_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()][:20]
            for line in lines:
                if '주소' in line or '거래' in line or '평당' in line:
                    print(f"   {line}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
