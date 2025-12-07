# Phase 4 - Day 1-2: Risk Matrix 5×5 Interactive Grid

**Status**: 🚀 Starting Now  
**Priority**: 🔴 CRITICAL  
**Timeline**: 2 days  
**Component**: RiskMatrixGrid

---

## 🎯 Objective

Build an interactive 5×5 Risk Matrix visualization that displays all 10 risks with:
- Color-coded risk levels (CRITICAL/HIGH/MEDIUM/LOW)
- Interactive hover tooltips
- Click to expand risk details + 3 response strategies
- Responsive design

---

## 📊 Component Specifications

### Visual Design

```
        IMPACT (영향도) →
        1    2    3    4    5
    ┌────┬────┬────┬────┬────┐
  5 │ 🟡 │ 🟠 │ 🟠 │ 🔴 │ 🔴 │
    ├────┼────┼────┼────┼────┤
  4 │ 🟡 │ 🟡 │ 🟠 │ 🟠 │ 🔴 │
P   ├────┼────┼────┼────┼────┤
R 3 │ 🟢 │ 🟡 │ 🟡 │ 🟠 │ 🟠 │
O   ├────┼────┼────┼────┼────┤
B 2 │ 🟢 │ 🟢 │ 🟡 │ 🟡 │ 🟠 │
A   ├────┼────┼────┼────┼────┤
B 1 │ 🟢 │ 🟢 │ 🟢 │ 🟡 │ 🟡 │
L   └────┴────┴────┴────┴────┘
I
T
Y
```

### Color Scheme
- 🔴 **CRITICAL**: rgb(239, 68, 68) - Score ≥ 20
- 🟠 **HIGH**: rgb(249, 115, 22) - Score 12-19
- 🟡 **MEDIUM**: rgb(234, 179, 8) - Score 6-11
- 🟢 **LOW**: rgb(34, 197, 94) - Score < 6

### Data Structure

```typescript
interface Risk {
  id: string;              // "R01", "R02", etc.
  name: string;            // "재무 타당성 부족"
  name_en: string;         // "Financial Viability Risk"
  category: string;        // "financial", "legal", etc.
  category_kr: string;     // "재무/자금"
  probability: number;     // 1-5
  impact: number;          // 1-5
  risk_score: number;      // probability × impact
  risk_level: string;      // "CRITICAL", "HIGH", etc.
  risk_level_kr: string;   // "심각", "높음", etc.
  description: string;     // Risk description
  response_strategies: string[];  // Array of 3 strategies
}

interface RiskMatrixProps {
  risks: Risk[];
  onRiskClick?: (risk: Risk) => void;
}
```

---

## 🛠️ Implementation Approaches

### Option 1: Pure React + CSS Grid (Simple)
**Pros**: 
- Fast to implement
- No external dependencies
- Full control over styling
- Lightweight

**Cons**:
- Manual positioning logic
- More CSS work

**Time**: ~4-6 hours

---

### Option 2: React + Recharts (Recommended)
**Pros**:
- Professional library
- Built-in responsiveness
- Easy customization
- Good documentation

**Cons**:
- Slight learning curve
- Larger bundle size

**Time**: ~6-8 hours

---

### Option 3: React + D3.js (Advanced)
**Pros**:
- Maximum customization
- Advanced interactions
- Industry standard

**Cons**:
- Steeper learning curve
- More complex code
- Longer development time

**Time**: ~10-12 hours

---

## ✅ Recommended: Option 2 (React + Recharts)

Good balance of power, ease of use, and development speed.

---

## 📝 Step-by-Step Implementation Plan

### Step 1: Setup React Component Structure (30 min)

```bash
# Create component directory
mkdir -p frontend/src/components/visualizations/RiskMatrix

# Create files
touch frontend/src/components/visualizations/RiskMatrix/index.tsx
touch frontend/src/components/visualizations/RiskMatrix/RiskMatrixGrid.tsx
touch frontend/src/components/visualizations/RiskMatrix/RiskCell.tsx
touch frontend/src/components/visualizations/RiskMatrix/RiskModal.tsx
touch frontend/src/components/visualizations/RiskMatrix/styles.module.css
```

### Step 2: Install Dependencies (10 min)

```bash
cd frontend
npm install recharts
npm install @types/recharts --save-dev
npm install clsx  # For conditional classNames
```

### Step 3: Create RiskMatrixGrid Component (2 hours)

**File**: `RiskMatrixGrid.tsx`

