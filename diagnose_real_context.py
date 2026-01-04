"""
실제 보고서 생성에 사용된 context_id의 구조 진단
목표: 왜 M2가 N/A로 나오는지 정확한 원인 파악
"""
import sys
sys.path.insert(0, "/home/user/webapp")

from app.services.context_storage import get_frozen_context
import json

# PDF에 출력된 context_id를 사용 (임의 ID로 테스트)
# 실제 PDF의 context_id가 있다면 여기에 입력
test_context_ids = [
    "test-001",  # 예시
]

print("=" * 80)
print("실제 Frozen Context 구조 진단")
print("=" * 80)

# 먼저 Redis/DB에 저장된 실제 context 확인
from app.services.context_storage import ContextStorageService
storage = ContextStorageService()

print("\n[Step 1] Redis에서 context 목록 확인...")
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    keys = r.keys("context:*")
    if keys:
        print(f"✅ Redis에서 {len(keys)}개 context 발견:")
        for key in keys[:5]:  # 첫 5개만
            print(f"   - {key}")
        
        # 첫 번째 context 분석
        if keys:
            first_key = keys[0]
            context_id = first_key.replace("context:", "")
            print(f"\n[Step 2] 첫 번째 context 분석: {context_id}")
            
            context_data = get_frozen_context(context_id)
            if context_data:
                print(f"✅ Context 로딩 성공")
                print(f"\n📊 최상위 키 목록:")
                for key in sorted(context_data.keys()):
                    print(f"   - {key}")
                
                # M2 구조 상세 분석
                print(f"\n🔍 M2 구조 상세 분석:")
                
                # 1. m2_result 확인
                if "m2_result" in context_data:
                    m2 = context_data["m2_result"]
                    print(f"   ✅ m2_result 존재")
                    print(f"      - Type: {type(m2)}")
                    if isinstance(m2, dict):
                        print(f"      - Keys: {list(m2.keys())}")
                        
                        # summary 확인
                        if "summary" in m2:
                            summary = m2["summary"]
                            print(f"      - summary Keys: {list(summary.keys())}")
                            
                            # land_value 후보 탐색
                            land_value_keys = [k for k in summary.keys() if "land" in k.lower() or "value" in k.lower()]
                            print(f"      - Land value 후보 키: {land_value_keys}")
                            
                            if land_value_keys:
                                for k in land_value_keys:
                                    print(f"         · {k} = {summary[k]}")
                        
                        # appraisal 확인
                        if "appraisal" in m2:
                            appraisal = m2["appraisal"]
                            print(f"      - appraisal Keys: {list(appraisal.keys())}")
                            
                            land_value_keys = [k for k in appraisal.keys() if "land" in k.lower() or "value" in k.lower()]
                            if land_value_keys:
                                print(f"      - Land value 후보 키: {land_value_keys}")
                                for k in land_value_keys:
                                    print(f"         · {k} = {appraisal[k]}")
                else:
                    # 최상위 appraisal 확인
                    if "appraisal" in context_data:
                        print(f"   ℹ️  m2_result 없음, 최상위 appraisal 존재")
                        appraisal = context_data["appraisal"]
                        print(f"      - Type: {type(appraisal)}")
                        if isinstance(appraisal, dict):
                            print(f"      - Keys: {list(appraisal.keys())}")
                    else:
                        print(f"   ❌ m2_result도 appraisal도 없음!")
                
                # M3-M6 간단 확인
                print(f"\n📊 M3-M6 구조:")
                for m in ["m3_result", "m4_result", "m5_result", "m6_result"]:
                    if m in context_data:
                        data = context_data[m]
                        if isinstance(data, dict):
                            print(f"   ✅ {m}: {list(data.keys())[:5]}...")
                        else:
                            print(f"   ✅ {m}: Type={type(data)}")
                    else:
                        print(f"   ❌ {m}: 없음")
                
                # 전체 구조 샘플 저장
                print(f"\n💾 전체 구조를 context_structure_sample.json에 저장...")
                with open("/home/user/webapp/context_structure_sample.json", "w", encoding="utf-8") as f:
                    json.dump(context_data, f, indent=2, ensure_ascii=False, default=str)
                print(f"   ✅ 저장 완료")
            else:
                print(f"❌ Context 로딩 실패")
    else:
        print("❌ Redis에 context가 없습니다")
        print("\n💡 실제 보고서 생성 후 다시 실행하세요")
        
except Exception as e:
    print(f"❌ Redis 연결 실패: {e}")
    print("\n💡 대안: 실제 PDF의 context_id를 제공하면 DB에서 확인 가능")

print("\n" + "=" * 80)
