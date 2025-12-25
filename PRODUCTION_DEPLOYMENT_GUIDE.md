# 🚀 ZeroSite v4.0 – 프로덕션 배포 가이드

**버전**: v4.0 (Phase 1+2+2.5 Complete)  
**배포일**: 2025-12-25  
**담당**: ZeroSite Backend Team  

---

## 📋 **배포 체크리스트**

### ✅ **사전 완료 항목**
- [x] PR #11 merged to main (commit: 2743862)
- [x] 모든 테스트 통과
- [x] Phase 1+2+2.5 기능 완성
- [x] 문서화 완료
- [x] 코드 리뷰 완료

### ⏳ **진행 중 항목**
- [ ] 프로덕션 서버 배포
- [ ] 실제 Context ID 테스트
- [ ] 모니터링 시스템 가동
- [ ] LH 검토자 피드백 수집

---

## 🔧 **1. 프로덕션 서버 배포**

### **Step 1: 코드 배포**

#### **Option A: Git Pull (권장)**
```bash
# 프로덕션 서버에 SSH 접속
ssh user@production-server

# 프로젝트 디렉토리로 이동
cd /path/to/webapp

# 최신 코드 가져오기
git fetch origin main
git checkout main
git pull origin main

# 배포 확인
git log --oneline -3
# 예상 출력:
# 4887650 docs: Production deployment ready...
# 2743862 Merge PR #11: ZeroSite v4.0 Final Reports...
# 403bf2b docs(phase2.5): Phase 2.5 Editorial Polish...
```

#### **Option B: Direct File Transfer**
```bash
# 로컬에서 핵심 파일만 전송
scp app/services/final_report_assembler.py user@production:/path/to/webapp/app/services/
scp app/services/final_report_html_renderer.py user@production:/path/to/webapp/app/services/
```

### **Step 2: 종속성 확인**

```bash
# Python 패키지 확인
pip list | grep -E "pydantic|redis"

# 필요시 설치
pip install pydantic==2.11.0
pip install redis

# 버전 확인
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import redis; print(f'Redis: {redis.__version__}')"
```

### **Step 3: Redis 확인**

```bash
# Redis 실행 확인
redis-cli ping
# 예상 출력: PONG

# Redis 정보 확인
redis-cli INFO | head -20

# Redis 연결 테스트
python -c "from app.services.context_storage import redis_client; print(redis_client.ping())"
# 예상 출력: True
```

### **Step 4: 애플리케이션 재시작**

```bash
# 현재 실행 중인 프로세스 확인
ps aux | grep "python.*app"

# 애플리케이션 재시작 (방법은 환경에 따라 다름)

# Option A: systemd
sudo systemctl restart zerosite

# Option B: supervisor
supervisorctl restart zerosite

# Option C: PM2
pm2 restart zerosite

# Option D: 수동
kill <PID>
python main.py &

# 재시작 확인
tail -f /path/to/logs/application.log
```

---

## 🧪 **2. 실제 Context ID로 테스트**

### **Step 1: Context ID 확인**

```bash
# Redis에서 사용 가능한 Context ID 확인
redis-cli KEYS "context:*" | head -10

# 또는 Python으로
python -c "
from app.services.context_storage import redis_client
keys = redis_client.keys('context:*')
print(f'Total contexts: {len(keys)}')
print(f'Sample IDs: {[k.decode().split(\":\")[1] for k in keys[:5]]}')
"
```

### **Step 2: 테스트 스크립트 실행**

```bash
# 실제 Context ID로 테스트
python production_test_with_real_context.py <context_id>

# 예시:
python production_test_with_real_context.py 01234567-89ab-cdef-0123-456789abcdef
```

