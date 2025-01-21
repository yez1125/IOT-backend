from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from models import get_model
from utils import process_data, get_available_features
import os

app = Flask(__name__)
CORS(app)

# 全局配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA_PATH = os.path.join(BASE_DIR, 'data', 'train_data.xlsx')

# 檢查目錄和文件
data_dir = os.path.join(BASE_DIR, 'data')
if not os.path.exists(data_dir):
    raise FileNotFoundError(
        f"錯誤：找不到必要的數據目錄：{data_dir}\n"
        f"請手動創建 'data' 目錄並確保將 train_data.xlsx 文件放入其中"
    )

if not os.path.exists(TRAIN_DATA_PATH):
    raise FileNotFoundError(
        f"錯誤：找不到訓練數據文件：{TRAIN_DATA_PATH}\n"
        f"請確保將 train_data.xlsx 文件放在正確的位置：\n"
        f"{TRAIN_DATA_PATH}"
    )

try:
    train_data = pd.read_excel(TRAIN_DATA_PATH)
except Exception as e:
    raise Exception(f"讀取訓練數據文件時發生錯誤：{str(e)}\n"
                   f"文件路徑：{TRAIN_DATA_PATH}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        test_data = pd.DataFrame(data['testData'])
        selected_features = data['selectedFeatures']
        model_type = data['modelType']
        
        # 確保所有需要的特徵都存在於測試數據中
        missing_features = [f for f in selected_features if f not in test_data.columns]
        if missing_features:
            raise ValueError(f"測試數據缺少以下特徵: {', '.join(missing_features)}")
            
        # 確保只使用選定的特徵進行訓練和預測
        model = get_model(model_type)
        X_train, y_train = process_data(train_data, selected_features)
        model.fit(X_train, y_train)
        
        # 只使用選定的特徵進行預測
        X_test = test_data[selected_features].copy()

        # 保存園區名稱（如果存在）
        if '園區名稱' in test_data.columns:
            X_test['園區名稱'] = test_data['園區名稱']
        
        if '園區類別' in test_data.columns:
            X_test['園區類別'] = test_data['園區類別']
        
        results = model.predict_with_probabilities(X_test)
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
        port=5003
    )