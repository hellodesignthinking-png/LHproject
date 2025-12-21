# M1 STEP-Based UX Implementation Plan

**Date**: 2025-12-17  
**Version**: 1.0  
**Status**: Planning Phase  
**Integration Target**: M4 V2 Complete Pipeline

---

## 🎯 Executive Summary

This document outlines the implementation plan for redesigning the M1 Land Information landing page from a **single-input API-flood approach** to a **STEP-based user verification UX**, addressing API rate limiting issues while improving data accuracy and user control.

---

## 🏗️ Current System Analysis

### Existing M1 Architecture (To Be Replaced)

```
[Current - BROKEN]
User Input (지번) 
    ↓
Single API Call (All APIs at once)
    ↓
Result Display
    ↓
Create CanonicalLandContext
    ↓
Pipeline (M2→M3→M4→M5→M6)
```

**Problems:**
- ❌ API rate limiting causes failures
- ❌ No user verification of auto-collected data
- ❌ No graceful degradation when APIs fail
- ❌ No data source transparency
- ❌ All-or-nothing approach

### Target M1 Architecture (New STEP-Based)

```
[New - STEP-BASED]
STEP 0: Start
    ↓
STEP 1: Address Input
    ↓ (Address API)
STEP 2: Location Verification (with Map)
    ↓ (Cadastral API)
STEP 3: Parcel/Area Confirmation (+ PDF Upload)
    ↓ (Land Use API)
STEP 4: Legal/Usage Information
    ↓ (Road API)
STEP 5: Road/Access Information
    ↓ (Transaction API)
STEP 6: Market/Transaction Data
    ↓
STEP 7: Comprehensive Verification
    ↓ (User Confirmation)
STEP 8: Context Freeze & Handoff to M2
    ↓
Pipeline (M2→M3→M4→M5→M6)
```

**Benefits:**
- ✅ API calls distributed across steps (no rate limit hit)
- ✅ User validates each step before proceeding
- ✅ Clear data source attribution (API/Manual/PDF)
- ✅ Graceful degradation (manual input fallback)
- ✅ Immutable CanonicalLandContext after freeze

---

## 📐 STEP-Based UX Specification

### Global UI Components

#### 1. Progress Bar Component
```jsx
<ProgressBar 
  currentStep={2}
  totalSteps={8}
  stepLabels={[
    "시작", "주소", "위치", "지번", 
    "법적정보", "도로", "시장", "확정"
  ]}
/>
```

**Visual Design:**
- Horizontal stepper with 8 dots
- Completed steps: Green ✅
- Current step: Blue (highlighted)
- Future steps: Gray (outline)
- Mobile: Simplified numeric display (2/8)

#### 2. Data Source Badge Component
```jsx
<DataSourceBadge 
  source="api"     // "api" | "manual" | "pdf"
  apiName="주소"   // Optional: specific API name
  timestamp="2024-01-15 14:30"
/>
```

**Visual Design:**
- 🟢 API 자동: Green pill badge
- 🔵 사용자 입력: Blue pill badge
- 🟠 PDF 기반: Orange pill badge
- Tooltip shows API name and timestamp

#### 3. Auto-Save Indicator
```jsx
<AutoSaveIndicator 
  status="saved"    // "saving" | "saved" | "error"
  lastSaved="2분 전"
/>
```

**Behavior:**
- Appears top-right of each step
- Saves form state every 10 seconds
- Persists in localStorage (session recovery)

---

## 📝 Step-by-Step Implementation

### STEP 0: Start Screen

**Purpose**: Introduce M1's role and set expectations

**UI Elements:**
```jsx
<M1StartScreen>
  <Title>토지 기본정보 입력 (M1)</Title>
  <Description>
    주소를 기준으로 토지의 사실관계를 단계적으로 확정합니다.
    모든 정보는 공공 API 자동 조회 + 사용자 검증 방식으로 수집됩니다.
  </Description>
  <InfoCards>
    <Card icon="📍">8단계 단계별 입력</Card>
    <Card icon="🔍">자동 조회 + 사용자 검증</Card>
    <Card icon="🔒">최종 확정 후 변경 불가</Card>
  </InfoCards>
  <CTAButton>주소 입력 시작</CTAButton>
</M1StartScreen>
```

