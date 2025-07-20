#!/usr/bin/env python3
"""
Socket 傳輸測試工具
用來快速測試 Socket 連線和資料傳輸
"""

import socket
import json
import time
from datetime import datetime
from socket_config import get_socket_config

def test_socket_connection():
    """測試 Socket 連線"""
    config = get_socket_config()
    
    print("🔍 Socket 連線測試")
    print("=" * 40)
    print(f"目標伺服器: {config['target_host']}:{config['target_port']}")
    print(f"傳輸功能: {'啟用' if config['enable_socket_transmission'] else '停用'}")
    print()
    
    if not config['enable_socket_transmission']:
        print("❌ Socket 傳輸已停用")
        return False
    
    try:
        # 建立 Socket 連線
        print("🔄 嘗試連接...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # 連接到目標伺服器
        sock.connect((config['target_host'], config['target_port']))
        print("✅ 連線成功!")
        
        # 發送測試資料
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'device_id': 'TEST_001',
            'data_type': 'connection_test',
            'message': '這是一個連線測試',
            'values': {
                'temperature': 25.0,
                'humidity': 60.0,
                'pm25': 10,
                'pm10': 15,
                'co2': 400,
                'tvoc': 0.2,
                'status': 'test'
            }
        }
        
        message = json.dumps(test_data, ensure_ascii=False) + '\n'
        encoded_message = message.encode('utf-8')
        
        print("📤 發送測試資料...")
        sock.sendall(encoded_message)
        print(f"✅ 已發送 {len(encoded_message)} 位元組")
        
        sock.close()
        print("✅ 連線已關閉")
        print()
        print("🎉 Socket 傳輸測試成功!")
        return True
        
    except ConnectionRefusedError:
        print(f"❌ 連線被拒絕: 端口 {config['target_port']} 沒有伺服器在監聽")
        print("💡 請確認 Socket 測試伺服器是否正在運行:")
        print("   python socket_test_server.py")
        return False
        
    except socket.timeout:
        print("❌ 連線逾時")
        return False
        
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        return False

def check_port_status():
    """檢查目標端口狀態"""
    config = get_socket_config()
    
    print("🔍 端口狀態檢查")
    print("=" * 40)
    
    try:
        # 嘗試連接來檢查端口是否開放
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((config['target_host'], config['target_port']))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {config['target_port']} 開放且有伺服器監聽")
            return True
        else:
            print(f"❌ 端口 {config['target_port']} 關閉或無伺服器監聽")
            return False
            
    except Exception as e:
        print(f"❌ 檢查端口時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    print("🧪 Socket 傳輸測試工具")
    print("=" * 50)
    
    # 檢查端口狀態
    port_open = check_port_status()
    print()
    
    if port_open:
        # 測試 Socket 連線
        test_socket_connection()
    else:
        print("💡 解決方案:")
        print("1. 啟動 Socket 測試伺服器:")
        print("   python socket_test_server.py")
        print("2. 確認端口設定正確")
        print("3. 檢查防火牆設定")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    main() 