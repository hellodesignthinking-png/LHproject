/**
 * Transaction Editor Component
 * ============================
 * 
 * 거래사례 직접 입력/수정 컴포넌트
 * 
 * Features:
 * - 거래사례 추가/삭제
 * - 각 필드 (날짜, 면적, 금액, 거리, 주소) 수정
 * - 실시간 유효성 검증
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-18
 */

import React, { useState } from 'react';
import { Transaction } from '../../types/m1.types';
import './TransactionEditor.css';

interface TransactionEditorProps {
  transactions: Transaction[];
  onChange: (transactions: Transaction[]) => void;
  readonly?: boolean;
}

export const TransactionEditor: React.FC<TransactionEditorProps> = ({
  transactions,
  onChange,
  readonly = false
}) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleAddTransaction = () => {
    const newTransaction: Transaction = {
      date: new Date().toISOString().split('T')[0], // YYYY-MM-DD
      area: 0,
      amount: 0,
      distance: 0,
      address: ''
    };
    onChange([...transactions, newTransaction]);
    setIsEditing(true);
  };

  const handleUpdateTransaction = (index: number, field: keyof Transaction, value: any) => {
    const updated = [...transactions];
    updated[index] = {
      ...updated[index],
      [field]: value
    };
    onChange(updated);
  };

  const handleDeleteTransaction = (index: number) => {
    const updated = transactions.filter((_, i) => i !== index);
    onChange(updated);
  };

  const calculatePricePerSqm = (transaction: Transaction): number => {
    if (transaction.area === 0) return 0;
    return Math.round(transaction.amount / transaction.area);
  };

  return (
    <div className="transaction-editor">
      <div className="transaction-header">
        <h4>
          💰 거래사례 
          <span className="transaction-count">({transactions.length}건)</span>
        </h4>
        {!readonly && (
          <button 
            className="btn-add-transaction" 
            onClick={handleAddTransaction}
            title="거래사례 추가"
          >
            + 거래사례 추가
          </button>
        )}
      </div>

      {transactions.length === 0 ? (
        <div className="transaction-empty">
          <p>📭 등록된 거래사례가 없습니다.</p>
          {!readonly && (
            <button className="btn-add-transaction-empty" onClick={handleAddTransaction}>
              + 첫 거래사례 추가하기
            </button>
          )}
        </div>
      ) : (
        <div className="transaction-list">
          {transactions.map((transaction, index) => (
            <div key={index} className="transaction-item">
              <div className="transaction-item-header">
                <span className="transaction-number">#{index + 1}</span>
                {!readonly && (
                  <button 
                    className="btn-delete-transaction"
                    onClick={() => handleDeleteTransaction(index)}
                    title="삭제"
                  >
                    🗑️ 삭제
                  </button>
                )}
              </div>

              <div className="transaction-fields">
                {/* 거래일자 */}
                <div className="transaction-field">
                  <label>거래일자</label>
                  {readonly ? (
                    <span className="field-value">{transaction.date}</span>
                  ) : (
                    <input
                      type="date"
                      value={transaction.date}
                      onChange={(e) => handleUpdateTransaction(index, 'date', e.target.value)}
                      max={new Date().toISOString().split('T')[0]}
                    />
                  )}
                </div>

                {/* 토지면적 */}
                <div className="transaction-field">
                  <label>토지면적 (㎡)</label>
                  {readonly ? (
                    <span className="field-value">{transaction.area.toLocaleString()} ㎡</span>
                  ) : (
                    <input
                      type="number"
                      value={transaction.area}
                      onChange={(e) => handleUpdateTransaction(index, 'area', parseFloat(e.target.value) || 0)}
                      min="0"
                      step="0.01"
                      placeholder="500.00"
                    />
                  )}
                </div>

                {/* 거래금액 */}
                <div className="transaction-field">
                  <label>거래금액 (원)</label>
                  {readonly ? (
                    <span className="field-value">{transaction.amount.toLocaleString()} 원</span>
                  ) : (
                    <input
                      type="number"
                      value={transaction.amount}
                      onChange={(e) => handleUpdateTransaction(index, 'amount', parseInt(e.target.value) || 0)}
                      min="0"
                      step="1000000"
                      placeholder="500000000"
                    />
                  )}
                </div>

                {/* 단가 (자동 계산) */}
                <div className="transaction-field">
                  <label>단가 (원/㎡)</label>
                  <span className="field-value calculated">
                    {calculatePricePerSqm(transaction).toLocaleString()} 원/㎡
                  </span>
                </div>

                {/* 거리 */}
                <div className="transaction-field">
                  <label>거리 (m)</label>
                  {readonly ? (
                    <span className="field-value">{transaction.distance.toLocaleString()} m</span>
                  ) : (
                    <input
                      type="number"
                      value={transaction.distance}
                      onChange={(e) => handleUpdateTransaction(index, 'distance', parseInt(e.target.value) || 0)}
                      min="0"
                      step="10"
                      placeholder="150"
                    />
                  )}
                </div>

                {/* 주소 */}
                <div className="transaction-field full-width">
                  <label>주소</label>
                  {readonly ? (
                    <span className="field-value">{transaction.address}</span>
                  ) : (
                    <input
                      type="text"
                      value={transaction.address}
                      onChange={(e) => handleUpdateTransaction(index, 'address', e.target.value)}
                      placeholder="서울특별시 강남구 역삼동 123-45"
                    />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 통계 정보 */}
      {transactions.length > 0 && (
        <div className="transaction-summary">
          <h5>📊 통계 요약</h5>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">총 거래건수</span>
              <span className="summary-value">{transactions.length}건</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">평균 단가</span>
              <span className="summary-value">
                {transactions.length > 0
                  ? Math.round(
                      transactions.reduce((sum, t) => sum + calculatePricePerSqm(t), 0) / transactions.length
                    ).toLocaleString()
                  : 0} 원/㎡
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">최고가</span>
              <span className="summary-value">
                {Math.max(...transactions.map(t => calculatePricePerSqm(t))).toLocaleString()} 원/㎡
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">최저가</span>
              <span className="summary-value">
                {Math.min(...transactions.map(t => calculatePricePerSqm(t))).toLocaleString()} 원/㎡
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 안내 메시지 */}
      {!readonly && (
        <div className="transaction-help">
          <p>💡 <strong>Tip:</strong></p>
          <ul>
            <li>최소 3건 이상의 거래사례를 입력하면 감정평가 정확도가 높아집니다</li>
            <li>대상 토지와 가까운 거래사례를 우선적으로 입력하세요</li>
            <li>최근 1년 이내의 거래사례가 가장 유효합니다</li>
            <li>단가는 자동으로 계산됩니다 (거래금액 ÷ 면적)</li>
          </ul>
        </div>
      )}
    </div>
  );
};