**Backend**: No API calls

**State Management:**
```typescript
interface M1State {
  currentStep: number;        // 0-8
  stepData: {
    step1: AddressData | null;
    step2: LocationData | null;
    step3: ParcelData | null;
    step4: LegalData | null;
    step5: RoadData | null;
    step6: MarketData | null;
    step7: VerificationData | null;
  };
  dataSources: Record<string, DataSource>;
  lastSaved: Date;
  isFrozen: boolean;
}

type DataSource = {
  source: 'api' | 'manual' | 'pdf';
  apiName?: string;
  timestamp: Date;
  confidence?: number;
};
```

---

### STEP 1: Address Input

**Purpose**: Collect 도로명 or 지번 address

**UI Elements:**
```jsx
<Step1AddressInput>
  <ProgressBar currentStep={1} totalSteps={8} />
  
  <FormSection>
    <Label>주소 입력 (필수)</Label>
    <AddressSearchInput 
      placeholder="도로명 주소 또는 지번 주소를 입력하세요"
      onSearch={handleAddressSearch}
      suggestions={addressSuggestions}
    />
    <HelpText>
      예시: 서울시 강남구 역삼동 123-45 또는 테헤란로 123
    </HelpText>
  </FormSection>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button 
      variant="primary" 
      onClick={goNext}
      disabled={!isAddressValid}
    >
      다음 단계
    </Button>
  </ButtonGroup>
  
  <AutoSaveIndicator status={saveStatus} />
</Step1AddressInput>
```

**API Call:**
```typescript
// Triggered on user input (debounced 500ms)
POST /api/m1/address/search
Request: { query: string }
Response: {
  suggestions: Array<{
    roadAddress: string;
    jibunAddress: string;
    coordinates: { lat: number; lon: number };
    sido: string;
    sigungu: string;
    dong: string;
  }>
}
```

**Validation:**
- Address must be selected from suggestions (not free text)
- Validate against Korean address format
- Show error if no results found

**State Update:**
```typescript
stepData.step1 = {
  roadAddress: string;
  jibunAddress: string;
  selectedAddress: string;
};
dataSources.address = { source: 'api', apiName: 'Address Search API' };
```

---

### STEP 2: Location/Coordinates Verification

**Purpose**: Verify location on map and confirm coordinates

**UI Elements:**
```jsx
<Step2LocationVerification>
  <ProgressBar currentStep={2} totalSteps={8} />
  
  <MapContainer>
    <KakaoMap 
      center={coordinates}
      marker={coordinates}
      zoom={16}
      onMarkerDrag={handleMarkerDrag}
    />
    <MapOverlay>
      <InfoCard>
        <DataSourceBadge source="api" apiName="Address API" />
        <Field label="위도" value={coordinates.lat} />
        <Field label="경도" value={coordinates.lon} />
        <Field label="행정동" value={dong} />
        <Field label="법정동" value={beopjeongDong} />
      </InfoCard>
    </MapOverlay>
  </MapContainer>
  
  <ManualInputSection collapsed={!apiFailure}>
    <Alert severity="warning" show={apiFailure}>
      API 조회 실패. 수동으로 위치를 지정하세요.
    </Alert>
    <CoordinateInputs 
      lat={coordinates.lat}
      lon={coordinates.lon}
      onChange={handleManualCoordinates}
    />
  </ManualInputSection>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button variant="primary" onClick={goNext}>확인하고 다음</Button>
  </ButtonGroup>
</Step2LocationVerification>
```

**API Call:**
```typescript
// Triggered on step entry
GET /api/m1/geocode
Request: { address: string }
Response: {
  coordinates: { lat: number; lon: number };
  sido: string;
  sigungu: string;
  dong: string;
  beopjeongDong: string;
  success: boolean;
}
```

**Validation:**
- Coordinates must be within Korea bounds
- If API fails, require manual input
- Marker drag updates coordinates

**State Update:**
```typescript
stepData.step2 = {
  coordinates: { lat, lon },
  sido, sigungu, dong, beopjeongDong
};
dataSources.coordinates = apiSuccess 
  ? { source: 'api', apiName: 'Geocoding API' }
  : { source: 'manual' };
```

---

