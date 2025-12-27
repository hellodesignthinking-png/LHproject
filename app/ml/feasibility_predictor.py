"""
ZeroSite v4.0 - Machine Learning Model
타당성 자동 예측 모델
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
from typing import Dict, Tuple, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FeasibilityPredictor:
    """
    타당성 자동 예측 모델
    
    과거 분석 데이터를 학습하여 새로운 부지의 사업 타당성을 예측합니다.
    """
    
    def __init__(self, model_path: str = "models/feasibility_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = [
            'area_sqm',
            'far_percent',
            'bcr_percent',
            'asking_price_per_sqm',
            'location_score',
            'development_score',
            'zone_encoded'
        ]
        
        # 모델이 이미 학습되어 있으면 로드
        if self.model_path.exists():
            self.load_model()
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        특징 추출 및 전처리
        
        Args:
            data: 원시 데이터 DataFrame
        
        Returns:
            전처리된 특징 DataFrame
        """
        df = data.copy()
        
        # 파생 변수 생성
        df['asking_price_per_sqm'] = df['asking_price_million'] * 1_000_000 / df['area_sqm']
        
        # 용도지역 인코딩
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            df['zone_encoded'] = self.label_encoder.fit_transform(df['zone'])
        else:
            df['zone_encoded'] = self.label_encoder.transform(df['zone'])
        
        # 필요한 특징만 선택
        features = df[self.feature_names]
        
        return features
    
    def train(
        self,
        training_data: pd.DataFrame,
        target_column: str = 'final_verdict',
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        모델 학습
        
        Args:
            training_data: 학습 데이터 (특징 + 타겟)
            target_column: 타겟 컬럼 이름 (GO, CONDITIONAL_GO, NO_GO)
            test_size: 테스트 데이터 비율
            random_state: 랜덤 시드
        
        Returns:
            평가 메트릭 딕셔너리
        """
        logger.info(f"Starting model training with {len(training_data)} samples")
        
        # 특징 추출
        X = self.prepare_features(training_data)
        y = training_data[target_column]
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        # 특징 스케일링
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 모델 학습
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # 모델 평가
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        }
        
        logger.info(f"Model training complete. Metrics: {metrics}")
        logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
        
        # 특징 중요도
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\nFeature Importance:\n{feature_importance}")
        
        return metrics
    
    def predict(self, land_data: Dict) -> Dict[str, any]:
        """
        타당성 예측
        
        Args:
            land_data: 부지 정보 딕셔너리
        
        Returns:
            예측 결과 딕셔너리
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load_model()")
        
        # DataFrame으로 변환
        df = pd.DataFrame([land_data])
        
        # 특징 추출
        features = self.prepare_features(df)
        
        # 스케일링
        features_scaled = self.scaler.transform(features)
        
        # 예측
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # 결과 구성
        classes = self.model.classes_
        confidence_dict = {
            cls: float(prob)
            for cls, prob in zip(classes, probabilities)
        }
        
        result = {
            'prediction': prediction,
            'confidence': float(max(probabilities)),
            'probabilities': confidence_dict,
            'recommendation': self._generate_recommendation(prediction, confidence_dict)
        }
        
        logger.info(f"Prediction: {prediction} (confidence: {result['confidence']:.2%})")
        
        return result
    
    def _generate_recommendation(self, prediction: str, probabilities: Dict[str, float]) -> str:
        """추천 메시지 생성"""
        confidence = probabilities[prediction]
        
        if prediction == "GO":
            if confidence > 0.8:
                return "높은 확률로 사업성이 우수합니다. 적극 추천합니다."
            elif confidence > 0.6:
                return "사업성이 양호합니다. 추가 검토 후 진행을 권장합니다."
            else:
                return "사업성이 있으나 신중한 검토가 필요합니다."
        
        elif prediction == "CONDITIONAL_GO":
            if confidence > 0.7:
                return "조건부 승인입니다. 위험 요소를 확인하고 대응책을 마련하세요."
            else:
                return "조건부 승인이나 불확실성이 높습니다. 신중한 판단이 필요합니다."
        
        else:  # NO_GO
            if confidence > 0.8:
                return "사업성이 낮습니다. 진행을 권장하지 않습니다."
            else:
                return "사업성이 불확실합니다. 추가 정보 수집 후 재평가를 권장합니다."
    
    def save_model(self):
        """모델 저장"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """모델 로드"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        
        logger.info(f"Model loaded from {self.model_path}")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """특징 중요도 반환"""
        if self.model is None:
            raise ValueError("Model not trained")
        
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)


# 샘플 데이터 생성 함수
def generate_sample_training_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    학습용 샘플 데이터 생성
    
    실제 프로덕션에서는 과거 분석 결과를 데이터베이스에서 조회해야 합니다.
    """
    np.random.seed(42)
    
    # 랜덤 데이터 생성
    data = {
        'area_sqm': np.random.uniform(300, 2000, n_samples),
        'far_percent': np.random.uniform(150, 300, n_samples),
        'bcr_percent': np.random.uniform(40, 80, n_samples),
        'asking_price_million': np.random.uniform(3000, 30000, n_samples),
        'location_score': np.random.uniform(60, 95, n_samples),
        'development_score': np.random.uniform(50, 90, n_samples),
        'zone': np.random.choice([
            '제1종일반주거지역',
            '제2종일반주거지역',
            '제3종일반주거지역',
            '준주거지역'
        ], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # 타겟 변수 생성 (규칙 기반)
    def determine_verdict(row):
        score = (
            (row['location_score'] * 0.3) +
            (row['development_score'] * 0.2) +
            (row['far_percent'] / 3) +
            (row['bcr_percent'] / 2)
        )
        
        if score > 120:
            return 'GO'
        elif score > 90:
            return 'CONDITIONAL_GO'
        else:
            return 'NO_GO'
    
    df['final_verdict'] = df.apply(determine_verdict, axis=1)
    
    return df
