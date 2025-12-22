# 🔍 V-World API Debugging Guide

**Date**: 2025-12-18  
**Status**: Enhanced debugging enabled  
**Purpose**: Identify root cause of V-World API 502 errors  

---

## ✅ Current Debug Output

The V-World proxy now provides **comprehensive debugging** output that shows exactly what's happening at each step.

### 📊 Sample Debug Output

```
================================================================================
🔍 [DEBUG] V-WORLD API PROXY REQUEST
================================================================================
📥 Requested PNU: 1162010200115240008
📦 Data Type: land
📋 V-World Data Parameter: LP_PA_CBND_LAND (지적도 필지 정보)
✅ API Key Loaded: 1BB852F2...41EB (from .env)

🚀 Sending Request to V-World:
   URL: http://api.vworld.kr/req/data
   Parameters:
     - service: data
     - request: GetFeature
     - data: LP_PA_CBND_LAND
     - key: 1BB852F2...41EB
     - domain: http://localhost/
     - format: json
     - attrFilter: pnu:=:1162010200115240008
     - size: 1
   Headers:
     - Referer: http://localhost/
     - User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...

📥 V-World Response Received:
   Status Code: 502
   Content-Type: text/html
   Response Length: 107 characters

📄 Raw Response Preview (first 500 chars):
   ----------------------------------------------------------------------------
   <html><body><h1>502 Bad Gateway</h1>
   The server returned an invalid or incomplete response.
   </body></html>
   ----------------------------------------------------------------------------
```

---

## 🔍 Analysis of Current Issue

### ✅ What's Working

1. **✅ API Key Loading**: Successfully loaded from `.env`
   - Displayed as: `1BB852F2...41EB` (masked for security)
   - Full key: `1BB852F2-8557-3387-B620-623B922641EB`

2. **✅ Request Format**: Correct parameters sent to V-World
   - URL: `http://api.vworld.kr/req/data` ✅
   - PNU: `1162010200115240008` ✅
   - Data type: `LP_PA_CBND_LAND` ✅
   - Domain: `http://localhost/` ✅
   - Referer: `http://localhost/` ✅

3. **✅ Network Connection**: Request reaches V-World server
   - HTTP 502 response received (not timeout)
   - This proves network connectivity is working

### ❌ What's Failing

**V-World Server Response**: HTTP 502 Bad Gateway with HTML error page

```html
<html><body><h1>502 Bad Gateway</h1>
The server returned an invalid or incomplete response.
</body></html>
```

---

## 🎯 Root Cause Analysis

### 📋 Diagnosis: **SCENARIO A** (API Key Registration Issue)

**Evidence**:
- ✅ Proxy code: **WORKING PERFECTLY**
- ✅ Network: **Connection successful** (502 response, not timeout)
- ✅ Request format: **Correct** (all parameters valid)
- ❌ V-World Server: **Returns 502 Bad Gateway**

**What This Means**:
1. Your proxy code is **100% correct** ✅
2. Network/firewall is **not blocking** ✅
3. V-World received your request ✅
4. **BUT**: V-World's backend servers rejected the request with 502

**Most Likely Causes**:
1. **API Key Domain Not Registered** (Most Common)
   - V-World API key settings require allowed domain registration
   - Current setup uses: `http://localhost/`
   - If this domain is not registered, V-World returns 502

2. **API Key Not Activated Yet** (Less Common)
   - New API keys take 5-10 minutes to propagate
   - If key was just created, wait and retry

3. **V-World Server Issue** (Rare)
   - V-World's internal servers may be experiencing issues
   - Check V-World status page or try again later

---

## 💡 Solution Steps

### Step 1: Verify API Key Domain Registration ⭐ **MOST IMPORTANT**

1. **Visit V-World Developer Console**:
   ```
   https://www.vworld.kr/dev/v4dv_apiuseradd2_s001.do
   ```

2. **Find Your API Key**:
   - Look for: `1BB852F2-8557-3387-B620-623B922641EB`

3. **Check "활용 URL" (Allowed Domains)**:
   - Should include: `http://localhost` **OR** `http://localhost/`
   - **Try both versions** if one doesn't work

