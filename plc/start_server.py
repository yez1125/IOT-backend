#!/usr/bin/env python3
"""
AIoT 監控系統 PLC 本地端 Server 啟動腳本 (FastAPI)
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("="*50)
    print("AIoT 監控系統 PLC 本地端 Server (FastAPI)")
    print("="*50)
    print("正在檢查必要套件...")
    
    # 檢查必要套件
    import fastapi
    import uvicorn
    import pymodbus
    import pymysql
    print("✓ 所有必要套件已安裝")
    
    print("正在啟動伺服器...")
    
    # 導入 FastAPI 應用
    from server import app
    import threading
    
    print("初始化將在 FastAPI startup 事件中自動執行...")
    
    print("\n" + "="*50)
    print("伺服器已啟動!")
    print("="*50)
    print("本地端 API 位址: http://localhost:8000")
    print("網路 API 位址: http://0.0.0.0:8000")
    print("\n🔥 FastAPI 特色:")
    print("  📚 Swagger UI: http://localhost:8000/docs")
    print("  📖 ReDoc: http://localhost:8000/redoc")
    print("  ⚡ 高效能 ASGI 伺服器")
    print("  🛡️ 自動 API 驗證")
    print("\n可用的 API 端點:")
    print("  GET  /                     - API 資訊")
    print("  GET  /api/sensors/current  - 目前感測器資料")
    print("  GET  /api/sensors/temperature - 溫度資料")
    print("  GET  /api/sensors/humidity - 濕度資料")
    print("  GET  /api/sensors/air_quality - 空氣品質資料")
    print("  POST /api/plc/control      - 控制 PLC 輸出")
    print("  GET  /api/status           - 系統狀態")
    print("\n按 Ctrl+C 停止伺服器")
    print("="*50)
    
    # 啟動 uvicorn 伺服器
    uvicorn.run(
        "server:app",
        host="0.0.0.0", 
        port=8000, 
        reload=False,  # 生產環境關閉自動重載
        access_log=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"錯誤: 缺少必要套件 - {e}")
    print("請執行: pip install -r requirements.txt")
    print("主要套件: fastapi, uvicorn, pymodbus, pymysql")
    sys.exit(1)
    
except KeyboardInterrupt:
    print("\n\n正在關閉伺服器...")
    print("伺服器已停止")
    sys.exit(0)
    
except Exception as e:
    print(f"啟動錯誤: {e}")
    sys.exit(1) 