### STEP 3: Parcel Number & Area Confirmation

**Purpose**: Confirm 지번, 지목, 대지면적 with PDF upload option

**UI Elements:**
```jsx
<Step3ParcelConfirmation>
  <ProgressBar currentStep={3} totalSteps={8} />
  
  <DataGrid>
    <GridRow>
      <Label>본번</Label>
      <Value editable>{bonbun}</Value>
      <DataSourceBadge source={dataSources.bonbun.source} />
    </GridRow>
    <GridRow>
      <Label>부번</Label>
      <Value editable>{bubun}</Value>
      <DataSourceBadge source={dataSources.bubun.source} />
    </GridRow>
    <GridRow>
      <Label>지목</Label>
      <Value editable>{jimok}</Value>
      <DataSourceBadge source={dataSources.jimok.source} />
    </GridRow>
    <GridRow emphasis>
      <Label>대지면적 (㎡)</Label>
      <Value editable required>{area}</Value>
      <DataSourceBadge source={dataSources.area.source} />
    </GridRow>
  </DataGrid>
  
  <PDFUploadSection>
    <UploadButton 
      accept=".pdf"
      onChange={handlePDFUpload}
    >
      토지대장 PDF 업로드
    </UploadButton>
    <HelpText>
      PDF에서 자동으로 정보를 추출합니다.
    </HelpText>
  </PDFUploadSection>
  
  <Alert severity="error" show={!area}>
    대지면적은 필수 입력 항목입니다.
  </Alert>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button 
      variant="primary" 
      onClick={goNext}
      disabled={!area}
    >
      확인하고 다음
    </Button>
  </ButtonGroup>
</Step3ParcelConfirmation>
```

**API Calls:**
```typescript
// On step entry
GET /api/m1/cadastral
Request: { coordinates: {lat, lon} }
Response: {
  bonbun: string;
  bubun: string;
  jimok: string;
  area: number;
  success: boolean;
}

// On PDF upload
POST /api/m1/parse-pdf
Request: FormData { file: File }
Response: {
  extracted: {
    bonbun?: string;
    bubun?: string;
    jimok?: string;
    area?: number;
  };
  confidence: Record<string, number>;
}
```

**Validation:**
- `area` is required (cannot proceed without it)
- Numeric validation for area (> 0)
- PDF extraction results are suggestions (user confirms)

**State Update:**
```typescript
stepData.step3 = { bonbun, bubun, jimok, area };
dataSources.area = pdfUploaded 
  ? { source: 'pdf', timestamp: uploadTime }
  : apiSuccess 
    ? { source: 'api', apiName: 'Cadastral API' }
    : { source: 'manual' };
```

---

### STEP 4: Legal/Usage Information

**Purpose**: Confirm 용도지역, 건폐율, 용적률, 이용상황

**UI Elements:**
```jsx
<Step4LegalInformation>
  <ProgressBar currentStep={4} totalSteps={8} />
  
  <InfoBanner variant="info">
    이 단계에서는 유리·불리 판단을 하지 않습니다.
    법적 기준 사실만 확인합니다.
  </InfoBanner>
  
  <DataGrid>
    <GridSection title="용도 지역">
      <GridRow>
        <Label>용도지역</Label>
        <Select value={zoneType} onChange={handleZoneChange}>
          <option>제1종일반주거지역</option>
          <option>제2종일반주거지역</option>
          <option>제3종일반주거지역</option>
          <option>준주거지역</option>
        </Select>
        <DataSourceBadge source={dataSources.zoneType.source} />
      </GridRow>
      <GridRow>
        <Label>지구·구역</Label>
        <Value editable>{zoneDetail}</Value>
        <DataSourceBadge source={dataSources.zoneDetail.source} />
      </GridRow>
    </GridSection>
    
    <GridSection title="법적 기준">
      <GridRow emphasis>
        <Label>건폐율 (%)</Label>
        <Value editable type="number">{bcr}</Value>
        <DataSourceBadge source={dataSources.bcr.source} />
      </GridRow>
      <GridRow emphasis>
        <Label>용적률 (%)</Label>
        <Value editable type="number">{far}</Value>
        <DataSourceBadge source={dataSources.far.source} />
      </GridRow>
    </GridSection>
    
    <GridSection title="이용 상황">
      <GridRow>
        <Label>이용상황</Label>
        <Value editable>{landUse}</Value>
        <DataSourceBadge source={dataSources.landUse.source} />
      </GridRow>
    </GridSection>
  </DataGrid>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button 
      variant="primary" 
      onClick={goNext}
      disabled={!bcr || !far}
    >
      확인하고 다음
    </Button>
  </ButtonGroup>
</Step4LegalInformation>
```

