"""
ZeroSite Mid-term: LH 실제 결정 데이터 수집 서비스
LH Pilot Program을 위한 데이터 수집 및 관리 시스템

Author: ZeroSite Development Team
Date: 2025-12-14
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum
import json
import uuid


class LHDecision(str, Enum):
    """LH 심사 결정"""
    APPROVED = "승인"
    REJECTED = "거절"
    CONDITIONAL = "조건부 승인"
    PENDING = "심사 중"


class RiskLevel(str, Enum):
    """리스크 레벨"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class LHCaseData(BaseModel):
    """LH Pilot 개별 케이스 데이터"""
    
    # 기본 정보
    case_id: str = Field(description="케이스 ID (예: PILOT-001)")
    context_id: str = Field(description="ZeroSite Context ID")
    submission_date: date = Field(description="LH 제출일")
    
    # 토지 정보
    address: str = Field(description="토지 주소")
    land_area_sqm: float = Field(description="토지 면적 (㎡)")
    zoning: str = Field(description="용도지역")
    
    # ZeroSite 예측 결과
    predicted_score: float = Field(description="ZeroSite 예측 점수 (0-100)")
    predicted_probability: float = Field(description="예측 승인 확률 (%)")
    predicted_risk: RiskLevel = Field(description="예측 리스크 레벨")
    predicted_grade: str = Field(description="예측 등급 (A/B/C/D/F)")
    
    # LH 실제 결정
    lh_decision: LHDecision = Field(description="LH 실제 결정")
    lh_decision_date: Optional[date] = Field(None, description="LH 결정일")
    lh_review_duration_days: Optional[int] = Field(None, description="심사 기간 (일)")
    lh_conditions: Optional[List[str]] = Field(None, description="승인 조건 (조건부 승인 시)")
    lh_rejection_reasons: Optional[List[str]] = Field(None, description="거절 사유")
    lh_reviewer_comments: Optional[str] = Field(None, description="LH 심사자 코멘트")
    
    # 예측 정확도
    prediction_correct: Optional[bool] = Field(None, description="예측 정확 여부")
    score_difference: Optional[float] = Field(None, description="예측 점수 - 실제 점수 차이")
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LHDataCollectionService:
    """
    LH 데이터 수집 및 관리 서비스
    
    기능:
    1. Pilot 케이스 등록
    2. LH 실제 결정 기록
    3. 예측 정확도 계산
    4. 통계 분석
    5. ML 학습 데이터 준비
    """
    
    def __init__(self, storage_path: str = "/home/user/webapp/data/lh_cases.json"):
        """
        초기화
        
        Args:
            storage_path: 데이터 저장 경로
        """
        self.storage_path = storage_path
        self.cases: Dict[str, LHCaseData] = {}
        self._load_cases()
    
    
    def _load_cases(self):
        """저장된 케이스 로드"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for case_id, case_dict in data.items():
                    self.cases[case_id] = LHCaseData(**case_dict)
        except FileNotFoundError:
            self.cases = {}
    
    
    def _save_cases(self):
        """케이스 저장"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            case_id: case.dict()
            for case_id, case in self.cases.items()
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    
    def register_pilot_case(
        self,
        context_id: str,
        address: str,
        land_area_sqm: float,
        zoning: str,
        predicted_score: float,
        predicted_probability: float,
        predicted_risk: str,
        predicted_grade: str
    ) -> LHCaseData:
        """
        Pilot 케이스 등록
        
        Args:
            context_id: ZeroSite Context ID
            address: 토지 주소
            land_area_sqm: 토지 면적
            zoning: 용도지역
            predicted_score: 예측 점수
            predicted_probability: 예측 확률
            predicted_risk: 예측 리스크
            predicted_grade: 예측 등급
            
        Returns:
            등록된 LHCaseData
        """
        # 케이스 ID 생성
        case_number = len(self.cases) + 1
        case_id = f"PILOT-{case_number:03d}"
        
        # 케이스 데이터 생성
        case = LHCaseData(
            case_id=case_id,
            context_id=context_id,
            submission_date=date.today(),
            address=address,
            land_area_sqm=land_area_sqm,
            zoning=zoning,
            predicted_score=predicted_score,
            predicted_probability=predicted_probability,
            predicted_risk=RiskLevel(predicted_risk),
            predicted_grade=predicted_grade,
            lh_decision=LHDecision.PENDING
        )
        
        # 저장
        self.cases[case_id] = case
        self._save_cases()
        
        return case
    
    
    def record_lh_decision(
        self,
        case_id: str,
        lh_decision: str,
        lh_decision_date: date,
        lh_conditions: Optional[List[str]] = None,
        lh_rejection_reasons: Optional[List[str]] = None,
        lh_reviewer_comments: Optional[str] = None
    ) -> LHCaseData:
        """
        LH 실제 결정 기록
        
        Args:
            case_id: 케이스 ID
            lh_decision: LH 결정 (승인/거절/조건부 승인)
            lh_decision_date: 결정일
            lh_conditions: 승인 조건
            lh_rejection_reasons: 거절 사유
            lh_reviewer_comments: 심사자 코멘트
            
        Returns:
            업데이트된 LHCaseData
        """
        if case_id not in self.cases:
            raise ValueError(f"Case {case_id} not found")
        
        case = self.cases[case_id]
        
        # LH 결정 기록
        case.lh_decision = LHDecision(lh_decision)
        case.lh_decision_date = lh_decision_date
        case.lh_conditions = lh_conditions
        case.lh_rejection_reasons = lh_rejection_reasons
        case.lh_reviewer_comments = lh_reviewer_comments
        
        # 심사 기간 계산
        case.lh_review_duration_days = (lh_decision_date - case.submission_date).days
        
        # 예측 정확도 계산
        case.prediction_correct = self._calculate_prediction_accuracy(case)
        
        # 업데이트 시간 기록
        case.updated_at = datetime.now()
        
        # 저장
        self._save_cases()
        
        return case
    
    
    def _calculate_prediction_accuracy(self, case: LHCaseData) -> bool:
        """
        예측 정확도 계산
        
        Args:
            case: LHCaseData
            
        Returns:
            예측이 정확한지 여부
        """
        # 예측 기준: 70점 이상 = 승인 예상, 70점 미만 = 거절 예상
        predicted_approval = case.predicted_score >= 70
        
        # 실제 결과
        actual_approval = case.lh_decision in [LHDecision.APPROVED, LHDecision.CONDITIONAL]
        
        # 일치 여부
        return predicted_approval == actual_approval
    
    
    def get_case(self, case_id: str) -> Optional[LHCaseData]:
        """케이스 조회"""
        return self.cases.get(case_id)
    
    
    def get_all_cases(self) -> List[LHCaseData]:
        """전체 케이스 조회"""
        return list(self.cases.values())
    
    
    def get_pending_cases(self) -> List[LHCaseData]:
        """심사 중인 케이스 조회"""
        return [
            case for case in self.cases.values()
            if case.lh_decision == LHDecision.PENDING
        ]
    
    
    def get_completed_cases(self) -> List[LHCaseData]:
        """심사 완료된 케이스 조회"""
        return [
            case for case in self.cases.values()
            if case.lh_decision != LHDecision.PENDING
        ]
    
    
    def calculate_accuracy_stats(self) -> Dict[str, Any]:
        """
        전체 정확도 통계 계산
        
        Returns:
            통계 딕셔너리
        """
        completed = self.get_completed_cases()
        
        if not completed:
            return {
                "total_cases": 0,
                "accuracy": 0.0,
                "message": "No completed cases yet"
            }
        
        # 정확도 계산
        correct_predictions = sum(1 for case in completed if case.prediction_correct)
        accuracy = correct_predictions / len(completed) * 100
        
        # 승인/거절 분포
        approved = sum(1 for case in completed if case.lh_decision == LHDecision.APPROVED)
        rejected = sum(1 for case in completed if case.lh_decision == LHDecision.REJECTED)
        conditional = sum(1 for case in completed if case.lh_decision == LHDecision.CONDITIONAL)
        
        # 평균 심사 기간
        avg_duration = sum(
            case.lh_review_duration_days or 0
            for case in completed
        ) / len(completed)
        
        # 점수 분포
        avg_predicted_score = sum(case.predicted_score for case in completed) / len(completed)
        
        return {
            "total_cases": len(completed),
            "accuracy": round(accuracy, 2),
            "correct_predictions": correct_predictions,
            "incorrect_predictions": len(completed) - correct_predictions,
            "lh_decisions": {
                "approved": approved,
                "rejected": rejected,
                "conditional": conditional
            },
            "avg_review_duration_days": round(avg_duration, 1),
            "avg_predicted_score": round(avg_predicted_score, 2)
        }
    
    
    def export_for_ml_training(self) -> List[Dict[str, Any]]:
        """
        ML 학습용 데이터 추출
        
        Returns:
            ML 학습용 데이터 리스트
        """
        completed = self.get_completed_cases()
        
        ml_data = []
        for case in completed:
            # Feature 추출
            features = {
                # Input features
                "land_area_sqm": case.land_area_sqm,
                "zoning": case.zoning,
                "predicted_score": case.predicted_score,
                "predicted_probability": case.predicted_probability,
                "predicted_risk": case.predicted_risk.value,
                
                # Target (Label)
                "lh_decision": case.lh_decision.value,
                "approved": 1 if case.lh_decision in [LHDecision.APPROVED, LHDecision.CONDITIONAL] else 0,
                
                # Metadata
                "case_id": case.case_id,
                "submission_date": str(case.submission_date),
                "lh_decision_date": str(case.lh_decision_date) if case.lh_decision_date else None
            }
            
            ml_data.append(features)
        
        return ml_data
    
    
    def generate_report(self) -> str:
        """
        전체 리포트 생성
        
        Returns:
            Markdown 형식 리포트
        """
        stats = self.calculate_accuracy_stats()
        pending = self.get_pending_cases()
        
        report = f"""# LH Pilot Program 데이터 수집 리포트

**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 전체 통계

- **총 케이스**: {len(self.cases)}개
- **완료**: {stats.get('total_cases', 0)}개
- **심사 중**: {len(pending)}개

---

## 🎯 예측 정확도

- **정확도**: {stats.get('accuracy', 0)}%
- **정확한 예측**: {stats.get('correct_predictions', 0)}개
- **부정확한 예측**: {stats.get('incorrect_predictions', 0)}개

---

## 📈 LH 결정 분포

- **승인**: {stats.get('lh_decisions', {}).get('approved', 0)}개
- **거절**: {stats.get('lh_decisions', {}).get('rejected', 0)}개
- **조건부 승인**: {stats.get('lh_decisions', {}).get('conditional', 0)}개

---

## ⏱️ 심사 기간

- **평균 심사 기간**: {stats.get('avg_review_duration_days', 0)}일

---

## 📊 예측 점수

- **평균 예측 점수**: {stats.get('avg_predicted_score', 0)}/100

---

## 📋 심사 중인 케이스

"""
        
        if pending:
            for case in pending:
                report += f"- {case.case_id}: {case.address} (제출일: {case.submission_date})\n"
        else:
            report += "없음\n"
        
        return report


# Singleton instance
lh_data_collection_service = LHDataCollectionService()