```typescript
import React, { useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { RiskModal } from './RiskModal';
import styles from './styles.module.css';

interface Risk {
  id: string;
  name: string;
  category: string;
  probability: number;
  impact: number;
  risk_score: number;
  risk_level: string;
  description: string;
  response_strategies: string[];
}

interface RiskMatrixGridProps {
  risks: Risk[];
}

export const RiskMatrixGrid: React.FC<RiskMatrixGridProps> = ({ risks }) => {
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);

  // Prepare data for ScatterChart
  const matrixData = risks.map(risk => ({
    x: risk.probability,
    y: risk.impact,
    z: risk.risk_score,
    risk: risk,
    fill: getRiskColor(risk.risk_score)
  }));

  const getRiskColor = (score: number): string => {
    if (score >= 20) return '#EF4444'; // CRITICAL - Red
    if (score >= 12) return '#F97316'; // HIGH - Orange
    if (score >= 6) return '#EAB308';  // MEDIUM - Yellow
    return '#22C55E';                  // LOW - Green
  };

  const handleCellClick = (data: any) => {
    setSelectedRisk(data.risk);
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Risk Matrix (5×5)</h2>
      
      <div className={styles.legend}>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{backgroundColor: '#EF4444'}}></span>
          CRITICAL (≥20)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{backgroundColor: '#F97316'}}></span>
          HIGH (12-19)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{backgroundColor: '#EAB308'}}></span>
          MEDIUM (6-11)
        </span>
        <span className={styles.legendItem}>
          <span className={styles.dot} style={{backgroundColor: '#22C55E'}}></span>
          LOW (&lt;6)
        </span>
      </div>

      <ResponsiveContainer width="100%" height={500}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Probability" 
            domain={[0, 6]}
            ticks={[1, 2, 3, 4, 5]}
            label={{ value: '발생확률 (Probability)', position: 'bottom' }}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Impact" 
            domain={[0, 6]}
            ticks={[1, 2, 3, 4, 5]}
            label={{ value: '영향도 (Impact)', angle: -90, position: 'left' }}
          />
          <ZAxis type="number" dataKey="z" range={[100, 400]} />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }}
            content={({ payload }) => {
              if (payload && payload.length > 0) {
                const data = payload[0].payload;
                return (
                  <div className={styles.tooltip}>
                    <p><strong>{data.risk.name}</strong></p>
                    <p>Category: {data.risk.category}</p>
                    <p>Score: {data.risk.risk_score}</p>
                    <p>Level: {data.risk.risk_level}</p>
                    <p style={{fontSize: '0.85em', marginTop: '8px'}}>
                      Click for details
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Scatter 
            data={matrixData} 
            onClick={handleCellClick}
            style={{ cursor: 'pointer' }}
          >
            {matrixData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      {selectedRisk && (
        <RiskModal 
          risk={selectedRisk} 
          onClose={() => setSelectedRisk(null)} 
        />
      )}
    </div>
  );
};
```

### Step 4: Create RiskModal Component (1 hour)

**File**: `RiskModal.tsx`

```typescript
import React from 'react';
import styles from './styles.module.css';

interface Risk {
  id: string;
  name: string;
  name_en: string;
  category_kr: string;
  risk_level_kr: string;
  description: string;
  response_strategies: string[];
}

interface RiskModalProps {
  risk: Risk;
  onClose: () => void;
}

export const RiskModal: React.FC<RiskModalProps> = ({ risk, onClose }) => {
  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>×</button>
        
        <h2>{risk.name}</h2>
        <p className={styles.nameEn}>{risk.name_en}</p>
        
        <div className={styles.riskDetails}>
          <span className={styles.badge}>{risk.category_kr}</span>
          <span className={styles.badge}>{risk.risk_level_kr}</span>
        </div>

        <div className={styles.description}>
          <h3>Risk Description</h3>
          <p>{risk.description}</p>
        </div>

        <div className={styles.strategies}>
          <h3>Response Strategies</h3>
          <ol>
            {risk.response_strategies.map((strategy, index) => (
              <li key={index}>{strategy}</li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
};
```

### Step 5: Add Styles (1 hour)

**File**: `styles.module.css`

