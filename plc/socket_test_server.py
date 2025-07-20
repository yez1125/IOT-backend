#!/usr/bin/env python3
"""
Socket 測試伺服器
用於接收並顯示從 PLC 傳來的感測器資料
"""

import socket
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any

class SocketTestServer:
    """
    Socket 測試伺服器類別
    """
    
    def __init__(self, host='127.0.0.1', port=8787):
        """
        初始化 Socket 伺服器
        
        Args:
            host (str): 綁定的 IP 地址
            port (int): 綁定的端口
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.client_threads = []
        self.data_count = 0
        self.start_time = datetime.now()
        
    def start(self):
        """啟動 Socket 伺服器"""
        try:
            # 建立 TCP Socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 綁定地址和端口
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)  # 最多 5 個等待連線
            
            self.running = True
            self.start_time = datetime.now()
            
            print("=" * 60)
            print("🔥 Socket 測試伺服器已啟動")
            print("=" * 60)
            print(f"📡 綁定地址: {self.host}:{self.port}")
            print(f"⏰ 啟動時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("🎯 等待 PLC 資料傳入...")
            print("👀 按 Ctrl+C 停止伺服器")
            print("=" * 60)
            
            # 開始監聽連線
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"\n🔗 新客戶端連線: {client_address[0]}:{client_address[1]}")
                    
                    # 為每個客戶端建立處理執行緒
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                except socket.error as e:
                    if self.running:
                        print(f"❌ 接受連線時發生錯誤: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ 啟動伺服器時發生錯誤: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """
        處理客戶端連線和資料接收
        
        Args:
            client_socket: 客戶端 Socket
            client_address: 客戶端地址
        """
        client_info = f"{client_address[0]}:{client_address[1]}"
        
        try:
            # 設定接收緩衝區
            buffer = ""
            
            while self.running:
                try:
                    # 接收資料
                    data = client_socket.recv(1024).decode('utf-8')
                    
                    if not data:
                        print(f"🔌 客戶端 {client_info} 已斷線")
                        break
                    
                    # 將接收到的資料加入緩衝區
                    buffer += data
                    
                    # 處理完整的資料包（以換行符號分隔）
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            self.process_data(line.strip(), client_info)
                    
                except socket.timeout:
                    continue
                except socket.error as e:
                    print(f"❌ 接收資料時發生錯誤: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ 處理客戶端 {client_info} 時發生錯誤: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def process_data(self, data: str, client_info: str):
        """
        處理接收到的資料
        
        Args:
            data (str): 接收到的 JSON 資料
            client_info (str): 客戶端資訊
        """
        try:
            # 解析 JSON 資料
            json_data = json.loads(data)
            self.data_count += 1
            
            # 顯示資料
            self.display_sensor_data(json_data, client_info)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析錯誤 (來源: {client_info}): {e}")
            print(f"原始資料: {data[:100]}...")
        except Exception as e:
            print(f"❌ 處理資料時發生錯誤: {e}")
    
    def display_sensor_data(self, data: Dict[str, Any], client_info: str):
        """
        顯示感測器資料
        
        Args:
            data (Dict): 感測器資料
            client_info (str): 客戶端資訊
        """
        print(f"\n📊 #{self.data_count:04d} 感測器資料 (來源: {client_info})")
        print(f"⏰ 時間: {data.get('timestamp', 'N/A')}")
        print(f"🏷️  設備: {data.get('device_id', 'N/A')}")
        print(f"📁 類型: {data.get('data_type', 'N/A')}")
        
        if 'values' in data:
            values = data['values']
            print("📈 感測器數值:")
            print(f"   🌡️  溫度: {values.get('temperature', 'N/A')} °C")
            print(f"   💧 濕度: {values.get('humidity', 'N/A')} %")
            print(f"   🌫️  PM2.5: {values.get('pm25', 'N/A')} μg/m³")
            print(f"   🌫️  PM10: {values.get('pm10', 'N/A')} μg/m³")
            print(f"   📊 PM2.5 平均: {values.get('pm25_average', 'N/A')} μg/m³")
            print(f"   📊 PM10 平均: {values.get('pm10_average', 'N/A')} μg/m³")
            print(f"   🫁 CO2: {values.get('co2', 'N/A')} ppm")
            print(f"   💨 TVOC: {values.get('tvoc', 'N/A')} mg/m³")
            print(f"   🔗 狀態: {values.get('status', 'N/A')}")
        
        print("-" * 50)
    
    def stop(self):
        """停止 Socket 伺服器"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        # 等待客戶端執行緒結束
        for thread in self.client_threads:
            thread.join(timeout=1)
        
        runtime = datetime.now() - self.start_time
        print(f"\n🛑 Socket 測試伺服器已停止")
        print(f"📊 統計資訊:")
        print(f"   ⏱️  運行時間: {runtime}")
        print(f"   📦 接收資料包: {self.data_count} 個")
        print("👋 感謝使用!")

def main():
    """主函數"""
    server = SocketTestServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 接收到停止信號...")
    except Exception as e:
        print(f"❌ 伺服器運行時發生錯誤: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main() 