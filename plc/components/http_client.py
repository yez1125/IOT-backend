#!/usr/bin/env python3
"""
HTTP 客戶端模組
用於向後端 API 發送感測器資料
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional

class HTTPClient:
    """
    HTTP 客戶端類別
    用於向後端 API 發送感測器資料
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8787", timeout: int = 5):
        """
        初始化 HTTP 客戶端
        
        Args:
            base_url (str): 後端 API 基礎 URL
            timeout (int): 請求逾時時間 (秒)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.connected = False
        self.last_error = None
        
        # 設定預設標頭
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PLC-Sensor-Client/1.0',
            'Accept': 'application/json'
        })
        
        print(f"🌐 HTTP 客戶端已初始化")
        print(f"   目標 API: {self.base_url}")
        print(f"   逾時設定: {self.timeout} 秒")
    
    def test_connection(self) -> bool:
        """
        測試與後端 API 的連線
        
        Returns:
            bool: 連線是否成功
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            self.connected = response.status_code < 400
            self.last_error = None
            
            if self.connected:
                print(f"✅ HTTP 連線測試成功 (狀態碼: {response.status_code})")
            else:
                print(f"⚠️  HTTP 連線測試失敗 (狀態碼: {response.status_code})")
                
            return self.connected
            
        except requests.exceptions.RequestException as e:
            self.connected = False
            self.last_error = str(e)
            print(f"❌ HTTP 連線測試失敗: {e}")
            return False
    
    def send_sensor_data(self, temperature: float, humidity: float, pm25: int, pm10: int,
                        pm25_avg: int, pm10_avg: int, co2: int, tvoc: float, 
                        status: str = 'connected', endpoint: str = '/api/sensors/data') -> bool:
        """
        發送感測器資料到後端 API
        
        Args:
            temperature (float): 溫度
            humidity (float): 濕度  
            pm25 (int): PM2.5
            pm10 (int): PM10
            pm25_avg (int): PM2.5 平均值
            pm10_avg (int): PM10 平均值
            co2 (int): CO2
            tvoc (float): TVOC
            status (str): 狀態
            endpoint (str): API 端點
            
        Returns:
            bool: 發送是否成功
        """
        try:
            # 準備資料
            sensor_data = {
                'timestamp': datetime.now().isoformat(),
                'device_id': 'PLC_001',
                'data_type': 'sensor_readings',
                'values': {
                    'temperature': temperature,
                    'humidity': humidity,
                    'pm25': pm25,
                    'pm10': pm10,
                    'pm25_average': pm25_avg,
                    'pm10_average': pm10_avg,
                    'co2': co2,
                    'tvoc': tvoc,
                    'status': status
                }
            }
            
            # 發送 POST 請求
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(
                url,
                json=sensor_data,
                timeout=self.timeout
            )
            
            if response.status_code < 400:
                self.connected = True
                self.last_error = None
                print(f"📤 HTTP 資料已發送: {response.status_code} - {len(response.content)} 位元組")
                return True
            else:
                self.connected = False
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ HTTP 發送失敗: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.connected = False
            self.last_error = str(e)
            print(f"❌ HTTP 發送錯誤: {e}")
            return False
    
    def send_custom_data(self, data: Dict[str, Any], endpoint: str = '/api/data') -> Optional[Dict]:
        """
        發送自定義資料到後端 API
        
        Args:
            data (Dict): 要發送的資料
            endpoint (str): API 端點
            
        Returns:
            Optional[Dict]: API 回應資料，發送失敗時返回 None
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code < 400:
                self.connected = True
                self.last_error = None
                return response.json() if response.content else {}
            else:
                self.connected = False
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                return None
                
        except requests.exceptions.RequestException as e:
            self.connected = False
            self.last_error = str(e)
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        取得 HTTP 客戶端狀態
        
        Returns:
            Dict: 狀態資訊
        """
        return {
            'connected': self.connected,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'last_error': self.last_error
        }
    
    def close(self):
        """關閉 HTTP 客戶端"""
        if self.session:
            self.session.close()
            print("✅ HTTP 客戶端已關閉") 