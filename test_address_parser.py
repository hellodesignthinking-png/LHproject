#!/usr/bin/env python3
"""
Test Advanced Address Parser
주소 파싱 테스트
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.advanced_address_parser import get_address_parser

print("=" * 100)
print("🧪 Advanced Address Parser Test")
print("=" * 100)

parser = get_address_parser()

test_cases = [
    "서울 마포구 월드컵북로 120",
    "월드컵북로 120",
    "서울시 마포구 상암동 123-4",
    "서울 강남구 테헤란로 427",
    "테헤란로 152",
    "서울시 강남구 역삼동 742-31",
    "서울 서초구 서초대로 78길 22",
    "송파구 잠실동 10-1",
    "여의도동 24",
    "서울시 용산구 이태원로 27길 44"
]

for address in test_cases:
    print(f"\n{'='*100}")
    print(f"📍 입력: {address}")
    print('='*100)
    
    result = parser.parse(address)
    
    print(f"✅ 결과:")
    print(f"   구: {result['gu']}")
    print(f"   동: {result['dong']}")
    print(f"   도로명: {result['road_name']}")
    print(f"   성공: {result['success']}")
    print(f"   방법: {result['method']}")
    
    if result['success']:
        sigungu_code = parser.get_sigungu_code(result['gu'])
        print(f"   시군구코드: {sigungu_code}")

print("\n" + "=" * 100)
print("🎉 Test Complete!")
print("=" * 100)
