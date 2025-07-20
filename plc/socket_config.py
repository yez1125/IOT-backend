"""
Socket 連線配置檔案
用於設定 PLC 資料傳輸的目標伺服器
"""

# Socket 傳輸配置
SOCKET_CONFIG = {
    # 目標伺服器設定
    'target_host': '127.0.0.1',  # 目標伺服器 IP (本地端)
    'target_port': 8787,         # 目標伺服器端口
    
    # 連線設定
    'timeout': 5,                # 連線逾時 (秒)
    'retry_interval': 10,        # 重試間隔 (秒)
    'max_retries': 3,           # 最大重試次數
    
    # 資料傳輸設定
    'data_format': 'json',       # 資料格式 (json/raw)
    'encoding': 'utf-8',         # 編碼格式
    'buffer_size': 1024,         # 緩衝區大小
    
    # 功能開關
    'enable_socket_transmission': True,  # 啟用 Socket 傳輸
    'enable_logging': True,              # 啟用詳細日誌
    'enable_reconnect': True,            # 啟用自動重連
}

# 資料格式範本
DATA_TEMPLATE = {
    'timestamp': '',        # 時間戳記
    'device_id': 'PLC_001', # 設備 ID
    'data_type': 'sensor_readings',  # 資料類型
    'values': {
        'temperature': 0.0,
        'humidity': 0.0,
        'pm25': 0,
        'pm10': 0,
        'pm25_average': 0,
        'pm10_average': 0,
        'co2': 0,
        'tvoc': 0.0,
        'status': 'connected'
    }
}

def get_socket_config():
    """取得 Socket 配置"""
    return SOCKET_CONFIG.copy()

def get_data_template():
    """取得資料範本"""
    return DATA_TEMPLATE.copy()

def update_target_server(host, port):
    """
    更新目標伺服器設定
    
    Args:
        host (str): 目標 IP 地址
        port (int): 目標端口
    """
    SOCKET_CONFIG['target_host'] = host
    SOCKET_CONFIG['target_port'] = port
    print(f"✅ 目標伺服器已更新: {host}:{port}")

def enable_socket_transmission(enabled=True):
    """
    啟用/停用 Socket 傳輸
    
    Args:
        enabled (bool): 是否啟用
    """
    SOCKET_CONFIG['enable_socket_transmission'] = enabled
    status = "啟用" if enabled else "停用"
    print(f"✅ Socket 傳輸已{status}")

# 顯示當前配置
def show_config():
    """顯示當前 Socket 配置"""
    print("📡 Socket 傳輸配置:")
    print(f"  目標伺服器: {SOCKET_CONFIG['target_host']}:{SOCKET_CONFIG['target_port']}")
    print(f"  傳輸狀態: {'啟用' if SOCKET_CONFIG['enable_socket_transmission'] else '停用'}")
    print(f"  連線逾時: {SOCKET_CONFIG['timeout']} 秒")
    print(f"  重試設定: {SOCKET_CONFIG['max_retries']} 次, 間隔 {SOCKET_CONFIG['retry_interval']} 秒") 