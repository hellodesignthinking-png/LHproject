/**
 * STEP 1: Address Input
 * ======================
 * Search and select address
 */

import React, { useState } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { AddressSuggestion } from '../../types/m1.types';
import './Step1AddressInput.css';

interface Step1Props {
  onNext: (address: AddressSuggestion) => void;
  onBack: () => void;
}

export const Step1AddressInput: React.FC<Step1Props> = ({ onNext, onBack }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (query.length < 3) {
      alert('주소를 3자 이상 입력해주세요.');
      return;
    }
    
    console.log('🔍 주소 검색 시작:', query);
    console.log('🔧 Config check:', {
      BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
      API_URL: `${import.meta.env.VITE_BACKEND_URL || 'https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai'}/api/m1/address/search`
    });
    setLoading(true);
    setSearched(false);
    
    try {
      const result = await m1ApiService.searchAddress(query);
      console.log('📝 검색 결과:', result);
      
      if (result.success && result.data && result.data.suggestions) {
        setSuggestions(result.data.suggestions);
        setSearched(true);
        console.log('✅ 검색 성공:', result.data.suggestions.length, '개 결과');
        
        // ⚠️ CRITICAL: Warn user if using mock data
        if (result.data.using_mock_data) {
          console.warn('⚠️ MOCK DATA: API key not provided - using development mock data');
          alert(
            '⚠️ 개발 모드: Kakao API 키가 없어 Mock 데이터를 반환합니다.\n\n' +
            '실제 주소 검색을 위해서는:\n' +
            '1. Step 0에서 Kakao API 키를 입력하거나\n' +
            '2. 관리자에게 API 키 설정을 요청하세요.\n\n' +
            '현재는 샘플 서울 주소만 검색됩니다.'
          );
        }
      } else {
        // Handle API errors
        setSuggestions([]);
        setSearched(true);
        
        if (!result.success && result.error) {
          const errorMsg = result.error.detail;
          if (typeof errorMsg === 'string') {
            console.error('❌ API 오류:', errorMsg);
            alert(`주소 검색 실패: ${errorMsg}`);
          } else if (Array.isArray(errorMsg)) {
            // Pydantic validation error format
            const msgs = errorMsg.map((e: any) => e.msg || e).join('\n');
            console.error('❌ 입력 검증 오류:', msgs);
            alert(`입력 오류:\n${msgs}`);
          } else {
            console.warn('⚠️ 검색 결과 없음');
            alert('검색 결과가 없습니다. 다른 주소를 입력해주세요.');
          }
        } else {
          console.warn('⚠️ 검색 결과 없음');
        }
      }
    } catch (error) {
      console.error('❌ 검색 오류:', error);
      alert('주소 검색 중 오류가 발생했습니다.\n네트워크 연결을 확인해주세요.');
      setSuggestions([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAddress = (address: AddressSuggestion) => {
    console.log('✅ 주소 선택:', address);
    onNext(address);
  };

  return (
    <div className="step1-container">
      <div className="step1-header">
        <h2 className="step1-title">
          <i className="fas fa-map-marker-alt" style={{ marginRight: '12px', color: '#4CAF50' }}></i>
          주소 입력
        </h2>
        <p className="step1-subtitle">
          분석하려는 토지의 주소를 검색해주세요
        </p>
      </div>

      <div className="search-card">
        <div className="search-form">
          <input
            type="text"
            className="address-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="예: 서울특별시 강남구 테헤란로 123"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <button 
            className="btn-search" 
            onClick={handleSearch} 
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                검색 중...
              </>
            ) : (
              <>
                <i className="fas fa-search"></i>
                주소 검색
              </>
            )}
          </button>
        </div>

        {searched && (
          <div className="suggestions-container">
            {suggestions.length > 0 ? (
              <>
                <div className="suggestions-header">
                  <i className="fas fa-list"></i> {suggestions.length}개의 주소를 찾았습니다
                </div>
                {suggestions.map((s, i) => (
                  <div 
                    key={i} 
                    className="suggestion-item" 
                    onClick={() => handleSelectAddress(s)}
                  >
                    <div className="suggestion-road">
                      <i className="fas fa-map-marker-alt" style={{ marginRight: '8px', color: '#4CAF50' }}></i>
                      {s.road_address}
                    </div>
                    <div className="suggestion-jibun">
                      <i className="fas fa-tag" style={{ marginRight: '8px' }}></i>
                      {s.jibun_address}
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <div className="empty-state">
                <i className="fas fa-search"></i>
                <p>검색 결과가 없습니다.</p>
                <p style={{ fontSize: '14px' }}>다른 주소로 다시 검색해보세요.</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="button-group">
        <button className="btn-back" onClick={onBack}>
          <i className="fas fa-arrow-left" style={{ marginRight: '8px' }}></i>
          이전
        </button>
      </div>
    </div>
  );
};

export default Step1AddressInput;
