# 향후 개선 계획 - Phase 7+

## 📋 개요

Phase 6 완료 후 추가 개선 사항들을 정리합니다. 각 개선 사항은 독립적으로 구현 가능하며, 우선순위에 따라 순차적으로 진행할 수 있습니다.

**작성일**: 2026-01-10  
**상태**: 계획 단계

---

## 🎯 개선 항목

### 1. Frontend 피드백 수집 UI

**목표**: 입주자가 직접 피드백을 제출할 수 있는 UI 구현

#### 1.1 피드백 수집 폼

**위치**: `/feedback-form`

**기능**:
```typescript
// 공간별 만족도 슬라이더
<SpaceSatisfactionSlider
  spaceName="커뮤니티 라운지"
  minScore={0}
  maxScore={100}
  onChange={(score) => handleSpaceScore(score)}
/>

// 프로그램 참여 체크리스트
<ProgramParticipation
  programs={['취업 세미나', '네트워킹', '육아 교류회']}
  onSelect={(programs) => handleProgramSelection(programs)}
/>

// 자유 의견 입력
<FeedbackTextArea
  placeholder="개선이 필요한 점이나 좋았던 점을 자유롭게 작성해주세요"
  maxLength={500}
/>
```

**디자인 요구사항**:
- 모바일 친화적 (반응형 디자인)
- 진행률 표시 (1/5, 2/5, ...)
- 자동 저장 기능 (임시 저장)
- 제출 완료 확인 페이지

**데이터 흐름**:
```
입주자 입력
    ↓
Frontend 검증
    ↓
POST /api/v4/phase6/feedback/submit
    ↓
Backend 분석 (자동)
    ↓
M7 업데이트 제안 생성
    ↓
관리자 대시보드에 표시
```

**예상 작업량**: 3-5일
- UI 컴포넌트: 2일
- API 연동: 1일
- 테스트: 1-2일

---

#### 1.2 피드백 제출 확인 페이지

**기능**:
- 제출 완료 메시지
- 제출된 피드백 요약
- 분석 결과 예상 시간 안내
- 이메일 알림 설정

**예시 화면**:
```
✅ 피드백이 제출되었습니다!

📊 제출 내용 요약:
   - 공간 만족도 평균: 78.5점
   - 프로그램 참여율: 65%
   - 전체 만족도: 82점

🔄 분석 예상 시간: 즉시
   분석 완료 시 이메일로 알림을 보내드립니다.

📧 알림 받을 이메일: user@example.com
   [변경]

[대시보드로 이동] [닫기]
```

---

### 2. 벤치마킹 DB 확장

**목표**: 더 많은 LH 공공임대 사례 추가

#### 2.1 데이터 수집 계획

**수집 대상**:
1. **LH 공식 자료**:
   - LH 공공임대 커뮤니티 운영 사례집
   - LH 연차 보고서
   - 공공임대 성과 평가 보고서

2. **지역별 사례**:
   - 서울: 마포구, 강남구, 송파구, 영등포구
   - 경기: 성남시, 고양시, 수원시, 용인시
   - 인천: 연수구, 남동구
   - 부산: 해운대구, 사하구

3. **유형별 사례**:
   - 청년형: 20-30세대
   - 신혼부부형: 30-50세대
   - 고령자형: 20-40세대
   - 다가구형: 50세대 이상

**목표 사례 수**:
```
현재: 2건
Phase 7: +10건 (총 12건)
Phase 8: +20건 (총 32건)
Phase 9: +50건 (총 82건)
```

#### 2.2 데이터 구조 확장

```python
class BenchmarkingCaseExtended(BenchmarkingCase):
    """확장된 벤치마킹 사례"""
    
    # 추가 필드
    demographics: Demographics  # 입주자 인구통계
    budget_breakdown: BudgetBreakdown  # 예산 세부 내역
    quarterly_reports: List[QuarterlyReport]  # 분기별 성과
    photos: List[str]  # 공간 사진 URL
    videos: List[str]  # 프로그램 영상 URL
    contact_info: ContactInfo  # 담당자 연락처
    
    # 성과 지표 확장
    retention_rate: float  # 입주자 재계약률
    complaint_rate: float  # 민원 발생률
    satisfaction_trend: List[float]  # 만족도 추이
    cost_efficiency: float  # 비용 효율성
```

