# 9. 리스크 관리 체계

## 9.1 리스크 분류

### Critical 등급 (자동 탈락)
- 주유소 25m 이내
- 위험물 저장소 50m 이내
- 용도지역 부적합

### High 등급 (재검토 필요)
- 장례식장 100m 이내
- 공장 200m 이내
- 개발행위 제한

### Medium 등급 (경고)
- 수요 점수 60점 미만
- 지하철 1.5km 초과
- 학교 1km 초과

### Low 등급 (참고)
- 소음·대기오염
- 경사지 10% 이상

## 9.2 ZeroSite 자동 검증

```python
def verify_risks(location):
    risks = []
    
    # LH 매입 제외 검증
    if has_gas_station_within_25m(location):
        risks.append({
            "category": "LH매입제외",
            "severity": "critical",
            "description": "주유소 25m 이내"
        })
    
    return risks
```

## 9.3 대응 전략

| 리스크 | 대응 방안 |
|--------|----------|
| Critical | 자동 탈락 표시, 대안 부지 추천 |
| High | 재검토 권장, 완화 방안 제시 |
| Medium | 경고 메시지, 개선 가능 항목 안내 |
| Low | 참고 사항, 모니터링 |

**Watermark**: ZeroSite | ZeroSite Land Report v5.0 | Risk Management | Page 10