**API Call:**
```typescript
GET /api/m1/land-use
Request: { coordinates: {lat, lon}, jimok: string }
Response: {
  zoneType: string;
  zoneDetail: string;
  bcr: number;
  far: number;
  landUse: string;
  regulations: string[];
  restrictions: string[];
  success: boolean;
}
```

**Validation:**
- BCR and FAR are required
- BCR must be <= 100
- FAR must be > 0
- Zone type must be selected

**State Update:**
```typescript
stepData.step4 = { zoneType, zoneDetail, bcr, far, landUse, regulations, restrictions };
dataSources.bcr = { source: apiSuccess ? 'api' : 'manual' };
dataSources.far = { source: apiSuccess ? 'api' : 'manual' };
```

---

### STEP 5: Road/Access Information

**Purpose**: Verify 접도, 도로폭, 도로위치

**UI Elements:**
```jsx
<Step5RoadInformation>
  <ProgressBar currentStep={5} totalSteps={8} />
  
  <MapContainer>
    <KakaoMap 
      center={coordinates}
      layers={['road', 'terrain']}
      roadHighlight={nearbyRoads}
    />
  </MapContainer>
  
  <DataGrid>
    <GridRow>
      <Label>접도 여부</Label>
      <Radio value={roadContact} onChange={handleRoadContact}>
        <option value="yes">접함</option>
        <option value="no">접하지 않음</option>
        <option value="partial">일부 접함</option>
      </Radio>
      <DataSourceBadge source={dataSources.roadContact.source} />
    </GridRow>
    <GridRow>
      <Label>도로 폭 (m)</Label>
      <Value editable type="number">{roadWidth}</Value>
      <DataSourceBadge source={dataSources.roadWidth.source} />
    </GridRow>
    <GridRow>
      <Label>도로 위치</Label>
      <Select value={roadType}>
        <option>도로</option>
        <option>이면도로</option>
        <option>막다른 도로</option>
        <option>광장</option>
      </Select>
      <DataSourceBadge source={dataSources.roadType.source} />
    </GridRow>
  </DataGrid>
  
  <PhotoUploadSection>
    <UploadButton accept="image/*" onChange={handlePhotoUpload}>
      현황 사진 업로드
    </UploadButton>
    <PhotoPreview images={uploadedPhotos} />
  </PhotoUploadSection>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button variant="primary" onClick={goNext}>확인하고 다음</Button>
  </ButtonGroup>
</Step5RoadInformation>
```

**API Call:**
```typescript
GET /api/m1/road-info
Request: { coordinates: {lat, lon}, radius: 100 }
Response: {
  nearbyRoads: Array<{
    name: string;
    width: number;
    type: string;
    distance: number;
  }>;
  roadContact: 'yes' | 'no' | 'partial';
  roadWidth: number;
  roadType: string;
  success: boolean;
}
```

**Validation:**
- Road width must be > 0 if `roadContact` is 'yes' or 'partial'
- Photo upload is optional

**State Update:**
```typescript
stepData.step5 = { roadContact, roadWidth, roadType, photos };
dataSources.roadWidth = { source: apiSuccess ? 'api' : 'manual' };
```

---

### STEP 6: Market/Transaction Data

**Purpose**: Display 공시지가 and 거래사례 (read-only, no judgment)