#### 2.3 DB 마이그레이션

**옵션 1: JSON 파일 → SQLite**
```python
# 파일: app/database/benchmarking_db.py
import sqlite3

def migrate_to_sqlite():
    """JSON 사례를 SQLite로 마이그레이션"""
    conn = sqlite3.connect('benchmarking.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benchmarking_cases (
            case_id TEXT PRIMARY KEY,
            case_name TEXT,
            location_json TEXT,
            housing_type TEXT,
            household_count INTEGER,
            -- ... (기타 필드)
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
```

**옵션 2: 클라우드 DB (PostgreSQL)**
- Supabase / Railway / Render 사용
- 실시간 업데이트 가능
- API로 접근

**예상 작업량**: 5-7일
- 데이터 수집: 3-4일
- DB 설계 및 마이그레이션: 2-3일
- 테스트: 1일

---

### 3. M7 생성 시 벤치마킹 자동 연동

**목표**: M7 생성 시 벤치마킹 추천을 자동으로 반영

#### 3.1 통합 로직

```python
# 파일: app/models/m7_community_plan.py

def generate_m7_from_context_with_benchmarking(
    m1_result,
    m2_result,
    m3_result,
    m4_result,
    m5_result,
    m6_result,
    context_id,
    use_benchmarking: bool = True  # 벤치마킹 사용 여부
):
    """M7 생성 + 벤치마킹 추천 통합"""
    
    # 1. 기본 M7 생성 (기존 로직)
    base_m7 = generate_m7_from_context(
        m1_result, m2_result, m3_result, 
        m4_result, m5_result, m6_result, 
        context_id
    )
    
    if not use_benchmarking:
        return base_m7
    
    # 2. 벤치마킹 추천 조회
    recommendations = get_benchmarking_recommendations(
        context_id=context_id,
        housing_type=m3_result.selected.name,
        household_count=m4_result.summary.legal_units,
        address=m1_result.address
    )
    
    # 3. 공간 구성에 벤치마킹 반영
    enhanced_spaces = enhance_spaces_with_benchmark(
        base_spaces=base_m7.community_spaces,
        recommendations=recommendations.space_recommendations,
        priority_threshold=0.8  # 유사도 80% 이상만 반영
    )
    
    # 4. 프로그램에 벤치마킹 반영
    enhanced_programs = enhance_programs_with_benchmark(
        base_programs=base_m7.programs,
        recommendations=recommendations.program_recommendations,
        satisfaction_threshold=80.0  # 만족도 80점 이상만 반영
    )
    
    # 5. 예산에 벤치마킹 반영
    budget_benchmark = recommendations.budget_benchmark
    adjusted_budget = {
        "monthly_cost_per_household": budget_benchmark["average_monthly_cost_per_household"],
        "budget_range": budget_benchmark["recommended_budget_range"],
        "based_on_cases": len(recommendations.recommended_cases)
    }
    
    # 6. 벤치마킹 정보 추가
    base_m7.benchmarking_applied = True
    base_m7.similar_cases_count = len(recommendations.recommended_cases)
    base_m7.similarity_score_avg = calculate_avg_similarity(recommendations)
    base_m7.budget_benchmark = adjusted_budget
    
    # 7. M7 업데이트 및 반환
    return M7CommunityPlan(
        **base_m7.model_dump(),
        community_spaces=enhanced_spaces,
        programs=enhanced_programs,
        benchmarking_metadata={
            "applied": True,
            "similar_cases": [c["case_id"] for c in recommendations.recommended_cases],
            "avg_similarity": base_m7.similarity_score_avg,
            "timestamp": datetime.now().isoformat()
        }
    )


def enhance_spaces_with_benchmark(
    base_spaces: List[CommunitySpace],
    recommendations: List[Dict],
    priority_threshold: float
) -> List[CommunitySpace]:
    """벤치마킹 기반 공간 구성 개선"""
    
    enhanced = base_spaces.copy()
    
    # 높은 유사도 + 높은 이용률 공간 추가
    for rec in recommendations:
        if (rec["similarity_score"] >= priority_threshold * 100 and
            rec["utilization_rate"] >= 80.0):
            
            # 이미 있는 공간인지 확인
            exists = any(s.space_name == rec["space_name"] for s in enhanced)
            
            if not exists:
                # 새 공간 추가
                new_space = CommunitySpace(
                    space_type=rec["space_type"],
                    space_name=rec["space_name"],
                    description=f"벤치마킹 추천 (유사도 {rec['similarity_score']:.1f}%, 이용률 {rec['utilization_rate']:.1f}%)",
                    capacity=20,  # 기본값
                    usage_schedule="예약제",
                    equipment=[],
                    benchmarked=True,
                    source_case=rec["source_case"]
                )
                enhanced.append(new_space)
    
    return enhanced
```