```css
.container {
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #1f2937;
}

.legend {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.legendItem {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.tooltip {
  background: white;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Modal Styles */
.modalOverlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modalContent {
  background: white;
  padding: 32px;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.closeButton {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #6b7280;
}

.closeButton:hover {
  color: #1f2937;
}

.nameEn {
  color: #6b7280;
  font-style: italic;
  margin-bottom: 16px;
}

.riskDetails {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.badge {
  background: #e5e7eb;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
}

.description {
  margin-bottom: 24px;
}

.description h3,
.strategies h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.strategies ol {
  padding-left: 20px;
}

.strategies li {
  margin-bottom: 12px;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 16px;
  }
  
  .modalContent {
    padding: 24px;
  }
}
```

### Step 6: Connect to Backend API (30 min)

**File**: `api/risks.ts`

```typescript
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const fetchRiskMatrix = async (address: string, landArea: number) => {
  const response = await axios.post(`${API_BASE}/api/v13/report/expert`, {
    address,
    land_area_sqm: landArea
  });
  
  return response.data.risk_analysis.enhanced.top_10_risks;
};
```

### Step 7: Create Container Page (30 min)

**File**: `pages/RiskMatrixPage.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { RiskMatrixGrid } from '../components/visualizations/RiskMatrix';
import { fetchRiskMatrix } from '../api/risks';

export const RiskMatrixPage: React.FC = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchRiskMatrix('서울시 강남구 역삼동 123', 500);
        setRisks(data);
      } catch (error) {
        console.error('Failed to load risks:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '24px' }}>
      <RiskMatrixGrid risks={risks} />
    </div>
  );
};
```

### Step 8: Testing (1 hour)

- [ ] Unit tests for RiskMatrixGrid
- [ ] Unit tests for RiskModal
- [ ] Integration test with mock data
- [ ] Visual regression test
- [ ] Accessibility test
- [ ] Performance test

### Step 9: Documentation (30 min)

- [ ] Component API documentation
- [ ] Usage examples
- [ ] Storybook story
- [ ] Props documentation

---

## 🧪 Testing Checklist

### Functional Tests
- [ ] Matrix displays correct 5×5 grid
- [ ] Colors match risk levels correctly
- [ ] Hover tooltip shows risk details
- [ ] Click opens modal with full details
- [ ] Modal shows 3 response strategies
- [ ] Close modal button works
- [ ] Click outside modal closes it

### Responsive Tests
- [ ] Desktop (1920x1080): Full layout
- [ ] Tablet (768x1024): Adjusted layout
- [ ] Mobile (375x667): Stacked layout
- [ ] Matrix scales properly
- [ ] Modal is scrollable on small screens

### Accessibility Tests
- [ ] Keyboard navigation works
- [ ] Screen reader announces risk levels
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] ARIA labels present

### Performance Tests
- [ ] Initial render <500ms
- [ ] Hover tooltip <50ms
- [ ] Modal open <100ms
- [ ] Re-renders optimized

---

## 📊 Sample Data for Testing

```json
{
  "risks": [
    {
      "id": "R01",
      "name": "재무 타당성 부족",
      "name_en": "Financial Viability Risk",
      "category": "financial",
      "category_kr": "재무/자금",
      "probability": 5,
      "impact": 5,
      "risk_score": 25,
      "risk_level": "CRITICAL",
      "risk_level_kr": "심각",
      "description": "NPV -131.7억원으로 사업 수익성 확보 실패. 투자 회수 불가능 위험",
      "response_strategies": [
        "사업 규모 확대 (필지 추가 매입) 또는 건축 규모 증대로 수익성 개선",
        "공사비 절감 방안 검토 (설계 최적화, VE 적용)",
        "임대료 상향 조정 또는 부대사업 도입으로 수익원 다각화"
      ]
    }
  ]
}
```

---

## ✅ Definition of Done

- [ ] Component renders correctly in all viewports
- [ ] All interactive features work
- [ ] Color scheme matches specification
- [ ] Tooltips show accurate information
- [ ] Modal displays full risk details
- [ ] Code passes ESLint
- [ ] Unit tests pass (>80% coverage)
- [ ] Accessibility audit passes (>90 score)
- [ ] Performance benchmarks met
- [ ] Code reviewed and approved
- [ ] Documentation complete
- [ ] Merged to main branch

---

## 🎯 Success Criteria

**This component will be considered successful when:**

1. Users can quickly identify high-risk areas
2. Interactive tooltips provide immediate context
3. Modal gives comprehensive risk details
4. Mobile users have full functionality
5. Loading and interaction feel instant
6. Visual design is professional and clear

---

**Estimated Total Time**: 6-8 hours (1-2 days with testing)

**Start Date**: 2025-12-06  
**Target Completion**: 2025-12-07

Let's build it! 🚀
