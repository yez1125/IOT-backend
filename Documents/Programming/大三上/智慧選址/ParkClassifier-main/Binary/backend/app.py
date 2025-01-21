from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from models import BinaryClassifier
from utils import process_data, get_available_features
import os

app = Flask(__name__)
CORS(app)

# 全局配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA_PATH = 'data/train_data.xlsx'

# 讀取並檢查訓練資料
try:
    train_data = pd.read_excel(TRAIN_DATA_PATH)
    print(f"成功讀取訓練資料，共 {len(train_data)} 筆資料")
    print("\n園區類別分布：")
    print(train_data['園區類別'].value_counts())
except Exception as e:
    print(f"讀取訓練資料時發生錯誤：{str(e)}")
    raise

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        test_data = pd.DataFrame(data['testData'])
        selected_features = data['selectedFeatures']
        park_type = data['parkType']
        
        # 確保所有需要的特徵都存在於測試數據中
        missing_features = [f for f in selected_features if f not in test_data.columns]
        for i in test_data.columns:
            print(i)
        if missing_features:
            raise ValueError(f"測試數據缺少以下特徵: {', '.join(missing_features)}")
        
        # 初始化分類器
        classifier = BinaryClassifier(park_type)
        
        # 處理訓練數據
        X_train, y_train = process_data(train_data, selected_features, park_type)
        
        # 只取測試集的特徵數據
        X_test = test_data[selected_features]
        park_names = test_data['園區名稱'] if '園區名稱' in test_data.columns else None
        
        # 訓練和預測
        results = classifier.train_and_predict(X_train, y_train, X_test, park_names)
        
        return jsonify(results)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

@app.route('/get_features', methods=['GET'])
def get_features():
    try:
        features = get_available_features(train_data)
        return jsonify({'features': features})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001
    )