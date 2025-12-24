"""
디자인/폰트/색상 개선 분석 스크립트
Design/Font/Color Improvement Analysis
"""

import re
from pathlib import Path

def analyze_html_report(html_path):
    """HTML 보고서에서 디자인 요소 분석"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 폰트 분석
    fonts = set(re.findall(r"font-family:\s*([^;]+);", content))
    
    # 색상 분석 (hex, rgb, named colors)
    colors = set(re.findall(r"#[0-9A-Fa-f]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)", content))
    
    # 폰트 크기 분석
    font_sizes = set(re.findall(r"font-size:\s*([^;]+);", content))
    
    return {
        'fonts': list(fonts),
        'colors': list(colors),
        'font_sizes': list(font_sizes)
    }

def main():
    test_outputs = Path('/home/user/webapp/test_outputs')
    html_files = list(test_outputs.glob('*63d9e69f.html'))
    
    print("=" * 80)
    print("📊 디자인/폰트/색상 분석 리포트")
    print("=" * 80)
    
    all_fonts = set()
    all_colors = set()
    all_sizes = set()
    
    for html_file in html_files[:3]:  # 첫 3개 파일만 분석
        print(f"\n📄 {html_file.name}")
        analysis = analyze_html_report(html_file)
        
        all_fonts.update(analysis['fonts'])
        all_colors.update(analysis['colors'])
        all_sizes.update(analysis['font_sizes'])
        
        print(f"  폰트: {len(analysis['fonts'])}종")
        print(f"  색상: {len(analysis['colors'])}개")
        print(f"  크기: {len(analysis['font_sizes'])}종")
    
    print("\n" + "=" * 80)
    print("📝 통합 분석 결과")
    print("=" * 80)
    
    print(f"\n폰트 종류 ({len(all_fonts)}종):")
    for font in sorted(all_fonts)[:10]:
        print(f"  - {font}")
    
    print(f"\n주요 색상 ({len(all_colors)}개):")
    for color in sorted(all_colors)[:15]:
        print(f"  - {color}")
    
    print(f"\n폰트 크기 ({len(all_sizes)}종):")
    for size in sorted(all_sizes)[:10]:
        print(f"  - {size}")

if __name__ == "__main__":
    main()
