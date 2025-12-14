#!/usr/bin/env python3
"""PDF 품질 검증"""

import subprocess
import os
import glob

def validate_pdf(pdf_path):
    """PDF 검증"""
    
    print(f"\n📄 검증: {os.path.basename(pdf_path)}")
    print("-" * 60)
    
    if not os.path.exists(pdf_path):
        print("❌ 파일 없음")
        return False
    
    # 파일 크기
    size = os.path.getsize(pdf_path)
    print(f"크기: {size:,} bytes ({size/1024:.1f} KB)")
    
    if size < 10000:
        print("❌ 파일 크기가 너무 작음 (에러 응답일 수 있음)")
        # 내용 확인
        with open(pdf_path, 'r', errors='ignore') as f:
            content = f.read(200)
            if 'detail' in content or 'error' in content.lower():
                print(f"   에러 내용: {content}")
        return False
    
    # PDF 정보 (pdfinfo 사용)
    try:
        result = subprocess.run(
            ['pdfinfo', pdf_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            info = result.stdout
            
            # 페이지 수 추출
            for line in info.split('\n'):
                if 'Pages:' in line:
                    pages = int(line.split(':')[1].strip())
                    print(f"페이지: {pages}")
                    
                    if pages == 36:
                        print("✅ 36페이지 확인")
                    else:
                        print(f"⚠️  페이지 수 불일치 (예상: 36, 실제: {pages})")
                    
                if 'Page size:' in line:
                    print(f"페이지 크기: {line.split(':')[1].strip()}")
                    
                if 'PDF version:' in line:
                    print(f"PDF 버전: {line.split(':')[1].strip()}")
            
            print("✅ PDF 유효")
            return True
        else:
            print(f"❌ pdfinfo 실패: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  pdfinfo 없음 (설치 필요: apt-get install poppler-utils)")
        
        # 간단 검증
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if header.startswith(b'%PDF'):
                print("✅ PDF 헤더 확인")
                return True
            else:
                print("❌ 유효한 PDF 아님")
                return False
    
    except Exception as e:
        print(f"❌ 검증 오류: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔍 PDF 품질 검증")
    print("="*60)
    
    pdf_dir = 'pdf_tests'
    
    if not os.path.exists(pdf_dir):
        print(f"❌ 디렉토리 없음: {pdf_dir}")
        print("   먼저 test_pdf_generation.sh를 실행하세요.")
        exit(1)
    
    pdf_files = glob.glob(f"{pdf_dir}/*.pdf")
    
    if not pdf_files:
        print(f"❌ PDF 파일 없음")
        print("   먼저 test_pdf_generation.sh를 실행하세요.")
        exit(1)
    
    print(f"\n📁 {len(pdf_files)}개 PDF 파일 발견\n")
    
    results = []
    for pdf in pdf_files:
        valid = validate_pdf(pdf)
        results.append(valid)
    
    print("\n" + "="*60)
    print("📊 검증 결과")
    print("="*60)
    
    total = len(results)
    passed = sum(results)
    
    print(f"총 {total}개 중 {passed}개 통과 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 모든 PDF 검증 통과!")
        exit(0)
    else:
        print(f"\n⚠️  {total-passed}개 실패")
        exit(1)
