/**
 * STEP 6: Market Data (시장 정보)
 * ================================
 * Fetch land price and transaction history
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { MarketDataResponse, Transaction, DataSourceInfo } from '../../types/m1.types';
import { DataSourceBadge } from '../shared/DataSourceBadge';

interface Step6Props {
  onNext: (data: MarketDataResponse, source: DataSourceInfo) => void;
  onBack: () => void;
  coordinates: { lat: number; lon: number };
  area: number;
  autoFetch?: boolean;
}

export const Step6MarketData: React.FC<Step6Props> = ({
  onNext,
  onBack,
  coordinates,
  area,
  autoFetch = true,
}) => {
  const [loading, setLoading] = useState(false);
  const [marketData, setMarketData] = useState<MarketDataResponse | null>(null);
  const [dataSource, setDataSource] = useState<DataSourceInfo | null>(null);
  const [radius, setRadius] = useState(1000);
  
  // 거래사례 분리: appraisal용(M2 계산) vs reference용(보고서)
  const [selectedForAppraisal, setSelectedForAppraisal] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (autoFetch && coordinates && area) {
      fetchMarketData();
    }
  }, [autoFetch, coordinates, area]);

  const fetchMarketData = async () => {
    setLoading(true);
    const result = await m1ApiService.getMarketData(coordinates, area, radius);
    setLoading(false);

    if (result.success) {
      setMarketData(result.data);
      setDataSource({
        source: 'api',
        apiName: '국토교통부 실거래가 API',
        timestamp: new Date().toISOString(),
      });
    } else {
      alert('시장 정보 조회 실패: ' + result.error.detail);
    }
  };

  const handleSubmit = () => {
    if (marketData && dataSource) {
      onNext(marketData, dataSource);
    }
  };

  const formatPrice = (amount: number): string => {
    if (amount >= 100000000) {
      const eok = Math.floor(amount / 100000000);
      const man = Math.floor((amount % 100000000) / 10000);
      return man > 0 ? `${eok}억 ${man}만원` : `${eok}억원`;
    } else if (amount >= 10000) {
      return `${Math.floor(amount / 10000)}만원`;
    }
    return `${amount}원`;
  };

  const formatDate = (dateStr: string): string => {
    return dateStr.replace(/(\d{4})(\d{2})(\d{2})/, '$1년 $2월 $3일');
  };

  return (
    <div className="step-container">
      <h2>시장 정보 (STEP 6)</h2>
      <p>공시지가 및 실거래가 정보를 확인합니다.</p>

      {dataSource && <DataSourceBadge {...dataSource} />}

      <div className="form-group">
        <label>검색 반경 (m)</label>
        <input
          type="number"
          value={radius}
          onChange={(e) => setRadius(parseInt(e.target.value))}
          min={100}
          max={5000}
          step={100}
        />
        <button onClick={fetchMarketData} disabled={loading} style={{ marginLeft: '10px' }}>
          재조회
        </button>
      </div>

      {loading && <p>조회 중...</p>}

      {marketData && (
        <div className="market-data-summary">
          <div className="price-info" style={{ marginBottom: '20px', padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
            <h3 style={{ marginTop: 0 }}>공시지가</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', margin: '10px 0' }}>
              {marketData.official_land_price ? formatPrice(marketData.official_land_price) : 'N/A'}
            </p>
            {marketData.official_land_price_date && (
              <p style={{ fontSize: '12px', color: '#666' }}>
                기준일: {formatDate(marketData.official_land_price_date)}
              </p>
            )}
            {marketData.official_land_price && area && (
              <p style={{ fontSize: '14px', color: '#666' }}>
                평당 약 {formatPrice(Math.floor(marketData.official_land_price / (area / 3.3058)))}
              </p>
            )}
          </div>

          <div className="transactions-info">
            <h3>인근 실거래가 ({marketData.transactions.length}건)</h3>
            <p style={{ fontSize: '13px', color: '#666', marginBottom: '10px' }}>
              💡 감정평가 계산용으로 사용할 거래사례를 선택하세요 (최대 5건)
            </p>
            {marketData.transactions.length === 0 ? (
              <p style={{ color: '#999' }}>실거래 정보가 없습니다.</p>
            ) : (
              <div className="transactions-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {marketData.transactions.map((tx: Transaction, idx: number) => {
                  const isSelected = selectedForAppraisal.has(idx);
                  const canSelect = isSelected || selectedForAppraisal.size < 5;
                  
                  return (
                    <div
                      key={idx}
                      style={{
                        padding: '10px',
                        marginBottom: '10px',
                        border: isSelected ? '2px solid #4CAF50' : '1px solid #ddd',
                        borderRadius: '4px',
                        background: isSelected ? '#e8f5e9' : '#fff',
                        cursor: canSelect ? 'pointer' : 'not-allowed',
                        opacity: canSelect ? 1 : 0.6,
                      }}
                      onClick={() => {
                        if (canSelect) {
                          setSelectedForAppraisal(prev => {
                            const newSet = new Set(prev);
                            if (newSet.has(idx)) {
                              newSet.delete(idx);
                            } else {
                              newSet.add(idx);
                            }
                            return newSet;
                          });
                        }
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => {}}
                          style={{ marginRight: '10px' }}
                          disabled={!canSelect}
                        />
                        <div style={{ flex: 1, display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ fontWeight: 'bold' }}>{formatPrice(tx.amount)}</span>
                          <span style={{ fontSize: '12px', color: '#666' }}>{formatDate(tx.date)}</span>
                        </div>
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginLeft: '30px' }}>
                        면적: {tx.area.toLocaleString()}㎡ ({(tx.area / 3.3058).toFixed(1)}평)
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginLeft: '30px' }}>거리: {tx.distance}m</div>
                      {tx.address && (
                        <div style={{ fontSize: '11px', color: '#999', marginTop: '3px', marginLeft: '30px' }}>{tx.address}</div>
                      )}
                      {isSelected && (
                        <div style={{ fontSize: '11px', color: '#4CAF50', marginTop: '5px', marginLeft: '30px' }}>
                          ✓ M2 감정평가 계산에 사용됨
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            <div style={{ marginTop: '10px', fontSize: '13px', color: '#666' }}>
              선택된 거래사례: {selectedForAppraisal.size}/5건
            </div>
          </div>
        </div>
      )}

      <div className="button-group" style={{ marginTop: '20px' }}>
        <button onClick={onBack}>이전</button>
        <button onClick={handleSubmit} disabled={!marketData}>
          {loading ? '조회 중...' : '다음'}
        </button>
      </div>
    </div>
  );
};

export default Step6MarketData;