**UI Elements:**
```jsx
<Step6MarketData>
  <ProgressBar currentStep={6} totalSteps={8} />
  
  <InfoBanner variant="info">
    이 단계에서는 가격 판단을 하지 않습니다.
    시장 데이터 사실만 표시합니다.
  </InfoBanner>
  
  <DataCard title="공시지가">
    <Field label="공시지가 (원/㎡)" value={officialLandPrice.toLocaleString()} />
    <Field label="기준일" value={officialLandPriceDate} />
    <DataSourceBadge source="api" apiName="공시지가 API" />
  </DataCard>
  
  <TransactionTable>
    <TableHeader>거래사례 (최근 1년)</TableHeader>
    <Table>
      <thead>
        <tr>
          <th>거래일</th>
          <th>면적 (㎡)</th>
          <th>거래금액 (만원)</th>
          <th>거리 (m)</th>
        </tr>
      </thead>
      <tbody>
        {transactions.map(tx => (
          <tr key={tx.id}>
            <td>{tx.date}</td>
            <td>{tx.area}</td>
            <td>{tx.amount.toLocaleString()}</td>
            <td>{tx.distance}</td>
          </tr>
        ))}
      </tbody>
    </Table>
    {transactions.length === 0 && (
      <EmptyState>거래 사례가 부족합니다.</EmptyState>
    )}
  </TransactionTable>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button variant="primary" onClick={goNext}>확인하고 다음</Button>
  </ButtonGroup>
</Step6MarketData>
```

**API Call:**
```typescript
GET /api/m1/market-data
Request: { 
  coordinates: {lat, lon}, 
  area: number,
  radius: 1000 
}
Response: {
  officialLandPrice: number;
  officialLandPriceDate: string;
  transactions: Array<{
    date: string;
    area: number;
    amount: number;
    distance: number;
    address: string;
  }>;
  success: boolean;
}
```

**Validation:**
- No required fields (data display only)
- Can proceed even if no transactions found

**State Update:**
```typescript
stepData.step6 = { officialLandPrice, transactions };
dataSources.officialLandPrice = { source: 'api', apiName: 'Official Land Price API' };
```

---

### STEP 7: Comprehensive Verification

**Purpose**: Final review of all collected data before freeze

**UI Elements:**
```jsx
<Step7Verification>
  <ProgressBar currentStep={7} totalSteps={8} />
  
  <WarningBanner>
    <Icon>⚠️</Icon>
    <Text>
      확정 후에는 수정할 수 없습니다.
      모든 정보를 다시 한번 확인하세요.
    </Text>
  </WarningBanner>
  
  <VerificationTable>
    <Section title="STEP 1: 주소">
      <Row label="도로명 주소" value={step1.roadAddress} source={dataSources.address} />
      <Row label="지번 주소" value={step1.jibunAddress} source={dataSources.address} />
      <EditButton onClick={() => goToStep(1)} />
    </Section>
    
    <Section title="STEP 2: 위치·좌표">
      <Row label="위도" value={step2.coordinates.lat} source={dataSources.coordinates} />
      <Row label="경도" value={step2.coordinates.lon} source={dataSources.coordinates} />
      <Row label="행정동" value={step2.dong} source={dataSources.coordinates} />
      <EditButton onClick={() => goToStep(2)} />
    </Section>
    
    <Section title="STEP 3: 지번·면적">
      <Row label="본번-부번" value={`${step3.bonbun}-${step3.bubun}`} source={dataSources.bonbun} />
      <Row label="지목" value={step3.jimok} source={dataSources.jimok} />
      <Row label="대지면적" value={`${step3.area.toLocaleString()} ㎡`} source={dataSources.area} emphasis />
      <EditButton onClick={() => goToStep(3)} />
    </Section>
    
    <Section title="STEP 4: 법적·이용 정보">
      <Row label="용도지역" value={step4.zoneType} source={dataSources.zoneType} />
      <Row label="건폐율" value={`${step4.bcr}%`} source={dataSources.bcr} emphasis />
      <Row label="용적률" value={`${step4.far}%`} source={dataSources.far} emphasis />
      <Row label="이용상황" value={step4.landUse} source={dataSources.landUse} />
      <EditButton onClick={() => goToStep(4)} />
    </Section>
    
    <Section title="STEP 5: 도로·접근">
      <Row label="도로 폭" value={`${step5.roadWidth}m`} source={dataSources.roadWidth} />
      <Row label="도로 위치" value={step5.roadType} source={dataSources.roadType} />
      <EditButton onClick={() => goToStep(5)} />
    </Section>
    
    <Section title="STEP 6: 시장·거래">
      <Row label="공시지가" value={`${step6.officialLandPrice.toLocaleString()}원/㎡`} source={dataSources.officialLandPrice} />
      <Row label="거래사례" value={`${step6.transactions.length}건`} source={dataSources.transactions} />
      <EditButton onClick={() => goToStep(6)} />
    </Section>
  </VerificationTable>
  
  <FinalConfirmation>
    <Checkbox 
      checked={confirmChecked}
      onChange={setConfirmChecked}
    >
      모든 정보를 확인했으며, 확정에 동의합니다.
    </Checkbox>
  </FinalConfirmation>
  
  <ButtonGroup>
    <Button variant="secondary" onClick={goBack}>이전</Button>
    <Button 
      variant="danger" 
      onClick={handleFreeze}
      disabled={!confirmChecked}
    >
      모든 정보 확정 (변경 불가)
    </Button>
  </ButtonGroup>
</Step7Verification>
```