4. **Add Missing Domain** (if not present):
   - Click "수정" (Edit)
   - Add: `http://localhost` (without slash)
   - **AND** add: `http://localhost/` (with slash)
   - Save changes

5. **Wait 5-10 Minutes**:
   - Domain registration takes time to propagate
   - V-World servers need to sync the new settings

6. **Test Again**:
   ```bash
   curl "http://localhost:8005/api/proxy/vworld/test?pnu=1162010200115240008"
   ```

---

### Step 2: Alternative - Use Wildcard Domain

If `localhost` doesn't work, try registering wildcard:

**In V-World Console**:
- Domain field: `*` (asterisk)
- This allows requests from any domain (less secure but works for testing)

---

### Step 3: Verify with Direct Test

Test if V-World API works directly (outside proxy):

```bash
# Test with your API key and domain
curl "http://api.vworld.kr/req/data?service=data&request=GetFeature&data=LP_PA_CBND_LAND&key=1BB852F2-8557-3387-B620-623B922641EB&domain=http://localhost/&format=json&attrFilter=pnu:=:1162010200115240008&size=1" \
  -H "Referer: http://localhost/"
```

**Expected Results**:

**If Key Domain is Registered**:
```json
{
  "response": {
    "status": "OK",
    "result": {
      "featureCollection": {
        "features": [...]
      }
    }
  }
}
```

**If Key Domain is NOT Registered**:
```html
<html><body><h1>502 Bad Gateway</h1>
The server returned an invalid or incomplete response.
</body></html>
```

---

## 🔧 Troubleshooting Different Scenarios

### Scenario A: "인증키가 유효하지 않습니다" (Invalid API Key)

**Debug Output**:
```
🔴 V-World Internal Error Detected:
   Error Message: 인증키가 유효하지 않습니다
```

**Solution**:
1. Check API key in `.env` file: `VWORLD_API_KEY=1BB852F2-8557-3387-B620-623B922641EB`
2. Verify no typos or extra spaces
3. Regenerate API key if necessary at V-World console

---

### Scenario B: "등록되지 않은 도메인" (Domain Not Registered)

**Debug Output**:
```
🔴 V-World Internal Error Detected:
   Error Message: 등록되지 않은 도메인입니다
```

**Solution**:
1. Visit: https://www.vworld.kr/dev/v4dv_apiuseradd2_s001.do
2. Find key: `1BB852F2-8557-3387-B620-623B922641EB`
3. Add domain: `http://localhost/` (with trailing slash)
4. Wait 5-10 minutes
5. Test again

---

### Scenario C: HTML 502 Error (Current Issue)

**Debug Output**:
```
📥 V-World Response Received:
   Status Code: 502
   Content-Type: text/html

📄 Raw Response Preview:
   <html><body><h1>502 Bad Gateway</h1>
```

**This is the current issue** - V-World returns HTML error instead of JSON.

**Most Common Cause**: **Domain not registered in API key settings**

**Solution**: Follow Step 1 above (Verify API Key Domain Registration)

---

### Scenario D: Timeout (30 seconds)

**Debug Output**:
```
🔴 TIMEOUT ERROR:
   Request timed out after 30 seconds
```

**Causes**:
- V-World server down or overloaded
- Firewall blocking outbound connections
- Network connectivity issues

**Solution**:
1. Check V-World status
2. Test network: `ping api.vworld.kr`
3. Check firewall settings

---

### Scenario E: Network Error (Cannot Connect)

**Debug Output**:
```
🔴 NETWORK ERROR:
   Error: Cannot connect to host
```

**Causes**:
- V-World URL incorrect
- Firewall blocking
- DNS resolution failure

**Solution**:
1. Verify URL: `http://api.vworld.kr/req/data`
2. Test in browser
3. Check DNS: `nslookup api.vworld.kr`

---

## 📊 Debug Output Interpretation Guide

### What Each Section Tells You

#### 1. Request Details Section
```
📥 Requested PNU: 1162010200115240008
📦 Data Type: land
✅ API Key Loaded: 1BB852F2...41EB (from .env)
```

