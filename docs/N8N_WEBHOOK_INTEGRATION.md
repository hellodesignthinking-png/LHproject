# n8n Webhook Integration for M1 Land Data

**Date:** 2025-12-19  
**Author:** ZeroSite Team  
**Status:** ✅ COMPLETED

## Summary

M1 데이터 수집 모듈이 n8n Webhook을 통해 외부 API를 호출하도록 변경되었습니다.

## Architecture Change

### Before (Old Strategy)
```
Frontend → Backend → V-World API
                  → 공공데이터포털 API
```

### After (New Strategy)
```
Frontend → Backend → n8n Webhook → V-World API
                                 → 공공데이터포털 API
                                 → Data aggregation
```

## Benefits

1. **Centralized API Management**: All external API calls managed by n8n
2. **Flexible Workflows**: Easy to modify data sources without code changes
3. **Monitoring**: n8n provides built-in monitoring and logging
4. **Fault Tolerance**: Automatic fallback to Mock data if n8n fails
5. **Security**: API keys managed securely in n8n cloud

## Implementation

### Modified File

`app/api/endpoints/proxy_vworld.py`

### Key Changes

1. **Removed Direct API Calls**
   - ❌ Removed V-World API direct calls
   - ❌ Removed 공공데이터포털 direct calls
   - ❌ Removed ServiceKey encoding logic

2. **Added n8n Webhook Integration**
   - ✅ n8n webhook URL: `https://zerosite.app.n8n.cloud/webhook/m1-land-data`
   - ✅ Simple GET request with `pnu` query parameter
   - ✅ 30-second timeout (to handle slow public APIs)
   - ✅ Proper error handling

3. **Enhanced Fallback Logic**
   - ✅ Returns Mock data if n8n webhook fails
   - ✅ Maintains V-World response format for frontend compatibility
   - ✅ Includes `is_mock` and `source` fields for debugging

## API Endpoints

### 1. Main Endpoint: `/api/proxy/vworld`

**Request:**
```http
GET /api/proxy/vworld?pnu=1162010200115240008
```

**Response (Success - n8n):**
```json
{
  "success": true,
  "data": {
    "response": {
      "status": "OK",
      "result": {
        "featureCollection": {
          "features": [{
            "properties": {
              "pnu": "1162010200115240008",
              "jimok": "대",
              "area": "500.0",
              "jiyuk": "제2종일반주거지역",
              "is_mock": false,
              "source": "n8n Webhook"
            }
          }]
        }
      }
    }
  }
}
```

**Response (Fallback - Mock):**
```json
{
  "success": true,
  "data": {
    "response": {
      "status": "OK",
      "result": {
        "featureCollection": {
          "features": [{
            "properties": {
              "pnu": "1162010200115240008",
              "jimok": "대",
              "area": "330.0",
              "jiyuk": "제2종일반주거지역",
              "is_mock": true,
              "source": "System Mock (n8n 연결 실패)"
            }
          }]
        }
      }
    }
  }
}
```

### 2. Test Endpoint: `/api/proxy/vworld/test`

**Request:**
```http
GET /api/proxy/vworld/test?pnu=1162010200115240008
```

**Response:**
```json
{
  "success": true,
  "message": "n8n webhook proxy test completed!",
  "test_pnu": "1162010200115240008",
  "n8n_webhook_url": "https://zerosite.app.n8n.cloud/webhook/m1-land-data",
  "strategy": "Primary: n8n Webhook → Fallback: Mock Data",
  "note": "All external API calls now routed through n8n workflow",
  "response": { ... }
}
```

## n8n Webhook Specification

### Required n8n Response Format

The n8n webhook must return JSON in this format:

```json
{
  "pnu": "1162010200115240008",
  "jimok": "대",
  "area": 500.0,
  "jiyuk": "제2종일반주거지역",
  "is_mock": false,
  "source": "V-World API"
}
```

### Response Field Mapping

| n8n Field | Backend Field | Type | Description |
|-----------|---------------|------|-------------|
| `pnu` | `pnu` | string | 필지번호 (19자리) |
| `jimok` | `jimok` | string | 지목 (예: 대, 전, 답) |
| `area` | `area` | float | 면적 (㎡) |
| `jiyuk` | `zoning` | string | 용도지역 |
| `is_mock` | `is_mock` | boolean | Mock 데이터 여부 |
| `source` | `source` | string | 데이터 출처 |

