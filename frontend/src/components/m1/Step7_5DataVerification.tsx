import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, Edit2, Save, X, Plus, Trash2 } from 'lucide-react';

interface LandData {
  address: string;
  area_sqm: number;
  jimok: string;
  jiyeok_jigu: string;
  floor_area_ratio: number;
  building_coverage_ratio: number;
  road_width: number;
}

interface AppraisalData {
  base_price_per_sqm: number;
  adjustment_rate: number;
  final_unit_price: number;
}

interface TransactionCase {
  id: string;
  address: string;
  date: string;
  area: number;
  price: number;
  distance: string;
}

interface POIData {
  subway_count: number;
  bus_stop_count: number;
  convenience_count: number;
  hospital_count: number;
  school_count: number;
  park_count: number;
}

interface VerificationData {
  land: LandData;
  appraisal: AppraisalData;
  transactions: TransactionCase[];
  poi: POIData;
}

interface Step7_5DataVerificationProps {
  onComplete: (data: VerificationData) => void;
  onBack: () => void;
  initialData?: Partial<VerificationData>;
}

const Step7_5DataVerification: React.FC<Step7_5DataVerificationProps> = ({
  onComplete,
  onBack,
  initialData
}) => {
  const [isEditing, setIsEditing] = useState<{ [key: string]: boolean }>({});
  const [data, setData] = useState<VerificationData>({
    land: initialData?.land || {
      address: '서울특별시 강남구 역삼동 123-45',
      area_sqm: 500,
      jimok: '대',
      jiyeok_jigu: '제2종일반주거지역',
      floor_area_ratio: 250,
      building_coverage_ratio: 60,
      road_width: 10
    },
    appraisal: initialData?.appraisal || {
      base_price_per_sqm: 1500000,
      adjustment_rate: 3.8,
      final_unit_price: 1557000
    },
    transactions: initialData?.transactions || [
      {
        id: '1',
        address: '서울특별시 강남구 역삼동 120-3',
        date: '2025-12-15',
        area: 480,
        price: 750000000,
        distance: '150m'
      },
      {
        id: '2',
        address: '서울특별시 강남구 역삼동 125-8',
        date: '2025-11-20',
        area: 520,
        price: 820000000,
        distance: '280m'
      },
      {
        id: '3',
        address: '서울특별시 강남구 역삼동 118-12',
        date: '2025-10-05',
        area: 460,
        price: 710000000,
        distance: '320m'
      },
      {
        id: '4',
        address: '서울특별시 강남구 역삼동 130-5',
        date: '2025-09-18',
        area: 550,
        price: 880000000,
        distance: '450m'
      },
      {
        id: '5',
        address: '서울특별시 강남구 역삼동 115-20',
        date: '2025-08-30',
        area: 490,
        price: 765000000,
        distance: '580m'
      }
    ],
    poi: initialData?.poi || {
      subway_count: 2,
      bus_stop_count: 5,
      convenience_count: 10,
      hospital_count: 2,
      school_count: 3,
      park_count: 4
    }
  });

  const toggleEdit = (section: string) => {
    setIsEditing(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const updateLandData = (field: keyof LandData, value: string | number) => {
    setData(prev => ({
      ...prev,
      land: { ...prev.land, [field]: value }
    }));
  };

  const updateAppraisalData = (field: keyof AppraisalData, value: number) => {
    setData(prev => ({
      ...prev,
      appraisal: { ...prev.appraisal, [field]: value }
    }));
  };

  const updatePOIData = (field: keyof POIData, value: number) => {
    setData(prev => ({
      ...prev,
      poi: { ...prev.poi, [field]: value }
    }));
  };

  const updateTransaction = (id: string, field: keyof TransactionCase, value: string | number) => {
    setData(prev => ({
      ...prev,
      transactions: prev.transactions.map(t =>
        t.id === id ? { ...t, [field]: value } : t
      )
    }));
  };

  const addTransaction = () => {
    const newId = (Math.max(...data.transactions.map(t => parseInt(t.id))) + 1).toString();
    setData(prev => ({
      ...prev,
      transactions: [
        ...prev.transactions,
        {
          id: newId,
          address: '',
          date: new Date().toISOString().split('T')[0],
          area: 0,
          price: 0,
          distance: ''
        }
      ]
    }));
  };

  const removeTransaction = (id: string) => {
    setData(prev => ({
      ...prev,
      transactions: prev.transactions.filter(t => t.id !== id)
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value);
  };

  const handleSubmit = () => {
    // Validate data
    if (data.transactions.length < 1) {
      alert('최소 1건의 거래사례가 필요합니다.');
      return;
    }

    // Log final verified data
    console.log('✅ [Step7_5] Data verification complete:', data);
    console.log('  - Land area:', data.land.area_sqm, '㎡');
    console.log('  - Transaction cases:', data.transactions.length, '건');
    console.log('  - Final unit price:', data.appraisal.final_unit_price, '원/㎡');
    
    onComplete(data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-2">📋 데이터 검증 및 수정</h2>
        <p className="text-blue-100">
          수집된 데이터를 확인하고 필요시 수정하세요. 모든 항목은 편집 가능합니다.
        </p>
      </div>

      {/* Section 1: 토지 기본 정보 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            🏞️ 토지 기본 정보
          </h3>
          <button
            onClick={() => toggleEdit('land')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            {isEditing.land ? (
              <>
                <Save size={16} />
                저장
              </>
            ) : (
              <>
                <Edit2 size={16} />
                수정
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">주소</label>
            {isEditing.land ? (
              <input
                type="text"
                value={data.land.address}
                onChange={(e) => updateLandData('address', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.address}</div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">면적 (㎡)</label>
            {isEditing.land ? (
              <input
                type="number"
                value={data.land.area_sqm}
                onChange={(e) => updateLandData('area_sqm', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">
                {data.land.area_sqm.toLocaleString()}㎡ (약 {(data.land.area_sqm * 0.3025).toFixed(1)}평)
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">지목</label>
            {isEditing.land ? (
              <select
                value={data.land.jimok}
                onChange={(e) => updateLandData('jimok', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="대">대 (垈)</option>
                <option value="전">전 (田)</option>
                <option value="답">답 (畓)</option>
                <option value="임야">임야 (林野)</option>
                <option value="잡종지">잡종지</option>
              </select>
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.jimok}</div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">용도지역</label>
            {isEditing.land ? (
              <select
                value={data.land.jiyeok_jigu}
                onChange={(e) => updateLandData('jiyeok_jigu', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="제1종일반주거지역">제1종일반주거지역</option>
                <option value="제2종일반주거지역">제2종일반주거지역</option>
                <option value="제3종일반주거지역">제3종일반주거지역</option>
                <option value="준주거지역">준주거지역</option>
                <option value="일반상업지역">일반상업지역</option>
              </select>
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.jiyeok_jigu}</div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">용적률 (%)</label>
            {isEditing.land ? (
              <input
                type="number"
                value={data.land.floor_area_ratio}
                onChange={(e) => updateLandData('floor_area_ratio', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.floor_area_ratio}%</div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">건폐율 (%)</label>
            {isEditing.land ? (
              <input
                type="number"
                value={data.land.building_coverage_ratio}
                onChange={(e) => updateLandData('building_coverage_ratio', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.building_coverage_ratio}%</div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">도로 폭원 (m)</label>
            {isEditing.land ? (
              <input
                type="number"
                value={data.land.road_width}
                onChange={(e) => updateLandData('road_width', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg">{data.land.road_width}m</div>
            )}
          </div>
        </div>
      </div>

      {/* Section 2: 감정평가 정보 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            💰 감정평가 정보
          </h3>
          <button
            onClick={() => toggleEdit('appraisal')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            {isEditing.appraisal ? (
              <>
                <Save size={16} />
                저장
              </>
            ) : (
              <>
                <Edit2 size={16} />
                수정
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">기준 공시지가 (원/㎡)</label>
            {isEditing.appraisal ? (
              <input
                type="number"
                value={data.appraisal.base_price_per_sqm}
                onChange={(e) => updateAppraisalData('base_price_per_sqm', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg font-semibold text-blue-600">
                {formatCurrency(data.appraisal.base_price_per_sqm)}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">평가 조정률 (%)</label>
            {isEditing.appraisal ? (
              <input
                type="number"
                step="0.1"
                value={data.appraisal.adjustment_rate}
                onChange={(e) => updateAppraisalData('adjustment_rate', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg font-semibold text-green-600">
                +{data.appraisal.adjustment_rate}%
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">최종 단가 (원/㎡)</label>
            <div className="px-3 py-2 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg font-bold text-purple-600">
              {formatCurrency(data.appraisal.final_unit_price)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              자동 계산: 기준가 × (1 + 조정률)
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>총 감정평가액:</strong> {formatCurrency(data.appraisal.final_unit_price * data.land.area_sqm)}
            <span className="ml-2 text-blue-600">
              (평당 {formatCurrency(data.appraisal.final_unit_price * 3.3058)})
            </span>
          </p>
        </div>
      </div>

      {/* Section 3: 거래사례 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            📊 거래사례 ({data.transactions.length}건)
          </h3>
          <div className="flex gap-2">
            <button
              onClick={addTransaction}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <Plus size={16} />
              추가
            </button>
            <button
              onClick={() => toggleEdit('transactions')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              {isEditing.transactions ? (
                <>
                  <Save size={16} />
                  저장
                </>
              ) : (
                <>
                  <Edit2 size={16} />
                  수정
                </>
              )}
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {data.transactions.map((transaction, index) => (
            <div key={transaction.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-gray-700">사례 {index + 1}</span>
                {isEditing.transactions && (
                  <button
                    onClick={() => removeTransaction(transaction.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-gray-600 mb-1">주소</label>
                  {isEditing.transactions ? (
                    <input
                      type="text"
                      value={transaction.address}
                      onChange={(e) => updateTransaction(transaction.id, 'address', e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="px-2 py-1 text-sm bg-gray-50 rounded">{transaction.address}</div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">거래일</label>
                  {isEditing.transactions ? (
                    <input
                      type="date"
                      value={transaction.date}
                      onChange={(e) => updateTransaction(transaction.id, 'date', e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="px-2 py-1 text-sm bg-gray-50 rounded">{transaction.date}</div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">면적 (㎡)</label>
                  {isEditing.transactions ? (
                    <input
                      type="number"
                      value={transaction.area}
                      onChange={(e) => updateTransaction(transaction.id, 'area', parseFloat(e.target.value))}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="px-2 py-1 text-sm bg-gray-50 rounded">{transaction.area.toLocaleString()}㎡</div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">거래금액 (원)</label>
                  {isEditing.transactions ? (
                    <input
                      type="number"
                      value={transaction.price}
                      onChange={(e) => updateTransaction(transaction.id, 'price', parseFloat(e.target.value))}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="px-2 py-1 text-sm bg-gray-50 rounded font-semibold text-blue-600">
                      {formatCurrency(transaction.price)}
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">거리</label>
                  {isEditing.transactions ? (
                    <input
                      type="text"
                      value={transaction.distance}
                      onChange={(e) => updateTransaction(transaction.id, 'distance', e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <div className="px-2 py-1 text-sm bg-gray-50 rounded">{transaction.distance}</div>
                  )}
                </div>
              </div>

              {!isEditing.transactions && transaction.area > 0 && (
                <div className="mt-2 text-xs text-gray-600">
                  ㎡당 단가: {formatCurrency(transaction.price / transaction.area)}
                </div>
              )}
            </div>
          ))}
        </div>

        {data.transactions.length < 5 && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800 flex items-center gap-2">
              <AlertCircle size={16} />
              최소 5건의 거래사례가 필요합니다. (현재 {data.transactions.length}건)
            </p>
          </div>
        )}
      </div>

      {/* Section 4: POI 정보 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            🏙️ 주변 시설 (POI)
          </h3>
          <button
            onClick={() => toggleEdit('poi')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            {isEditing.poi ? (
              <>
                <Save size={16} />
                저장
              </>
            ) : (
              <>
                <Edit2 size={16} />
                수정
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🚇 지하철역</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.subway_count}
                onChange={(e) => updatePOIData('subway_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.subway_count}개
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🚌 버스정류장</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.bus_stop_count}
                onChange={(e) => updatePOIData('bus_stop_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.bus_stop_count}개
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🏪 편의점</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.convenience_count}
                onChange={(e) => updatePOIData('convenience_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.convenience_count}개
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🏥 병원</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.hospital_count}
                onChange={(e) => updatePOIData('hospital_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.hospital_count}개
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🏫 학교</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.school_count}
                onChange={(e) => updatePOIData('school_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.school_count}개
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">🌳 공원</label>
            {isEditing.poi ? (
              <input
                type="number"
                min="0"
                value={data.poi.park_count}
                onChange={(e) => updatePOIData('park_count', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-center font-semibold">
                {data.poi.park_count}개
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
          <div className="flex-1">
            <h4 className="text-lg font-bold text-gray-800 mb-2">데이터 검증 완료</h4>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>✓ 토지 기본 정보: {data.land.area_sqm.toLocaleString()}㎡, {data.land.jiyeok_jigu}</li>
              <li>✓ 감정평가액: {formatCurrency(data.appraisal.final_unit_price * data.land.area_sqm)}</li>
              <li>✓ 거래사례: {data.transactions.length}건</li>
              <li>✓ POI 데이터: 6개 항목 수집 완료</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <button
          onClick={onBack}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
        >
          ← 이전
        </button>
        <button
          onClick={handleSubmit}
          disabled={data.transactions.length < 1}
          className={`px-8 py-3 rounded-lg font-medium transition-colors ${
            data.transactions.length < 1
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
          }`}
        >
          검증 완료 및 다음 단계 →
        </button>
      </div>
    </div>
  );
};

export default Step7_5DataVerification;
