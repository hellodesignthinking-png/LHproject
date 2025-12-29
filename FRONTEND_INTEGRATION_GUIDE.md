# 🎨 ZeroSite v6.5 - Frontend Integration Guide

**작성일**: 2025-12-29  
**대상**: React Frontend Developers  
**API Version**: v3.0.0

---

## 🚀 API Endpoints

### Base URL
```
https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai
```

### Module Endpoints (REAL APPRAISAL STANDARD)

#### M2: 토지감정평가
```javascript
GET /demo/m2_classic
```
**Response**: HTML report (26 KB)  
**Content**: 토지감정평가 보고서 (거래사례 중심, 시가 기준)

#### M3: 공급 유형 판단
```javascript
GET /demo/m3_supply_type
```
**Response**: HTML report (20 KB)  
**Content**: 공급 유형 선정 보고서 (신혼희망타운, 청년주택 등)

#### M4: 건축 규모 판단
```javascript
GET /demo/m4_building_scale
```
**Response**: HTML report (20 KB)  
**Content**: 건축 규모 판단 보고서 (세대수, 주차대수)

#### M5: 사업성 분석
```javascript
GET /demo/m5_feasibility
```
**Response**: HTML report (8 KB)  
**Content**: 사업성 분석 보고서 (PASS/FAIL)

#### M6: LH 종합 판단
```javascript
GET /demo/m6_comprehensive
```
**Response**: HTML report (2 KB)  
**Content**: LH 종합 판단 보고서 (최종 PASS/FAIL, 종합 점수)

---

## 📦 React Component Example

### Basic Usage

```jsx
import React, { useState } from 'react';

const ReportViewer = () => {
  const [selectedModule, setSelectedModule] = useState('m2_classic');
  const baseUrl = 'https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai';

  const modules = [
    { id: 'm2_classic', name: 'M2: 토지감정평가', icon: '📊' },
    { id: 'm3_supply_type', name: 'M3: 공급 유형 판단', icon: '🏘️' },
    { id: 'm4_building_scale', name: 'M4: 건축 규모 판단', icon: '🏗️' },
    { id: 'm5_feasibility', name: 'M5: 사업성 분석', icon: '💰' },
    { id: 'm6_comprehensive', name: 'M6: LH 종합 판단', icon: '✅' }
  ];

  return (
    <div className="report-viewer">
      <div className="module-selector">
        {modules.map(module => (
          <button
            key={module.id}
            onClick={() => setSelectedModule(module.id)}
            className={selectedModule === module.id ? 'active' : ''}
          >
            {module.icon} {module.name}
          </button>
        ))}
      </div>

      <iframe
        src={`${baseUrl}/demo/${selectedModule}`}
        title={`Report ${selectedModule}`}
        style={{
          width: '100%',
          height: '800px',
          border: '1px solid #dee2e6',
          borderRadius: '8px'
        }}
      />
    </div>
  );
};

export default ReportViewer;
```

