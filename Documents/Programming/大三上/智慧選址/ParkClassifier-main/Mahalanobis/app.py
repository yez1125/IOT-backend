from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import json
from scipy.stats import boxcox
from scipy.spatial.distance import mahalanobis
from flask_cors import CORS
import os

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)

# 使用絕對路徑載入模型參數
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model_parameters.json")
print(f"嘗試讀取文件：{model_path}")

with open(model_path, "r", encoding="utf-8") as f:
    params = json.load(f)

# 解壓參數
reported_mean = np.array(params["reported_mean"])
approved_mean = np.array(params["approved_mean"])
scientic_mean = np.array(params["scientic_mean"])
other_mean = np.array(params["other_mean"])

reported_cov_inv = np.array(params["reported_cov_inv"])
approved_cov_inv = np.array(params["approved_cov_inv"])
scientic_cov_inv = np.array(params["scientic_cov_inv"])
other_cov_inv = np.array(params["other_cov_inv"])

boxcox_lambdas = params["boxcox_lambdas"]

# 解壓分箱區間
distance_bins = {
    "reported": params["distance_reported_bins"],
    "approved": params["distance_approved_bins"],
    "scientic": params["distance_scientic_bins"]
}

score_bins = {
    "reported": params["score_reported_bins"],
    "approved": params["score_approved_bins"],
    "scientic": params["score_scientic_bins"]
}

# 連續欄位名稱
continuous_columns = [
    "面積(公頃)", "台鐵站距離(公里)", "高鐵站距離(公里)", "捷運站距離(公里)",
    "國際商用機場距離(公里)", "國際商用港口距離(公里)", "快速道路、高速公路交流道距離(公里)",
    "園區半徑3公里(性別比例)", "園區半徑3公里(戶量)", "園區半徑3公里(人口密度)",
    "園區半徑3公里(扶養比)", "園區半徑3公里(扶幼比)", "園區半徑3公里(扶老比)",
    "園區半徑3公里(老化指數)", "園區半徑3公里(戶數)", "園區半徑3公里(人口數)",
    "園區半徑3公里(男性人口數)", "園區半徑3公里(女性人口數)", "其他園區距離(公里)",
    "都市計畫地區距離(公里)","園區半徑5公里(生產中工廠數量)", "園區半徑5公里(製造業使用面積(公頃))"
]

# Box-Cox 轉換函數
def apply_boxcox_transform(data, lambdas):
    """對數據進行 Box-Cox 轉換"""
    transformed_data = []
    for col, value in zip(continuous_columns, data):
        if col in lambdas:  # 若 lambda 存在
            lambda_value = lambdas[col]
            # Box-Cox 轉換，避免負數或零
            value = value if value > 0 else 1e-6
            transformed_data.append(boxcox(value, lambda_value))
        else:
            transformed_data.append(value)  # 未包含於 lambdas 的欄位保持原樣
    return np.array(transformed_data)

# 馬氏距離計算函數
def calculate_mahalanobis_distance(new_data, mean_data, cov_inv):
    return mahalanobis(new_data, mean_data, cov_inv)

# 距離和分數等級計算函數
def calculate_levels(value, bins, labels):
    """根據分箱區間計算等級"""
    for i in range(len(bins) - 1):
        if bins[i] <= value < bins[i + 1]:
            return labels[i]
    return labels[-1]  # 超出最大區間則返回最高等級

@app.route('/')
def index():
    return render_template('Mahalanobis_distance.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    # 讀取上傳的 Excel 檔案
    try:
        data = pd.read_excel(file)
    except Exception as e:
        return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400

    # 確認是否包含「園區類別」欄位
    if '園區名稱' not in data.columns:
        return jsonify({'error': 'Missing "園區名稱" column in input Excel'}), 400

    # 檢查是否包含所有必要欄位
    missing_columns = [col for col in continuous_columns if col not in data.columns]
    if missing_columns:
        return jsonify({'error': f'Missing columns in input Excel: {missing_columns}'}), 400

    results = []
    labels_10 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]  # 距離等級（1 到 10）
    labels_5 = [1, 2, 3, 4, 5]  # 分數等級（1 到 5）

    for _, row in data.iterrows():
        try:
            park_name = row["園區名稱"]  # 獲取園區名稱
            row_data = np.array(row[continuous_columns]).flatten()

            # Box-Cox 轉換
            transformed_data = [
                boxcox(row_data[i], boxcox_lambdas[continuous_columns[i]])
                if continuous_columns[i] in boxcox_lambdas else row_data[i]
                for i in range(len(row_data))
            ]

            # 計算馬氏距離
            distance_to_reported = calculate_mahalanobis_distance(transformed_data, reported_mean, reported_cov_inv)
            distance_to_approved = calculate_mahalanobis_distance(transformed_data, approved_mean, approved_cov_inv)
            distance_to_scientic = calculate_mahalanobis_distance(transformed_data, scientic_mean, scientic_cov_inv)
            distance_to_other = calculate_mahalanobis_distance(transformed_data, other_mean, other_cov_inv)

            # 計算分數
            total_distance = distance_to_reported + distance_to_approved + distance_to_scientic + distance_to_other
            score_reported = 10 * (1 - (distance_to_reported / total_distance))
            score_approved = 10 * (1 - (distance_to_approved / total_distance))
            score_scientic = 10 * (1 - (distance_to_scientic / total_distance))
            score_other = 10 * (1 - (distance_to_other / total_distance))

            # 計算等級
            reported_distance_level = calculate_levels(distance_to_reported, distance_bins["reported"], labels_10)
            approved_distance_level = calculate_levels(distance_to_approved, distance_bins["approved"], labels_10)
            scientic_distance_level = calculate_levels(distance_to_scientic, distance_bins["scientic"], labels_10)

            reported_score_level = calculate_levels(score_reported, score_bins["reported"], labels_5)
            approved_score_level = calculate_levels(score_approved, score_bins["approved"], labels_5)
            scientic_score_level = calculate_levels(score_scientic, score_bins["scientic"], labels_5)

            # 判斷最接近的類別
            distances = {
                "報編工業區": distance_to_reported,
                "編定工業區": distance_to_approved,
                "科技產業園區": distance_to_scientic,
                "其他": distance_to_other
            }
            predicted_category = min(distances, key=distances.get)

            # 將結果添加到列表
            results.append({
                "index": park_name,
                "predicted_category": predicted_category,
                "distances": distances,
                "scores": {
                    "報編工業區": score_reported,
                    "編定工業區": score_approved,
                    "科技產業園區": score_scientic,
                    "其他": score_other
                },
                "levels": {
                    "報編工業區": reported_distance_level,
                    "編定工業區": approved_distance_level,
                    "科技產業園區": scientic_distance_level,
                },
                "score_levels": {
                    "報編工業區": reported_score_level,
                    "編定工業區": approved_score_level,
                    "科技產業園區": scientic_score_level,
                }

            })
        except Exception as e:
            results.append({"園區名稱": row["園區名稱"], "error": str(e)})

    return app.response_class(
        response=json.dumps(results, ensure_ascii=False, indent=2),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5002
    )