**예상 출력:**
```
================================================================================
🧪 PRODUCTION TEST: Context ID = 01234567-89ab-cdef-0123-456789abcdef
================================================================================

📦 Step 1: Loading frozen context...
✅ Success: Frozen context loaded
   Keys: ['m2_result', 'm3_result', 'm4_result', 'm5_result', 'm6_result', ...]

   Module Presence:
   - M2 (토지감정): ✓
   - M3 (주택유형): ✓
   - M4 (용적률/세대수): ✓
   - M5 (사업성): ✓
   - M6 (LH 검토): ✓

================================================================================
📊 Step 2: Generating 6 report types...
================================================================================

🔄 Generating Quick Check Report...
✅ Success: Quick Check Report
   HTML size: 12,125 characters
   N/A occurrences: 0
   N/A (검증 필요): 0
   KPI presence: 6/6
      - 토지감정가: ✓
      - NPV: ✓
      - IRR: ✓
      - 세대수: ✓
      - 주택유형: ✓
      - LH 판단: ✓

[... 5개 추가 보고서 ...]

================================================================================
📋 PRODUCTION TEST SUMMARY
================================================================================

Context ID: 01234567-89ab-cdef-0123-456789abcdef
Frozen Context: ✓ Loaded

Report Generation:
  ✅ Successful: 6/6
  ❌ Failed: 0/6

✅ Successful Reports:
   - quick_check: 12,125 chars, KPI: 6/6
   - financial_feasibility: 13,700 chars, KPI: 6/6
   - lh_technical: 21,107 chars, KPI: 6/6
   - executive_summary: 14,669 chars, KPI: 6/6
   - landowner_summary: 23,755 chars, KPI: 6/6
   - all_in_one: 39,888 chars, KPI: 6/6

================================================================================
✅ PRODUCTION TEST PASSED: All 6 reports generated successfully
================================================================================
```

### **Step 3: 다중 Context 테스트**

```bash
# 여러 Context ID로 배치 테스트
cat > batch_test.sh << 'EOF'
#!/bin/bash
CONTEXT_IDS=(
    "context-id-1"
    "context-id-2"
    "context-id-3"
    "context-id-4"
    "context-id-5"
)

for cid in "${CONTEXT_IDS[@]}"; do
    echo "Testing: $cid"
    python production_test_with_real_context.py "$cid"
    echo "---"
done
EOF

chmod +x batch_test.sh
./batch_test.sh
```

---

## 📊 **3. 보고서 생성 모니터링**

### **Step 1: 모니터링 시스템 시작**

```python
# monitoring_service.py 생성
from production_monitoring import ProductionMonitor
import time

monitor = ProductionMonitor()

# 실제 보고서 생성 후 기록
# (이 코드는 실제 보고서 생성 엔드포인트에 통합)

def generate_and_monitor(report_type, context_id):
    start = time.time()
    try:
        # 보고서 생성 로직
        assembled = assemble_final_report(report_type, frozen_context, context_id)
        html = render_final_report_html(report_type, assembled)
        
        duration_ms = (time.time() - start) * 1000
        
        monitor.record_generation(
            report_type=report_type,
            context_id=context_id,
            success=True,
            duration_ms=duration_ms,
            html_size=len(html),
            na_count=html.count('N/A'),
            kpi_present=6  # 실제 KPI 체크 로직
        )
        
        return html
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        
        monitor.record_generation(
            report_type=report_type,
            context_id=context_id,
            success=False,
            duration_ms=duration_ms,
            error=str(e)
        )
        
        raise

# 주기적으로 대시보드 출력
while True:
    monitor.print_dashboard()
    monitor.save_report("production_monitoring_report.txt")
    time.sleep(3600)  # 1시간마다
```

### **Step 2: 실시간 모니터링 확인**

```bash
# 실시간 모니터링 로그 확인
tail -f production_monitoring_report.txt

# 또는 주기적 출력
watch -n 60 cat production_monitoring_report.txt
```

---

## 📝 **4. LH 검토자 피드백 수집**

### **Step 1: 피드백 템플릿 배포**

```bash
# LH 검토자에게 피드백 템플릿 전달
# 파일: LH_REVIEWER_FEEDBACK_TEMPLATE.md

# 방법 1: 이메일 첨부
# 방법 2: 내부 문서 시스템 업로드
# 방법 3: GitHub Issues 링크 제공
```

### **Step 2: 샘플 보고서 생성 및 전달**

```bash
# 대표적인 Context ID로 all_in_one 보고서 생성
python production_test_with_real_context.py <representative_context_id>

# HTML을 PDF로 변환 (선택)
wkhtmltopdf report.html report.pdf

# 검토자에게 전달:
# 1. HTML 파일
# 2. PDF 파일 (선택)
# 3. 피드백 템플릿
```

### **Step 3: 피드백 수집 및 분석**

```bash
# 피드백 파일 수집
mkdir -p feedback_collected
mv LH_Feedback_*.md feedback_collected/

# 피드백 요약 생성
python analyze_feedback.py feedback_collected/
```

---

## 🎯 **성공 기준**

### **배포 성공 기준**
- [x] 코드가 프로덕션 서버에 정상 배포됨
- [ ] 애플리케이션이 정상 실행됨
- [ ] Redis 연결이 정상 작동함
- [ ] 로그에 에러가 없음

