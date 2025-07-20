"""
Socket 客戶端模組
用於將 PLC 感測器資料傳送到目標伺服器
"""

import socket
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from socket_config import get_socket_config, get_data_template

class SocketClient:
    """
    Socket 客戶端類別
    負責將感測器資料透過 TCP Socket 傳送到目標伺服器
    """
    
    def __init__(self):
        """初始化 Socket 客戶端"""
        self.config = get_socket_config()
        self.socket = None
        self.connected = False
        self.retry_count = 0
        self.last_error = None
        self.lock = threading.Lock()  # 執行緒安全
        
        print(f"📡 Socket 客戶端已初始化")
        print(f"   目標: {self.config['target_host']}:{self.config['target_port']}")
    
    def connect(self) -> bool:
        """
        建立 Socket 連線
        
        Returns:
            bool: 連線成功返回 True，失敗返回 False
        """
        if not self.config['enable_socket_transmission']:
            if self.config['enable_logging']:
                print("💡 Socket 傳輸已停用")
            return False
        
        try:
            with self.lock:
                # 建立 TCP Socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.config['timeout'])
                
                # 連線到目標伺服器
                target = (self.config['target_host'], self.config['target_port'])
                self.socket.connect(target)
                
                self.connected = True
                self.retry_count = 0
                self.last_error = None
                
                if self.config['enable_logging']:
                    print(f"✅ Socket 連線成功: {target[0]}:{target[1]}")
                
                return True
                
        except socket.timeout:
            self.last_error = "連線逾時"
            if self.config['enable_logging']:
                print(f"⏰ Socket 連線逾時: {self.config['target_host']}:{self.config['target_port']}")
        except ConnectionRefusedError:
            self.last_error = "連線被拒絕"
            if self.config['enable_logging']:
                print(f"❌ Socket 連線被拒絕: {self.config['target_host']}:{self.config['target_port']}")
        except Exception as e:
            self.last_error = str(e)
            if self.config['enable_logging']:
                print(f"❌ Socket 連線失敗: {e}")
        
        self.connected = False
        return False
    
    def disconnect(self) -> None:
        """關閉 Socket 連線"""
        try:
            with self.lock:
                if self.socket:
                    self.socket.close()
                    self.socket = None
                self.connected = False
                
                if self.config['enable_logging']:
                    print("✅ Socket 連線已關閉")
                    
        except Exception as e:
            if self.config['enable_logging']:
                print(f"⚠️  關閉 Socket 連線時發生錯誤: {e}")
    
    def send_sensor_data(self, temperature: float, humidity: float, 
                        pm25: int, pm10: int, pm25_avg: int, pm10_avg: int,
                        co2: int, tvoc: float, status: str = 'connected') -> bool:
        """
        發送感測器資料
        
        Args:
            temperature (float): 溫度
            humidity (float): 濕度
            pm25 (int): PM2.5
            pm10 (int): PM10
            pm25_avg (int): PM2.5 一小時平均
            pm10_avg (int): PM10 一小時平均
            co2 (int): CO2
            tvoc (float): TVOC
            status (str): 連線狀態
            
        Returns:
            bool: 發送成功返回 True，失敗返回 False
        """
        if not self.config['enable_socket_transmission']:
            return False
        
        # 建立資料包
        data_packet = self._create_data_packet(
            temperature, humidity, pm25, pm10, pm25_avg, pm10_avg, co2, tvoc, status
        )
        
        # 嘗試發送資料
        return self._send_data(data_packet)
    
    def _create_data_packet(self, temperature: float, humidity: float,
                           pm25: int, pm10: int, pm25_avg: int, pm10_avg: int,
                           co2: int, tvoc: float, status: str) -> str:
        """
        建立資料包
        
        Returns:
            str: JSON 格式的資料包
        """
        template = get_data_template()
        template['timestamp'] = datetime.now().isoformat()
        template['values'].update({
            'temperature': temperature,
            'humidity': humidity,
            'pm25': pm25,
            'pm10': pm10,
            'pm25_average': pm25_avg,
            'pm10_average': pm10_avg,
            'co2': co2,
            'tvoc': tvoc,
            'status': status
        })
        
        return json.dumps(template, ensure_ascii=False)
    
    def _send_data(self, data: str) -> bool:
        """
        發送資料到目標伺服器
        
        Args:
            data (str): 要發送的資料
            
        Returns:
            bool: 發送成功返回 True，失敗返回 False
        """
        max_retries = self.config['max_retries']
        
        for attempt in range(max_retries + 1):
            try:
                # 檢查連線狀態
                if not self.connected:
                    if not self.connect():
                        if attempt < max_retries:
                            time.sleep(self.config['retry_interval'])
                            continue
                        return False
                
                # 發送資料
                with self.lock:
                    if self.socket:
                        # 添加換行符號作為資料結束標記
                        message = data + '\n'
                        encoded_message = message.encode(self.config['encoding'])
                        self.socket.sendall(encoded_message)
                        
                        if self.config['enable_logging']:
                            print(f"📤 資料已發送: {len(encoded_message)} 位元組")
                        
                        return True
                
            except socket.error as e:
                self.last_error = f"Socket 錯誤: {e}"
                self.connected = False
                
                if self.config['enable_logging']:
                    print(f"❌ 發送失敗 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    print(f"🔄 {self.config['retry_interval']} 秒後重試...")
                    time.sleep(self.config['retry_interval'])
                    continue
                
            except Exception as e:
                self.last_error = f"未知錯誤: {e}"
                if self.config['enable_logging']:
                    print(f"❌ 發送資料時發生未知錯誤: {e}")
                return False
        
        return False
    
    def is_connected(self) -> bool:
        """
        檢查連線狀態
        
        Returns:
            bool: 連線狀態
        """
        return self.connected
    
    def get_status(self) -> Dict[str, Any]:
        """
        取得 Socket 客戶端狀態
        
        Returns:
            Dict: 狀態資訊
        """
        return {
            'connected': self.connected,
            'target_host': self.config['target_host'],
            'target_port': self.config['target_port'],
            'enabled': self.config['enable_socket_transmission'],
            'retry_count': self.retry_count,
            'last_error': self.last_error
        }
    
    def test_connection(self) -> bool:
        """
        測試連線
        
        Returns:
            bool: 測試成功返回 True
        """
        print(f"🔍 測試 Socket 連線...")
        
        if self.connect():
            # 發送測試資料
            test_data = {
                'timestamp': datetime.now().isoformat(),
                'device_id': 'PLC_001',
                'data_type': 'connection_test',
                'message': 'Socket 連線測試'
            }
            
            success = self._send_data(json.dumps(test_data, ensure_ascii=False))
            self.disconnect()
            
            if success:
                print("✅ Socket 連線測試成功")
            else:
                print("❌ Socket 連線測試失敗")
            
            return success
        else:
            print("❌ 無法建立 Socket 連線")
            return False 