**API Call:**
```typescript
POST /api/m1/freeze-context
Request: {
  stepData: M1StepData;
  dataSources: Record<string, DataSource>;
}
Response: {
  contextId: string;
  landInfoContext: CanonicalLandContext;
  frozen: true;
  createdAt: string;
}
```

**Validation:**
- User must check confirmation checkbox
- All required fields from previous steps must be present
- Creates immutable `CanonicalLandContext` with `frozen=true`

**State Update:**
```typescript
// Create final CanonicalLandContext
const landContext = new CanonicalLandContext({
  parcel_id: generateParcelId(bonbun, bubun),
  address: roadAddress,
  road_address: roadAddress,
  coordinates: { lat, lon },
  sido, sigungu, dong,
  area_sqm: area,
  area_pyeong: area / 3.3058,
  land_category: jimok,
  land_use: landUse,
  zone_type: zoneType,
  zone_detail: zoneDetail,
  far: far,
  bcr: bcr,
  road_width: roadWidth,
  road_type: roadType,
  terrain_height: 0,
  terrain_shape: 'flat',
  regulations: regulations,
  restrictions: restrictions,
  data_source: 'step_based_collection',
  retrieval_date: new Date().toISOString(),
  frozen: true  // IMMUTABLE
});
```

---

### STEP 8: Context Freeze Completion

**Purpose**: Confirm freeze and transition to M2

**UI Elements:**
```jsx
<Step8Completion>
  <SuccessAnimation />
  
  <Message variant="success">
    <Icon>✅</Icon>
    <Title>토지 기본정보가 확정되었습니다.</Title>
  </Message>
  
  <ContextDetails>
    <Field label="Context ID" value={contextId} copyable />
    <Field label="확정 시각" value={createdAt} />
    <Field label="대지면적" value={`${area.toLocaleString()} ㎡`} />
    <Field label="용적률" value={`${far}%`} />
    <Field label="건폐율" value={`${bcr}%`} />
  </ContextDetails>
  
  <InfoCard>
    <Text>
      이 정보는 변경할 수 없으며, 
      이후 M2(감정평가) → M3(주택유형) → M4(용적검토) → M5(사업성) → M6(LH심사)
      단계에서 그대로 사용됩니다.
    </Text>
  </InfoCard>
  
  <ButtonGroup>
    <Button 
      variant="primary" 
      size="large"
      onClick={() => navigateTo('/m2-appraisal', { contextId })}
    >
      감정평가(M2)로 이동 →
    </Button>
    <Button 
      variant="secondary"
      onClick={() => navigateTo('/m1-start')}
    >
      다른 토지 분석
    </Button>
  </ButtonGroup>
</Step8Completion>
```

**Backend Action:**
- Save frozen `CanonicalLandContext` to database
- Generate unique `context_id`
- Set up for M2 pipeline entry

**State Update:**
```typescript
// Clear M1 session state
localStorage.removeItem('m1_draft_state');

// Set M2 entry point
sessionStorage.setItem('pipeline_context_id', contextId);
sessionStorage.setItem('pipeline_current_module', 'M2');
```

---

## 🔄 Integration with M4 V2 Pipeline

### Data Flow After M1 Freeze