### **테스트 성공 기준**
- [ ] 실제 Context ID로 6종 보고서 모두 생성 성공
- [ ] 6대 핵심 KPI 모두 표시됨
- [ ] 의사결정 필드에 N/A 없음
- [ ] HTML 크기가 예상 범위 내 (quick_check: 12k, all_in_one: 39k)

### **모니터링 성공 기준**
- [ ] 보고서 생성 성공률 ≥ 95%
- [ ] 평균 KPI 표시 ≥ 5.5/6
- [ ] 평균 N/A 발생 ≤ 2건
- [ ] 평균 생성 시간 ≤ 2초

### **피드백 수집 성공 기준**
- [ ] LH 검토자 피드백 ≥ 3명
- [ ] 평균 점수 ≥ 4.0/5.0
- [ ] "즉시 제출 가능" 또는 "소폭 수정 후 제출" 의견
- [ ] 치명적 이슈 0건

---

## 🚨 **문제 해결**

### **Issue 1: Context ID를 찾을 수 없음**
```bash
# 증상: "Context ID not found in storage"

# 확인:
redis-cli EXISTS context:<context_id>

# 해결:
# 1. Context ID 철자 확인
# 2. Redis 데이터 확인
# 3. 필요시 mock data 재생성
```

### **Issue 2: Redis 연결 실패**
```bash
# 증상: "Redis connection failed"

# 확인:
redis-cli ping

# 해결:
# 1. Redis 실행 확인: sudo systemctl status redis
# 2. Redis 재시작: sudo systemctl restart redis
# 3. 설정 확인: cat /etc/redis/redis.conf
```

### **Issue 3: 보고서 생성 실패**
```bash
# 증상: "Assembly returned None" 또는 "Rendering returned None"

# 확인:
python -c "
from app.services.final_report_assembler import assemble_final_report
from app.services.context_storage import get_frozen_context

context_id = '<your_context_id>'
frozen = get_frozen_context(context_id)
print('Frozen context keys:', list(frozen.keys()))

result = assemble_final_report('quick_check', frozen, context_id)
print('Assembly result:', type(result))
"

# 해결:
# 1. 로그 확인: tail -f /path/to/logs/application.log
# 2. 데이터 구조 확인
# 3. 필요시 코드 디버깅
```

### **Issue 4: KPI 누락**
```bash
# 증상: KPI present < 6

# 확인:
# HTML에서 누락된 KPI 검색
grep -i "토지감정가\|NPV\|IRR\|세대수\|주택유형\|LH" report.html

# 해결:
# 1. frozen_context에 해당 모듈 데이터 존재 확인
# 2. 파싱 로직 확인
# 3. 필요시 defensive rendering 추가
```

---

## 📞 **지원 연락처**

**기술 지원**:
- Backend Team: backend@zerosite.com
- DevOps Team: devops@zerosite.com

**긴급 연락**:
- 24/7 On-call: +82-10-XXXX-XXXX

**문서 및 리소스**:
- GitHub: https://github.com/hellodesignthinking-png/LHproject
- Wiki: [내부 위키 링크]
- Slack: #zerosite-production

---

## 📅 **배포 일정**

| 단계 | 예상 시간 | 담당자 | 상태 |
|------|-----------|--------|------|
| 1. 코드 배포 | 30분 | DevOps | ✅ |
| 2. Context ID 테스트 | 1시간 | Backend | ⏳ |
| 3. 모니터링 설정 | 30분 | Backend | ⏳ |
| 4. 샘플 보고서 생성 | 1시간 | Backend | ⏳ |
| 5. LH 검토자 전달 | 1일 | PM | 📅 |
| 6. 피드백 수집 | 3-5일 | PM | 📅 |
| 7. 최종 검증 | 1일 | All | 📅 |

**총 예상 시간**: 5-7일 (피드백 수집 포함)

---

## ✅ **배포 완료 체크**

배포 완료 후 아래 항목을 확인하세요:

```bash
# 체크리스트
□ 코드가 프로덕션 서버에 배포됨
□ 애플리케이션이 정상 실행됨
□ Redis 연결 정상
□ 실제 Context ID로 테스트 완료
□ 6종 보고서 모두 생성 성공
□ 모니터링 시스템 가동
□ 샘플 보고서 LH 검토자에게 전달
□ 피드백 템플릿 배포
□ 문서화 완료
□ 팀 공유 완료
```

**모든 항목 완료 시: 🎉 배포 완료!**

---

**🚀 ZeroSite v4.0 – 프로덕션 배포 성공을 기원합니다! 🚀**