#### 3.2 API 엔드포인트 수정

```python
# 파일: app/routers/m7_community_plan_router.py

@router.post("/api/v4/reports/m7/generate-with-benchmarking")
async def generate_m7_with_benchmarking(
    context_id: str = Query(...),
    use_benchmarking: bool = Query(True, description="벤치마킹 사용 여부")
):
    """M7 생성 (벤치마킹 자동 연동)"""
    
    # Context 조회
    context = context_storage.get_frozen_context(context_id)
    if not context:
        raise HTTPException(404, "Context not found")
    
    # M7 생성 (벤치마킹 포함)
    m7_plan = generate_m7_from_context_with_benchmarking(
        m1_result=context.m1_result,
        m2_result=context.m2_result,
        m3_result=context.m3_result,
        m4_result=context.m4_result,
        m5_result=context.m5_result,
        m6_result=context.m6_result,
        context_id=context_id,
        use_benchmarking=use_benchmarking
    )
    
    return {
        "success": True,
        "m7_plan": m7_plan.model_dump(),
        "benchmarking_applied": m7_plan.benchmarking_applied,
        "similar_cases_count": m7_plan.similar_cases_count,
        "message": "✅ M7 생성 완료 (벤치마킹 자동 연동)"
    }
```

**예상 작업량**: 4-6일
- 통합 로직 구현: 2-3일
- API 수정: 1일
- 테스트 및 검증: 1-2일

---

### 4. 실시간 피드백 대시보드

**목표**: 관리자가 실시간으로 피드백을 모니터링하고 M7 업데이트를 승인

#### 4.1 대시보드 화면 구성

**위치**: `/admin/feedback-dashboard`

**섹션**:

```
┌─────────────────────────────────────────────────────────┐
│ 📊 피드백 대시보드                    [새로고침] [설정]  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│ 🔢 전체 통계                                             │
│   ┌─────────┬─────────┬─────────┬─────────┐           │
│   │ 수집된  │ 분석 중 │ 개선안  │ 적용 완료│           │
│   │ 피드백  │         │ 대기    │          │           │
│   │   24건  │   3건   │   5건   │   8건   │           │
│   └─────────┴─────────┴─────────┴─────────┘           │
│                                                           │
│ 📈 만족도 추이                                           │
│   [차트: 월별 만족도 변화]                              │
│   • 1월: 75.2점                                          │
│   • 2월: 78.5점 ▲                                       │
│   • 3월: 82.1점 ▲                                       │
│                                                           │
│ 🚨 주요 개선 필요 영역                                   │
│   ┌─────────────────────────────────────────┐         │
│   │ 1. 공유 주방 (만족도 58.2점) ⚠️ HIGH    │         │
│   │    - 청소 문제                           │         │
│   │    - 시설 노후화                         │         │
│   │    [M7 업데이트 제안 보기]               │         │
│   ├─────────────────────────────────────────┤         │
│   │ 2. 취미 활동실 (이용률 32.1%) ⚠️ MEDIUM │         │
│   │    - 홍보 부족                           │         │
│   │    - 프로그램 다양성 부족                │         │
│   │    [M7 업데이트 제안 보기]               │         │
│   └─────────────────────────────────────────┘         │
│                                                           │
│ ✅ 최근 피드백 (실시간)                                  │
│   ┌─────────────────────────────────────────┐         │
│   │ 🆕 2분 전 | 입주자 A | 전체 만족도 85점 │         │
│   │    "커뮤니티 라운지가 좋습니다"          │         │
│   │    [상세보기]                            │         │
│   ├─────────────────────────────────────────┤         │
│   │ 🆕 15분 전 | 입주자 B | 전체 만족도 72점│         │
│   │    "주방 청소 개선 필요"                 │         │
│   │    [상세보기]                            │         │
│   └─────────────────────────────────────────┘         │
│                                                           │
│ 🔄 M7 업데이트 제안 (승인 대기)                         │
│   ┌─────────────────────────────────────────┐         │
│   │ Proposal #12 | 우선순위: HIGH           │         │
│   │ • 공유 주방 용도 변경 제안               │         │
│   │ • 예상 효과: 만족도 +15점               │         │
│   │ [승인] [거부] [수정]                    │         │
│   └─────────────────────────────────────────┘         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### 4.2 실시간 업데이트 (WebSocket)

```typescript
// frontend/src/services/feedbackWebSocket.ts