```
[M1 FREEZE]
CanonicalLandContext (frozen=true)
    ↓
[M2 Appraisal]
AppraisalContext (uses M1 land_value, frozen=true)
    ↓
[M3 Housing Type]
HousingTypeContext (uses M1 location data)
    ↓
[M4 Capacity V2] ← ALREADY COMPLETE ✅
CapacityContextV2 (uses M1 area_sqm, far, bcr)
  - legal_capacity
  - incentive_capacity
  - massing_options (3-5)
  - unit_summary
  - parking_solutions (Alt A & B)
  - schematic_drawings (4 SVG files) ← NEW
    ↓
[M5 Feasibility]
FeasibilityContext (uses M4 incentive_capacity)
    ↓
[M6 LH Review]
LHReviewContext (uses M4 incentive_capacity.total_units)
```

### Key Integration Points

#### 1. M1 → M4 Data Mapping
```python
# M4 CapacityServiceV2.run() receives:
land_ctx: CanonicalLandContext  # From M1 freeze
housing_type_ctx: HousingTypeContext  # From M3

# M4 uses these M1 fields:
- land_ctx.area_sqm       → site area calculation
- land_ctx.far            → legal FAR capacity
- land_ctx.bcr            → building coverage ratio
- land_ctx.parcel_id      → schematic file naming
- land_ctx.zone_type      → incentive FAR calculation
```

#### 2. Immutability Enforcement
```python
# In M1 freeze endpoint
@dataclass(frozen=True)
class CanonicalLandContext:
    parcel_id: str
    area_sqm: float
    far: float
    bcr: float
    # ... all other fields
    frozen: bool = True  # Set at freeze time

# M4 receives read-only context
def run(land_ctx: CanonicalLandContext, ...):
    # Attempting to modify raises FrozenInstanceError
    # land_ctx.area_sqm = 2000  # ❌ Error
```

#### 3. API Endpoint Flow
```typescript
// Frontend flow after M1 completion
const response = await fetch('/api/m1/freeze-context', {
  method: 'POST',
  body: JSON.stringify(stepData)
});
const { contextId } = await response.json();

// Navigate to M2 with context
router.push(`/m2-appraisal?context_id=${contextId}`);

// M2 loads frozen context
const landContext = await fetch(`/api/m1/context/${contextId}`);

// Eventually reaches M4
const capacityResult = await fetch('/api/v4/pipeline/analyze', {
  method: 'POST',
  body: JSON.stringify({ parcel_id: contextId })
});
```

---

## 🧪 Testing Strategy

### Unit Tests

1. **Component Tests** (Jest + React Testing Library)
   ```typescript
   describe('Step1AddressInput', () => {
     it('should disable next button when address is empty');
     it('should show address suggestions on input');
     it('should validate selected address format');
   });
   
   describe('Step7Verification', () => {
     it('should display all collected data');
     it('should require confirmation checkbox');
     it('should call freeze API on confirm');
   });
   ```

2. **State Management Tests**
   ```typescript
   describe('M1StateManager', () => {
     it('should save step data to localStorage');
     it('should recover state after refresh');
     it('should clear state after freeze');
   });
   ```

### Integration Tests

1. **Full Step Flow**
   ```typescript
   describe('M1 Full Flow', () => {
     it('should complete all 8 steps with API success');
     it('should handle API failures gracefully');
     it('should allow manual input fallback');
     it('should create frozen CanonicalLandContext');
   });
   ```

2. **M1 → M4 Pipeline**
   ```typescript
   describe('M1 to M4 Integration', () => {
     it('should pass frozen context to M4');
     it('should prevent context modification');
     it('should generate schematics with M1 data');
   });
   ```

### E2E Tests (Cypress/Playwright)

```typescript
describe('M1 STEP-Based UX', () => {
  it('should complete full user journey', () => {
    cy.visit('/m1-start');
    cy.findByText('주소 입력 시작').click();
    
    // STEP 1: Address
    cy.findByLabelText('주소 입력').type('서울시 강남구 역삼동 123-45');
    cy.findByText('다음 단계').click();
    
    // STEP 2: Location
    cy.get('[data-testid="map-container"]').should('be.visible');
    cy.findByText('확인하고 다음').click();
    
    // ... continue through all steps
    
    // STEP 7: Verification
    cy.findByLabelText('모든 정보를 확인했으며').check();
    cy.findByText('모든 정보 확정').click();
    
    // STEP 8: Completion
    cy.findByText('토지 기본정보가 확정되었습니다').should('be.visible');
    cy.findByText('감정평가(M2)로 이동').click();
    
    // Verify navigation to M2
    cy.url().should('include', '/m2-appraisal');
  });
});
```

