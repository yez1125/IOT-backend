from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from abc import ABC, abstractmethod
from sklearn.exceptions import ConvergenceWarning
import warnings

class BaseModel(ABC):
    def __init__(self, params=None):
        self.model = None
        self.params = params or {}
        self.label_encoder = LabelEncoder()
    
    @abstractmethod
    def fit(self, X, y):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass
    
    @abstractmethod
    def predict_proba(self, X):
        pass
    
    def predict_with_probabilities(self, data):
    # 保存園區名稱和園區類別
        park_names = data['園區名稱'].values if '園區名稱' in data.columns else None
        park_categories = data['園區類別'].values if '園區類別' in data.columns else None
        
        # 移除非特徵列進行預測
        features_only = data.drop(['園區名稱', '園區類別'], axis=1, errors='ignore')
        
        probabilities = self.predict_proba(features_only)
        predictions = self.predict(features_only)
        
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            results.append({
                '園區名稱': park_names[i] if park_names is not None else f"Sample_{i}",
                '園區類別': park_categories[i] if park_categories is not None else "未知",
                '預測機率': {
                    class_name: float(prob * 100)
                    for class_name, prob in zip(self.label_encoder.classes_, probs)
                },
                '預測結果': f"{pred} ({probs.max()*100:.2f}%)"
            })
        return results

class RandomForestModel(BaseModel):
    def __init__(self):
        super().__init__({
            'n_estimators': 300,
            'max_depth': 10,
            'random_state': 42
        })
        self.model = RandomForestClassifier(**self.params)
    
    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.model.fit(X, y_encoded)
        return self
    
    def predict(self, X):
        predictions = self.model.predict(X)
        return self.label_encoder.inverse_transform(predictions)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

class XGBoostModel(BaseModel):
    def __init__(self):
        super().__init__({
            'n_estimators': 200,
            'max_depth': 5,
            'learning_rate': 0.1,
            'random_state': 42
        })
        self.model = XGBClassifier(**self.params)
    
    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.model.fit(X, y_encoded)
        return self
    
    def predict(self, X):
        predictions = self.model.predict(X)
        return self.label_encoder.inverse_transform(predictions)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

class SVMModel(BaseModel):
    def __init__(self):
        super().__init__({
            'kernel': 'rbf',
            'probability': True,
            'random_state': 42
        })
        self.model = SVC(**self.params)
    
    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.model.fit(X, y_encoded)
        return self
    
    def predict(self, X):
        predictions = self.model.predict(X)
        return self.label_encoder.inverse_transform(predictions)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

warnings.filterwarnings('ignore', category=ConvergenceWarning)
class LogisticModel(BaseModel):
    def __init__(self):
        super().__init__({
            'random_state': 42,
            'max_iter': 10000
        })
        self.model = LogisticRegression(**self.params)
    
    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.model.fit(X, y_encoded)
        return self
    
    def predict(self, X):
        predictions = self.model.predict(X)
        return self.label_encoder.inverse_transform(predictions)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

class EnsembleModel(BaseModel):
    def __init__(self, model_type='full'):
        super().__init__()
        self.model_type = model_type
        self.models = self._get_models()
        
    def _get_models(self):
        base_models = [
            ('rf', RandomForestModel().model),
            ('xgb', XGBoostModel().model),
            ('svm', SVMModel().model)
        ]
        
        if self.model_type == 'full':
            base_models.append(('lr', LogisticModel().model))
            
        return base_models
    
    def fit(self, X, y):
        y_encoded = self.label_encoder.fit_transform(y)
        self.model = VotingClassifier(estimators=self.models, voting='soft')
        self.model.fit(X, y_encoded)
        return self
    
    def predict(self, X):
        predictions = self.model.predict(X)
        return self.label_encoder.inverse_transform(predictions)
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

def get_model(model_type):
    """根據模型類型返回相應的模型實例"""
    models = {
        'rf': RandomForestModel,
        'xgb': XGBoostModel,
        'svm': SVMModel,
        'lr': LogisticModel,
        'ensemble_basic': lambda: EnsembleModel(model_type='basic'),
        'ensemble_full': lambda: EnsembleModel(model_type='full')
    }
    
    if model_type not in models:
        raise ValueError(f"不支持的模型類型: {model_type}")
        
    return models[model_type]()