export class FeedbackWebSocket {
  private ws: WebSocket;
  
  connect() {
    this.ws = new WebSocket('ws://localhost:49999/ws/feedback');
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'new_feedback') {
        this.handleNewFeedback(data.feedback);
      } else if (data.type === 'analysis_complete') {
        this.handleAnalysisComplete(data.analysis);
      } else if (data.type === 'proposal_created') {
        this.handleNewProposal(data.proposal);
      }
    };
  }
  
  handleNewFeedback(feedback) {
    // 알림 표시
    toast.info(`새 피드백이 도착했습니다! (만족도: ${feedback.overall_satisfaction}점)`);
    
    // 대시보드 업데이트
    updateDashboard(feedback);
  }
}
```

**Backend WebSocket**:
```python
# app/websockets/feedback_ws.py

from fastapi import WebSocket
import asyncio

class FeedbackBroadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    async def broadcast(self, message: dict):
        """모든 연결된 클라이언트에 메시지 전송"""
        for connection in self.connections:
            await connection.send_json(message)
    
    async def notify_new_feedback(self, feedback: ResidentFeedback):
        await self.broadcast({
            "type": "new_feedback",
            "feedback": feedback.model_dump(),
            "timestamp": datetime.now().isoformat()
        })

broadcaster = FeedbackBroadcaster()

@app.websocket("/ws/feedback")
async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        broadcaster.connections.remove(websocket)
```

#### 4.3 알림 시스템

**이메일 알림**:
```python
# app/services/notification_service.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

async def send_feedback_notification(
    to_email: str,
    feedback_summary: dict
):
    """피드백 분석 완료 알림"""
    
    message = Mail(
        from_email='noreply@lhproject.com',
        to_emails=to_email,
        subject='[LH Project] 피드백 분석이 완료되었습니다',
        html_content=f'''
        <h2>피드백 분석 결과</h2>
        <p>평균 만족도: {feedback_summary["avg_satisfaction"]}점</p>
        <p>개선 필요 영역: {feedback_summary["improvement_count"]}개</p>
        <p><a href="https://lhproject.com/dashboard">대시보드에서 확인하기</a></p>
        '''
    )
    
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
```

**Slack 알림**:
```python
from slack_sdk import WebClient

async def send_slack_notification(channel: str, message: str):
    """Slack 알림 전송"""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    
    client.chat_postMessage(
        channel=channel,
        text=message,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔔 *새 피드백 알림*\n{message}"
                }
            }
        ]
    )
```

**예상 작업량**: 7-10일
- 대시보드 UI: 3-4일
- WebSocket 실시간 연동: 2-3일
- 알림 시스템: 1-2일
- 테스트: 1-2일

---

## 📊 우선순위 및 로드맵

### 우선순위

| 순위 | 항목 | 이유 | 예상 기간 |
|------|------|------|-----------|
| 1 | M7 생성 시 벤치마킹 자동 연동 | 즉시 효과 확인 가능 | 4-6일 |
| 2 | 벤치마킹 DB 확장 | 추천 정확도 향상 | 5-7일 |
| 3 | Frontend 피드백 수집 UI | 사용자 편의성 | 3-5일 |
| 4 | 실시간 피드백 대시보드 | 관리 효율성 | 7-10일 |

### 로드맵

```
Phase 7 (Week 1-2):
├─ M7 생성 시 벤치마킹 자동 연동
└─ 벤치마킹 DB 확장 (10건)

