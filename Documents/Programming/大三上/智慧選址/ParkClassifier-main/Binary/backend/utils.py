import pandas as pd
import numpy as np

# 園區類型對應
PARK_TYPE_MAPPING = {
    'reported': '報編工業區',
    'designated': '編定工業區'
}

# 推薦特徵
PARK_TYPE_FEATURES = {
    'reported': [
        '面積(公頃)', 
        '國際商用港口距離(公里)',  
        '園區半徑3公里(戶數)',
        '園區半徑3公里(人口數)', 
        '園區半徑3公里(女性人口數)',
        '園區半徑3公里(人口密度)'
    ],
    'designated': [
        '面積(公頃)', 
        '國際商用港口距離(公里)',  
        '園區半徑3公里(人口密度)',
        '園區半徑3公里(戶量)',
        '台鐵站距離(公里)',
        '快速道路、高速公路交流道距離(公里)',
        '捷運站距離(公里)'
    ]
}

def process_data(data, features, park_type):
    """處理數據，準備二元分類"""
    # 使用使用者選擇的特徵
    X = data[features].copy()
    
    # 將 park_type 轉換為實際的園區類別名稱
    actual_park_type = PARK_TYPE_MAPPING.get(park_type, park_type)
    
    # 創建二元標籤
    y = (data['園區類別'] == actual_park_type).astype(int)
    
    # 打印標籤分布
    print(f"\n園區類別分布:")
    print(data['園區類別'].value_counts())
    print(f"\n目標類別 '{actual_park_type}' 的樣本數: {y.sum()}")
    
    return X, y

def get_available_features(data):
    """獲取可用特徵列表"""
    features_to_exclude = ['園區名稱', '園區類別', '開發依據', '縣市', '鄉鎮區']
    return [col for col in data.columns if col not in features_to_exclude]