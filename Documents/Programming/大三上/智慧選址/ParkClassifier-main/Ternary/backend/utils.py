from imblearn.combine import SMOTETomek

def process_data(data, features):
    """處理數據，包括特徵選擇和重採樣"""
    X = data[features]
    y = data['園區類別'].apply(convert_to_three_classes)
    
    # 使用 SMOTETomek 處理不平衡數據
    smote_tomek = SMOTETomek(random_state=42)
    X_resampled, y_resampled = smote_tomek.fit_resample(X, y)
    
    return X_resampled, y_resampled

def convert_to_three_classes(category):
    """將園區類別轉換為三分類"""
    if category in ['編定工業區', '報編工業區']:
        return category
    return '其他'

def get_available_features(data):
    """獲取可用特徵列表"""
    features_to_exclude = ['園區名稱', '園區類別', '開發依據', '縣市', '鄉鎮區']
    return [col for col in data.columns if col not in features_to_exclude]