### Advanced: Fetch & Display

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ReportDownloader = ({ moduleId }) => {
  const [loading, setLoading] = useState(false);
  const [reportHtml, setReportHtml] = useState(null);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/demo/${moduleId}`,
        { responseType: 'text' }
      );
      setReportHtml(response.data);
    } catch (error) {
      console.error('Failed to fetch report:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [moduleId]);

  if (loading) return <div>Loading report...</div>;

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: reportHtml }} />
    </div>
  );
};

export default ReportDownloader;
```

### Download as PDF

```jsx
import React from 'react';

const DownloadButton = ({ moduleId, moduleName }) => {
  const handleDownload = () => {
    const url = `https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/demo/${moduleId}`;
    
    // Method 1: Direct link
    window.open(url, '_blank');

    // Method 2: Trigger browser download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${moduleName}_Report.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button onClick={handleDownload} className="download-btn">
      📥 Download {moduleName} Report
    </button>
  );
};

export default DownloadButton;
```

---

## 🎨 Styling Guide

### Module Cards

```jsx
const ModuleCard = ({ module, onSelect }) => (
  <div 
    className="module-card"
    onClick={() => onSelect(module.id)}
    style={{
      background: 'white',
      border: '2px solid #0066cc',
      borderRadius: '12px',
      padding: '24px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      ':hover': {
        transform: 'translateY(-4px)',
        boxShadow: '0 8px 16px rgba(0,102,204,0.2)'
      }
    }}
  >
    <div style={{ fontSize: '48px', marginBottom: '16px' }}>
      {module.icon}
    </div>
    <h3 style={{ color: '#2c3e50', marginBottom: '8px' }}>
      {module.name}
    </h3>
    <p style={{ color: '#6c757d', fontSize: '14px' }}>
      {module.description}
    </p>
  </div>
);
```

### CSS Styles

```css
/* Module Grid */
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 24px;
}

/* Module Card */
.module-card {
  background: white;
  border: 2px solid #0066cc;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 102, 204, 0.2);
}

.module-card.active {
  background: #e8f4f8;
  border-color: #0044aa;
}

/* Report Viewer */
.report-viewer {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
}

.report-iframe {
  width: 100%;
  height: 800px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  background: white;
}

/* Loading Spinner */
.loading-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0066cc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## 📊 Module Data Structure

### M2: Land Appraisal
```typescript
interface M2Report {
  report_id: string;
  address: string;
  land_area_sqm: number;
  land_area_pyeong: number;
  total_value: number;
  price_per_sqm: number;
  price_per_pyeong: number;
  confidence_level: string;
  confidence_score: number;
}
```

### M3: Supply Type
```typescript
interface M3Report {
  report_id: string;
  project_address: string;
  selected_supply_type: string;
  policy_target_score: number;
  demand_score: number;
  total_score: number;
}
```

### M4: Building Scale
```typescript
interface M4Report {
  report_id: string;
  project_address: string;
  selected_scale: string;
  total_units: number;
  legal_score: number;
  review_score: number;
  total_score: number;
}
```

### M5: Feasibility
```typescript
interface M5Report {
  report_id: string;
  project_address: string;
  feasibility_result: 'PASS' | 'FAIL';
  total_cost: number;
  lh_purchase_price: number;
  profit_rate: number;
  total_score: number;
}
```

### M6: Comprehensive
```typescript
interface M6Report {
  final_decision: 'PASS' | 'FAIL';
  total_score: number;
  m3_score: number;
  m4_score: number;
  m5_score: number;
}
```

---

## 🔐 API Authentication (Future)

현재는 인증이 필요 없지만, 향후 프로덕션 배포 시 추가 예정:

```javascript
// Example with Bearer Token
const fetchReport = async (moduleId, token) => {
  const response = await fetch(
    `${baseUrl}/demo/${moduleId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.text();
};
```

---

## 🚀 Deployment Checklist

### Frontend Integration Steps

1. **Environment Variables**
```javascript
// .env.production
REACT_APP_API_BASE_URL=https://your-production-api.com
REACT_APP_API_VERSION=v3.0.0
```

2. **API Client Setup**
```javascript
// src/api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default apiClient;
```

3. **Module Service**
```javascript
// src/services/reportService.js
import apiClient from '../api/client';

export const reportService = {
  getReport: async (moduleId) => {
    const response = await apiClient.get(`/demo/${moduleId}`);
    return response.data;
  },
  
  downloadReport: (moduleId, filename) => {
    const url = `${process.env.REACT_APP_API_BASE_URL}/demo/${moduleId}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  }
};
```

---

## 📱 Mobile Responsive

```css
/* Mobile First */
@media (max-width: 768px) {
  .module-grid {
    grid-template-columns: 1fr;
  }

  .report-iframe {
    height: 600px;
  }

  .module-card {
    padding: 16px;
  }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .module-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 🧪 Testing

```javascript
// Example Jest test
describe('ReportViewer', () => {
  it('should render all module buttons', () => {
    const { getAllByRole } = render(<ReportViewer />);
    const buttons = getAllByRole('button');
    expect(buttons).toHaveLength(5); // M2-M6
  });

  it('should load report on button click', async () => {
    const { getByText, getByTitle } = render(<ReportViewer />);
    const m2Button = getByText(/M2: 토지감정평가/);
    
    fireEvent.click(m2Button);
    
    await waitFor(() => {
      expect(getByTitle(/Report m2_classic/)).toBeInTheDocument();
    });
  });
});
```

---

## 📊 Performance Optimization

### Lazy Loading

```jsx
import React, { lazy, Suspense } from 'react';

const ReportViewer = lazy(() => import('./components/ReportViewer'));

const App = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <ReportViewer />
  </Suspense>
);
```

### Caching

```javascript
// Using React Query
import { useQuery } from 'react-query';

const useReport = (moduleId) => {
  return useQuery(
    ['report', moduleId],
    () => fetchReport(moduleId),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );
};
```

---

## 🔗 Useful Links

- **API Documentation**: https://8091-..../docs
- **GitHub Repository**: https://github.com/hellodesignthinking-png/LHproject
- **Branch**: feature/expert-report-generator

---

**작성자**: ZeroSite Development Team  
**버전**: 1.0.0  
**최종 업데이트**: 2025-12-29
