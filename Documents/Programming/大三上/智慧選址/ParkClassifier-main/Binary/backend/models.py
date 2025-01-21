from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import numpy as np
from utils import PARK_TYPE_MAPPING

class BinaryClassifier:
    def __init__(self, park_type):
        self.park_type = PARK_TYPE_MAPPING.get(park_type, park_type)
        print(f"初始化分類器，目標園區類型: {self.park_type}")
        
        # 定義模型參數
        self.rf_params = {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42,
            'class_weight': 'balanced'
        }
        
        self.xgb_params = {
            'n_estimators': 100,
            'max_depth': 5,
            'learning_rate': 0.1,
            'random_state': 42,
            'scale_pos_weight': 1
        }
        
    def safe_predict_proba(self, model, X):
        """安全地獲取預測概率"""
        try:
            proba = model.predict_proba(X)
            if proba.shape[1] == 2:
                return proba[:, 1]
            return proba[:, 0]
        except (IndexError, AttributeError):
            # 如果出現問題，返回預測值
            return model.predict(X).astype(float)
        
    def train_and_predict(self, X_train, y_train, X_test, park_names=None):
        # 標準化數據
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 訓算類別權重
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        if pos_count > 0:
            self.xgb_params['scale_pos_weight'] = neg_count / pos_count
        
        print(f"訓練數據分布 - 正例: {pos_count}, 負例: {neg_count}")
        
        # 訓練兩個模型
        xgb = XGBClassifier(**self.xgb_params)
        rf = RandomForestClassifier(**self.rf_params)
        
        xgb.fit(X_train_scaled, y_train)
        rf.fit(X_train_scaled, y_train)
        
        # 獲取模型分數
        xgb_score = xgb.score(X_train_scaled, y_train)
        rf_score = rf.score(X_train_scaled, y_train)
        
        print(f"模型分數 - XGBoost: {xgb_score:.4f}, RandomForest: {rf_score:.4f}")
        
        # 安全地獲取預測概率
        xgb_pred = self.safe_predict_proba(xgb, X_test_scaled)
        rf_pred = self.safe_predict_proba(rf, X_test_scaled)
        
        # 計算加權預測結果
        total_score = xgb_score + rf_score
        xgb_weight = xgb_score / total_score
        rf_weight = rf_score / total_score
        
        weighted_pred = (xgb_pred * xgb_weight) + (rf_pred * rf_weight)
        
        # 轉換為百分比分數
        suitability_scores = weighted_pred * 100
        
        # 確保分數在0-100之間
        suitability_scores = np.clip(suitability_scores, 0, 100)
        
        print(f"分數範圍: {np.min(suitability_scores):.2f} - {np.max(suitability_scores):.2f}")
        
        results = {
            "suitability_scores": [float(score) for score in suitability_scores],
            "park_names": park_names.tolist() if park_names is not None else [f"Sample_{i}" for i in range(len(suitability_scores))]
        }
        
        return results