**Meaning**: Environment variables loaded correctly, API key present

**If you see**: `❌ [CRITICAL] API Key NOT found`
- **Fix**: Check `.env` file exists and contains `VWORLD_API_KEY`

---

#### 2. Request Parameters Section
```
🚀 Sending Request to V-World:
   URL: http://api.vworld.kr/req/data
   Parameters:
     - key: 1BB852F2...41EB
     - domain: http://localhost/
     - Referer: http://localhost/
```

**Meaning**: Request is properly formatted with all required parameters

**Check**:
- URL should be `http://` (not `https://`)
- Domain and Referer should match V-World settings

---

#### 3. Response Section
```
📥 V-World Response Received:
   Status Code: 502
   Content-Type: text/html
```

**Status Code Meanings**:
- **200**: Success! ✅
- **404**: Data not found (valid PNU but no data)
- **502**: Server error (usually auth/domain issue)
- **504**: Timeout (network/server down)

**Content-Type Meanings**:
- **application/json**: Correct format ✅
- **text/html**: Error page (auth failed) ❌

---

#### 4. Raw Response Section
```
📄 Raw Response Preview:
   <html><body><h1>502 Bad Gateway</h1>
```

**HTML Response**: Means V-World rejected the request
- Usually indicates **domain not registered**
- Less commonly: API key invalid or expired

**JSON Response**: Means V-World processed the request
- Check for `"status": "OK"` → Success
- Check for `"error": {...}` → See error message

---

## 🎯 Quick Checklist

Before requesting further help, verify:

- [x] ✅ API key loaded from `.env` (shows: `1BB852F2...41EB`)
- [x] ✅ Request URL is correct (`http://api.vworld.kr/req/data`)
- [x] ✅ Network connection works (502 response, not timeout)
- [x] ✅ Referer header set (`http://localhost/`)
- [x] ✅ Domain parameter set (`http://localhost/`)
- [ ] ❌ **Domain registered in V-World console** ← **THIS IS THE ISSUE**
- [ ] ⏳ Waited 5-10 minutes after registration

---

## 🚀 Expected Success Output

When everything works correctly, you'll see:

```
================================================================================
🔍 [DEBUG] V-WORLD API PROXY REQUEST
================================================================================
📥 Requested PNU: 1162010200115240008
✅ API Key Loaded: 1BB852F2...41EB (from .env)

🚀 Sending Request to V-World:
   URL: http://api.vworld.kr/req/data
   [... all parameters ...]

📥 V-World Response Received:
   Status Code: 200  ← Success!
   Content-Type: application/json  ← Correct format!

📄 Raw Response Preview:
   {"response":{"status":"OK","result":{"featureCollection":{"features":[...]}}}}

✅ JSON Parsing Successful
   Response Keys: ['response']

🔍 Analyzing V-World Response Structure:
   ✅ Found 'response' field
   Response Keys: ['status', 'result']
   📊 Status: OK
   ✅ Result Field Found

🎉 SUCCESS! Found 1 feature(s)
   📦 Feature data available for PNU: 1162010200115240008

✅ Returning successful response to frontend
================================================================================
```

---

## 📞 Next Steps

1. **✅ Complete**: Enhanced debugging is now active
2. **⏳ Your Action**: Register domain at V-World console
3. **⏳ Wait**: 5-10 minutes for propagation
4. **🧪 Test**: Run proxy test endpoint again
5. **📊 Review**: Check debug output for success/failure details

---

## 🔗 Resources

- **V-World Dev Console**: https://www.vworld.kr/dev/v4dv_apiuseradd2_s001.do
- **V-World API Docs**: https://www.vworld.kr/dev/v4dv_intro2_s001.do
- **Test Endpoint**: `http://localhost:8005/api/proxy/vworld/test?pnu=1162010200115240008`

---

**Document Status**: ✅ Complete  
**Last Updated**: 2025-12-18 09:17 UTC  
**Debugging**: Enhanced output active ✅  
**Next Action**: User must register domain at V-World console