Phase 8 (Week 3-4):
├─ Frontend 피드백 수집 UI
└─ 벤치마킹 DB 확장 (20건 추가)

Phase 9 (Week 5-6):
├─ 실시간 피드백 대시보드
├─ WebSocket 실시간 연동
└─ 알림 시스템 (이메일/Slack)

Phase 10 (Week 7-8):
├─ 벤치마킹 DB 확장 (50건 추가)
├─ 머신러닝 기반 추천 개선
└─ 성능 최적화 및 캐싱
```

---

## 🔧 기술 스택 확장

### 새로운 의존성

**Frontend**:
```json
{
  "dependencies": {
    "socket.io-client": "^4.5.0",
    "recharts": "^2.5.0",
    "react-toastify": "^9.1.0",
    "react-hook-form": "^7.43.0"
  }
}
```

**Backend**:
```python
# requirements.txt
websockets>=11.0
sendgrid>=6.9.7
slack-sdk>=3.19.0
celery>=5.2.7  # 백그라운드 작업
redis>=4.5.0  # 캐싱
```

---

## 📝 문서화 계획

### 추가 문서

1. **PHASE7_BENCHMARKING_AUTO_INTEGRATION.md**
   - 벤치마킹 자동 연동 구현
   - API 사용법
   - 예제 코드

2. **PHASE8_FEEDBACK_UI_GUIDE.md**
   - 피드백 UI 사용 가이드
   - 컴포넌트 문서
   - 스타일 가이드

3. **PHASE9_REALTIME_DASHBOARD.md**
   - 대시보드 사용법
   - WebSocket 연동 가이드
   - 알림 설정 방법

4. **BENCHMARKING_DATABASE_SCHEMA.md**
   - DB 스키마 상세
   - 데이터 입력 가이드
   - 마이그레이션 절차

---

## ✅ 개선 완료 체크리스트

### Phase 7
- [ ] M7 생성 로직에 벤치마킹 통합
- [ ] 벤치마킹 DB 10건 추가
- [ ] API 엔드포인트 수정
- [ ] 테스트 케이스 작성
- [ ] 문서 작성 (PHASE7_*.md)

### Phase 8
- [ ] 피드백 수집 폼 UI 구현
- [ ] 피드백 제출 API 연동
- [ ] 모바일 반응형 디자인
- [ ] 벤치마킹 DB 20건 추가
- [ ] 문서 작성 (PHASE8_*.md)

### Phase 9
- [ ] 대시보드 UI 구현
- [ ] WebSocket 서버 구축
- [ ] 실시간 업데이트 로직
- [ ] 이메일 알림 시스템
- [ ] Slack 알림 시스템
- [ ] 문서 작성 (PHASE9_*.md)

### Phase 10
- [ ] 벤치마킹 DB 50건 추가
- [ ] 머신러닝 추천 알고리즘
- [ ] 캐싱 시스템 구축
- [ ] 성능 최적화
- [ ] 전체 통합 테스트

---

## 🎯 성공 지표 (KPI)

### Phase 7
- ✅ 벤치마킹 자동 연동률: 100%
- ✅ M7 생성 시간: <5초
- ✅ 추천 정확도: >85%

### Phase 8
- ✅ 피드백 수집률: >60% (입주자 대비)
- ✅ 폼 완료율: >80%
- ✅ 모바일 사용률: >40%

### Phase 9
- ✅ 대시보드 로딩 시간: <2초
- ✅ 실시간 업데이트 지연: <500ms
- ✅ 알림 전송 성공률: >99%

### Phase 10
- ✅ DB 사례 수: >80건
- ✅ 추천 정확도: >90%
- ✅ API 응답 시간: <200ms (캐싱 적용)

---

## 📞 지원 및 문의

추가 개선 사항이나 구현 중 질문이 있으시면:
1. GitHub Issue 생성
2. Slack #lhproject 채널
3. 이메일: dev@lhproject.com

---

**작성일**: 2026-01-10  
**다음 업데이트**: Phase 7 시작 시  
**상태**: 계획 완료 → 구현 대기