---

## 📱 Responsive Design

### Mobile Adaptations

1. **Progress Bar**: Numeric indicator (e.g., "2/8")
2. **Map**: Full-screen modal on small screens
3. **Data Grid**: Vertical layout (label over value)
4. **Buttons**: Full-width on mobile
5. **Photo Upload**: Camera integration

### Accessibility

- ARIA labels for all form fields
- Keyboard navigation support (Tab, Enter, Esc)
- Screen reader announcements for step changes
- High contrast mode support
- Focus indicators

---

## 🚀 Deployment Checklist

### Backend Requirements

- [ ] Create `/api/m1/address/search` endpoint
- [ ] Create `/api/m1/geocode` endpoint
- [ ] Create `/api/m1/cadastral` endpoint
- [ ] Create `/api/m1/land-use` endpoint
- [ ] Create `/api/m1/road-info` endpoint
- [ ] Create `/api/m1/market-data` endpoint
- [ ] Create `/api/m1/parse-pdf` endpoint
- [ ] Create `/api/m1/freeze-context` endpoint (returns CanonicalLandContext)
- [ ] Create `/api/m1/context/{id}` GET endpoint

### Frontend Requirements

- [ ] Implement 8 STEP components
- [ ] Implement progress bar component
- [ ] Implement data source badge component
- [ ] Implement auto-save mechanism
- [ ] Integrate Kakao Map API
- [ ] Implement PDF upload/parsing
- [ ] Implement photo upload
- [ ] Add state persistence (localStorage)
- [ ] Add error boundaries
- [ ] Add loading states

### Testing Requirements

- [ ] Write unit tests for all components
- [ ] Write integration tests for step flow
- [ ] Write E2E tests for full journey
- [ ] Test API failure scenarios
- [ ] Test browser refresh recovery
- [ ] Test mobile responsiveness
- [ ] Test accessibility compliance

---

## 📊 Success Metrics

### UX Metrics

- **Completion Rate**: % of users who reach STEP 8
- **Drop-off Rate by Step**: Identify problematic steps
- **Time per Step**: Average completion time
- **API vs Manual Input Ratio**: Effectiveness of auto-fill
- **Edit Rate**: How often users go back to edit

### Technical Metrics

- **API Success Rate**: % of successful API calls
- **Context Freeze Success Rate**: % of successful freezes
- **M1 → M2 Handoff Success**: % of successful transitions
- **Error Rate by Step**: Identify failure points

### Business Metrics

- **User Satisfaction**: Survey after M1 completion
- **Data Accuracy**: Comparison with source data
- **Time Savings**: vs. manual entry

---

## 📚 Documentation

### User Guide

Create `/docs/m1-user-guide.md`:
- Screenshot walkthrough of all 8 steps
- Common issues and solutions
- Tips for faster completion
- FAQs

### Developer Guide

Create `/docs/m1-developer-guide.md`:
- Component architecture
- State management patterns
- API integration guide
- Testing strategies

---

## 🎯 Next Steps

1. **Review and Approve** this implementation plan
2. **Create Jira tickets** for each STEP component
3. **Set up frontend project** structure
4. **Design mockups** for all 8 steps
5. **Implement backend APIs** (address, geocode, cadastral, etc.)
6. **Implement STEP components** one by one
7. **Write tests** for each component
8. **Integration testing** with M4 V2 pipeline
9. **UAT** with real users
10. **Production deployment**

---

## ✅ Sign-Off

**M1 STEP-Based UX Implementation Plan: READY**

This plan provides:
- [x] Complete STEP-by-step specification
- [x] UI/UX design for all 8 steps
- [x] API endpoint requirements
- [x] Integration with M4 V2 pipeline
- [x] Testing strategy
- [x] Deployment checklist

**Ready for development kickoff!** 🚀

---

**Date**: 2025-12-17  
**Author**: ZeroSite Architecture Team  
**Status**: Planning Complete, Awaiting Approval
