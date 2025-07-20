#!/usr/bin/env python3
"""
AIoT 監控系統一體化啟動腳本
同時啟動 Socket 接收伺服器和 PLC 資料傳送服務
"""

import sys
import os
import threading
import time
import subprocess

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_socket_receiver():
    """啟動 Socket 接收伺服器"""
    print("🔄 啟動 Socket 接收伺服器...")
    
    try:
        from socket_test_server import SocketTestServer
        
        # 建立 Socket 接收伺服器
        server = SocketTestServer(host='127.0.0.1', port=8787)
        
        print("📡 Socket 接收伺服器已準備就緒")
        server.start()  # 這會阻塞直到伺服器停止
        
    except KeyboardInterrupt:
        print("\n🛑 Socket 接收伺服器已停止")
    except Exception as e:
        print(f"❌ Socket 接收伺服器錯誤: {e}")

def start_plc_sender():
    """啟動 PLC 資料傳送伺服器"""
    print("🔄 啟動 PLC 資料傳送伺服器...")
    
    # 等待一下讓 Socket 接收伺服器先啟動
    time.sleep(2)
    
    try:
        import uvicorn
        from server import app
        
        print("🚀 PLC 資料傳送伺服器已準備就緒")
        
        # 啟動 FastAPI 伺服器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ PLC 資料傳送伺服器錯誤: {e}")

def main():
    """主函數"""
    print("🔥 AIoT 監控系統一體化啟動")
    print("=" * 60)
    print("此腳本將同時啟動:")
    print("  📡 Socket 接收伺服器 (port 8787) - 接收並顯示感測器資料")
    print("  🚀 PLC 資料傳送伺服器 (port 8000) - 讀取 PLC 並傳送資料")
    print("=" * 60)
    
    try:
        # 建立執行緒來啟動 Socket 接收伺服器
        socket_thread = threading.Thread(target=start_socket_receiver, daemon=True)
        socket_thread.start()
        
        # 在主執行緒中啟動 PLC 資料傳送伺服器
        start_plc_sender()
        
    except KeyboardInterrupt:
        print("\n\n🛑 正在關閉所有服務...")
        print("👋 系統已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 啟動錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 檢查必要套件
    try:
        import fastapi
        import uvicorn
        import pymodbus
        import pymysql
        print("✅ 所有必要套件已安裝")
    except ImportError as e:
        print(f"❌ 缺少必要套件: {e}")
        print("請執行: pip install -r requirements.txt")
        sys.exit(1)
    
    main() 