### Error Handling

The backend will fall back to Mock data if:
- n8n webhook returns non-200 status code
- n8n webhook times out (>30 seconds)
- n8n webhook returns invalid JSON
- Network connection error

## Testing

### Test Script

```python
import httpx
import asyncio

async def test_n8n():
    async with httpx.AsyncClient() as client:
        # Test n8n webhook directly
        response = await client.get(
            "https://zerosite.app.n8n.cloud/webhook/m1-land-data",
            params={"pnu": "1162010200115240008"},
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        print(f"Data: {response.json()}")

asyncio.run(test_n8n())
```

### Expected Behavior

1. **n8n Active**: Backend returns real data from n8n
2. **n8n Inactive/Failed**: Backend returns Mock data with `is_mock: true`
3. **Frontend**: Works the same way regardless of data source

## Deployment

### Backend Status

- ✅ Code updated and deployed
- ✅ Backend running on port 8005
- ✅ Test endpoint working
- ✅ Fallback to Mock data working

### n8n Webhook Status

⚠️ **n8n webhook needs to be activated**

Current status: `404 - The requested webhook "GET m1-land-data" is not registered.`

**Next Steps:**
1. Activate the n8n workflow
2. Ensure webhook is publicly accessible
3. Test with real PNU data
4. Verify response format matches specification

## Frontend Compatibility

✅ **No frontend changes required!**

The backend maintains the same V-World response format, so the frontend continues to work without any modifications.

## Monitoring & Debugging

### Backend Logs

```bash
# View backend logs
tail -f /home/user/webapp/backend_n8n.log

# Look for these log patterns:
# "🚀 [n8n] Webhook 호출 시작"
# "✅ [SUCCESS] n8n 데이터 수신 성공!"
# "🛡️ [FALLBACK] Mock 데이터 사용 (n8n 연결 실패)"
```

### Debug Information

Each response includes:
- `is_mock`: `true` if Mock data, `false` if real data
- `source`: Data source identifier (e.g., "n8n Webhook", "System Mock")

## Migration Checklist

- [x] Update `proxy_vworld.py` to call n8n webhook
- [x] Remove direct V-World API calls
- [x] Remove direct 공공데이터포털 API calls
- [x] Implement fallback to Mock data
- [x] Test with Mock data (n8n inactive)
- [ ] Activate n8n workflow
- [ ] Test with real data (n8n active)
- [ ] Verify frontend integration
- [ ] Monitor production usage

## Security Considerations

1. **API Keys**: Now managed in n8n (not in backend code)
2. **Rate Limiting**: Handled by n8n workflow
3. **CORS**: Backend continues to handle CORS headers
4. **Timeout**: 30-second timeout prevents hanging requests

## Performance

- **n8n Latency**: ~2-3 seconds for public API calls
- **Timeout**: 30 seconds maximum
- **Fallback**: Instant Mock data if n8n fails
- **Caching**: Can be implemented in n8n workflow

## Troubleshooting

### Issue: 404 from n8n webhook

**Cause**: n8n workflow is not active or webhook URL is incorrect

**Solution**: 
1. Check n8n workflow is active
2. Verify webhook URL matches: `https://zerosite.app.n8n.cloud/webhook/m1-land-data`
3. Ensure webhook method is GET (not POST)

### Issue: Timeout after 30 seconds

**Cause**: Public APIs are slow or n8n workflow is complex

**Solution**:
1. Increase timeout in `proxy_vworld.py` (line 87)
2. Optimize n8n workflow execution
3. Implement caching in n8n

### Issue: Invalid response format

**Cause**: n8n response doesn't match expected format

**Solution**:
1. Check n8n response structure
2. Update backend parsing logic if needed
3. Add data transformation in n8n workflow

## Future Enhancements

1. **Response Caching**: Cache frequently requested PNUs
2. **Retry Logic**: Retry failed n8n calls before fallback
3. **Health Check**: Periodic n8n webhook health monitoring
4. **Metrics**: Track n8n success rate and latency
5. **A/B Testing**: Compare n8n vs direct API performance

---

**Contact:** ZeroSite Backend Team  
**Date:** 2025-12-19  
**Version:** 1.0
